"""Yemek adı eşleştirici: TF-IDF harf 2–4 n-gram + bge-m3, Reciprocal Rank Fusion (embedding ağırlığı 0,5).

Colab karşılaştırmasında (sentetik 703 sorgu) bu birleşim Acc@1 0,878, Recall@5 0,966 verdi.
Aday kümesi: tüm alias yazımları + standart yemek adları. Bir sorgu için en yakın standart yemekler döner.
bge-m3 embedding'leri bir kez hesaplanıp data/nutrition/matcher_cache.npz'ye yazılır; çalışma anında model yalnızca
yeni (önbellekte olmayan) bir sorgu geldiğinde yüklenir. Model yüklenemezse yalnız TF-IDF ile çalışır.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .nutrition import N, tables

EMB_MODEL = "BAAI/bge-m3"
CACHE = N / "matcher_cache.npz"


def tr_lower(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower()


def norm(s: str) -> str:
    s = tr_lower(s)
    s = re.sub(r"\bçorbası\b", "çorba", s)
    s = re.sub(r"\bkebabı\b", "kebap", s)
    s = re.sub(r"[^\wçğıöşüâ ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def rrf(score_mats, k=60, weights=None):
    weights = weights or [1.0] * len(score_mats)
    out = np.zeros_like(score_mats[0], dtype=float)
    for S, w in zip(score_mats, weights):
        ranks = np.argsort(np.argsort(-S, axis=1), axis=1) + 1
        out += w / (k + ranks)
    return out


class NameMatcher:
    def __init__(self, use_embedding=True, emb_weight=0.5):
        dish, alias, *_ = tables()
        texts, ids = [], []
        for did, row in dish.iterrows():
            texts.append(row["name_tr"]); ids.append(did)
        for (comp, raw), dids in alias.items():
            if len(dids) == 1:
                texts.append(raw); ids.append(dids[0])
        self.texts, self.ids = texts, np.array(ids)
        self.names = dish["name_tr"].to_dict()
        self.tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), preprocessor=norm, sublinear_tf=True)
        self.T = self.tfidf.fit_transform(texts)
        self.emb_weight = emb_weight
        self.model = None
        self.E = None
        if use_embedding:
            self._load_cache()

    # -------------------------------------------------------------- embedding
    def _encoder(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(EMB_MODEL, device="cpu")
        return self.model

    def _load_cache(self):
        if CACHE.exists():
            z = np.load(CACHE, allow_pickle=True)
            if list(z["texts"]) == self.texts:
                self.E = z["E"]; return
        try:
            self.E = self._encoder().encode(self.texts, normalize_embeddings=True, batch_size=32)
            np.savez(CACHE, texts=np.array(self.texts, dtype=object), E=self.E)
        except Exception as e:  # noqa: BLE001
            print("bge-m3 yüklenemedi, yalnız TF-IDF:", e)
            self.E = None

    # -------------------------------------------------------------- eşleştirme
    def scores(self, queries: list[str]) -> np.ndarray:
        S_lex = (self.tfidf.transform(queries) @ self.T.T).toarray()
        if self.E is None:
            return S_lex
        Q = self._encoder().encode(queries, normalize_embeddings=True)
        S_emb = Q @ self.E.T
        return rrf([S_lex, S_emb], weights=[1.0, self.emb_weight])

    def match(self, query: str, k=5) -> list[dict]:
        s = self.scores([query])[0]
        order = np.argsort(-s)
        out, seen = [], set()
        for i in order:
            d = self.ids[i]
            if d in seen:
                continue
            seen.add(d)
            out.append(dict(dish_id=str(d), name=self.names.get(d, d), score=float(s[i]), via=self.texts[i]))
            if len(out) == k:
                break
        return out
