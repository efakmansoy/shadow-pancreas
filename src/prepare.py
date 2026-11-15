"""Ham Excel dosyalarından öğün olaylarını üretir.

Girdi : data/raw/seker_takip_yemekli.xlsx, data/raw/menu_2026.xlsx
Çıktı : data/events.csv        (öğün başına bir satır, ölçümler + menü kalemleri)
        data/menu_days.csv     (menüsü olan tüm gün/öğünler; olay olsun olmasın, demo ve "yarın" uyarısı için)
        data/items_raw.csv     (benzersiz menü kalemi yazımları ve sıklıkları)

Kurallar (plan.html "Veri" bölümü):
- hafta sonu, resmi tatil ve arife günleri çıkarılır
- menüsü olmayan öğün çıkarılır
- açlık veya tokluk ölçümü eksik (boş ya da 0) olan öğün çıkarılır
- Q sütunu ve ORTALAMALAR sütunları kullanılmaz
"""
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"

# 2026 resmi tatilleri + arifeler (yalnızca bu tarihler; hafta sonları ayrıca düşülür)
HOLIDAYS = {
    date(2026, 1, 1): "Yılbaşı",
    date(2026, 3, 19): "Ramazan Bayramı arifesi",
    date(2026, 3, 20): "Ramazan Bayramı",
    date(2026, 3, 21): "Ramazan Bayramı",
    date(2026, 3, 22): "Ramazan Bayramı",
    date(2026, 4, 23): "Ulusal Egemenlik ve Çocuk Bayramı",
    date(2026, 5, 1): "Emek ve Dayanışma Günü",
    date(2026, 5, 19): "Atatürk'ü Anma, Gençlik ve Spor Bayramı",
    date(2026, 5, 26): "Kurban Bayramı arifesi",
    date(2026, 5, 27): "Kurban Bayramı",
    date(2026, 5, 28): "Kurban Bayramı",
    date(2026, 5, 29): "Kurban Bayramı",
    date(2026, 5, 30): "Kurban Bayramı",
    date(2026, 7, 15): "Demokrasi ve Milli Birlik Günü",
    date(2026, 8, 30): "Zafer Bayramı",
    date(2026, 10, 28): "Cumhuriyet Bayramı arifesi",
    date(2026, 10, 29): "Cumhuriyet Bayramı",
}

MEALS = {  # öğün -> (açlık, insülin, tokluk, ek doz) sütun indeksleri
    "kahvalti": (1, 2, 3, 4),
    "ogle": (5, 6, 7, 8),
    "aksam": (9, 10, 11, 12),
}
MENU_MEAL = {"Kahvaltı": "kahvalti", "Öğle Yemeği": "ogle", "Akşam Yemeği": "aksam"}
COMPONENTS = ["Çorba", "Ana Yemek", "Pilav / Makarna", "Yoğurt / Süt", "Salata / Yeşillik",
              "Tatlı / Meyve", "Kahvaltılık Tabağı", "Hamur İşi", "Diğer"]
COMP_KEY = {"Çorba": "corba", "Ana Yemek": "ana", "Pilav / Makarna": "pilav", "Yoğurt / Süt": "yogurt",
            "Salata / Yeşillik": "salata", "Tatlı / Meyve": "tatli", "Kahvaltılık Tabağı": "kahvaltilik",
            "Hamur İşi": "hamur", "Diğer": "diger"}
# İçecek/çeşni gibi besin etkisi ihmal edilebilir ya da ölçülmeyen kalemler ayrıca işaretlenir (normalize aşamasında)


def num(v):
    """0 ya da boş -> None (eksik veri)."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f == 0 else f


GARNISH_MODS = {"domates", "biber", "maydanoz", "maydanozlu", "kırmızı", "soğuk", "zerdeçal", "susam",
                "napoliten", "arabiatta", "salçalı", "püreli", "mantarlı", "kaşarlı", "beyaz soslu",
                "kehribar soslu", "meksika sos", "meksika soslu", "kendi sosu"}


def _top_split(s: str, seps: str) -> list[str]:
    """Parantez dışındaki ayırıcılarla böl."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if depth == 0 and ch in seps:
            out.append(cur); cur = ""
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]


def _is_modifier(part: str) -> bool:
    low = part.lower().replace("İ", "i")
    if low in GARNISH_MODS:
        return True
    last = low.split()[-1]
    return bool(re.search(r"(l[ıiuü]|s[ıiuü]z|sos|sosu|soslu|usulü)$", last))


