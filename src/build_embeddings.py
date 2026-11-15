"""Öğün (menü) embedding'leri: TR-MTEB turkish-embedding-model, "ad: malzemeler" metni.

Her standart yemek bir kez kodlanır; öğün embedding'i ana bileşenlerin (çorba, ana, pilav, tatlı, hamur işi,
kahvaltı yumurtası) karbonhidrat ağırlıklı ortalamasıdır (normalize). Sabit kalemler (salata, yoğurt, çay) dahil edilmez.
Çıktı: data/dish_embeddings.npz, data/event_embeddings.npz, data/menu_embeddings.npz
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shadow_pancreas import nutrition as NU  # noqa: E402

MODEL = "trmteb/turkish-embedding-model"
MAIN = {"corba", "ana", "pilav", "tatli", "hamur"}


def meal_emb(items, dE, dish):
    vecs, ws = [], []
    for it in items:
        if it["comp"] not in MAIN:
            continue
        ids, _ = NU.resolve(it["comp"], it["raw"])
        for d in ids:
            if d in dE:
                vecs.append(dE[d]); ws.append(max(float(dish.loc[d, "carb"]), 5.0))
    if not vecs:
        return None
    v = np.average(np.stack(vecs), axis=0, weights=ws)
    return v / np.linalg.norm(v)


def main():
    from sentence_transformers import SentenceTransformer
    dish, *_ = NU.tables()
    texts = [f"{r.name_tr}: {r.desc}" for r in dish.itertuples()]
    m = SentenceTransformer(MODEL, device="cpu")
    E = m.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
    dE = dict(zip(dish.index, E))
    np.savez(ROOT / "data" / "dish_embeddings.npz", ids=np.array(dish.index, dtype=object), E=E)
    for src, key, out in [("events.csv", "event_id", "event_embeddings.npz"), ("menu_days.csv", None, "menu_embeddings.npz")]:
        df = pd.read_csv(ROOT / "data" / src)
        ids, vs = [], []
        for r in df.itertuples():
            v = meal_emb(json.loads(r.items), dE, dish)
            if v is None:
                v = np.zeros(E.shape[1])
            ids.append(getattr(r, key) if key else f"{r.date}_{r.meal}"); vs.append(v)
        np.savez(ROOT / "data" / out, ids=np.array(ids, dtype=object), E=np.stack(vs))
        print(out, len(ids))


if __name__ == "__main__":
    main()
