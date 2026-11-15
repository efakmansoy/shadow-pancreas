"""Uygulama motoru (bugün odaklı).

Akış: bugünün menüsü (menü dosyası ya da kullanıcı girişi) + o anki açlık
  -> menü besin vektörü -> benzer geçmiş öğünler (ağırlıklı kNN: açlık + besin vektörü + son 7 gün)
  -> her vakanın o gün vurulan insülini ve tokluğu + LLM bağlamı.
Sistem doz önermez; yalnızca kullanıcının kendi geçmiş kayıtlarını gösterir.
Kullanıcı kayıtları: data/user/menus.json (girilen menüler), data/user/records.csv (girilen öğün sonuçları).
"""
from __future__ import annotations

import json
import os
import threading
from datetime import date as Date
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import nutrition as NU
from .models import WKNN

ROOT = Path(__file__).resolve().parents[2]
USER = ROOT / "data" / "user"


def data_dir() -> Path:
    """Veri klasörü. SHADOW_PANCREAS_DATA verilmişse o; yoksa gerçek (özel) veri varsa data/, yoksa SENTETİK demo verisi (data/synthetic/)."""
    env = os.environ.get("SHADOW_PANCREAS_DATA")
    if env:
        return (ROOT / env).resolve()
    return ROOT / "data" if (ROOT / "data" / "events_all.csv").exists() else ROOT / "data" / "synthetic"
MEALS = ["kahvalti", "ogle", "aksam"]
MEAL_NAME = {"kahvalti": "kahvaltı", "ogle": "öğle yemeği", "aksam": "akşam yemeği"}
MEAL_NAME_EN = {"kahvalti": "breakfast", "ogle": "lunch", "aksam": "dinner"}
COMP_ORDER = ["corba", "ana", "pilav", "salata", "yogurt", "tatli", "kahvaltilik", "hamur", "diger"]
COMP_NAME = {"corba": "Çorba", "ana": "Ana yemek", "pilav": "Pilav / makarna", "yogurt": "Yoğurt / süt",
             "salata": "Salata", "tatli": "Tatlı / meyve", "kahvaltilik": "Kahvaltılık", "hamur": "Hamur işi",
             "diger": "Diğer"}
COMP_NAME_EN = {"corba": "Soup", "ana": "Main dish", "pilav": "Rice / pasta", "yogurt": "Yogurt / milk",
                "salata": "Salad", "tatli": "Dessert / fruit", "kahvaltilik": "Breakfast plate", "hamur": "Pastry",
                "diger": "Other"}
AY = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
AY_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
         "December"]


def tarih_metni(d: str, lang: str) -> str:
    x = Date.fromisoformat(d)
    if lang == "en":
        return f"{x.day} {AY_EN[x.month - 1]} {x.year}"
    return f"{x.day} {AY[x.month - 1]} {x.year}"


GUN = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
GUN_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MAIN_COMPS = ("corba", "ana", "pilav", "tatli", "hamur")
ACLIK_YAKIN = 30  # açlığı bugüne ±30 mg/dL içinde olan vakalar "yakın" sayılır
COMP_W = {"ana": 1.0, "pilav": 0.8, "tatli": 0.7, "hamur": 0.7, "corba": 0.6}


