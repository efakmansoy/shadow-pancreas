"""Tokluk (2. saat) tahmin modelleri.

B0  eğitim ortalaması
B1  aynı öğünün medyanı
B2  prototip: aynı öğün, açlık ±15 mg/dL penceresindeki tokluk ortalaması
M1  ağırlıklı kNN, yemek bilgisi yok
M2  ağırlıklı kNN + besin vektörü (ana model)
M3  LightGBM + besin vektörü (alternatif)

Her model fit(df) / predict(df) arayüzüne sahip. kNN modelleri ayrıca neighbors() ile açıklanabilir komşu listesi verir.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MEALS = ["kahvalti", "ogle", "aksam"]


# --------------------------------------------------------------------------- taban çizgileri
class B0:
    name = "B0 ortalama"

    def fit(self, df):
        self.m = df.tokluk.mean(); return self

    def predict(self, df):
        return np.full(len(df), self.m)


class B1:
    name = "B1 öğün medyanı"

    def fit(self, df):
        self.m = df.groupby("meal").tokluk.median().to_dict(); self.g = df.tokluk.median(); return self

    def predict(self, df):
        return np.array([self.m.get(x, self.g) for x in df.meal])


class B2:
    """Prototipin yöntemi: aynı öğün, |açlık - sorgu| <= tol olan geçmiş öğünlerin tokluk ortalaması."""
    name = "B2 prototip (±15)"

    def __init__(self, tol=15):
        self.tol = tol

    def fit(self, df):
        self.df = df[["meal", "aclik", "tokluk"]].reset_index(drop=True)
        self.fallback = df.groupby("meal").tokluk.mean().to_dict(); return self

    def predict(self, df):
        out = []
        for m, a in zip(df.meal, df.aclik):
            s = self.df[(self.df.meal == m) & ((self.df.aclik - a).abs() <= self.tol)]
            out.append(s.tokluk.mean() if len(s) else self.fallback.get(m, self.df.tokluk.mean()))
        return np.array(out)


# --------------------------------------------------------------------------- ağırlıklı kNN
FEATS_BASE = ["aclik", "prev_bg", "dow", "r7_meal"]
FEATS_NUTR = ["n_carb", "n_gl", "n_sweet_carb", "n_starch_carb", "n_fat", "n_protein", "n_fiber"]


class WKNN:
    """Ağırlıklı kNN regresyon.

    Mesafe: sqrt( sum_j w_j * z_j^2 ) + w_meal * [öğün farklı] + w_emb * (1 - cos(menü embedding))
    z = eğitim verisinde standartlaştırılmış fark. Tahmin: mesafe-ağırlıklı (gauss çekirdek) ortalama.
    target='delta' ise tokluk - açlık farkı tahmin edilip açlık geri eklenir; 'level' ise doğrudan tokluk.
    """

    def __init__(self, weights: dict, k=15, w_meal=3.0, w_emb=0.0, target="level", bw=1.0, name="kNN", emb=None):
        self.weights, self.k, self.w_meal, self.w_emb = dict(weights), k, w_meal, w_emb
        self.target, self.bw, self.name, self.emb = target, bw, name, emb

    def _X(self, df):
        cols = list(self.weights)
        X = df[cols].astype(float).copy()
        for c in cols:
            X[c] = X[c].fillna(self.fill[c])
        return ((X - self.mu) / self.sd).values

    def fit(self, df):
        cols = list(self.weights)
        self.fill = {c: df[c].median() for c in cols}
        X = df[cols].astype(float).fillna(self.fill)
        self.mu, self.sd = X.mean(), X.std().replace(0, 1)
        self.Xtr = self._X(df)
        self.w = np.array([self.weights[c] for c in cols])
        self.meal = df.meal.to_numpy(dtype=object)
        self.y = (df.tokluk - df.aclik).values if self.target == "delta" else df.tokluk.values
        self.ids = df.event_id.to_numpy(dtype=object)
        self.train = df.reset_index(drop=True)
        self.Etr = self._E(df)
        return self

    def _E(self, df):
        if self.emb is None or self.w_emb == 0:
            return None
        return np.stack([self.emb[e] for e in df.event_id])

    def _dist(self, df):
        Xq = self._X(df)
        d2 = (((Xq[:, None, :] - self.Xtr[None, :, :]) ** 2) * self.w).sum(-1)
        D = np.sqrt(d2) + self.w_meal * (df.meal.to_numpy(dtype=object)[:, None] != self.meal[None, :])
        if self.Etr is not None:
            Eq = self._E(df)
            D = D + self.w_emb * (1 - Eq @ self.Etr.T)
        # aynı olay / aynı gün kendi komşusu olmasın (demo sorgularında o günün kaydı geçmiş sayılmaz)
        D = D + 1e6 * (df.event_id.to_numpy(dtype=object)[:, None] == self.ids[None, :])
        if "date" in df and "date" in self.train:
            D = D + 1e6 * (df.date.to_numpy(dtype=object)[:, None] == self.train.date.to_numpy(dtype=object)[None, :])
        return D

    def predict(self, df, return_nb=False):
        D = self._dist(df)
        k = min(self.k, D.shape[1])
        idx = np.argsort(D, axis=1)[:, :k]
        dk = np.take_along_axis(D, idx, 1)
        h = np.maximum(dk[:, -1:], 1e-6) * self.bw
        w = np.exp(-(dk / h) ** 2)
        w = w / w.sum(1, keepdims=True)
        yk = self.y[idx]
        p = (w * yk).sum(1)
        if self.target == "delta":
            p = p + df.aclik.values
        if return_nb:
            return p, idx, w, dk
        return p

    def neighbors(self, q: pd.DataFrame, n=5):
        p, idx, w, dk = self.predict(q, return_nb=True)
        rows = self.train.iloc[idx[0][:n]].copy()
        rows["agirlik"] = w[0][:n]
        rows["mesafe"] = dk[0][:n]
        return p[0], rows


# --------------------------------------------------------------------------- gradient boosting
class GBM:
    def __init__(self, feats, name="M3 LightGBM", **kw):
        self.feats, self.name = feats, name
        self.kw = dict(n_estimators=300, learning_rate=0.03, num_leaves=7, min_child_samples=15,
                       subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=5.0, verbose=-1)
        self.kw.update(kw)

    def _X(self, df):
        X = df[self.feats].astype(float).copy()
        for m in MEALS:
            X[f"meal_{m}"] = (df.meal == m).astype(float)
        return X

    def fit(self, df):
        import lightgbm as lgb
        self.m = lgb.LGBMRegressor(**self.kw).fit(self._X(df), df.tokluk)
        return self

    def predict(self, df):
        return self.m.predict(self._X(df))


class Ridge:
    def __init__(self, feats, name="Ridge", alpha=10.0):
        self.feats, self.name, self.alpha = feats, name, alpha

    def _X(self, df):
        X = df[self.feats].astype(float).copy()
        X = X.fillna(self.fill)
        for m in MEALS:
            X[f"meal_{m}"] = (df.meal == m).astype(float)
        return X

    def fit(self, df):
        from sklearn.linear_model import Ridge as R
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        self.fill = {c: df[c].median() for c in self.feats}
        self.m = make_pipeline(StandardScaler(), R(alpha=self.alpha)).fit(self._X(df), df.tokluk)
        return self

    def predict(self, df):
        return self.m.predict(self._X(df))


# --------------------------------------------------------------------------- konformal aralık
class Conformal:
    """Bölünmüş konformal: eğitim içi (ay-dışarıda) artıkların kuantilleri ile asimetrik aralık.

    lower = tahmin + q_lo(artık), upper = tahmin + q_hi(artık); coverage = 1 - alpha.
    """

    def __init__(self, make_model, alpha=0.2):
        self.make_model, self.alpha = make_model, alpha

    def fit(self, df):
        res = []
        for m in sorted(df.month.unique()):
            tr, va = df[df.month != m], df[df.month == m]
            if len(tr) < 30 or len(va) == 0:
                continue
            p = self.make_model().fit(tr).predict(va)
            res.append(va.tokluk.values - p)
        res = np.concatenate(res)
        n = len(res)
        lo_q = np.floor((n + 1) * (self.alpha / 2)) / n
        hi_q = np.ceil((n + 1) * (1 - self.alpha / 2)) / n
        self.lo, self.hi = np.quantile(res, max(lo_q, 0)), np.quantile(res, min(hi_q, 1))
        self.res = res
        self.model = self.make_model().fit(df)
        return self

    def predict(self, df):
        p = self.model.predict(df)
        return p, p + self.lo, p + self.hi
