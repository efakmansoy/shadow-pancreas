"""Tarif/alias dosyalarını doğrular ve porsiyon besin değerlerini yazdırır.

Kullanım: python src/check_recipes.py <onek> [<onek> ...]   (önek yoksa tüm dishes_*.csv birleşik kontrol edilir)
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
N = ROOT / "data" / "nutrition"
COMP_OWNER = {"a": {"ana", "pilav"}, "b": {"corba", "tatli", "yogurt", "salata", "kahvaltilik", "hamur", "diger"}}
CATS = set("corba et_yemegi tavuk_yemegi balik kofte sebze_yemegi baklagil patates_garnitur ekmek_hamur pilav makarna borek "
           "serbetli_tatli sutlu_tatli pasta_kek meyve kahvaltilik kahvalti_yumurta icecek sos salata sut_urunu tatlandirici".split())
NUTR = ["carb", "sugar", "fiber", "protein", "fat", "kcal"]


def load(prefixes):
    D, R, A = [], [], []
    for p in prefixes:
        D.append(pd.read_csv(N / f"dishes_{p}.csv"))
        R.append(pd.read_csv(N / f"recipes_{p}.csv"))
        A.append(pd.read_csv(N / f"aliases_{p}.csv", keep_default_na=False))
    return pd.concat(D), pd.concat(R), pd.concat(A)


def dish_nutrition(dishes, recipes, ing):
    r = recipes.merge(ing, on="ingredient_id", how="left")
    for k in NUTR:
        r[k] = r[k] * r["grams"] / 100
    r["gi_carb"] = r["carb"] * r["gi"]
    g = r.groupby("dish_id")[NUTR + ["gi_carb", "grams"]].sum()
    g["gi"] = (g["gi_carb"] / g["carb"].where(g["carb"] > 0)).round(0)
    g = g.drop(columns="gi_carb").round(1)
    return dishes.set_index("dish_id").join(g)


def main():
    prefixes = sys.argv[1:] or sorted(p.stem.split("_", 1)[1] for p in N.glob("dishes_*.csv"))
    ing = pd.read_csv(N / "ingredients.csv")
    dishes, recipes, aliases = load(prefixes)
    errs = []
    dup = dishes.dish_id[dishes.dish_id.duplicated()]
    if len(dup):
        errs.append(f"tekrarlanan dish_id: {list(dup)}")
    bad_cat = dishes[~dishes.category.isin(CATS)]
    if len(bad_cat):
        errs.append(f"geçersiz kategori: {bad_cat[['dish_id','category']].values.tolist()}")
    bad_ing = recipes[~recipes.ingredient_id.isin(ing.ingredient_id)]
    if len(bad_ing):
        errs.append(f"bilinmeyen ingredient_id: {sorted(set(bad_ing.ingredient_id))}")
    no_recipe = set(dishes.dish_id) - set(recipes.dish_id)
    if no_recipe:
        errs.append(f"tarifi olmayan yemek: {sorted(no_recipe)}")
    orphan = set(recipes.dish_id) - set(dishes.dish_id)
    if orphan:
        errs.append(f"dishes'ta olmayan tarif: {sorted(orphan)}")
    all_dish = set(dishes.dish_id)
    if not sys.argv[1:]:
        pass
    for p in prefixes:  # diğer ajanların dish'lerine referans serbest; birleşik kontrolde hepsi çözülmeli
        pass
    ref = {d for s in aliases.dish_ids for d in s.split("|") if d}
    missing_ref = ref - all_dish
    if missing_ref:
        errs.append(f"(birleşik kontrolde çözülmeli) alias'ta olup dishes'ta olmayan: {sorted(missing_ref)}")
    items = pd.read_csv(ROOT / "data" / "items_raw.csv")
    own = set().union(*[COMP_OWNER.get(p, set()) for p in prefixes]) if all(p in COMP_OWNER for p in prefixes) else set(items.comp)
    need = items[items.comp.isin(own)][["comp", "raw"]]
    have = set(map(tuple, aliases[["comp", "raw"]].values))
    miss = [tuple(x) for x in need.values if tuple(x) not in have]
    if miss:
        errs.append(f"alias'ı olmayan {len(miss)} kalem: {miss[:40]}")
    nut = dish_nutrition(dishes, recipes, ing)
    pd.set_option("display.width", 220); pd.set_option("display.max_rows", 500)
    print(nut[["name_tr", "category", "grams"] + NUTR + ["gi"]].to_string())
    print(f"\n{len(dishes)} yemek, {len(recipes)} tarif satırı, {len(aliases)} alias")
    print("\nHATALAR:" if errs else "\nHata yok.")
    for e in errs:
        print(" -", e)


if __name__ == "__main__":
    main()
