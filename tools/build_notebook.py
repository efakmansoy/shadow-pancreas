"""notebooks/embedding_karsilastirma.ipynb dosyasını üretir (veri ve değerlendirme kodu notebook'a gömülür)."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1] / "notebooks"
SYN = (ROOT / "synthetic_data.py").read_text(encoding="utf-8")
RUN1 = (ROOT / "run_one.py").read_text(encoding="utf-8")
EVAL = (ROOT / "embed_eval.py").read_text(encoding="utf-8")

cells = []
NL = chr(10)


def md(s):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")})


def code(s):
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip("\n")})


md("""
# Shadow Pancreas — Türkçe yemek adları için embedding karşılaştırması

**Amaç:** Menü dosyasındeki yemek adlarını (ör. *"Domates Çorba (Kaşarlı)"*, *"Kol Böreği"*, *"Şöbiyet"*) standart yemeklere bağlamak ve besin değeri bilinmeyen yemeklere en yakın yemeği bulmak için hangi embedding modelinin işe yaradığını ölçmek.

**Veri:** Tamamen **sentetik**: 127 standart yemek, 702 yazım varyantı/eş ad sorgusu, 38 elle işaretlenmiş zor çift. Besin değerleri porsiyon başına *yaklaşık* değerler, yalnızca bu deney için. Asıl sistemdeki değerler TürKomp + USDA FDC ile hesaplanacak.

| Görev | Soru | Metrik |
|---|---|---|
| **T1 Ad eşleştirme** | "Ezo Gelin Çorbası", "Koy Bazlamsi", "Spagetti (Napoliten)" → doğru standart yemek mi? | Acc@1, Recall@5, MRR |
| **T2 Karbonhidrat kNN** | Bir yemeği veritabanından çıkar; en yakın 3 komşunun karbonhidratıyla tahmin et | MAE (g/porsiyon), kategori isabeti |
| **T3 Zor çiftler** | *Ekmek ~ Bazlama* yakın, *Ekmek ~ Ekmek Kadayıfı* uzak çıkıyor mu? | ROC-AUC (0.5 = rastgele) |
| **T4 Besin korelasyonu** | Kosinüs benzerliği besin benzerliğiyle ne kadar örtüşüyor? | Spearman ρ |

T2–T4 iki biçimde ölçülür: **ad** (yalnızca yemek adı) ve **zengin** (ad + kısa malzeme açıklaması; gerçek sistemde bu açıklamayı yerel LLM üretecek).

**Çalıştırma:** `Çalışma zamanı → Çalışma zamanı türünü değiştir → T4 GPU`, ardından `Tümünü çalıştır`.

**EmbeddingGemma** gated bir model. Önce [huggingface.co/google/embeddinggemma-300m](https://huggingface.co/google/embeddinggemma-300m) sayfasında lisansı kabul et, sonra Colab'da soldaki anahtar simgesinden (*Secrets*) `HF_TOKEN` adıyla token'ını ekle ve "not defteri erişimi"ni aç. Token yoksa bu model atlanır, diğerleri çalışır.

Her embedding modeli **ayrı bir süreçte** çalışır. Bir model GPU'da çökerse diğerleri etkilenmez ve o model bir kez de CPU'da denenir.
""")

code("""
# transformers 5.x bazı modellerin kendi koduyla (gte-multilingual, embeddingmagibu) uyumsuz -> 4.x'e sabitle
!pip -q install "transformers>=4.56,<5" "sentence-transformers>=5.1,<6"
import sentence_transformers, transformers, torch
print("sentence-transformers", sentence_transformers.__version__, "| transformers", transformers.__version__)
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "yok (CPU'da da çalışır, daha yavaş)")
""")

code("""
# İsteğe bağlı: gated modeller (EmbeddingGemma) için Hugging Face girişi
try:
    from google.colab import userdata
    from huggingface_hub import login
    login(userdata.get("HF_TOKEN"))
    print("HF girişi yapıldı")
except Exception as e:
    print("HF_TOKEN yok, gated modeller atlanabilir:", type(e).__name__)
