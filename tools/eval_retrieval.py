"""Geri getirme (retrieval) kalitesi: RAGAS context precision'ın vaka tabanlı karşılığı.

Belge RAG'inde "getirilen parça soruya ilgili mi?" diye sorulur. Burada getirilen şey geçmiş öğün vakaları; bir vaka,
sonucu (tokluk durumu) sorgu öğününün gerçek sonucuyla aynıysa "ilgili" sayılır. Ay-dışarıda: her öğün için yalnızca
başka aylardaki vakalar getirilir.

  durum isabeti@5   : ilk 5 vakadan gerçek durumla (hipo/hedef/hiper) aynı olanların oranı
  context precision : RAGAS formülü, ilgili vakaların sıra ağırlıklı ortalama hassasiyeti (ilk 5)
  |Δtokluk|@5       : ilk 5 vakanın tokluğu ile gerçek tokluk arasındaki ortalama fark
Karşılaştırma: rastgele aynı-öğün vakaları, prototip penceresi (aynı öğün, açlık ±15, en yakın 5), M1 (yemeksiz kNN),
M2 (besin vektörlü kNN, uygulamadaki).
Çıktı: reports/retrieval_eval.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import evaluate as EV  # noqa: E402
from shadow_pancreas.models import FEATS_NUTR, WKNN  # noqa: E402

RNG = np.random.default_rng(0)
K = 5


def ctx_precision(rel):
    rel = np.asarray(rel, dtype=float)
    if rel.sum() == 0:
        return 0.0
    prec = np.cumsum(rel) / (np.arange(len(rel)) + 1)
    return float((prec * rel).sum() / rel.sum())


def main():
    ev, _ = EV.load()
    cfg = json.load(open(ROOT / "reports" / "final_model.json", encoding="utf-8"))["knn"]
    m1cfg = dict(cfg); m1cfg["weights"] = {k: v for k, v in cfg["weights"].items() if not k.startswith("n_")}
    methods = {"rastgele (aynı öğün)": None, "prototip (±15)": "b2", "M1 kNN (yemeksiz)": m1cfg, "M2 kNN + besin": cfg}
    res = {}
    for name, c in methods.items():
        hit, cp, dt = [], [], []
        for m in sorted(ev.month.unique()):
            tr, te = ev[ev.month != m].reset_index(drop=True), ev[ev.month == m]
            model = WKNN(**c).fit(tr) if isinstance(c, dict) else None
            for _, q in te.iterrows():
                qd = te.loc[[q.name]]
                if model is not None:
                    _, nb = model.neighbors(qd, n=K)
                elif c == "b2":
                    s = tr[tr.meal == q.meal].assign(d=lambda x: (x.aclik - q.aclik).abs())
                    nb = s[s.d <= 15].nsmallest(K, "d")
                    if len(nb) == 0:
                        nb = s.nsmallest(K, "d")
                else:
                    s = tr[tr.meal == q.meal]
                    nb = s.iloc[RNG.choice(len(s), K, replace=False)]
                rel = (nb.status.values == q.status).astype(int)
                hit.append(rel.mean()); cp.append(ctx_precision(rel)); dt.append(np.abs(nb.tokluk.values - q.tokluk).mean())
        res[name] = dict(durum_isabeti_at5=round(float(np.mean(hit)), 3), context_precision=round(float(np.mean(cp)), 3),
                         ort_tokluk_farki_at5=round(float(np.mean(dt)), 1), n=len(hit))
        print(name, res[name])
    json.dump(dict(sonuc=res, yontem=__doc__.strip()), open(ROOT / "reports" / "retrieval_eval.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
