"""Shadow Pancreas — yerel sunucu.

Çalıştırma:  python app/server.py   (http://127.0.0.1:8000)
LLM:         llama-server ayrı süreçte, varsayılan http://127.0.0.1:8081 (DIYALIFE_LLM_URL ile değiştirilebilir).
             Erişilemezse özetler şablondan üretilir, uygulama çalışmaya devam eder.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date as Date
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from diyalife import nutrition as NU  # noqa: E402
from diyalife import summarizer as SU  # noqa: E402
from diyalife.engine import GUN, GUN_EN, MEALS, Engine  # noqa: E402
from diyalife.matcher import NameMatcher  # noqa: E402

app = FastAPI(title="Shadow Pancreas")
STATIC = ROOT / "app" / "static"
MATCHER = NameMatcher(use_embedding=os.environ.get("DIYALIFE_NO_EMB") != "1")
ENGINE = Engine(matcher=MATCHER)
MSG = {"menu_yok": {"tr": "Bu tarih ve öğün için menü yok. Önce menüyü gir.",
                    "en": "No menu for this date and meal yet. Enter the menu first."},
       "aclik": {"tr": "Açlık değeri 20–600 mg/dL arasında olmalı.", "en": "Pre-meal glucose must be 20–600 mg/dL."},
       "ogun": {"tr": "Geçersiz öğün.", "en": "Invalid meal."},
       "tarih": {"tr": "Geçersiz tarih.", "en": "Invalid date."},
       "yemek": {"tr": "Yemek bulunamadı.", "en": "Dish not found."}}


def L(lang):
    return "tr" if lang == "tr" else "en"


def err(status, key, lang):
    raise HTTPException(status, detail=dict(code=key, message=MSG[key][L(lang)]))


def check_dm(d, meal, lang):
    try:
        Date.fromisoformat(d)
    except Exception:  # noqa: BLE001
        err(422, "tarih", lang)
    if meal not in MEALS:
        err(422, "ogun", lang)


class SimilarQ(BaseModel):
    date: str
    meal: str
    aclik: float
    lang: str = "en"


class MenuIn(BaseModel):
    date: str
    meal: str
    items: list[dict]
    lang: str = "en"


class RecordIn(BaseModel):
    date: str
    meal: str
    aclik: float
    insulin: float | None = None
    tokluk: float | None = None


@app.get("/api/status")
def status():
    return dict(llm=SU.llm_available(), llm_url=SU.LLM_URL, model=ENGINE.cfg.get("label"), n_events=len(ENGINE.events),
                disclaimer="This project is a prototype and is not medical advice. "
                           "(Bu proje bir prototiptir ve tıbbi tavsiye değildir.)")


@app.get("/api/today")
def today(lang: str = "en"):
    d = Date.today()
    meals = [m for m in MEALS if ENGINE.menu_for(d.isoformat(), m) is not None]
    return dict(date=d.isoformat(), gun=(GUN_EN if L(lang) == "en" else GUN)[d.weekday()], meals_with_menu=meals, synthetic=ENGINE.synthetic)


@app.get("/api/dishes")
def dishes():
    return ENGINE.dishes()


@app.get("/api/match")
def match(q: str):
    return MATCHER.match(q, k=5)


@app.get("/api/menu")
def menu(date: str, meal: str, lang: str = "en"):
    check_dm(date, meal, lang)
    m = ENGINE.menu_for(date, meal, L(lang))
    if m is None:
        err(404, "menu_yok", lang)
    return m


@app.put("/api/menu")
def put_menu(m: MenuIn):
    check_dm(m.date, m.meal, m.lang)
    out = ENGINE.save_menu(m.date, m.meal, m.items, L(m.lang))
    if out is None:
        err(422, "yemek", m.lang)
    return out


@app.post("/api/similar")
def similar(q: SimilarQ):
    check_dm(q.date, q.meal, q.lang)
    if not (20 <= q.aclik <= 600):
        err(422, "aclik", q.lang)
    try:
        return ENGINE.similar(q.date, q.meal, q.aclik, lang=L(q.lang))
    except ValueError:
        err(404, "menu_yok", q.lang)


@app.post("/api/record")
def record(r: RecordIn):
    check_dm(r.date, r.meal, "en")
    return ENGINE.record(r.date, r.meal, r.aclik, r.insulin, r.tokluk)


@app.get("/api/history")
def history(lang: str = "en"):
    return ENGINE.history(L(lang))


@app.post("/api/summary")
def summary(ctx: dict, lang: str = "en"):
    return SU.summarize(ctx, L(lang))


@app.post("/api/summary/stream")
def summary_stream(ctx: dict, lang: str = "en"):
    """SSE: önce LLM token'ları ('token'), sonunda kontrol sonucu ('final'). Kontrol geçmezse final metni şablondur."""
    lg = L(lang)

    def gen():
        text = ""
        try:
            payload = dict(messages=[{"role": "system", "content": SU.system_for(lg)},
                                     {"role": "user", "content": json.dumps(ctx, ensure_ascii=False)}],
                           temperature=0.2, max_tokens=260, stream=True)
            with httpx.Client(timeout=60) as c, c.stream("POST", f"{SU.LLM_URL}/v1/chat/completions", json=payload) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    delta = json.loads(data)["choices"][0].get("delta", {}).get("content") or ""
                    if delta:
                        text += delta
                        yield f"event: token\ndata: {json.dumps(delta, ensure_ascii=False)}\n\n"
            chk = SU.check(text, ctx, lg)
            final = dict(text=text, source="llm", check=chk, lang=lg) if chk["ok"] else \
                dict(text=SU.template_summary(ctx, lg), source="şablon", check=chk, rejected=text, lang=lg)
        except Exception as e:  # noqa: BLE001
            final = dict(text=SU.template_summary(ctx, lg), source="şablon", check=None, error=str(e)[:200], lang=lg)
        yield f"event: final\ndata: {json.dumps(final, ensure_ascii=False)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/api/recipe/{dish_id}")
def recipe(dish_id: str, lang: str = "en"):
    dish, *_ = NU.tables()
    if dish_id not in dish.index:
        err(404, "yemek", lang)
    d = dish.loc[dish_id]
    return dict(dish_id=dish_id, name=d["name_tr"], category=d["category"], portion=d["portion_desc"],
                desc=d["desc"], carb=round(float(d["carb"]), 1), protein=round(float(d["protein"]), 1),
                fat=round(float(d["fat"]), 1), fiber=round(float(d["fiber"]), 1), kcal=round(float(d["kcal"])),
                gi=round(float(d["gi"])), gi_class=NU.gi_class(float(d["gi"])), ingredients=NU.dish_recipe(dish_id))


@app.get("/api/report")
def report():
    out = {}
    for f in ["results_cv.json", "results_test.json", "llm_bakeoff.json", "matcher_eval.json", "nutrition_validation.json",
              "findings.json", "retrieval_eval.json", "final_eval.json"]:
        p = ROOT / "reports" / f
        if p.exists():
            out[f.removesuffix(".json")] = json.load(open(p, encoding="utf-8"))
    out["final_model"] = ENGINE.cfg
    return JSONResponse(out)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host=os.environ.get("DIYALIFE_HOST", "0.0.0.0"), port=int(os.environ.get("DIYALIFE_PORT", "8000")))
