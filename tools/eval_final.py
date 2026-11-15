"""Son doğruluk testleri (uygulamanın şu anki hali).

A) Geri getirme — havuzdaki her öğün sırayla "bugün" kabul edilir; o günün kendi kayıtları dışarıda bırakılır.
   Yöntemler: uygulama (menü öncelikli: birebir yemek > aynı aile > açlık), prototip (aynı öğün, açlık ±15),
   rastgele (aynı öğün). İlk 5 vaka için:
     menu_ortusme      : bugünün ana yemeklerinden, getirilen vakada birebir bulunanların ortalama oranı
     ilk_vaka_eslesme  : 1. sıradaki vakada en az bir birebir aynı yemek olan sorgu oranı
     durum_isabeti     : vakanın tokluk durumu (düşük/hedef/yüksek) gerçek sonuçla aynı mı
     context_precision : RAGAS formülü (sıra ağırlıklı), ilgili = aynı durum
     tokluk_farki      : |vaka tokluğu − gerçek tokluk| ortalaması (mg/dL)
     aclik_yakin_orani : açlığı ±30 içinde olan vaka oranı
B) LLM (Gemma 4 E4B, llama-server :8081) — 30 öğün × TR/EN = 60 özet:
     kontrol_gecme     : tüm otomatik kontrollerden geçme (sayı, tarih, yasak dil, ortalama yok, uzunluk)
     sayi_sadakati, tarih_sadakati, yasak_dil
     iddia_dogrulugu   : özette geçen her tarih için o cümledeki sayılar gerçekten o vakaya mı ait
                         (açlık/ünite/ek doz/tokluk; bugünkü açlık ve 70/180 eşikleri serbest)
     sure_s            : özet başına süre
Çıktı: reports/final_eval.json, reports/final_llm_outputs.csv
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from diyalife import summarizer as SU  # noqa: E402
from diyalife.engine import Engine, tarih_metni  # noqa: E402

RNG = np.random.default_rng(7)
K = 5


def cprec(rel):
    rel = np.asarray(rel, float)
    if rel.sum() == 0:
        return 0.0
    return float(((np.cumsum(rel) / (np.arange(len(rel)) + 1)) * rel).sum() / rel.sum())


def retrieval(E):
    ev = E.events
    md = {r.event_id: set(E._main_dishes(json.loads(r.items))) for r in ev.itertuples()}
    res = {m: dict(ov=[], first=[], hit=[], cp=[], dt=[], near=[]) for m in ["uygulama", "prototip_15", "rastgele"]}
    t0 = time.time()
    for q in ev.itertuples():
        Q = md[q.event_id]
        if not Q:
            continue
        pool = ev[ev.date != q.date]
        # uygulama
        out = E.similar(q.date, q.meal, q.aclik, n=K)["similar"]
        app = pool.set_index("event_id").loc[[s["event_id"] for s in out]].reset_index()
        same = pool[pool.meal == q.meal].assign(d=lambda x: (x.aclik - q.aclik).abs())
        w = same[same.d <= 15].nsmallest(K, "d")
        proto = w if len(w) else same.nsmallest(K, "d")
        rnd = same.iloc[RNG.choice(len(same), min(K, len(same)), replace=False)]
        for m, nb in [("uygulama", app), ("prototip_15", proto), ("rastgele", rnd)]:
            if not len(nb):
                continue
            ovs = [len(Q & md[e]) / len(Q) for e in nb.event_id]
            rel = (nb.status.values == q.status).astype(int)
            R = res[m]
            R["ov"].append(np.mean(ovs)); R["first"].append(ovs[0] > 0); R["hit"].append(rel.mean())
            R["cp"].append(cprec(rel)); R["dt"].append(np.abs(nb.tokluk.values - q.tokluk).mean())
            R["near"].append(np.mean(np.abs(nb.aclik.values - q.aclik) <= 30))
    out = {m: dict(n=len(R["ov"]), menu_ortusme=round(float(np.mean(R["ov"])), 3),
                   ilk_vaka_eslesme=round(float(np.mean(R["first"])), 3),
                   durum_isabeti=round(float(np.mean(R["hit"])), 3), context_precision=round(float(np.mean(R["cp"])), 3),
                   tokluk_farki=round(float(np.mean(R["dt"])), 1), aclik_yakin_orani=round(float(np.mean(R["near"])), 3))
           for m, R in res.items()}
    print("geri getirme", round(time.time() - t0), "sn")
    for m, v in out.items():
        print(" ", m, v)
    return out


MONTHS = ("Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık|January|February|March|April|May|"
          "June|July|August|September|October|November|December")


def claims(text, ctx):
    """Özetteki her tarih geçen cümle için: cümledeki sayılar o tarihin vakasına mı ait?"""
    cases = {c["tarih"]: c for c in ctx.get("aclik_yakin_vakalar", []) + ctx.get("aclik_farkli_vakalar", [])}
    free = {str(ctx["bugunku_aclik"]), "70", "180", "2"}
    ok = bad = 0
    details = []
    for sent in re.split(r"(?<=[.!?;])\s+", text):
        found = [m for m in re.finditer(rf"\b(\d{{1,2}}) ({MONTHS}) (\d{{4}})", sent)]
        if not found:
            continue
        for i, m in enumerate(found):
            # bu tarihin "kapsamı": tarihten bir sonraki tarihe kadar
            seg = sent[m.end(): found[i + 1].start() if i + 1 < len(found) else len(sent)]
            c = cases.get(m.group(0))
            if c is None:
                bad += 1; details.append(("bilinmeyen_tarih", m.group(0))); continue
            vals = {str(v) for v in (c["aclik"], c["insulin_unite"], c["ek_doz"], c["tokluk"]) if v is not None}
            vals |= {v.replace(".", ",") for v in vals}
            nums = re.findall(r"\d+(?:[.,]\d+)?", seg)
            wrong = [n for n in nums if n not in vals and n not in free]
            if wrong:
                bad += 1; details.append(("yanlis_sayi", m.group(0), wrong))
            else:
                ok += 1
    return ok, bad, details


def llm(E, n=30):
    if not SU.llm_available():
        print("LLM sunucusu yok, B testi atlandı"); return None
    ev = E.events
    pick = pd.concat([g.sample(min(10, len(g)), random_state=3) for _, g in ev.groupby("meal")]).head(n)
    rows = []
    for q in pick.itertuples():
        for lang in ["tr", "en"]:
            r = E.similar(q.date, q.meal, q.aclik, lang=lang)
            ctx = r["context"]
            t0 = time.time()
            try:
                g = SU.llm_summary(ctx, lang=lang, max_tokens=260)
                text = g["text"]
            except Exception as e:  # noqa: BLE001
                text = ""; print("hata", e)
            sec = time.time() - t0
            c = SU.check(text, ctx, lang)
            ok, bad, det = claims(text, ctx)
            rows.append(dict(event_id=q.event_id, lang=lang, text=text, sure_s=round(sec, 2), gecti=c["ok"],
                             sayi_hata=";".join(x for x in c["bad_numbers"] if not re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]", x)),
                             tarih_hata=";".join(x for x in c["bad_numbers"] if re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]", x)),
                             yasak=";".join(c["bad_language"]), iddia_dogru=ok, iddia_yanlis=bad, detay=str(det)[:300],
                             kelime=c["words"]))
            print(q.event_id, lang, "geçti" if c["ok"] else "KALDI", ok, bad, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "reports" / "final_llm_outputs.csv", index=False)

    def agg(d):
        tot = d.iddia_dogru.sum() + d.iddia_yanlis.sum()
        return dict(n=len(d), kontrol_gecme=round(float(d.gecti.mean()), 3),
                    sayi_sadakati=round(float((d.sayi_hata == "").mean()), 3),
                    tarih_sadakati=round(float((d.tarih_hata == "").mean()), 3),
                    yasak_dil=round(float((d.yasak != "").mean()), 3),
                    iddia_dogrulugu=round(float(d.iddia_dogru.sum() / tot), 3) if tot else None, iddia_sayisi=int(tot),
                    ort_sure_s=round(float(d.sure_s.mean()), 2), ort_kelime=round(float(d.kelime.mean()), 1))
    out = {"toplam": agg(df), "tr": agg(df[df.lang == "tr"]), "en": agg(df[df.lang == "en"])}
    for k, v in out.items():
        print(" ", k, v)
    return out


def main():
    E = Engine()
    out = dict(geri_getirme=retrieval(E), llm=llm(E), havuz=len(E.events), model="gemma-4-E4B (Q4, llama.cpp)",
               yontem=__doc__.strip())
    json.dump(out, open(ROOT / "reports" / "final_eval.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
