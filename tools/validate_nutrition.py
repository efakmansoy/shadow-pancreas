"""Tarif ayrıştırmasıyla hesaplanan porsiyon karbonhidratını bağımsız bir referansla karşılaştırır.

Referans: USDA SR Legacy'deki HAZIR/PİŞMİŞ yemek kayıtları (100 g başına ölçülmüş değer) × servis ağırlığı.
Tarif tarafı malzemelerin çiğ değerlerinden toplanır; referans tarafı yemeğin kendisinin laboratuvar analizi.
Bazı eşleşmeler yakın analogdur (simit ≈ bagel, poğaça ≈ croissant); bu tabloda açıkça yazılır.
Çıktı: reports/nutrition_validation.json
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shadow_pancreas import nutrition as NU  # noqa: E402

# dish_id, USDA fdc_id, servis ağırlığı (g, pişmiş/sunulmuş), not
PAIRS = [
    ("pirinc_pilavi", 168878, 180, "pişmiş beyaz pirinç; 65 g çiğ pirinç ≈ 180 g pişmiş"),
    ("bulgur_pilavi", 170287, 230, "pişmiş bulgur; 65 g kuru ≈ 230 g pişmiş"),
    ("kuskus_pilavi", 169700, 200, "pişmiş kuskus"),
    ("makarna_sade", 168928, 200, "pişmiş makarna; 80 g kuru ≈ 200 g pişmiş"),
    ("etsiz_kuru_fasulye", 175203, 160, "haşlanmış kuru fasulye (sos hariç)"),
    ("nohut_yemegi", 173757, 160, "haşlanmış nohut (sos hariç)"),
    ("patates_pure", 168555, 150, "ev yapımı püre, süt + tereyağı"),
    ("lavas", 172816, 50, "pide ekmeği (pita)"),
    ("pide", 174915, 50, "pide ekmeği (pita)"),
    ("simit", 175049, 90, "analog: sade bagel"),
    ("pogaca", 174987, 70, "analog: tereyağlı kruvasan"),
    ("firin_sutlac", 168782, 150, "hazır sütlaç (rice pudding)"),
    ("muhallebi", 168785, 150, "vanilyalı puding, tam yağlı süt"),
    ("dondurma", 167575, 100, "vanilyalı dondurma"),
    ("elmali_tart", 175011, 100, "elmalı turta"),
    ("browni_kek", 174944, 100, "analog: kremalı kek (brownie kaydı yok)"),
    ("islak_kek", 174944, 100, "analog: çikolata kremalı kek"),
    ("kiymali_lazanya", 172114, 250, "kıymalı lazanya, pişmiş"),
    ("sebzeli_lazanya", 172106, 250, "sebzeli lazanya, pişmiş"),
    ("pizza", 170317, 150, "peynirli pizza, normal hamur"),
    ("patates_kizartmasi", 170437, 100, "fırınlanmış dondurulmuş patates kızartması"),
    ("yogurt", 171284, 150, "sade tam yağlı yoğurt"),
]


def main():
    dish, *_ = NU.tables()
    u = pd.read_csv(ROOT / "data" / "external" / "usda_sr_legacy_compact.csv").set_index("fdc_id")
    rows = []
    for did, fdc, g, note in PAIRS:
        if did not in dish.index:
            print("yok:", did); continue
        ref = float(u.loc[fdc, "carb"]) * g / 100
        ours = float(dish.loc[did, "carb"])
        rows.append(dict(dish_id=did, yemek=dish.loc[did, "name_tr"], tarif_karb=round(ours, 1), referans_karb=round(ref, 1),
                         fark=round(ours - ref, 1), usda=f"FDC {fdc}: {u.loc[fdc, 'description']}", servis_g=g, not_=note))
    df = pd.DataFrame(rows)
    mae = float(df.fark.abs().mean())
    rel = float((df.fark.abs() / df.referans_karb).median())
    out = dict(n=len(df), mae_g=round(mae, 1), medyan_bagil_hata=round(rel, 3), bias_g=round(float(df.fark.mean()), 1),
               satirlar=df.to_dict("records"),
               yontem="Tarif ayrıştırması (çiğ malzeme × USDA) ile USDA'nın pişmiş/hazır yemek analizinin servis ağırlığı "
                      "ile çarpımı karşılaştırıldı. Servis ağırlıkları varsayımdır.")
    json.dump(out, open(ROOT / "reports" / "nutrition_validation.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pd.set_option("display.width", 200)
    print(df[["yemek", "tarif_karb", "referans_karb", "fark", "not_"]].to_string())
    print(f"MAE {mae:.1f} g, medyan bağıl hata {rel:.1%}, ortalama sapma {df.fark.mean():+.1f} g")


if __name__ == "__main__":
    main()
