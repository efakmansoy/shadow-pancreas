"""Malzeme sözlüğünü USDA FoodData Central SR Legacy (CC0) değerleriyle eşleştirir.

Girdi : data/nutrition/ingredient_vocab.csv, data/external/usda_sr_legacy_compact.csv
Çıktı : data/nutrition/ingredients.csv  (100 g başına karb, şeker, lif, protein, yağ, kcal + GI)
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
N = ROOT / "data" / "nutrition"

# usda_hint ile birebir eşleşmeyen kalemler için elle seçilmiş FDC kimlikleri
OVERRIDE = {
    "bugday_dovme": 169721, "pirinc_unu": 169714, "ekmek": 174924, "patates_kizartma": 170437,
    "salca": 170459, "meyve": 171688, "uzum_kuru": 168165, "dana_kiyma": 171796, "tavuk_gogus": 171077,
}
SUBSTR = {
    "galeta_unu": "Bread, crumbs, dry, grated, plain",
    "kuzu_et": 'Lamb, leg, whole (shank and sirloin), separable lean and fat, trimmed to 1/4" fat, choice, raw',
    "sivi_yag": "Oil, sunflower, linoleic, (approx. 65%)",
}


def main():
    v = pd.read_csv(N / "ingredient_vocab.csv")
    u = pd.read_csv(ROOT / "data" / "external" / "usda_sr_legacy_compact.csv")
    by_desc = {d.lower(): i for i, d in enumerate(u.description)}
    rows = []
    for r in v.itertuples():
        if r.ingredient_id in OVERRIDE:
            m = u[u.fdc_id == OVERRIDE[r.ingredient_id]].iloc[0]
        elif r.ingredient_id in SUBSTR:
            m = u[u.description == SUBSTR[r.ingredient_id]].iloc[0]
        else:
            m = u.iloc[by_desc[r.usda_hint.lower()]]
        rows.append(dict(ingredient_id=r.ingredient_id, name_tr=r.name_tr, fdc_id=int(m.fdc_id),
                         usda_desc=m.description, gi=r.gi,
                         **{k: round(float(0 if pd.isna(m[k]) else m[k]), 2)
                            for k in ["carb", "sugar", "fiber", "protein", "fat", "kcal"]}))
    out = pd.DataFrame(rows)
    out.to_csv(N / "ingredients.csv", index=False)
    print(out[["ingredient_id", "fdc_id", "carb", "protein", "fat", "kcal", "gi"]].to_string())


if __name__ == "__main__":
    main()