""")

code("%%writefile synthetic_data.py\n" + SYN)
code("%%writefile embed_eval.py\n" + EVAL)
code("%%writefile run_one.py\n" + RUN1)

md("## 1. Sentetik veri")
code("""
import importlib, pandas as pd, numpy as np
import synthetic_data, embed_eval
importlib.reload(synthetic_data); importlib.reload(embed_eval)
from synthetic_data import build
from embed_eval import *

dishes, queries, pairs = build(seed=42)
nsim = nutrition_similarity(dishes)
ddf = pd.DataFrame(dishes)
qdf = pd.DataFrame(queries).assign(hedef=lambda x: x.target_id.map(ddf.name))
pdf = pd.DataFrame(pairs).assign(a_ad=lambda x: x.a.map(ddf.name), b_ad=lambda x: x.b.map(ddf.name))
print(len(ddf), "yemek |", len(qdf), "sorgu |", len(pdf), "zor çift")
display(qdf.kind.value_counts().rename("sorgu türü"))
display(qdf.sample(12, random_state=1)[["query", "kind", "hedef"]])
display(ddf[["name", "category", "carb", "protein", "fat", "fiber", "gi", "desc"]].head(10))
ddf.to_csv("sentetik_yemekler.csv", index=False); qdf.to_csv("sentetik_sorgular.csv", index=False); pdf.to_csv("zor_ciftler.csv", index=False)
""")

md("## 2. Taban çizgileri (embedding'siz)")
code("""
B = baselines(dishes)
print(f"T2 karbonhidrat MAE | genel ortalama: {B['global_mean_mae']:.1f} g | kategori ortalaması (kategori biliniyorsa): {B['category_mean_mae']:.1f} g")

results, per_kind_all, wrong_all, pair_sims_all, S_all = [], {}, {}, {}, {}
lex_corpus = [d["name"] for d in dishes] + [a for d in dishes for a in d["aliases"]] + texts_for(dishes, True)
for an in ["char_wb", "word"]:
    enc = LexicalEncoder(an); enc.fit(lex_corpus)
    row, pk, wrong, ps, S = evaluate(enc, dishes, queries, pairs, nsim)
    results.append(row); per_kind_all[enc.name] = pk; wrong_all[enc.name] = wrong; pair_sims_all[enc.name] = ps; S_all[enc.name] = S
pd.DataFrame(results).round(3)
""")

md("## 3. Embedding modelleri" + NL + "Her model ayrı bir süreçte yüklenir ve ölçülür. GPU'da hata veren model bir kez CPU'da tekrar denenir. Yine de çalışmayan modelin hata nedeni yazdırılır.")
code("""
import subprocess, pickle, os, sys, time
OUT = "sonuclar_tmp"; os.makedirs(OUT, exist_ok=True)
device = "cuda" if torch.cuda.is_available() else "cpu"
skipped = {}
for i, (label, mid, cfg) in enumerate(DENSE_MODELS):
    for f in (f"{OUT}/{i}.pkl", f"{OUT}/{i}.err"):
        if os.path.exists(f): os.remove(f)
    for dev in ([device, "cpu"] if device == "cuda" else ["cpu"]):
        t0 = time.time()
        p = subprocess.run([sys.executable, "run_one.py", str(i), dev, OUT], capture_output=True, text=True)
        if os.path.exists(f"{OUT}/{i}.pkl"):
            break
        print(f"  {label}: {dev} başarısız ({time.time()-t0:.0f}s)" + (" -> CPU'da tekrar deneniyor" if dev == "cuda" else ""))
    if not os.path.exists(f"{OUT}/{i}.pkl"):
        err = open(f"{OUT}/{i}.err", encoding="utf-8").read() if os.path.exists(f"{OUT}/{i}.err") else p.stderr[-2000:]
        skipped[label] = err.splitlines()[0][:200] if err else "bilinmeyen hata"
        print("ATLANDI", label, "->", skipped[label]); continue
    r = pickle.load(open(f"{OUT}/{i}.pkl", "rb"))
    row = r["row"]; results.append(row)
    per_kind_all[label] = r["per_kind"]; wrong_all[label] = r["wrong"]; pair_sims_all[label] = r["pair_sims"]; S_all[label] = r["S"]
    print(f"OK {label:28s} [{row['cihaz']}] T1@1={row['T1_acc@1']:.3f}  T2 MAE={row['T2_carbMAE_zengin']:.1f}  T3 AUC(zengin)={row['T3_AUC_zengin']:.2f}")
