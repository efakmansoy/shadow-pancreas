"""Model değerlendirmesi.

Geliştirme: Ocak–Haziran (5 ay) üzerinde ay-dışarıda çapraz doğrulama (LOMO). kNN ağırlıkları her dış katta
yalnızca eğitim aylarının iç LOMO'suyla rastgele aramayla seçilir (iç içe, sızıntısız).
Son test: Ekim (40 öğün), yalnızca en sonda bir kez.

Çıktı: reports/results.json, reports/predictions_cv.csv, reports/predictions_test.csv
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shadow_pancreas.models import B0, B1, B2, FEATS_NUTR, GBM, WKNN, Conformal, Ridge  # noqa: E402

REP = ROOT / "reports"
REP.mkdir(exist_ok=True)
RNG = np.random.default_rng(42)
TEST_MONTH = 10


def load():
    ev = pd.read_csv(ROOT / "data" / "events.csv")
    nut = pd.read_csv(ROOT / "data" / "event_nutrition.csv")
    ev = ev.merge(nut, on="event_id")
    emb = None
    p = ROOT / "data" / "event_embeddings.npz"
    if p.exists():
        z = np.load(p, allow_pickle=True)
        emb = dict(zip(z["ids"], z["E"]))
    return ev, emb


# --------------------------------------------------------------------------- metrikler
def metrics(y, p, lo=None, hi=None):
    y, p = np.asarray(y), np.asarray(p)
    out = dict(n=int(len(y)), mae=float(np.mean(np.abs(y - p))), rmse=float(np.sqrt(np.mean((y - p) ** 2))))
    hy, hp = y > 180, p > 180
    out.update(hiper_gercek=int(hy.sum()), hiper_yakalanan=int((hy & hp).sum()), hiper_kacan=int((hy & ~hp).sum()),
               hiper_yanlis_alarm=int((~hy & hp).sum()))
    if lo is not None:
        lo, hi = np.asarray(lo), np.asarray(hi)
        out["kapsama"] = float(np.mean((y >= lo) & (y <= hi)))
        out["aralik_genislik"] = float(np.mean(hi - lo))
        ly, lp = y < 70, lo < 70
        out.update(hipo_gercek=int(ly.sum()), hipo_yakalanan=int((ly & lp).sum()), hipo_kacan=int((ly & ~lp).sum()),
                   hipo_yanlis_alarm=int((~ly & lp).sum()))
        uh = hi > 180  # aralığın üst ucu 180'i aşıyorsa "hiper olabilir" uyarısı
        out.update(hiper_uyari_yakalanan=int((hy & uh).sum()), hiper_uyari_yanlis=int((~hy & uh).sum()))
    return out


def boot_ci(y, p, q=None, n=2000):
    """MAE için (ve q verilirse MAE(p) - MAE(q) farkı için) %95 bootstrap aralığı."""
    y, p = np.asarray(y), np.asarray(p)
    idx = RNG.integers(0, len(y), (n, len(y)))
    a = np.abs(y - p)[idx].mean(1)
    if q is None:
        return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    b = np.abs(y - np.asarray(q))[idx].mean(1)
    d = a - b
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


# --------------------------------------------------------------------------- kNN ağırlık araması
def sample_cfg(feats, use_emb):
    w = {f: float(RNG.choice([0, 0.25, 0.5, 1, 2, 4])) for f in feats}
    if "insulin" in w:  # benzer vaka = benzer doz: insülin ağırlığı en az 1 (tasarım kısıtı)
        w["insulin"] = float(RNG.choice([1, 2, 4]))
    w["aclik"] = float(RNG.choice([0.5, 1, 2, 4, 8]))
    return dict(weights=w, k=int(RNG.choice([5, 8, 12, 15, 20, 30, 45])), w_meal=float(RNG.choice([0, 0.5, 1, 2, 4])),
                w_emb=float(RNG.choice([0, 1, 2, 4, 8])) if use_emb else 0.0,
                target=str(RNG.choice(["level", "delta"])), bw=float(RNG.choice([0.7, 1.0, 1.5, 3.0])))


def inner_score(cfg, df, emb):
    errs = []
    for m in sorted(df.month.unique()):
        tr, va = df[df.month != m], df[df.month == m]
        p = WKNN(emb=emb, **cfg).fit(tr).predict(va)
        errs.append(np.abs(va.tokluk.values - p))
    return float(np.mean(np.concatenate(errs)))


def tune_knn(df, feats, emb=None, use_emb=False, n_iter=120):
    cands = [sample_cfg(feats, use_emb) for _ in range(n_iter)]
    # elle başlangıç noktaları
    base = {f: 0.0 for f in feats}; base["aclik"] = 1.0
    if "insulin" in base:
        base["insulin"] = 1.0
    cands.append(dict(weights=base, k=15, w_meal=4.0, w_emb=0.0, target="level", bw=1.0))
    scores = [inner_score(c, df, emb) for c in cands]
    best = cands[int(np.argmin(scores))]
    return best, float(np.min(scores))


# --------------------------------------------------------------------------- deney tanımları
def specs(emb):
    base = ["aclik", "prev_bg", "dow", "r7_meal"]
    carb = base + ["n_carb"]
    full = base + FEATS_NUTR
    S = {
        "B0 ortalama": lambda df: B0(),
        "B1 öğün medyanı": lambda df: B1(),
        "B2 prototip (±15)": lambda df: B2(15),
        "M1 kNN (yemeksiz)": ("knn", base, False),
        "M2 kNN + besin vektörü": ("knn", full, False),
        "M3 LightGBM + besin": lambda df: GBM(full, name="M3"),
        # ablasyon
        "A: kNN + yalnız karbonhidrat": ("knn", carb, False),
        "A: kNN + besin + menü embedding": ("knn", full, True),
        "A: kNN + yalnız menü embedding": ("knn", base, True),
        "A: Ridge yemeksiz": lambda df: Ridge(base, name="ridge0"),
        "A: Ridge + besin": lambda df: Ridge(full, name="ridge1"),
        "A: LightGBM yemeksiz": lambda df: GBM(base, name="gbm0"),
        "M4 kNN + besin + insülin (uygulama)": ("knn", full + ["insulin"], False),
        "M5 LightGBM + besin + insülin": lambda df: GBM(full + ["insulin"], name="gbm_ins"),
    }
    if emb is None:
        S = {k: v for k, v in S.items() if not (isinstance(v, tuple) and v[2])}
    return S


def make_factory(spec, train, emb, log):
    if callable(spec):
        return lambda: spec(train)
    _, feats, use_emb = spec
    cfg, sc = tune_knn(train, feats, emb, use_emb)
    log.append(dict(cfg=cfg, inner_mae=sc))
    return lambda: WKNN(emb=emb, **cfg)


def run():
    ev, emb = load()
    dev = ev[ev.month != TEST_MONTH].reset_index(drop=True)
    test = ev[ev.month == TEST_MONTH].reset_index(drop=True)
    S = specs(emb)
    results, preds, tuned = {}, [], {}
    for name, spec in S.items():
        print("…", name, flush=True)
        ys, ps, los, his, rows = [], [], [], [], []
        tuned[name] = []
        for m in sorted(dev.month.unique()):
            tr, te = dev[dev.month != m], dev[dev.month == m]
            fac = make_factory(spec, tr, emb, tuned[name])
            conf = Conformal(fac, alpha=0.2).fit(tr)
            p, lo, hi = conf.predict(te)
            ys.append(te.tokluk.values); ps.append(p); los.append(lo); his.append(hi)
            rows.append(pd.DataFrame(dict(event_id=te.event_id, model=name, pred=p, lo=lo, hi=hi)))
        y, p, lo, hi = map(np.concatenate, (ys, ps, los, his))
        r = metrics(y, p, lo, hi)
        r["mae_ci95"] = boot_ci(y, p)
        results[name] = r
        preds.append(pd.concat(rows))
        print(f"   MAE {r['mae']:.1f}  kapsama {r['kapsama']:.2f}  hiper {r['hiper_yakalanan']}/{r['hiper_gercek']} "
              f"(yanlış {r['hiper_yanlis_alarm']})  hipo {r['hipo_yakalanan']}/{r['hipo_gercek']} (yanlış {r['hipo_yanlis_alarm']})",
              flush=True)
    P = pd.concat(preds).merge(ev[["event_id", "tokluk", "meal", "month", "aclik"]], on="event_id")
    P.to_csv(REP / "predictions_cv.csv", index=False)

    # baseline'a göre eşleştirilmiş fark aralıkları
    piv = P.pivot_table(index="event_id", columns="model", values="pred")
    yv = P.drop_duplicates("event_id").set_index("event_id").loc[piv.index, "tokluk"].values
    diffs = {}
    for name in S:
        for ref in ["B2 prototip (±15)", "M1 kNN (yemeksiz)"]:
            if name != ref:
                diffs[f"{name} − {ref}"] = boot_ci(yv, piv[name].values, piv[ref].values)

    # gruplar
    groups = {}
    for name in ["B2 prototip (±15)", "M1 kNN (yemeksiz)", "M2 kNN + besin vektörü", "M3 LightGBM + besin"]:
        q = P[P.model == name].copy()
        q["err"] = (q.tokluk - q.pred).abs()
        q["aclik_band"] = pd.cut(q.aclik, [0, 100, 180, 1000], labels=["<100", "100–180", ">180"])
        groups[name] = dict(ogun=q.groupby("meal").err.mean().round(1).to_dict(),
                            ay=q.groupby("month").err.mean().round(1).to_dict(),
                            aclik=q.groupby("aclik_band", observed=True).err.mean().round(1).to_dict())

    json.dump(dict(cv=results, farklar=diffs, gruplar=groups,
                   tuned={k: v for k, v in tuned.items() if v}), open(REP / "results_cv.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, default=float)
    return ev, dev, test, emb, results


def final_test(names):
    """Ekim'de tek seferlik son test (geliştirme verisinin tamamıyla eğitilir)."""
    ev, emb = load()
    dev = ev[ev.month != TEST_MONTH].reset_index(drop=True)
    test = ev[ev.month == TEST_MONTH].reset_index(drop=True)
    S = specs(emb)
    out, rows, cfgs = {}, [], {}
    for name in names:
        log = []
        fac = make_factory(S[name], dev, emb, log)
        conf = Conformal(fac, alpha=0.2).fit(dev)
        p, lo, hi = conf.predict(test)
        r = metrics(test.tokluk, p, lo, hi); r["mae_ci95"] = boot_ci(test.tokluk, p)
        out[name] = r
        cfgs[name] = log
        rows.append(pd.DataFrame(dict(event_id=test.event_id, model=name, pred=p, lo=lo, hi=hi)))
        print(f"TEST {name}: MAE {r['mae']:.1f} {r['mae_ci95']} kapsama {r['kapsama']:.2f}", flush=True)
    P = pd.concat(rows).merge(ev[["event_id", "tokluk", "meal"]], on="event_id")
    P.to_csv(REP / "predictions_test.csv", index=False)
    piv = P.pivot_table(index="event_id", columns="model", values="pred")
    yv = P.drop_duplicates("event_id").set_index("event_id").loc[piv.index, "tokluk"].values
    diffs = {f"{a} − {b}": boot_ci(yv, piv[a].values, piv[b].values) for a in names for b in names if a != b}
    json.dump(dict(test=out, farklar=diffs, cfg=cfgs), open(REP / "results_test.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        final_test(sys.argv[2].split(","))
    else:
        run()
