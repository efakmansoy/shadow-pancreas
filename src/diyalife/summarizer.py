"""Yerel LLM ile Türkçe özet + sadakat/güvenlik kontrolü + şablon yedek.

LLM yalnızca yapılandırılmış bağlam JSON'unu anlatır. Çıktı iki filtreden geçer:
  1) sayı sadakati: özetteki her sayı bağlamda (ya da izinli sabitlerde) bulunmalı
  2) yasak dil: doz/ünite/talimat kalıpları
Geçemezse şablon özet döner. Hipo riski varsa ilk cümlede geçmesi zorunlu.
"""
from __future__ import annotations

import json
import os
import re
import time

import httpx

LLM_URL = os.environ.get("DIYALIFE_LLM_URL", "http://127.0.0.1:8081")
ALLOWED_CONST = {"2", "70", "180", "100"}  # 2 saat, hedef aralık sınırları

SYSTEM = (
    "Sen Tip 1 diyabetli bir kişinin kendi geçmiş kayıtlarını ona hatırlatan bir yardımcısın. "
    "Sana bir JSON verilecek: bugünkü öğün, bugünün menüsü, bugünkü açlık şekeri ve menüsü bugüne benzeyen geçmiş öğünler. "
    "Bu öğünler iki gruptadır: aclik_yakin_vakalar (açlığı bugüne yakın) ve aclik_farkli_vakalar (açlığı çok farklı). "
    "Her vakada o günkü açlık, vurulan insülin (ünite), ek doz ve 2. saat tokluk var.\n"
    "KURALLAR:\n"
    "- Türkçe, sade, kısa yaz: en fazla 4 cümle, en fazla 90 kelime. Madde işareti kullanma. 'sen' diye hitap et.\n"
    "- ASLA ortalama alma, toplama veya hesap yapma. Vakaları tek tek anlat: tarih, açlık, ünite, tokluk.\n"
    "- Önce açlığı bugüne yakın vakaları anlat (en fazla 2–3 tane). Hangi yemeklerin aynı olduğunu söyle.\n"
    "- Açlığı çok farklı vakaları ancak bir cümleyle, açlığın farklı olduğunu belirterek an.\n"
    "- aclik_yakin_vakalar boşsa, bu açlık seviyesinde benzer menülü kayıt olmadığını açıkça söyle.\n"
    "- Yalnızca JSON'daki sayıları kullan.\n"
    "- Bugün için asla doz önerme: 'şu kadar vur', 'vurmalısın', 'öneririm' gibi ifadeler kullanma. Sadece geçmişi anlat.\n"
    "- Kurallardan, JSON'dan veya alan adlarından bahsetme.\n"
    "- Son cümle şu olsun: 'Kararı her zaman kendi planına ve ekibine göre ver.'"
)

SYSTEM_EN = (
    "You remind a Type 1 diabetic user of their own past records. "
    "You get a JSON (field names are Turkish): today's meal (ogun_adi), today's menu (bugunku_menu), today's pre-meal "
    "glucose (bugunku_aclik) and past meals whose menu resembles today's, in two groups: aclik_yakin_vakalar (pre-meal "
    "glucose close to today's) and aclik_farkli_vakalar (very different pre-meal glucose). Each case has that day's "
    "pre-meal glucose (aclik), insulin injected (insulin_unite, units), correction (ek_doz) and 2-hour post-meal glucose "
    "(tokluk; durum: hedef=in range, hiper=high, hipo=low).\n"
    "RULES:\n"
    "- Plain, short English: at most 4 sentences and 90 words. No bullet points. Address the user as 'you'.\n"
    "- NEVER average, add up or calculate anything. Describe cases one by one: date, pre-meal value, units, post-meal value.\n"
    "- First describe the cases with a pre-meal value close to today's (at most 2–3) and say which dishes were the same.\n"
    "- Mention cases with a very different pre-meal value in at most one sentence, saying that their pre-meal value differed.\n"
    "- If aclik_yakin_vakalar is empty, say clearly that there is no similar-menu record at this glucose level.\n"
    "- Use only numbers that appear in the JSON.\n"
    "- Never suggest a dose for today: no 'take X units', 'you should', 'I recommend'. Only describe the past.\n"
    "- Do not mention rules, JSON or field names. Dish names stay in Turkish.\n"
    "- The last sentence must be: 'Always make your decisions with your own plan and care team.'"
)

