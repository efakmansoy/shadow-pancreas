"""SENTETİK (SYNTHETIC) demo veri üreteci — gerçek kişi verisi İÇERMEZ.

FULLY SYNTHETIC DATA GENERATOR. Every value written by this script is randomly generated from a
hand-written toy model of a Type 1 diabetic user's day. No real person's glucose, insulin or menu
records are read, copied or fitted. The output is for demo / testing of the public repo only and is
NOT medical data.

Çıktı (data/synthetic/, src/prepare.py ile aynı şema / sütun adları):
  daily_log.csv            30 gün (2026-03-02 .. 2026-03-31): yatış, lantus, öğün açlık/insülin/tokluk, ek doz
  menu_days.csv            gün x öğün menüleri (items JSON + m_* hücreleri)
  events_all.csv           öğün başına bir satır (prev_bg, r7_*, status ...; prepare.py mantığıyla)
  event_nutrition_all.csv  nutrition.build_event_nutrition ile (projenin kendi besin tabloları)

Menüler data/nutrition/aliases_*.csv içinde geçen standart yemek yazımlarından elle kurulmuş
havuzlardan rastgele (tohumlu) seçilir; böylece eşleştirici/besin tabloları hepsini çözer.

Sentetik glikoz modeli (gerçek veriye uydurulmamış, tamamen elle seçilmiş):
  açlık   : önceki ölçüme (gece yatış / önceki öğünün tokluğu) kısmi bağlı + gürültü, ~70-280 mg/dL
  insülin : esas olarak açlığa bağlı (düzeltme dozu), karbonhidrata çok az; 1..14 ünite, 0.5 adım
  tokluk  : açlığa + öğün karbonhidratına hafif bağlı, insülinin "beklenen"den sapmasına bağlı, gürültülü
Kullanım: python tools/make_synthetic.py [--seed N]
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shadow_pancreas import nutrition as NU  # noqa: E402

OUT = ROOT / "data" / "synthetic"
START, DAYS = date(2026, 3, 2), 30
MEALS = ["kahvalti", "ogle", "aksam"]
COMPS = ["corba", "ana", "pilav", "yogurt", "salata", "tatli", "kahvaltilik", "hamur", "diger"]
GUN = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

# --- menü havuzları (alias tablosundaki standart yazımlar) ---------------------------------------
SOUPS = ["Mercimek Çorbası", "Ezogelin Çorbası", "Tarhana Çorbası", "Yayla Çorbası", "Domates Çorba",
         "Şehriyeli Tavuk Çorba", "Sebze Çorbası", "Kremalı Mantar Çorba", "Düğün Çorbası", "Brokoli Çorba"]
# ağırlıklar: bazı ana yemekler ay içinde sık tekrar eder (benzer vaka bulunabilsin)
MAINS = {"Izgara Köfte": 6, "Etli Kuru Fasulye": 5, "Sebzeli Piliç": 5, "Etli Nohut": 4, "Piliç Baget Fırın": 4,
         "Karnıyarık": 3, "Etli Taze Fasulye": 3, "Dana Kavurma": 3, "İzmir Köfte": 3, "Et Döner": 3,
         "Patlıcan Musakka": 2, "Orman Kebabı": 2, "Etli Biber Dolma": 2}
GARNISH = {"Izgara Köfte": "Patates Püresi", "Dana Kavurma": "Patates Püresi", "Piliç Baget Fırın": "Elma Dilim Patates",
           "Et Döner": "Lavaş"}
RICE = {"Pirinç Pilavı": 5, "Bulgur Pilavı": 4, "Şehriyeli Pirinç Pilavı": 3, "Makarna": 2,
        "Napoliten Soslu Makarna": 2, "Sebzeli Bulgur Pilavı": 2, "Peynirli Makarna": 1, "Su Böreği": 1}
DESSERTS = {"Meyve": 5, "Fırın Sütlaç": 3, "Kazandibi": 2, "Revani": 2, "Şekerpare": 2, "Sakızlı Muhallebi": 2,
            "Islak Kek": 2, "Supangle": 1, "Baklava": 1, "Kemalpaşa Tatlısı": 1}
SALADS = ["Mevsim Yeşillikleri", "Salata / Zeytinyağlı"]
PLATE = ["Beyaz Peynir", "Zeytin", "Çeri Domates", "Salatalık", "Kaşar Peyniri", "Tereyağı", "Tahin Pekmez"]
BF_MAIN = {"Omlet": 3, "Menemen": 3, None: 2}
BF_PASTRY = {"Simit": 3, "Poğaça": 2, "Açma": 2, "Zeytinli Açma": 1, "Kaşarlı Poğaça": 1}
BF_SWEET = {"Bal": 2, "Reçel": 2, None: 3}


def pick(rng, d: dict):
    keys = list(d)
    p = np.array([d[k] for k in keys], float)
    return keys[rng.choice(len(keys), p=p / p.sum())]


def make_menu(rng, meal: str, recent: list[str]) -> list[dict]:
    it = []
    add = lambda comp, raw: it.append({"comp": comp, "raw": raw, "mods": []})  # noqa: E731
    if meal == "kahvalti":
        for x in rng.choice(PLATE, size=int(rng.integers(3, 6)), replace=False):
            add("kahvaltilik", str(x))
        m = pick(rng, BF_MAIN)
        if m:
            add("ana", m)
        add("hamur", pick(rng, BF_PASTRY))
        s = pick(rng, BF_SWEET)
        if s:
            add("tatli", s)
        if rng.random() < 0.4:
            add("yogurt", "Süt")
        if rng.random() < 0.25:
            add("diger", "Sosis")
        add("diger", "Çay")
        return it
    add("corba", str(rng.choice(SOUPS)))
    m = pick(rng, MAINS)
    for _ in range(5):  # aynı ana yemek art arda iki öğünde gelmesin
        if m not in recent:
            break
        m = pick(rng, MAINS)
    add("ana", m)
    if m in GARNISH and rng.random() < 0.7:
        add("ana", GARNISH[m])
    add("pilav", pick(rng, RICE))
    add("salata", str(rng.choice(SALADS)))
    if rng.random() < 0.6:
        add("yogurt", "Yoğurt")
    add("tatli", pick(rng, DESSERTS))
    return it


def cells(items: list[dict]) -> dict:
    out = {}
    for c in COMPS:
        raws = [x["raw"] for x in items if x["comp"] == c]
        out[f"m_{c}"] = ("; " if c == "kahvaltilik" else ", ").join(raws) if raws else None
    return out


def status(v):
    return "hipo" if v < 70 else ("hiper" if v > 180 else "hedef")


def r5(x):  # glikoz tam sayı mg/dL
    return float(int(round(x)))


def main(seed: int = 20260302):
    rng = np.random.default_rng(seed)
    OUT.mkdir(parents=True, exist_ok=True)
    days = [START + timedelta(days=i) for i in range(DAYS)]

    # 1) menüler
    menu_rows, recent = [], []
    for d in days:
        for meal in MEALS:
            items = make_menu(rng, meal, recent)
            if meal != "kahvalti":
                recent = (recent + [x["raw"] for x in items if x["comp"] == "ana"])[-2:]
            menu_rows.append(dict(date=d.isoformat(), meal=meal, gun=GUN[d.weekday()], is_weekend=d.weekday() >= 5,
                                  holiday=None, items=items, **cells(items)))

    # 2) sentetik glikoz/insülin günlüğü
    base_ins = {"kahvalti": 4.0, "ogle": 4.5, "aksam": 4.5}
    log, prev_yatis = [], float(rng.normal(150, 30))
    by_key = {(r["date"], r["meal"]): r["items"] for r in menu_rows}
    for d in days:
        row = {"date": d.isoformat(), "yatis_ekdoz": None, "lantus": 18.0 if d < date(2026, 3, 16) else 19.0,
               "gece03": None, "gece_ekdoz": None}
        prev = prev_yatis
        for meal in MEALS:
            carb = NU.meal_vector(by_key[(d.isoformat(), meal)])["total"]["carb"]
            ac = float(np.clip(0.45 * prev + 0.55 * 125 + rng.normal(0, 44), 68, 285))
            if rng.random() < 0.05:  # ara sıra düşük açlık
                ac = float(rng.uniform(62, 80))
            exp_ins = base_ins[meal] + (ac - 120) / 35 + 0.004 * (carb - 90)
            ins = float(np.clip(np.round((exp_ins + rng.normal(0, 0.8)) * 2) / 2, 1, 14))
            tk = (0.5 * ac + 68 + 0.30 * (carb - 90) - 14 * (ins - exp_ins) + rng.normal(0, 32))
            if rng.random() < 0.04:  # birkaç tokluk hipo vakası
                tk = float(rng.uniform(52, 68))
            tk = float(np.clip(tk, 50, 310))
            ek = float(rng.choice([1.0, 1.5, 2.0])) if ac > 230 and rng.random() < 0.5 else None
            row.update({f"{meal}_aclik": r5(ac), f"{meal}_insulin": ins, f"{meal}_tokluk": r5(tk), f"{meal}_ekdoz": ek})
            prev = tk
        yatis = float(np.clip(0.5 * prev + 70 + rng.normal(0, 30), 75, 280))
        row["yatis"] = r5(yatis)
        if yatis > 220 and rng.random() < 0.6:
            row["yatis_ekdoz"] = float(rng.choice([1.0, 1.5, 2.0]))
        if rng.random() < 0.1:
            row["gece03"] = r5(np.clip(yatis * 0.8 + rng.normal(0, 20), 70, 250))
        prev_yatis = yatis
        log.append(row)
    cols = ["date", "yatis", "yatis_ekdoz", "lantus", "gece03", "gece_ekdoz"] + [
        f"{m}_{k}" for m in MEALS for k in ("aclik", "insulin", "tokluk", "ekdoz")]
    log = pd.DataFrame(log)[cols]
    L = log.assign(date=pd.to_datetime(log.date).dt.date).set_index("date")

    # 3) olaylar (src/prepare.py mantığı)
    events = []
    for mr in menu_rows:
        d, meal = date.fromisoformat(mr["date"]), mr["meal"]
        R = L.loc[d]
        idx = MEALS.index(meal)
        if idx > 0:
            prev, prev_kind = R[f"{MEALS[idx - 1]}_tokluk"], f"{MEALS[idx - 1]}_tokluk"
        else:
            pd_ = d - timedelta(days=1)
            prev = L.loc[pd_, "gece03"] if pd_ in L.index else None
            if prev is None or pd.isna(prev):
                prev = L.loc[pd_, "yatis"] if pd_ in L.index else None
                prev_kind = "onceki_yatis"
            else:
                prev_kind = "gece03"
        win = L.loc[(L.index >= d - timedelta(days=7)) & (L.index < d)]
        allt = pd.concat([win[f"{x}_tokluk"] for x in MEALS]).dropna()
        r7m = win[f"{meal}_tokluk"].dropna()
        tk = R[f"{meal}_tokluk"]
        events.append(dict(
            event_id=f"{d.isoformat()}_{meal}", date=d.isoformat(), meal=meal, month=d.month, dow=d.weekday(),
            excluded=None, aclik=R[f"{meal}_aclik"], insulin=R[f"{meal}_insulin"], ekdoz=R[f"{meal}_ekdoz"],
            prev_bg=None if prev is None or pd.isna(prev) else prev, prev_kind=prev_kind,
            r7_all=allt.mean() if len(allt) >= 5 else None, r7_meal=r7m.mean() if len(r7m) >= 3 else None,
            r7_hipo=int((allt < 70).sum()) if len(allt) else None, tokluk=tk, status=status(tk),
            items=json.dumps(mr["items"], ensure_ascii=False), **{k: mr[k] for k in mr if k.startswith("m_")}))
    ev = pd.DataFrame(events)

    md = pd.DataFrame(menu_rows)
    md["items"] = md["items"].map(lambda x: json.dumps(x, ensure_ascii=False))
    md = md[["date", "meal", "gun", "is_weekend", "holiday", "items"] + [f"m_{c}" for c in COMPS]]

    nut = NU.build_event_nutrition(ev)

    log.to_csv(OUT / "daily_log.csv", index=False)
    md.to_csv(OUT / "menu_days.csv", index=False)
    ev.to_csv(OUT / "events_all.csv", index=False)
    nut.to_csv(OUT / "event_nutrition_all.csv", index=False)
    print(f"SYNTHETIC data -> {OUT}: log={len(log)} menu={len(md)} events={len(ev)} nutrition={len(nut)}")
    print("status:", ev.status.value_counts().to_dict(), "| unknown items:", int(nut.n_unknown.sum()))


if __name__ == "__main__":
    main(int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 20260302)
