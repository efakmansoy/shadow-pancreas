"""LLM karşılaştırması için gerçek veriden 20 bağlam JSON'u üretir (reports/llm_queries.json).

Seçim: farklı öğünler, düşük/orta/yüksek açlık, gerçekte hipo ve hiper olan öğünler, Ekim (kahvaltısız ay).
Her sorgu o günün kendi kaydı geçmişten çıkarılarak hesaplanır (engine aynı günü komşu yapmaz).
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shadow_pancreas.engine import Engine  # noqa: E402

E = Engine()
ev = E.events
pick = []
pick += ev[ev.status == "hipo"].sample(4, random_state=1).event_id.tolist()
pick += ev[ev.status == "hiper"].sample(5, random_state=1).event_id.tolist()
for meal in ["kahvalti", "ogle", "aksam"]:
    g = ev[(ev.status == "hedef") & (ev.meal == meal)]
    pick += g[g.aclik < 100].sample(1, random_state=2).event_id.tolist()
    pick += g[g.aclik > 200].sample(1, random_state=2).event_id.tolist() if (g.aclik > 200).any() else []
    pick += g[(g.aclik >= 100) & (g.aclik <= 200)].sample(1, random_state=2).event_id.tolist()
rest = ev[~ev.event_id.isin(pick)].sample(20, random_state=3).event_id.tolist()
pick = (pick + rest)[:20]
out, meta = [], []
for eid in pick:
    r = ev[ev.event_id == eid].iloc[0]
    q = E.query(r.date, r.meal, r.aclik, None if pd.isna(r.prev_bg) else r.prev_bg)
    out.append(q["context"])
    meta.append(dict(event_id=eid, gercek_tokluk=int(r.tokluk), tahmin=q["prediction"]))
json.dump(out, open(ROOT / "reports" / "llm_queries.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(meta, open(ROOT / "reports" / "llm_queries_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), "sorgu;", sum(c["riskler"]["hipo_riski"] for c in out), "hipo riskli")
print(json.dumps(out[0], ensure_ascii=False, indent=1))