FORBIDDEN_EN = [
    r"\baverage", r"\bmean\b", r"\bin total\b",
    r"\byou should\b", r"\byou must\b", r"\bmake sure\b", r"\bi recommend\b", r"\brecommend", r"\bconsider (taking|injecting)\b",
    r"\b(take|inject|use|give)\s+(about\s+|around\s+)?\d+(\.\d+)?\s*units?\b", r"\btoday you (can|could|might) (take|inject)\b",
    r"\b(increase|reduce|lower|raise|adjust)\b[^.]{0,20}\b(insulin|dose)\b",
    r"\b(required|requires|needed|needs)\b", r"\bnecessary\b",
    r"\bdiagnos", r"\btreatment\b", r"\bmedication\b", r"\bdefinitely\b", r"\bcertainly\b",
]

FORBIDDEN = [
    r"\bortalama", r"\btoplam",
    r"vurmalı", r"vurabilirsin", r"vurman\b", r"yapmalı", r"almalı", r"artırmalı", r"azaltmalı", r"\bartır\b",
    r"gerek(ti|iyor|ir|mişti|iyordu)\b", r"ihtiyaç",
    r"\bazalt\b", r"öneririm", r"tavsiye ederim", r"\bmutlaka\b", r"\bkesinlikle\b", r"teşhis", r"tedavi", r"ilaç", r"gerek(ti|iyor|ir|mişti|iyordu)", r"ihtiyaç",
    r"bugün\s+\d+(?:[.,]\d+)?\s*ünite", r"\d+(?:[.,]\d+)?\s*ünite\s+(vur|yap|al)\b",
]


def _numbers_in(obj) -> set[str]:
    s = json.dumps(obj, ensure_ascii=False)
    out = set()
    for x in re.findall(r"\d+(?:\.\d+)?", s):
        f = float(x)
        out.add(str(int(round(f))))
        out.add(x)
        if "." in x:
            out.add(x.replace(".", ","))
    return out


def check(text: str, ctx: dict, lang: str = "tr") -> dict:
    allowed = _numbers_in(ctx) | ALLOWED_CONST
    # tarih biçimlerini ve yüzdeleri sayı olarak yakala
    nums = re.findall(r"\d+(?:[.,]\d+)?", text)
    bad_nums = [n for n in nums if n not in allowed and n.replace(",", ".") not in allowed
                and (n.lstrip("0") or "0") not in allowed]
    pats = FORBIDDEN + FORBIDDEN_EN if lang == "en" else FORBIDDEN
    bad_lang = [p for p in pats if re.search(p, text, flags=re.IGNORECASE)]
    first = re.split(r"(?<=[.!?])\s+", text.strip())[0] if text.strip() else ""
    hipo_ok = True
    if ctx.get("riskler", {}).get("hipo_riski"):
        hipo_ok = bool(re.search(r"hipo|düşük|hypo|\blow\b", first, flags=re.IGNORECASE))
    # tarih sadakati: özetteki her "gün ay" ifadesi bağlamda birebir geçmeli
    ctx_s = json.dumps(ctx, ensure_ascii=False)
    months = ("Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık|January|February|March|April|"
              "May|June|July|August|September|October|November|December")
    bad_dates = [m.group(0) for m in re.finditer(rf"\b(\d{{1,2}})\s+({months})", text)
                 if not re.search(rf"\b{m.group(1)} {m.group(2)}\b", ctx_s)]
    bad_dates += [x for x in re.findall(r"\d{4}-\d{2}-\d{2}", text) if x not in ctx_s]
    bad_nums = bad_nums + bad_dates
    words = len(text.split())
    ok = not bad_nums and not bad_lang and hipo_ok and 0 < words <= 110
    return dict(ok=ok, bad_numbers=bad_nums, bad_language=bad_lang, hipo_first=hipo_ok, words=words)


MEAL_EN = {"kahvaltı": "breakfast", "öğle yemeği": "lunch", "akşam yemeği": "dinner"}


