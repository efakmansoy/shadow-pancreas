"""RAGAS ile LLM özetlerinin değerlendirmesi (tamamen yerel).

Örnekler: reports/llm_queries.json (20 bağlam) + reports/llm_outputs.csv (her modelin özeti).
  user_input         : kullanıcının sorusu (öğün, açlık, menü)
  retrieved_contexts : geri getirilen bağlam: menü/besin, tahmin aralığı, benzer vaka özeti, tek tek benzer vakalar
  response           : modelin özeti
Ölçütler: Faithfulness (özetteki iddiaların bağlamca desteklenme oranı), ResponseRelevancy (özetin soruya uygunluğu).
Hakem LLM: Qwen3.5-9B (llama-server, ayrı port), üretici modellerden farklı aile. Embedding: TR-MTEB (yerel).
Çıktı: reports/ragas.json, reports/ragas_rows.csv

Kullanım: python tools/eval_ragas.py   (hakem sunucusunu kendisi başlatır)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import llm_bakeoff as LB  # noqa: E402

JUDGE = "qwen3.5-9b"
PORT = 8083


def question(c):
    menu = ", ".join(m["ad"] for m in c["menu"])
    return (f"Bugün {c['tarih']} {c['ogun_adi']} için açlık şekerim {c['aclik']} mg/dL. Menü: {menu}. "
            f"Geçmişte benzer öğünlerden sonra 2. saat şekerim nasıldı ve bu öğünde ne beklemeliyim?")


def contexts(c):
    t, b, m = c["tahmin"], c["benzer_ozet"], c["menu_toplam"]
    out = [
        f"Menü toplamı: yaklaşık {m['karbonhidrat_g']} g karbonhidrat (tatlıdan {m['tatli_karbonhidrat_g']} g), "
        f"{m['yag_g']} g yağ, {m['protein_g']} g protein, glisemik sınıf {m['glisemik_sinif']}. Bu menü geçmiş aynı öğün "
        f"menülerinin %{m['gecmis_menulere_gore_karbonhidrat_yuzdelik']}'inden daha fazla karbonhidrat içeriyor.",
        f"Tahmin (kategori): en olası sonuç '{t['en_olasi']}'. Olasılıklar: düşük (70 altı) yaklaşık "
        f"%{t['olasilik_yuzde']['dusuk']}, hedefte (70–180) yaklaşık %{t['olasilik_yuzde']['hedefte']}, "
        f"yüksek (180 üstü) yaklaşık %{t['olasilik_yuzde']['yuksek']}. Düşük şeker dikkat notu: "
        f"{'evet' if c['riskler']['hipo_riski'] else 'hayır'}.",
        f"En benzer {b['benzer_vaka_sayisi']} geçmiş öğünün {b['hedefte']} tanesinde tokluk hedefte (70–180), "
        f"{b['hiper']} tanesinde 180 üstü, {b['hipo']} tanesinde 70 altı; ortalama tokluk {b['tokluk_ortalama']} mg/dL. "
        f"Bu açlık seviyesinde (±20) aynı öğünden {b['yakin_acliktaki_gecmis_ogun']} geçmiş kayıt var"
        f"{', veri az' if b['az_veri'] else ''}.",
    ]
    for v in c["benzer_vakalar"]:
        out.append(f"Benzer vaka {v['tarih']}: açlık {v['aclik']}, tokluk {v['tokluk']} ({v['durum']}), "
                   f"yaklaşık {v['karbonhidrat_g']} g karbonhidrat, menü: {v['menu']}.")
    out.append("Kural: sistem insülin dozu önermez; kararı kullanıcı kendi planına ve ekibine göre verir.")
    return out


class LocalEmb:
    """ragas için yerel embedding (TR-MTEB)."""

    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.m = SentenceTransformer("trmteb/turkish-embedding-model", device="cpu")

    def embed_query(self, t):
        return self.m.encode([t], normalize_embeddings=True)[0].tolist()

    def embed_documents(self, ts):
        return self.m.encode(ts, normalize_embeddings=True).tolist()

    async def aembed_query(self, t):
        return self.embed_query(t)

    async def aembed_documents(self, ts):
        return self.embed_documents(ts)


def main(models=None):
    from langchain_openai import ChatOpenAI
    from ragas import EvaluationDataset, RunConfig, evaluate
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import Faithfulness, ResponseRelevancy

    Q = json.load(open(ROOT / "reports" / "llm_queries.json", encoding="utf-8"))
    out = pd.read_csv(ROOT / "reports" / "llm_outputs.csv").fillna({"text": ""})
    sys.path.insert(0, str(ROOT / "src"))
    from diyalife.summarizer import template_summary
    tpl = pd.DataFrame([dict(model="şablon (referans)", qid=i, text=template_summary(c)) for i, c in enumerate(Q)])
    out = pd.concat([out, tpl], ignore_index=True)
    models = models or sorted(out.model.unique())
    LB.PORT = PORT
    proc, _ = LB.start(JUDGE)
    try:
        llm = LangchainLLMWrapper(ChatOpenAI(base_url=f"http://127.0.0.1:{PORT}/v1", api_key="yerel", model=JUDGE,
                                             temperature=0, max_tokens=2048, timeout=300))
        emb = LangchainEmbeddingsWrapper(LocalEmb())
        metrics = [Faithfulness(llm=llm), ResponseRelevancy(llm=llm, embeddings=emb)]
        rows, summary = [], {}
        for m in models:
            g = out[(out.model == m) & (out.text.str.len() > 0)]
            samples = [dict(user_input=question(Q[int(r.qid)]), retrieved_contexts=contexts(Q[int(r.qid)]),
                            response=r.text) for r in g.itertuples()]
            ds = EvaluationDataset.from_list(samples)
            res = evaluate(ds, metrics=metrics, run_config=RunConfig(timeout=300, max_workers=2, max_retries=2),
                           show_progress=False)
            df = res.to_pandas()
            df["model"] = m
            df["qid"] = g.qid.values
            rows.append(df)
            summary[m] = {k: (None if np.isnan(df[k].mean()) else round(float(df[k].mean()), 3))
                          for k in ["faithfulness", "answer_relevancy"] if k in df}
            summary[m]["n_gecerli"] = int(df["faithfulness"].notna().sum())
            print(m, summary[m], flush=True)
    finally:
        proc.kill()
    R = pd.concat(rows)
    R.to_csv(ROOT / "reports" / "ragas_rows.csv", index=False)
    json.dump(dict(sonuc=summary, hakem=JUDGE, yontem=__doc__.strip()), open(ROOT / "reports" / "ragas.json", "w",
              encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