def status(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return "hipo" if v < 70 else ("hiper" if v > 180 else "hedef")


def _f(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)


def _i(v):
    v = _f(v)
    return None if v is None else (int(v) if float(v).is_integer() else round(v, 1))


class Engine:
    def __init__(self, matcher=None):
        self.lock = threading.Lock()
        self.cfg = json.load(open(ROOT / "reports" / "final_model.json", encoding="utf-8"))
        self.matcher = matcher
        D = self.data_dir = data_dir()
        self.synthetic = D.name == "synthetic"
        self.menu = pd.read_csv(D / "menu_days.csv")
        self.menu["items"] = self.menu["items"].map(json.loads)
        self.menu_idx = {(r.date, r.meal): r["items"] for _, r in self.menu.iterrows()}
        self.log = pd.read_csv(D / "daily_log.csv")
        self.log["date"] = self.log["date"].astype(str)
        USER.mkdir(parents=True, exist_ok=True)
        self.user_menus = self._load_json(USER / "menus.json", {})
        # benzer vaka havuzu: hafta sonları dahil, resmi tatiller hariç
        ev = pd.read_csv(D / "events_all.csv")
        ev = ev[ev.excluded.fillna("") != "tatil"].drop(columns="excluded")
        self.base_events = ev.merge(pd.read_csv(D / "event_nutrition_all.csv"), on="event_id")
        z = np.load(ROOT / "data" / "dish_embeddings.npz", allow_pickle=True)
        self.dish_emb = dict(zip(z["ids"], z["E"]))
        self._rebuild()

    # ------------------------------------------------------------------ kalıcı kullanıcı verisi
    @staticmethod
    def _load_json(p, default):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return default

    def _user_records(self) -> pd.DataFrame:
        p = USER / "records.csv"
        if p.exists():
            return pd.read_csv(p)
        return pd.DataFrame(columns=["date", "meal", "aclik", "insulin", "tokluk", "saved_at"])

    def _rebuild(self):
        """Geçmiş vakalar = Excel kaydından gelen öğünler + kullanıcının uygulamada kaydettiği (tokluğu olan) öğünler."""
        ev = self.base_events.copy()
        ur = self._user_records()
        extra = []
        for r in ur.itertuples():
            if pd.isna(r.tokluk) or pd.isna(r.aclik):
                continue
            items = self._items(r.date, r.meal)
            if not items:
                continue
            mv = NU.meal_vector(items, self.matcher)
            dt = Date.fromisoformat(r.date)
            row = dict(event_id=f"u_{r.date}_{r.meal}", date=r.date, meal=r.meal, month=dt.month, dow=dt.weekday(),
                       aclik=float(r.aclik), insulin=_f(r.insulin), ekdoz=None, prev_bg=np.nan, tokluk=float(r.tokluk),
                       status=status(float(r.tokluk)), items=json.dumps(items, ensure_ascii=False),
                       r7_meal=self._r7(r.date, r.meal), source="kullanıcı")
            row.update({f"n_{k}": v for k, v in mv["total"].items()})
            extra.append(row)
        ev["source"] = "kayıt"
        if extra:
            ex = pd.DataFrame(extra)
            ev = pd.concat([ev[~(ev.date + ev.meal).isin(ex.date + ex.meal)], ex], ignore_index=True)
        self.events = ev.reset_index(drop=True)
        self._md_cache = None
        self.knn = WKNN(emb=None, **self.cfg["knn"]).fit(self.events)

    # ------------------------------------------------------------------ menü
    def _items(self, d, meal):
        um = self.user_menus.get(d, {}).get(meal)
        if um:
            return um
        return self.menu_idx.get((d, meal))

    def menu_for(self, d: str, meal: str, lang: str = "tr"):
        um = self.user_menus.get(d, {}).get(meal)
        items, source = (um, "kullanıcı") if um else (self.menu_idx.get((d, meal)), "menu")
        if not items:
            return None
        mv = NU.meal_vector(items, self.matcher)
        names = COMP_NAME_EN if lang == "en" else COMP_NAME
        comps = []
        for c in COMP_ORDER:
            lines = [ln for ln in mv["lines"] if ln["comp"] == c]
            raws = [it["raw"] for it in items if it["comp"] == c]
            if raws:
                comps.append(dict(comp=c, title=names[c], raw=raws, dishes=lines,
                                  carb=round(sum(x["carb"] for x in lines), 1)))
        return dict(date=d, meal=meal, source=source, items=items, components=comps, total=mv["total"],
                    lines=mv["lines"])

    def save_menu(self, d: str, meal: str, items: list[dict], lang="tr"):
        clean = []
        dish, *_ = NU.tables()
        for it in items:
            comp, raw, did = it.get("comp"), (it.get("raw") or "").strip(), it.get("dish_id")
            if comp not in COMP_ORDER or not (raw or did):
                continue
            if did and did not in dish.index:
                did = None
            if not did:
                ids, _ = NU.resolve(comp, raw, self.matcher)
                did = ids[0] if ids else None
            clean.append(dict(comp=comp, raw=raw or str(dish.loc[did, "name_tr"]), dish_id=did))
        with self.lock:
            self.user_menus.setdefault(d, {})[meal] = clean
            json.dump(self.user_menus, open(USER / "menus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            self._rebuild()
        return self.menu_for(d, meal, lang)

    def dishes(self):
        dish, *_ = NU.tables()
        return [dict(dish_id=i, name=r["name_tr"], category=r["category"], carb=round(float(r["carb"]), 1))
                for i, r in dish.sort_values("name_tr").iterrows()]

    # ------------------------------------------------------------------ benzer senaryolar
    def _r7(self, d, meal):
        start = (Date.fromisoformat(d) - timedelta(days=7)).isoformat()
        w = self.log[(self.log.date >= start) & (self.log.date < d)][f"{meal}_tokluk"].dropna().tolist()
        ur = self._user_records()
        if len(ur):
            u = ur[(ur.meal == meal) & (ur.date >= start) & (ur.date < d)].tokluk.dropna().tolist()
            w += u
        return float(np.mean(w)) if len(w) >= 3 else np.nan

    # benzerlik: 1) birebir aynı yemek sayısı  2) aynı aileden yemekler (kısmi puan)  3) açlık yakınlığı (en son)
    FAMILY_MIN = 0.85  # TR-MTEB "ad: malzeme" kosinüsü; bu eşiğin altı aynı aile sayılmaz

    def _main_dishes(self, items):
        """Her gün sabit olan kalemler (salata, yoğurt, kahvaltı tabağı, çay vb.) hariç ana yemekler -> {dish_id: (kategori, bileşen)}."""
        dish, *_ = NU.tables()
        out = {}
        for it in items:
            if it["comp"] not in MAIN_COMPS + ("ana",):
                continue
            ids, _ = NU.resolve(it["comp"], it["raw"], self.matcher, it.get("dish_id"))
            for d in ids:
                if d in dish.index and dish.loc[d, "category"] not in ("sos", "salata", "sut_urunu", "icecek",
                                                                       "tatlandirici", "kahvaltilik"):
                    out[d] = (dish.loc[d, "category"], it["comp"])
        return out

    def _dish_sim(self, a, b):
        if a == b:
            return 1.0
        ea, eb = self.dish_emb.get(a), self.dish_emb.get(b)
        if ea is None or eb is None:
            return 0.0
        return float(ea @ eb)

    def similar(self, d: str, meal: str, aclik: float, n=12, lang="tr"):
        menu = self.menu_for(d, meal, lang)
        if menu is None:
            raise ValueError("menu_yok")
        dish, *_ = NU.tables()
        Q = self._main_dishes(menu["items"])
        gun = GUN_EN if lang == "en" else GUN
        cands = []
        if getattr(self, "_md_cache", None) is None:
            self._md_cache = {r.event_id: self._main_dishes(json.loads(r.items)) for r in self.events.itertuples()}
        for r in self.events.itertuples():
            if r.date == d:
                continue
            P = self._md_cache[r.event_id]
            exact = [q for q in Q if q in P]
            fam = []
            soft = float(len(exact))
            for q in Q:
                if q in P:
                    continue
                best, bp = 0.0, None
                for p in P:
                    if P[p][0] != Q[q][0]:
                        continue
                    s = self._dish_sim(q, p)
                    if s > best:
                        best, bp = s, p
                if best >= self.FAMILY_MIN:
                    soft += best
                    fam.append((q, bp))
            if not exact and not fam:
                continue
            # aynı sayıda birebir eşleşmede ana yemek eşleşmesi çorba eşleşmesinden önce gelir
            wex = sum(COMP_W.get(Q[q][1], 0.6) for q in exact) + sum(
                COMP_W.get(Q[q][1], 0.6) * self._dish_sim(q, p) for q, p in fam)
            cands.append((len(exact), round(wex, 2), round(soft, 2), -abs(r.aclik - aclik), r, exact, fam, P))
        cands.sort(key=lambda x: x[:4], reverse=True)
        nq = max(len(Q), 1)
        out = []
        for n_ex, _, soft, _, r, exact, fam, P in cands[:n]:
            names = [dish.loc[x, "name_tr"] for x in P]
            level = "ayni_menu" if n_ex == len(Q) and len(P) == len(Q) else (
                "cogu_ayni" if n_ex >= max(2, (nq + 1) // 2) else ("benzer" if soft >= nq / 2 else "kismi"))
            out.append(dict(event_id=r.event_id, date=r.date, gun=gun[Date.fromisoformat(r.date).weekday()], meal=r.meal,
                            aclik=_i(r.aclik), insulin=_i(r.insulin), ekdoz=_i(r.ekdoz), tokluk=_i(r.tokluk),
                            status=status(r.tokluk), carb=round(r.n_carb), aclik_fark=int(round(r.aclik - aclik)),
                            carb_fark=int(round(r.n_carb - menu["total"]["carb"])),
                            ortak_yemek=[dish.loc[x, "name_tr"] for x in exact],
                            benzer_yemek=[f"{dish.loc[a, 'name_tr']} ≈ {dish.loc[b, 'name_tr']}" for a, b in fam],
                            eslesen=n_ex, toplam=len(Q), eslesme_puani=round(soft / nq, 2), eslesme=level,
                            menu=names[:6], source=getattr(r, "source", "kayıt")))
        # ortalama yok: doz açlığa göre değiştiği için yalnızca açlığı bugüne yakın (±30) vakaların aralıkları verilir
        for s_ in out:
            s_["yakin_aclik"] = abs(s_["aclik_fark"]) <= ACLIK_YAKIN
        near = [s_ for s_ in out if s_["yakin_aclik"]]
        ins = [s_["insulin"] for s_ in near if s_["insulin"] is not None]
        tok = [s_["tokluk"] for s_ in near if s_["tokluk"] is not None]
        st = [s_["status"] for s_ in out]
        stats = dict(n=len(out), hedefte=st.count("hedef"), hiper=st.count("hiper"), hipo=st.count("hipo"),
                     yakin_n=len(near), yakin_aralik=ACLIK_YAKIN,
                     insulin_min=min(ins) if ins else None, insulin_max=max(ins) if ins else None,
                     tokluk_min=min(tok) if tok else None, tokluk_max=max(tok) if tok else None,
                     insulin_ort=None, tokluk_ort=None,
                     ayni_menu=sum(s_["eslesme"] == "ayni_menu" for s_ in out), bugunku_yemek_sayisi=len(Q))
        ctx = self.context(d, meal, aclik, menu, out, stats, lang)
        return dict(date=d, meal=meal, aclik=aclik, menu=menu, similar=out, stats=stats, context=ctx, lang=lang)

    def context(self, d, meal, aclik, menu, sims, stats, lang="tr"):
        t = menu["total"]

        def case(s_):
            return dict(tarih=tarih_metni(s_["date"], lang), ayni_yemekler=s_["ortak_yemek"], menu=", ".join(s_["menu"][:4]),
                        aclik=s_["aclik"], aclik_farki=s_["aclik_fark"], insulin_unite=s_["insulin"], ek_doz=s_["ekdoz"],
                        tokluk=s_["tokluk"], durum=s_["status"])

        near = [s_ for s_ in sims if s_["yakin_aclik"]]
        far = [s_ for s_ in sims if not s_["yakin_aclik"]]
        return {
            "ogun_adi": MEAL_NAME[meal], "tarih": d, "bugunku_aclik": int(round(aclik)),
            "bugunku_menu": [ln["name"] for ln in menu["lines"] if ln["comp"] in MAIN_COMPS],
            "menu_karbonhidrat_g": round(t["carb"]),
            "aclik_yakin_vakalar": [case(s_) for s_ in near[:4]],
            "aclik_farkli_vakalar": [case(s_) for s_ in far[:3]],
            "yakin_aralik_mg_dl": ACLIK_YAKIN,
        }

    # ------------------------------------------------------------------ kayıt
    def record(self, d, meal, aclik, insulin, tokluk):
        with self.lock:
            ur = self._user_records()
            ur = ur[~((ur.date == d) & (ur.meal == meal))]
            ur = pd.concat([ur, pd.DataFrame([dict(date=d, meal=meal, aclik=aclik, insulin=insulin, tokluk=tokluk,
                                                   saved_at=datetime.now().isoformat(timespec="seconds"))])])
            ur.to_csv(USER / "records.csv", index=False)
            self._rebuild()
        return dict(ok=True, in_history=tokluk is not None)

    # ------------------------------------------------------------------ geçmiş
    def history(self, lang="tr"):
        gun = GUN_EN if lang == "en" else GUN
        ev = self.base_events.set_index(["date", "meal"])
        ur = self._user_records()
        uidx = {(r.date, r.meal): r for r in ur.itertuples()}
        dates = set(self.log.date) | set(ur.date) | set(self.user_menus)
        days = []
        L = self.log.set_index("date")
        for d in sorted(dates, reverse=True):
            meals = {}
            for m in MEALS:
                cell = None
                if (d, m) in uidx:
                    r = uidx[(d, m)]
                    cell = dict(aclik=_i(r.aclik), insulin=_i(r.insulin), tokluk=_i(r.tokluk), ekdoz=None,
                                source="kullanıcı")
                elif d in L.index:
                    r = L.loc[d]
                    cell = dict(aclik=_i(r[f"{m}_aclik"]), insulin=_i(r[f"{m}_insulin"]), tokluk=_i(r[f"{m}_tokluk"]),
                                ekdoz=_i(r[f"{m}_ekdoz"]), source="kayıt")
                    if all(cell[k] is None for k in ("aclik", "insulin", "tokluk")):
                        cell = None
                items = self._items(d, m)
                names = []
                if items:
                    mv = NU.meal_vector(items, self.matcher)
                    names = [ln["name"] for ln in mv["lines"] if ln["comp"] in MAIN_COMPS][:6]
                if cell is None and not names:
                    continue
                cell = cell or dict(aclik=None, insulin=None, tokluk=None, ekdoz=None, source=None)
                cell["status"] = status(cell["tokluk"])
                cell["menu"] = names
                meals[m] = cell
            if not meals:
                continue
            extra = {}
            if d in L.index:
                extra = dict(yatis=_i(L.loc[d, "yatis"]), lantus=_i(L.loc[d, "lantus"]))
            days.append(dict(date=d, gun=gun[Date.fromisoformat(d).weekday()], meals=meals, **extra))
        months = sorted({x["date"][:7] for x in days}, reverse=True)
        return dict(months=months, days=days)
