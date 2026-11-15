"""Yerel LLM karşılaştırması (llama-server).

Her aday model için llama-server ayrı başlatılır, 20 bağlam JSON'u (reports/llm_queries.json) özetlenir,
otomatik ölçümler hesaplanır: sayı sadakati, yasak dil, hipo-ilk-cümle kuralı, uzunluk, hız, VRAM.
Çıktı: reports/llm_bakeoff.json, reports/llm_outputs.csv, reports/llm_blind.csv (model adları gizli, puanlama için)

Kullanım: python tools/llm_bakeoff.py [model_adı ...]
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from diyalife import summarizer as S  # noqa: E402

SERVER = r"D:\downloads\down3\llama\llama-server.exe"
PORT = 8082
CANDIDATES = {
    "qwen3.5-9b": dict(m=r"E:\model\Qwen3.5-9B-Q4_K_M.gguf", extra=[]),
    "gemma4-e4b": dict(m=r"E:\model\gemma4-e4b.gguf", extra=["--chat-template-file", r"E:\model\gemma4-official.jinja"]),
    "gemma4-e2b": dict(m=r"E:\model\gemma-4-E2B-it-Q4_K_M.gguf", extra=[]),
    "gemma4-26b-a4b": dict(m=r"E:\model\gemma-4-26B-A4B-it-UD-Q4_K_M.gguf", extra=["--n-cpu-moe", "24"], ngl="99"),
}


def vram():
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True).stdout
        return int(o.strip().splitlines()[0])
    except Exception:  # noqa: BLE001
        return None


def start(name):
    c = CANDIDATES[name]
    cmd = [SERVER, "-m", c["m"], "-ngl", c.get("ngl", "99"), "-c", "8192", "--jinja", "--reasoning", "off",
           "--temp", "0.2", "--host", "127.0.0.1", "--port", str(PORT), "-fa", "on", "--no-webui"] + c["extra"]
    log = open(ROOT / "reports" / f"llama_{name}.log", "w", encoding="utf-8")
    p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
    t0 = time.time()
    while time.time() - t0 < 300:
        if p.poll() is not None:
            raise RuntimeError(f"{name} başlatılamadı, bkz. reports/llama_{name}.log")
        try:
            if httpx.get(f"http://127.0.0.1:{PORT}/health", timeout=2).status_code == 200:
                return p, time.time() - t0
        except Exception:  # noqa: BLE001
            pass
        time.sleep(2)
    p.kill()
    raise RuntimeError("zaman aşımı")


def main(names, lang="tr"):
    queries = json.load(open(ROOT / "reports" / "llm_queries.json", encoding="utf-8"))
    S.LLM_URL = f"http://127.0.0.1:{PORT}"
    summary, rows = {}, []
    for name in names:
        tag = name if lang == "tr" else f"{name}@{lang}"
        print("==", tag, flush=True)
        try:
            p, load_s = start(name)
        except Exception as e:  # noqa: BLE001
            summary[name] = dict(error=str(e)); print(e); continue
        try:
            S.llm_summary(queries[0], timeout=600, lang=lang)  # ısınma
            vr = vram()
            res = []
            for i, q in enumerate(queries):
                try:
                    r = S.llm_summary(q, timeout=240, lang=lang)
                except Exception as e:  # noqa: BLE001
                    print(f"  q{i:02d} HATA {e}", flush=True)
                    r = dict(text="", seconds=240.0, tok_per_s=None)
                c = S.check(r["text"], q, lang)
                res.append(dict(model=tag, qid=i, text=r["text"], ok=c["ok"], bad_numbers=";".join(c["bad_numbers"]),
                                bad_language=";".join(c["bad_language"]), hipo_first=c["hipo_first"], words=c["words"],
                                seconds=r["seconds"], tok_per_s=r["tok_per_s"]))
                print(f"  q{i:02d} ok={c['ok']} {r['seconds']:.1f}s", flush=True)
            df = pd.DataFrame(res)
            n_hipo = sum(1 for q in queries if q["riskler"]["hipo_riski"])
            summary[tag] = dict(
                gecen_oran=float(df.ok.mean()),
                sayi_sadakati=float((df.bad_numbers == "").mean()),
                yasak_dil_orani=float((df.bad_language != "").mean()),
                hipo_ilk_cumle=f"{int(df[[q['riskler']['hipo_riski'] for q in queries]].hipo_first.sum())}/{n_hipo}",
                ort_kelime=float(df.words.mean()), ort_sure_s=float(df.seconds.mean()),
                tok_per_s=float(df.tok_per_s.mean()), yukleme_s=load_s, vram_mb=vr)
            rows.append(df)
            print(summary[tag], flush=True)
        finally:
            p.kill(); p.wait(); time.sleep(3)
        save(summary, rows)


def save(summary, rows):
    old = {}
    f = ROOT / "reports" / "llm_bakeoff.json"
    if f.exists():
        old = json.load(open(f, encoding="utf-8"))
    old.update(summary)
    json.dump(old, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if rows:
        out = pd.concat(rows)
        fo = ROOT / "reports" / "llm_outputs.csv"
        if fo.exists():
            prev = pd.read_csv(fo)
            out = pd.concat([prev[~prev.model.isin(out.model.unique())], out])
        out.to_csv(fo, index=False)
        # kör puanlama sayfası
        b = out.sample(frac=1, random_state=7).reset_index(drop=True)
        key = {m: f"Model-{chr(65+i)}" for i, m in enumerate(sorted(b.model.unique()))}
        random.seed(7)
        b["kod"] = b.model.map(key)
        b[["qid", "kod", "text"]].assign(puan_1_5="").to_csv(ROOT / "reports" / "llm_blind.csv", index=False)
        json.dump(key, open(ROOT / "reports" / "llm_blind_key.json", "w"), indent=1)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--lang=")]
    lg = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--lang=")), "tr")
    main(args or list(CANDIDATES), lg)
