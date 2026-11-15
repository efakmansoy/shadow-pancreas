"""Türkçe yemek adları için embedding modeli karşılaştırması.

Görevler
  T1  Ad eşleştirme   : yazım varyantı / eş ad -> standart yemek adı (Acc@1, Recall@5, MRR)
  T2  Karbonhidrat kNN: veritabanında olmayan bir yemeğin karbonhidratını en yakın 3 komşudan
                        tahmin et (leave-one-out MAE, g/porsiyon) + en yakın komşu kategori isabeti
  T3  Zor çiftler     : "ekmek~bazlama" yakın, "ekmek~ekmek kadayıfı" uzak çıkmalı (ROC-AUC)
  T4  Besin korelasyonu: kosinüs benzerliği ile besin vektörü benzerliği arasındaki Spearman
T2-T4 iki metin biçimiyle ölçülür: yalnızca ad, ad + kısa malzeme açıklaması (zenginleştirilmiş).
"""
import gc
import time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import roc_auc_score

from synthetic_data import tr_lower

GI_NUM = {"D": 0.0, "O": 1.0, "Y": 2.0}

# Adaylar: (görünen ad, HF kimliği veya [alternatif kimlikler], ayarlar)
#   prefix_q / prefix_d / prefix_s : sorgu / doküman / simetrik görevlerde metne eklenecek önek
#   prompt_q / prompt_d / prompt_s : modelin kendi prompt adları (varsa önek yerine kullanılır)
#   trust : trust_remote_code
QWEN_Q = ("Instruct: Given a Turkish dish name from a menu (may contain typos or missing "
          "Turkish characters), retrieve the canonical name of the same dish\nQuery: ")
QWEN_S = "Instruct: Given a Turkish dish name, retrieve dishes with similar ingredients and nutrition\nQuery: "
DENSE_MODELS = [
    ("MiniLM-L12 çok dilli", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", {}),
    ("e5-small", "intfloat/multilingual-e5-small", dict(prefix_q="query: ", prefix_d="passage: ", prefix_s="query: ")),
    ("e5-base", "intfloat/multilingual-e5-base", dict(prefix_q="query: ", prefix_d="passage: ", prefix_s="query: ")),
    ("e5-large", "intfloat/multilingual-e5-large", dict(prefix_q="query: ", prefix_d="passage: ", prefix_s="query: ")),
    ("bge-m3", "BAAI/bge-m3", {}),
    ("gte-multilingual-base", "Alibaba-NLP/gte-multilingual-base", dict(trust=True)),
    ("Qwen3-Embedding-0.6B", "Qwen/Qwen3-Embedding-0.6B", dict(prefix_q=QWEN_Q, prefix_s=QWEN_S)),
    ("EmbeddingGemma-300m", "google/embeddinggemma-300m",
     dict(prompt_q="query", prompt_d="document", prompt_s="STS")),
    ("TR-MTEB turkish-embedding", "trmteb/turkish-embedding-model", {}),
    ("embeddingmagibu-200m", ["magibu/embeddingmagibu-200m", "alibayram/embeddingmagibu-200m"], dict(trust=True)),
    ("BERTurk NLI-STS", "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr", {}),
]


# ---------------------------------------------------------------- kodlayıcılar
class LexicalEncoder:
    """TF-IDF taban çizgisi. analyzer='char_wb' harf n-gram, 'word' kelime."""

    def __init__(self, analyzer):
        self.name = "TF-IDF " + ("harf 2-4" if analyzer == "char_wb" else "kelime")
        self.analyzer = analyzer
        self.vec = None

    def fit(self, corpus):
        kw = dict(analyzer=self.analyzer, preprocessor=tr_lower)
        if self.analyzer == "char_wb":
            kw["ngram_range"] = (2, 4)
        self.vec = TfidfVectorizer(**kw).fit(corpus)

    def encode(self, texts, mode="s"):
        m = self.vec.transform(texts).toarray()
        n = np.linalg.norm(m, axis=1, keepdims=True)
        return m / np.maximum(n, 1e-12)


class DenseEncoder:
    def __init__(self, label, model_id, cfg, device=None):
        from sentence_transformers import SentenceTransformer
        self.name = label
        self.cfg = cfg
        ids = model_id if isinstance(model_id, list) else [model_id]
        last = None
        for mid in ids:
            try:
                self.model = SentenceTransformer(mid, device=device, trust_remote_code=cfg.get("trust", False))
                self.model_id = mid
                break
            except Exception as e:  # noqa: BLE001
                last = e
        else:
            raise last
        self.prompts = getattr(self.model, "prompts", {}) or {}

    def fit(self, corpus):
        pass

    def encode(self, texts, mode="s"):
        kw = dict(normalize_embeddings=True, batch_size=64, convert_to_numpy=True, show_progress_bar=False)
        pname = self.cfg.get("prompt_" + mode)
        if pname and pname in self.prompts:
            kw["prompt_name"] = pname
        elif self.cfg.get("prefix_" + mode):
            kw["prompt"] = self.cfg["prefix_" + mode]
        return self.model.encode(list(texts), **kw)

    def close(self):
        del self.model
        gc.collect()
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------- yardımcılar
def nutrition_matrix(dishes):
    X = np.array([[d["carb"], d["protein"], d["fat"], d["fiber"], GI_NUM[d["gi"]]] for d in dishes], float)
    Z = (X - X.mean(0)) / X.std(0)
    Z[:, 0] *= 2.0  # diyabet için karbonhidrat en önemli bileşen
    return Z


def nutrition_similarity(dishes):
    Z = nutrition_matrix(dishes)
    d = np.sqrt(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1))
    return -d