def split_items(comp: str, text) -> list[dict]:
    """Bir menü hücresini kalemlere ayırır.

    Her kalem: {"raw": görünen ad, "mods": [niteleyiciler]}.
    'Hamburger (Elma Dilim Patates, Soğan Halkası)' -> Hamburger + Elma Dilim Patates + Soğan Halkası
    'Domates Çorba (Kaşarlı)' -> 'Kaşarlı Domates Çorba'
    'Tepsi Kebabı (Püre, Domates, Biber)' -> 'Tepsi Kebabı' (mods: Domates, Biber) + 'Püre'
    'Et Döner / Cips Patates - Lavaş' -> Et Döner + Cips Patates + Lavaş
    """
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return []
    s = str(text).strip()
    if not s:
        return []
    seps = ";" if comp in ("Kahvaltılık Tabağı",) else ";,"
    out = []
    for part in _top_split(s, seps):
        groups = re.findall(r"\(([^()]*)\)", part)
        base = re.sub(r"\s*\([^()]*\)?", " ", part)
        base = re.sub(r"\s+", " ", base).strip(" )")
        extra, mods = [], []
        for g in groups:
            for q in re.split(r"[,;]", g):
                q = q.strip()
                if not q:
                    continue
                if _is_modifier(q):
                    mods.append(q)
                else:
                    extra.append(q)
        subs = [x.strip() for x in re.split(r"\s*/\s*|\s+-\s+", base) if x.strip()]
        if comp == "Salata / Yeşillik" and base.lower().startswith("salata"):
            subs = [base]  # 'Salata / Zeytinyağlı' tek kalem
        for i, sub in enumerate(subs):
            m_ = mods if i == 0 else []
            # tek kelimelik sıfat niteleyicileri ada ön ek olarak koy (Kaşarlı Domates Çorba gibi)
            pre = [x for x in m_ if x.lower() not in ("domates", "biber", "maydanoz", "kırmızı", "soğuk", "zerdeçal", "susam")]
            name = (" ".join(pre) + " " + sub).strip() if pre else sub
            out.append({"raw": name, "mods": m_})
        for e in extra:
            for sub in [x.strip() for x in re.split(r"\s*/\s*|\s+-\s+", e) if x.strip()]:
                out.append({"raw": sub, "mods": []})
    return out


def load_menu() -> pd.DataFrame:
    m = pd.read_excel(RAW / "menu_2026.xlsx", sheet_name="Tüm Menüler")
    rows = []
    for _, r in m.iterrows():
        d = pd.to_datetime(r["Tarih"], format="%d.%m.%Y").date()
        meal = MENU_MEAL[r["Öğün"].strip()]
        items = []
        raw = {}
        for c in COMPONENTS:
            v = r.get(c)
            raw[COMP_KEY[c]] = None if pd.isna(v) else str(v).strip()
            for it in split_items(c, v):
                items.append({"comp": COMP_KEY[c], **it})
        rows.append(dict(date=d, meal=meal, gun=r["Gün"], items=items, **{f"m_{k}": v for k, v in raw.items()}))
    return pd.DataFrame(rows)


def load_log() -> pd.DataFrame:
    g = pd.read_excel(RAW / "seker_takip_yemekli.xlsx", header=None)
    rows = []
    for i in range(2, len(g)):
        r = g.iloc[i].tolist()
        d = r[0]
        if pd.isna(d):
            continue
        d = pd.to_datetime(d).date()
        day = {"date": d, "yatis": num(r[13]), "yatis_ekdoz": num(r[14]), "lantus": num(r[15]),
               "gece03": num(r[16]), "gece_ekdoz": num(r[17])}
        for meal, (a, ins, t, ek) in MEALS.items():
            day[f"{meal}_aclik"] = num(r[a])
            day[f"{meal}_insulin"] = num(r[ins])
            day[f"{meal}_tokluk"] = num(r[t])
            day[f"{meal}_ekdoz"] = num(r[ek])
        rows.append(day)
    return pd.DataFrame(rows).set_index("date").sort_index()


def status(v: float) -> str:
    return "hipo" if v < 70 else ("hiper" if v > 180 else "hedef")


