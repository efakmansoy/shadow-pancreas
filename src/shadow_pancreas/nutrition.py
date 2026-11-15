"""Yemek adı -> besin vektörü.

Zincir: menü kalemi (ham yazım) --alias--> standart yemek(ler) --tarif--> malzeme gramajı --USDA--> besin değeri.
Alias tablosunda olmayan yeni bir yazım gelirse NameMatcher (TF-IDF + bge-m3, RRF) en yakın standart yemeği önerir.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
N = ROOT / "data" / "nutrition"
NUTR = ["carb", "sugar", "fiber", "protein", "fat", "kcal"]
# Hızlı emilen karbonhidrat grupları (özellik olarak ayrı tutulur)
SWEET_CATS = {"serbetli_tatli", "sutlu_tatli", "pasta_kek", "tatlandirici"}
STARCH_CATS = {"pilav", "makarna", "patates_garnitur", "ekmek_hamur", "borek"}


def _read_all(stem: str, **kw) -> pd.DataFrame:
    files = sorted(N.glob(f"{stem}_*.csv"))
    if not files:
        raise FileNotFoundError(f"{N}/{stem}_*.csv yok")
    return pd.concat([pd.read_csv(f, **kw) for f in files], ignore_index=True)


@lru_cache(maxsize=1)
def tables():
    ing = pd.read_csv(N / "ingredients.csv")
    dishes = _read_all("dishes")
    recipes = _read_all("recipes")
    aliases = _read_all("aliases", keep_default_na=False)
    r = recipes.merge(ing, on="ingredient_id", how="left")
    for k in NUTR:
        r[k] = r[k] * r["grams"] / 100
    r["gl"] = r["carb"] * r["gi"] / 100  # glisemik yük katkısı
    g = r.groupby("dish_id")[NUTR + ["gl", "grams"]].sum()
    g["gi"] = (100 * g["gl"] / g["carb"].where(g["carb"] > 0)).fillna(0)
    dish = dishes.set_index("dish_id").join(g).fillna({k: 0 for k in NUTR + ["gl", "grams", "gi"]})
    alias = {(a.comp, a.raw): [d for d in a.dish_ids.split("|") if d] for a in aliases.itertuples()}
    return dish, alias, recipes, ing


def gi_class(gi: float) -> str:
    return "düşük" if gi < 55 else ("orta" if gi < 70 else "yüksek")


def resolve(comp: str, raw: str, matcher=None, dish_id: str | None = None) -> tuple[list[str], str]:
    """Bir kalemi standart yemek kimliklerine çevirir. Dönüş: (dish_ids, kaynak).
    dish_id verilmişse (kullanıcı menü girerken yemeği seçtiyse) doğrudan o kullanılır."""
    dish, alias, *_ = tables()
    if dish_id and dish_id in dish.index:
        return [dish_id], "kullanıcı"
    if (comp, raw) in alias:
        return alias[(comp, raw)], "alias"
    for (c, r), ids in alias.items():  # aynı yazım başka bileşende geçmişse
        if r.lower() == raw.lower():
            return ids, "alias"
    if matcher is not None:
        cands = matcher.match(raw, k=1)
        if cands:
            return [cands[0]["dish_id"]], "eşleştirici"
    return [], "bilinmiyor"


def meal_vector(items: list[dict], matcher=None) -> dict:
    """Öğün kalemleri -> toplam besin vektörü + açıklama satırları."""
    dish, *_ = tables()
    tot = {k: 0.0 for k in NUTR + ["gl"]}
    tot.update(sweet_carb=0.0, starch_carb=0.0)
    lines, seen = [], set()
    for it in items:
        ids, src = resolve(it["comp"], it["raw"], matcher, it.get("dish_id"))
        for d in ids:
            if d not in dish.index:
                continue
            key = (it["comp"], d)
            if key in seen:  # aynı öğünde aynı yemek iki kez sayılmasın
                continue
            seen.add(key)
            row = dish.loc[d]
            for k in NUTR + ["gl"]:
                tot[k] += float(row[k])
            if row["category"] in SWEET_CATS:
                tot["sweet_carb"] += float(row["carb"])
            if row["category"] in STARCH_CATS:
                tot["starch_carb"] += float(row["carb"])
            lines.append(dict(comp=it["comp"], raw=it["raw"], dish_id=d, name=row["name_tr"], category=row["category"],
                              carb=round(float(row["carb"]), 1), protein=round(float(row["protein"]), 1),
                              fat=round(float(row["fat"]), 1), kcal=round(float(row["kcal"])),
                              gi=round(float(row["gi"])), source=src))
    tot["gi"] = 100 * tot["gl"] / tot["carb"] if tot["carb"] > 0 else 0.0
    return {"total": {k: round(v, 1) for k, v in tot.items()}, "lines": lines}


def dish_recipe(dish_id: str) -> list[dict]:
    """'Bu değerler nereden geldi?' için malzeme dökümü."""
    _, _, recipes, ing = tables()
    r = recipes[recipes.dish_id == dish_id].merge(ing, on="ingredient_id")
    out = []
    for x in r.itertuples():
        out.append(dict(ingredient=x.name_tr, grams=x.grams, carb=round(x.carb * x.grams / 100, 1),
                        protein=round(x.protein * x.grams / 100, 1), fat=round(x.fat * x.grams / 100, 1),
                        usda=f"FDC {x.fdc_id}: {x.usda_desc}"))
    return out


def build_event_nutrition(events: pd.DataFrame, matcher=None) -> pd.DataFrame:
    rows = []
    for e in events.itertuples():
        mv = meal_vector(json.loads(e.items), matcher)
        rows.append({"event_id": e.event_id, **{f"n_{k}": v for k, v in mv["total"].items()},
                     "n_unknown": sum(1 for it in json.loads(e.items)
                                      if resolve(it["comp"], it["raw"], matcher)[1] == "bilinmiyor")})
    return pd.DataFrame(rows)