def _fmt(v):
    if v is None:
        return "?"
    return str(int(v)) if float(v).is_integer() else str(v)


def template_summary(ctx: dict, lang: str = "tr") -> str:
    near, far = ctx.get("aclik_yakin_vakalar", []), ctx.get("aclik_farkli_vakalar", [])
    en = lang == "en"
    meal = MEAL_EN.get(ctx["ogun_adi"], ctx["ogun_adi"]) if en else ctx["ogun_adi"]
    a = ctx["bugunku_aclik"]

    def one(c):
        same = ", ".join(c.get("ayni_yemekler") or [])
        if en:
            return (f"{c['tarih']} (same: {same}): pre-meal {_fmt(c['aclik'])}, {_fmt(c['insulin_unite'])} units, "
                    f"post-meal {_fmt(c['tokluk'])}")
        return (f"{c['tarih']} (aynı: {same}): açlık {_fmt(c['aclik'])}, {_fmt(c['insulin_unite'])} ünite, "
                f"tokluk {_fmt(c['tokluk'])}")

    parts = []
    if en:
        if near:
            parts.append(f"Similar-menu {meal}s with a pre-meal value close to today's {a}: " + "; ".join(one(c) for c in near[:3]) + ".")
        else:
            parts.append(f"There is no similar-menu record with a pre-meal value close to today's {a}.")
        if far:
            parts.append("With a different pre-meal value: " + "; ".join(one(c) for c in far[:2]) + ".")
        parts.append("Always make your decisions with your own plan and care team.")
    else:
        if near:
            parts.append(f"Bugünkü açlığına ({a}) yakın, menüsü benzer {meal} kayıtların: " + "; ".join(one(c) for c in near[:3]) + ".")
        else:
            parts.append(f"Bugünkü açlığına ({a}) yakın, menüsü benzer bir kaydın yok.")
        if far:
            parts.append("Açlığın farklı olduğu günler: " + "; ".join(one(c) for c in far[:2]) + ".")
        parts.append("Kararı her zaman kendi planına ve ekibine göre ver.")
    return " ".join(parts)


def _post(payload, timeout=60):
    with httpx.Client(timeout=timeout) as c:
        r = c.post(f"{LLM_URL}/v1/chat/completions", json=payload)
        r.raise_for_status()
        return r.json()


def llm_available() -> dict | None:
    try:
        with httpx.Client(timeout=2) as c:
            r = c.get(f"{LLM_URL}/v1/models")
            if r.status_code == 200:
                d = r.json()
                return {"model": (d.get("data") or [{}])[0].get("id", "?")}
    except Exception:  # noqa: BLE001
        return None
    return None


def system_for(lang: str) -> str:
    return SYSTEM_EN if lang == "en" else SYSTEM


def llm_summary(ctx: dict, temperature=0.2, max_tokens=220, system=None, timeout=60, lang="tr") -> dict:
    system = system or system_for(lang)
    t0 = time.time()
    payload = dict(messages=[{"role": "system", "content": system},
                             {"role": "user", "content": json.dumps(ctx, ensure_ascii=False)}],
                   temperature=temperature, max_tokens=max_tokens, stream=False)
    d = _post(payload, timeout=timeout)
    text = d["choices"][0]["message"]["content"].strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    u = d.get("usage", {})
    tm = d.get("timings", {})
    return dict(text=text, seconds=time.time() - t0, completion_tokens=u.get("completion_tokens"),
                tok_per_s=tm.get("predicted_per_second"))


def summarize(ctx: dict, lang: str = "tr") -> dict:
    """Uygulama giriş noktası: LLM dener, kontrol eder, gerekirse şablona düşer."""
    try:
        r = llm_summary(ctx, lang=lang)
        c = check(r["text"], ctx, lang)
        if c["ok"]:
            return dict(text=r["text"], source="llm", check=c, seconds=round(r["seconds"], 2), lang=lang)
        return dict(text=template_summary(ctx, lang), source="şablon", check=c, rejected=r["text"],
                    seconds=round(r["seconds"], 2), lang=lang)
    except Exception as e:  # noqa: BLE001
        return dict(text=template_summary(ctx, lang), source="şablon", check=None, error=str(e)[:200], lang=lang)