def main():
    menu = load_menu()
    log = load_log()
    order = ["kahvalti", "ogle", "aksam"]

    menu["is_weekend"] = menu["date"].map(lambda d: d.weekday() >= 5)
    menu["holiday"] = menu["date"].map(lambda d: HOLIDAYS.get(d))

    events, drop = [], {"hafta_sonu": 0, "tatil": 0, "olcum_eksik": 0, "kayit_yok": 0, "menu_bos": 0}
    for _, mr in menu.iterrows():
        d, meal = mr["date"], mr["meal"]
        # Hafta sonu ve tatil öğünleri değerlendirme setine girmez (events.csv), ama uygulamanın benzer vaka
        # havuzuna girer (events_all.csv): şeker kaydı o günler için de var.
        excl = "hafta_sonu" if mr["is_weekend"] else ("tatil" if isinstance(mr["holiday"], str) else None)
        if excl:
            drop[excl] += 1
        if not mr["items"]:
            drop["menu_bos"] += 1; continue
        if d not in log.index:
            drop["kayit_yok"] += 1; continue
        L = log.loc[d]
        ac, tk = L[f"{meal}_aclik"], L[f"{meal}_tokluk"]
        if ac is None or tk is None or pd.isna(ac) or pd.isna(tk):
            drop["olcum_eksik"] += 1; continue
        # önceki öğün bağlamı: aynı günün önceki öğününün tokluğu; kahvaltı için önceki gecenin yatış ölçümü
        idx = order.index(meal)
        if idx > 0:
            prev = L[f"{order[idx-1]}_tokluk"]
            prev_kind = f"{order[idx-1]}_tokluk"
        else:
            pd_ = d - timedelta(days=1)
            prev = log.loc[pd_, "gece03"] if pd_ in log.index else None
            if prev is None or pd.isna(prev):
                prev = log.loc[pd_, "yatis"] if pd_ in log.index else None
                prev_kind = "onceki_yatis"
            else:
                prev_kind = "gece03"
        # yakın geçmiş (yalnızca önceki günler; tahmin anında bilinen bilgi). Tam kayıt kullanılır: hafta sonları ve
        # menüsü olmayan aylar da dahil, çünkü şeker ölçümleri her gün var.
        win = log.loc[(log.index >= d - timedelta(days=7)) & (log.index < d)]
        allt = pd.concat([win[f"{x}_tokluk"] for x in order]).dropna()
        r7_all = allt.mean() if len(allt) >= 5 else None
        r7_meal = win[f"{meal}_tokluk"].dropna()
        r7_meal = r7_meal.mean() if len(r7_meal) >= 3 else None
        r7_hipo = int((allt < 70).sum()) if len(allt) else None
        ins = L[f"{meal}_insulin"]
        ek = L[f"{meal}_ekdoz"]
        events.append(dict(
            event_id=f"{d.isoformat()}_{meal}", date=d.isoformat(), meal=meal, month=d.month, dow=d.weekday(),
            excluded=excl,
            aclik=ac, insulin=None if pd.isna(ins) else ins, ekdoz=None if ek is None or pd.isna(ek) else ek,
            prev_bg=None if prev is None or pd.isna(prev) else prev, prev_kind=prev_kind,
            r7_all=r7_all, r7_meal=r7_meal, r7_hipo=r7_hipo,
            tokluk=tk, status=status(tk),
            items=json.dumps(mr["items"], ensure_ascii=False),
            **{k: mr[k] for k in mr.index if k.startswith("m_")},
        ))
    ev_all = pd.DataFrame(events)
    ev_all.to_csv(OUT / "events_all.csv", index=False)
    ev = ev_all[ev_all.excluded.isna()].drop(columns="excluded").reset_index(drop=True)
    ev.to_csv(OUT / "events.csv", index=False)
    print("uygulama havuzu (hafta sonu/tatil dahil):", len(ev_all))
    log.reset_index().to_csv(OUT / "daily_log.csv", index=False)

    md = menu[["date", "meal", "gun", "is_weekend", "holiday", "items"] + [c for c in menu.columns if c.startswith("m_")]].copy()
    md["items"] = md["items"].map(lambda x: json.dumps(x, ensure_ascii=False))
    md["date"] = md["date"].map(lambda d: d.isoformat())
    md.to_csv(OUT / "menu_days.csv", index=False)

    allit = [(it["comp"], it["raw"]) for its in menu["items"] for it in its]
    ir = pd.DataFrame(allit, columns=["comp", "raw"]).value_counts().reset_index(name="n")
    ir.to_csv(OUT / "items_raw.csv", index=False)

    print("olay:", len(ev), "| düşülen:", drop)
    print(ev.groupby(["month", "meal"]).size().unstack(fill_value=0))
    print(ev.status.value_counts().to_dict())
    print("benzersiz kalem yazımı:", ir.raw.nunique(), "| (bileşen, yazım) çifti:", len(ir))


if __name__ == "__main__":
    main()
