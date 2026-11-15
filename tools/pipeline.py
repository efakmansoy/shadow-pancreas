"""Tüm veri + model hattını baştan çalıştırır.

1 prepare            ham Excel -> events.csv, menu_days.csv, daily_log.csv, items_raw.csv
2 build_ingredients  malzeme sözlüğü -> USDA değerleri
3 check_recipes      tarif/alias tutarlılık kontrolü (hata varsa durur)
4 event_nutrition    öğün besin vektörleri
5 build_embeddings   TR-MTEB yemek/öğün embedding'leri
6 validate_nutrition USDA hazır yemek analizleriyle karşılaştırma
7 evaluate           ay-dışarıda CV (Ocak–Haziran), ablasyon
8 final test         Ekim'de tek seferlik test
9 finalize_model     uygulama modeli (tüm veri)
10 make_llm_queries  LLM karşılaştırma sorguları
Kullanım: python tools/pipeline.py [--from N] [--to M]
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TEST_MODELS = "B2 prototip (±15),M1 kNN (yemeksiz),M2 kNN + besin vektörü,M3 LightGBM + besin,A: Ridge yemeksiz,M4 kNN + besin + insülin (uygulama),M5 LightGBM + besin + insülin"
STEPS = [
    [PY, "src/prepare.py"],
    [PY, "src/build_ingredients.py"],
    [PY, "src/check_recipes.py"],
    [PY, "-c", "import sys; sys.path.insert(0,'src'); import pandas as pd; from diyalife import nutrition as NU; "
               "NU.build_event_nutrition(pd.read_csv('data/events.csv')).to_csv('data/event_nutrition.csv', index=False)"],
    [PY, "src/build_embeddings.py"],
    [PY, "tools/validate_nutrition.py"],
    [PY, "src/evaluate.py"],
    [PY, "src/evaluate.py", "test", TEST_MODELS],
    [PY, "tools/finalize_model.py"],
    [PY, "tools/make_llm_queries.py"],
]


def main():
    start = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 1
    end = int(sys.argv[sys.argv.index("--to") + 1]) if "--to" in sys.argv else len(STEPS)
    for i, cmd in enumerate(STEPS, 1):
        if i < start or i > end:
            continue
        print(f"\n=== {i}: {' '.join(cmd[1:3])}", flush=True)
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        tail = "\n".join(r.stdout.strip().splitlines()[-25:])
        print(tail, flush=True)
        if r.returncode != 0 or (i == 3 and "HATALAR" in r.stdout):
            print(r.stderr[-3000:]); sys.exit(f"adım {i} başarısız")


if __name__ == "__main__":
    main()
