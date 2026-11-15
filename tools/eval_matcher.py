"""Ad eşleştiricinin GERÇEK menü yazımlarıyla değerlendirmesi (birini-dışarıda-bırak).

Her elle etiketlenmiş alias (tek yemeğe giden) için o yazım aday kümesinden çıkarılır, eşleştirici kalan adaylar
(standart yemek adları + diğer yazımlar) içinden doğru yemeği bulabiliyor mu? Standart adı yazımla birebir aynı olan
satırlar çıkarılır (aksi halde soru kolay olur). TF-IDF tek başına, bge-m3 tek başına ve RRF birleşimi karşılaştırılır.
Çıktı: reports/matcher_eval.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shadow_pancreas.matcher import NameMatcher, norm, rrf  # noqa: E402


def main():
    M = NameMatcher(use_embedding=True)
    texts, ids = M.texts, M.ids
    n_dish = len(M.names)
    q_idx = [i for i in range(n_dish, len(texts)) if norm(texts[i]) != norm(M.names.get(ids[i], ""))]
    queries = [texts[i] for i in q_idx]
    S_lex = (M.tfidf.transform(queries) @ M.T.T).toarray()
    variants = {"TF-IDF harf 2–4": S_lex}
    if M.E is not None:
        Q = M._encoder().encode(queries, normalize_embeddings=True, batch_size=32)
        S_emb = Q @ M.E.T
        variants["bge-m3"] = S_emb
        variants["RRF TF-IDF + bge-m3 (0,5)"] = rrf([S_lex, S_emb], weights=[1.0, 0.5])
        variants["RRF TF-IDF + bge-m3 (1,0)"] = rrf([S_lex, S_emb], weights=[1.0, 1.0])
    out = {}
    wrong = {}
    for name, S in variants.items():
        S = S.copy()
        hit1 = hit5 = 0
        rr = []
        wl = []
        for r, i in enumerate(q_idx):
            S[r, i] = -1e9  # kendisi aday olamaz
            # aynı normalize yazıma sahip başka adaylar da çıkarılır (aynı metnin kopyası)
            same = [j for j, t in enumerate(texts) if norm(t) == norm(texts[i])]
            S[r, same] = -1e9
            order = np.argsort(-S[r])
            seen, ranked = set(), []
            for j in order:
                if ids[j] not in seen:
                    seen.add(ids[j]); ranked.append(ids[j])
                if len(ranked) >= 50:
                    break
            gold = ids[i]
            pos = ranked.index(gold) + 1 if gold in ranked else 999
            hit1 += pos == 1; hit5 += pos <= 5; rr.append(1 / pos)
            if pos != 1 and len(wl) < 15:
                wl.append(dict(sorgu=texts[i], dogru=M.names.get(gold, gold), tahmin=M.names.get(ranked[0], ranked[0])))
        n = len(q_idx)
        out[name] = dict(n=n, acc1=round(hit1 / n, 3), recall5=round(hit5 / n, 3), mrr=round(float(np.mean(rr)), 3))
        wrong[name] = wl
        print(name, out[name])
    json.dump(dict(sonuc=out, hatalar=wrong, yontem=__doc__.strip()), open(ROOT / "reports" / "matcher_eval.json", "w",
              encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