print("Atlananlar:", skipped)
""")

md("## 4. Sonuç tablosu\n`genel_sıra`: T1 Acc@1, T2 MAE (zengin), T2 kategori isabeti (zengin), T3 AUC (ad ve zengin), T4 ρ (zengin) metriklerindeki sıraların ortalaması. Küçük olan daha iyi.")
code("""
df = pd.DataFrame(results)
df["genel_sıra"] = composite(df)
df = df.sort_values("genel_sıra").reset_index(drop=True)
show = ["model", "cihaz", "genel_sıra", "T1_acc@1", "T1_recall@5", "T2_carbMAE_ad", "T2_carbMAE_zengin", "T2_kategori@1_zengin",
        "T3_AUC_ad", "T3_AUC_zengin", "T4_spearman_ad", "T4_spearman_zengin", "parametre_M", "boyut", "süre_sn"]
show = [c for c in show if c in df]
(df[show].style.format(precision=3)
   .background_gradient(subset=["T1_acc@1", "T3_AUC_ad", "T3_AUC_zengin", "T4_spearman_zengin"], cmap="Greens")
   .background_gradient(subset=["T2_carbMAE_zengin"], cmap="Greens_r"))
""")

code("""
import matplotlib.pyplot as plt
fig, ax = plt.subplots(2, 2, figsize=(14, 9))
order = df.model
def bar(a, col, title, ref=None, lo=False):
    a.barh(order, df[col], color="#3b7a57"); a.invert_yaxis(); a.set_title(title)
    for r, lab in (ref or []):
        a.axvline(r, ls="--", c="#b5523b"); a.text(r, len(order) - 0.5, " " + lab, color="#b5523b", va="bottom")
bar(ax[0, 0], "T1_acc@1", "T1 Ad eşleştirme — Acc@1 (yüksek iyi)")
bar(ax[0, 1], "T2_carbMAE_zengin", "T2 Karbonhidrat kNN MAE, g (düşük iyi)",
    ref=[(B["global_mean_mae"], "genel ort."), (B["category_mean_mae"], "kategori ort.")])
bar(ax[1, 0], "T3_AUC_ad", "T3 Zor çiftler AUC — yalnızca ad (0.5 = rastgele)", ref=[(0.5, "rastgele")])
bar(ax[1, 1], "T4_spearman_zengin", "T4 Besin korelasyonu ρ — zengin metin")
plt.tight_layout(); plt.show()
""")

md("## 4b. Hibrit ad eşleştirme (RRF)" + NL + "TF-IDF harf n-gram ile her embedding modelinin sıralamaları Reciprocal Rank Fusion ile birleştirilir. TF-IDF yazım hatalarında, embedding eş adlarda güçlü olduğu için birleşimin ikisini de geçmesi beklenir.")
code("""
hyb_rows, hyb_kind = [], {}
lex = "TF-IDF harf 2-4"
dense_names = [x for x in S_all if not x.startswith("TF-IDF")]
for m in dense_names:
    for w in [0.5, 1.0, 2.0]:
        S = rrf([S_all[lex], S_all[m]], weights=[1.0, w])
        met, pk_h = rank_metrics(S, queries)
        name = f"RRF: TF-IDF + {m}" + ("" if w == 1.0 else f" (embedding ağırlığı {w:g})")
        hyb_rows.append({"yöntem": name, "T1_acc@1": met["acc1"], "T1_recall@5": met["r5"], "T1_mrr": met["mrr"]})
        hyb_kind[name] = pk_h