def texts_for(dishes, enriched):
    if enriched:
        return [f'{d["name"]}: {d["desc"]}' for d in dishes]
    return [d["name"] for d in dishes]


# ---------------------------------------------------------------- görevler
def task_match(enc, dishes, queries):
    D = enc.encode([d["name"] for d in dishes], mode="d")
    Q = enc.encode([q["query"] for q in queries], mode="q")
    S = Q @ D.T
    tgt = np.array([q["target_id"] for q in queries])
    order = np.argsort(-S, axis=1)
    rank = np.array([np.where(order[i] == tgt[i])[0][0] + 1 for i in range(len(tgt))])
    per_kind = pd.Series(rank == 1).groupby([q["kind"] for q in queries]).mean()
    wrong = [(queries[i]["query"], dishes[tgt[i]]["name"], dishes[order[i, 0]]["name"])
             for i in np.where(rank != 1)[0]]
    return dict(acc1=(rank == 1).mean(), r5=(rank <= 5).mean(), mrr=(1 / rank).mean()), per_kind, wrong, S


def task_carb_knn(enc, dishes, enriched, k=3):
    E = enc.encode(texts_for(dishes, enriched), mode="s")
    S = E @ E.T
    np.fill_diagonal(S, -np.inf)
    carb = np.array([d["carb"] for d in dishes])
    cat = np.array([d["category"] for d in dishes])
    nn = np.argsort(-S, axis=1)[:, :k]
    w = np.take_along_axis(S, nn, 1)
    w = np.exp((w - w.max(1, keepdims=True)) * 20)  # yakın komşuya daha çok ağırlık
    est = (carb[nn] * w).sum(1) / w.sum(1)
    return dict(carb_mae=np.abs(est - carb).mean(), cat_hit1=(cat[nn[:, 0]] == cat).mean())


def task_pairs(enc, dishes, pairs, enriched):
    E = enc.encode(texts_for(dishes, enriched), mode="s")
    sims = np.array([E[p["a"]] @ E[p["b"]] for p in pairs])
    labels = np.array([p["label"] for p in pairs])
    return roc_auc_score(labels, sims), sims


def task_corr(enc, dishes, enriched, nsim):
    E = enc.encode(texts_for(dishes, enriched), mode="s")
    S = E @ E.T
    iu = np.triu_indices(len(dishes), 1)
    return spearmanr(S[iu], nsim[iu]).correlation


def baselines(dishes):
    carb = np.array([d["carb"] for d in dishes], float)
    cat = np.array([d["category"] for d in dishes])
    n = len(carb)
    glob = np.abs((carb.sum() - carb) / (n - 1) - carb).mean()
    est = []
    for i in range(n):
        m = (cat == cat[i]) & (np.arange(n) != i)
        est.append(carb[m].mean() if m.any() else carb.mean())
    return dict(global_mean_mae=glob, category_mean_mae=np.abs(np.array(est) - carb).mean())


def evaluate(enc, dishes, queries, pairs, nsim):
    t0 = time.time()
    row = dict(model=enc.name)
    m, per_kind, wrong, S = task_match(enc, dishes, queries)
    row.update({"T1_acc@1": m["acc1"], "T1_recall@5": m["r5"], "T1_mrr": m["mrr"]})
    for enriched, tag in [(False, "ad"), (True, "zengin")]:
        c = task_carb_knn(enc, dishes, enriched)
        row[f"T2_carbMAE_{tag}"] = c["carb_mae"]
        row[f"T2_kategori@1_{tag}"] = c["cat_hit1"]
        auc, sims = task_pairs(enc, dishes, pairs, enriched)
        row[f"T3_AUC_{tag}"] = auc
        row[f"T4_spearman_{tag}"] = task_corr(enc, dishes, enriched, nsim)
        if tag == "ad":
            pair_sims = sims
    row["süre_sn"] = time.time() - t0
    return row, per_kind, wrong, pair_sims, S


def composite(df):
    """Her metrikte sıralama yapıp ortalama sıra -> 'genel sıra' (küçük daha iyi)."""
    cols_hi = ["T1_acc@1", "T3_AUC_ad", "T3_AUC_zengin", "T4_spearman_zengin", "T2_kategori@1_zengin"]
    cols_lo = ["T2_carbMAE_zengin"]
    r = pd.concat([df[c].rank(ascending=False) for c in cols_hi] + [df[c].rank(ascending=True) for c in cols_lo], axis=1)
    return r.mean(1)


# ---------------------------------------------------------------- hibrit (RRF)
def rank_metrics(S, queries):
    """Sorgu x yemek skor matrisinden T1 metrikleri ve sorgu türüne göre Acc@1."""
    tgt = np.array([q["target_id"] for q in queries])
    order = np.argsort(-S, axis=1)
    rank = np.array([np.where(order[i] == tgt[i])[0][0] + 1 for i in range(len(tgt))])
    per_kind = pd.Series(rank == 1).groupby([q["kind"] for q in queries]).mean()
    return dict(acc1=(rank == 1).mean(), r5=(rank <= 5).mean(), mrr=(1 / rank).mean()), per_kind


def rrf(score_mats, k=60, weights=None):
    """Reciprocal Rank Fusion: her yöntemin sıralamasını 1/(k+sıra) ile toplar."""
    weights = weights or [1.0] * len(score_mats)
    out = np.zeros_like(score_mats[0], dtype=float)
    for S, w in zip(score_mats, weights):
        ranks = np.argsort(np.argsort(-S, axis=1), axis=1) + 1
        out += w / (k + ranks)
    return out
