"""Uygulamanın kullanacağı modeli tüm veriyle ayarlar ve reports/final_model.json'a yazar.

Karar: kNN + besin vektörü + yapılan insülin. Benzer vaka karşılaştırması uygulanan dozu hesaba katmalı (kullanıcı/uzman
kararı). Doğruluğu diğer yöntemlerle istatistiksel olarak ayırt edilemiyor; tahmin ekrandaki benzer vakaların ağırlıklı
ortalaması olduğu için açıklanabilir. Sistem doz önermez; doz yalnızca "yapılan doz" olarak girilir.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import evaluate as EV  # noqa: E402
from shadow_pancreas.models import FEATS_NUTR  # noqa: E402

ev, emb = EV.load()
feats = ["aclik", "r7_meal"] + FEATS_NUTR  # hafta sonu da kullanılacağı için gün yok; önceki ölçüm isteğe bağlı olduğu için yok
cfg, sc = EV.tune_knn(ev, feats, None, False, n_iter=200)
out = dict(predictor="knn", label="Benzer senaryo: açlık + menü besin vektörü (kNN)", knn=cfg, inner_mae=sc,
           note="Girdi: o anki açlık + bugünün menüsü (besin vektörü) + son 7 günün aynı öğün tokluk ortalaması. Çıktı: benzer geçmiş öğünler; her birinin vurulan insülini ve tokluğu gösterilir.")
json.dump(out, open(ROOT / "reports" / "final_model.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out)