for m in [lex] + dense_names:
    met, _ = rank_metrics(S_all[m], queries)
    hyb_rows.append({"yöntem": m + " (tek başına)", "T1_acc@1": met["acc1"], "T1_recall@5": met["r5"], "T1_mrr": met["mrr"]})
hyb = pd.DataFrame(hyb_rows).sort_values("T1_acc@1", ascending=False).reset_index(drop=True)
display(hyb.style.format(precision=3).background_gradient(subset=["T1_acc@1"], cmap="Greens"))
best_h = hyb[hyb["yöntem"].str.startswith("RRF")].iloc[0]["yöntem"]
print("En iyi hibrit:", best_h)
display(pd.DataFrame({best_h: hyb_kind[best_h], lex: per_kind_all[lex]}).T.style.format("{:.2f}"))
hyb.to_csv("hibrit_sonuclari.csv", index=False)
""")

md("## 5. Hangi tür sorguda hata yapıyor? (T1)")
code("""
pk = pd.DataFrame(per_kind_all).T.loc[df.model]
display(pk.style.format("{:.2f}").background_gradient(cmap="RdYlGn", vmin=0.3, vmax=1))
""")

md("## 6. Zor çiftlerde benzerlikler (yalnızca ad)\nEtiket 1: besin olarak yakın (yüksek benzerlik beklenir). Etiket 0: kelime olarak benzer ama besin olarak farklı (düşük benzerlik beklenir).")
code("""
top = list(df.model[:4]) + [m for m in ["TF-IDF harf 2-4"] if m not in list(df.model[:4])]
tbl = pdf[["a_ad", "b_ad", "label"]].copy()
for m in top:
    tbl[m] = np.round(pair_sims_all[m], 2)
display(tbl.sort_values("label", ascending=False).style.background_gradient(subset=top, cmap="Blues"))
""")

md("## 7. En iyi modelin hataları (T1)")
code("""
best = df.model[0]
print("En iyi:", best, "| hatalı sorgu sayısı:", len(wrong_all[best]))
display(pd.DataFrame(wrong_all[best], columns=["sorgu", "doğru", "modelin seçtiği"]).head(30))
""")

md("""
## 8. Karar notları
- **T1 (ad eşleştirme)** normalizasyon adımı için belirleyici. Harf n-gram TF-IDF burada güçlü bir rakip; bir embedding onu geçemiyorsa normalizasyonda **hibrit** (TF-IDF + embedding, RRF ile birleştirme) kullanılmalı.
- **T3 / T4** "ekmek ~ bazlama" sorununun ölçüsü. Embedding'in tek başına besin benzerliğini yakalaması beklenmez. Asıl benzerlik **besin vektöründen** gelecek; embedding yalnızca (a) adı standart yemeğe bağlamak ve (b) besin değeri bilinmeyen yemek için yedek tahmin üretmek için kullanılacak.
- **T2**'de bir embedding *kategori ortalaması* çizgisinin altına iniyorsa yedek tahminci olarak işe yarıyor demektir.
- Menüdeki yemek kümesi sabit (~570 ad). Embedding'ler bir kez hesaplanıp dosyaya yazılabilir, yani çalışma anında embedding sunucusu gerekmeyebilir. Gerekirse kazanan modelin GGUF sürümü `llama-server --embeddings` ile ayrı bir portta çalıştırılabilir.
- Seçimde hız ve boyut da önemli: farklar küçükse küçük modeli seç.
""")

code("""
df.to_csv("embedding_sonuclari.csv", index=False)
pk.to_csv("embedding_sorgu_turu.csv")
try:
    from google.colab import files
    for f in ["embedding_sonuclari.csv", "embedding_sorgu_turu.csv", "hibrit_sonuclari.csv"]:
        files.download(f)
except Exception:
    print("Colab dışında: CSV dosyaları çalışma klasörüne yazıldı.")
""")

nb = {
    "cells": cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {"provenance": [], "gpuType": "T4"},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}
out = ROOT / "embedding_karsilastirma.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("yazıldı:", out, len(cells), "hücre")
