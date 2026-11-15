"""Tek bir embedding modelini AYRI SÜREÇTE değerlendirir.

Neden ayrı süreç: bir model CUDA 'device-side assert' verirse GPU bağlamı bozulur ve aynı
süreçteki sonraki tüm modeller de düşer. Her model kendi sürecinde çalışınca hata yayılmaz.

Kullanım: python run_one.py <DENSE_MODELS indeksi> <cuda|cpu> <çıktı klasörü>
Çıktı: <klasör>/<indeks>.pkl  (row, per_kind, wrong, pair_sims, S)  veya  <indeks>.err
"""
import pickle
import sys
import time
import traceback

idx, device, outdir = int(sys.argv[1]), sys.argv[2], sys.argv[3]

from synthetic_data import build  # noqa: E402
from embed_eval import DENSE_MODELS, DenseEncoder, evaluate, nutrition_similarity  # noqa: E402

label, mid, cfg = DENSE_MODELS[idx]
dishes, queries, pairs = build(seed=42)
nsim = nutrition_similarity(dishes)
try:
    t0 = time.time()
    enc = DenseEncoder(label, mid, cfg, device=device)
    load = time.time() - t0
    row, per_kind, wrong, pair_sims, S = evaluate(enc, dishes, queries, pairs, nsim)
    row.update(yükleme_sn=load, cihaz=device, model_id=enc.model_id,
               boyut=int(enc.encode(["test"]).shape[1]),
               parametre_M=round(sum(p.numel() for p in enc.model.parameters()) / 1e6))
    with open(f"{outdir}/{idx}.pkl", "wb") as f:
        pickle.dump(dict(row=row, per_kind=per_kind, wrong=wrong, pair_sims=pair_sims, S=S), f)
    print("OK", label, device)
except Exception as e:  # noqa: BLE001
    with open(f"{outdir}/{idx}.err", "w", encoding="utf-8") as f:
        f.write(f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}")
    print("HATA", label, device, type(e).__name__, str(e)[:200])
    sys.exit(1)
