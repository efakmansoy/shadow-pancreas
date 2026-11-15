# -*- coding: utf-8 -*-
"""Önek a: ana + pilav bileşenleri için dishes/recipes/aliases üretir."""
import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
N = ROOT / "data" / "nutrition"
ING = {r["ingredient_id"]: r["name_tr"] for r in csv.DictReader(open(N/"ingredients.csv", encoding="utf-8"))}

def R(s):
    d = {}
    for part in s.split(","):
        part = part.strip()
        if not part: continue
        k, g = part.rsplit(" ", 1)
        assert k in ING, k
        d[k] = d.get(k, 0) + float(g)
    return d

def add(*rs):
    out = {}
    for r in rs:
        r = R(r) if isinstance(r, str) else r
        for k, v in r.items(): out[k] = out.get(k, 0) + v
    return out

DISHES = {}  # id -> (name, cat, recipe dict)
def D(i, name, cat, rec):
    assert i not in DISHES, i
    DISHES[i] = (name, cat, add(rec))

KB = "dana_kiyma 100, galeta_unu 10, sogan 15, sivi_yag 5"
BEGENDI = "patlican 100, sut 40, tereyagi 8, un 8, kasar 10"
PURE = "patates 120, sut 30, tereyagi 5"

# ---- Kahvaltı yumurta
D("omlet", "Omlet", "kahvalti_yumurta", "yumurta 100, sivi_yag 5")
D("menemen", "Menemen", "kahvalti_yumurta", "yumurta 100, domates 100, biber 40, sivi_yag 8")

# ---- Garnitürler / soslar
D("patates_pure", "Patates Püresi", "patates_garnitur", PURE)
D("kup_patates", "Küp Patates", "patates_garnitur", "patates 120, sivi_yag 8")
D("susamli_patates", "Susamlı Patates", "patates_garnitur", "patates 120, sivi_yag 8, susam 5")
D("patates_tava", "Patates Tava", "patates_garnitur", "patates 120, sivi_yag 10")
D("kutuk_patates", "Kütük Patates", "patates_garnitur", "patates 120, sivi_yag 8")
D("baby_patates", "Baby Patates", "patates_garnitur", "patates 120, tereyagi 5, sivi_yag 5")
D("blonjor_patates", "Blonjör Patates", "patates_garnitur", "patates 120, sivi_yag 8")
D("patates_kizartmasi", "Patates Kızartması", "patates_garnitur", "patates_kizartma 100")
D("elma_dilim_patates", "Elma Dilim Patates", "patates_garnitur", "patates_kizartma 100")
D("kibrit_patates", "Kibrit Patates", "patates_garnitur", "patates_kizartma 100")
D("cips_patates", "Cips Patates", "patates_garnitur", "patates_kizartma 100")
D("yaprak_patates", "Yaprak Patates", "patates_garnitur", "patates_kizartma 100")
D("sogan_halkasi", "Soğan Halkası", "sebze_yemegi", "sogan 60, un 15, yumurta 10, sivi_yag 12")
D("arpacik_sogan", "Arpacık Soğan", "sebze_yemegi", "sogan 80, sivi_yag 5")
D("karamelize_sogan", "Karamelize Soğan", "sebze_yemegi", "sogan 80, seker 5, tereyagi 5")
D("havuc_garnitur", "Havuç", "sebze_yemegi", "havuc 100, tereyagi 5")
D("lavas", "Lavaş", "ekmek_hamur", "ekmek 50")
D("pide", "Pide", "ekmek_hamur", "ekmek 50")
D("patlican_puresi", "Patlıcan Püresi (Beğendi)", "sebze_yemegi", BEGENDI)
D("bbq_sos", "Barbekü Sos", "sos", "ketcap 30")
D("meksika_sos", "Meksika Sos", "sos", "domates 60, misir 25, biber 30, sogan 20, sivi_yag 5")
D("mantar_sos", "Mantar Sos", "sos", "mantar 70, krema 20, un 5, tereyagi 5")
D("avci_sos", "Avcı Sos", "sos", "mantar 40, domates 50, biber 20, sogan 20, salca 5, sivi_yag 5")
D("beyaz_sos", "Beyaz Sos", "sos", "sut 80, un 10, tereyagi 8")
D("kendi_sosu", "Kendi Sosu (Demi-glace)", "sos", "sogan 20, havuc 15, salca 8, un 5, tereyagi 5")

# ---- Köfteler
K = lambda x="": add(KB, x) if x else add(KB)
D("izgara_kofte", "Izgara Köfte", "kofte", K())
D("sis_kofte", "Şiş Köfte", "kofte", K())
D("akhisar_kofte", "Akhisar Köfte", "kofte", K())
D("doner_kofte", "Döner Köfte", "kofte", K())
D("rosto_kofte", "Rosto Köfte", "kofte", K("sogan 25, domates 30, salca 5"))
D("sahan_kofte", "Sahan Köfte", "kofte", K("domates 50, biber 20"))
D("izmir_kofte", "İzmir Köfte", "kofte", K("patates 60, domates 60, biber 20, sivi_yag 5"))
D("kayseri_kofte", "Kayseri Köfte", "kofte", K("domates 50, biber 20"))
D("kayhan_kofte", "Kayhan Köfte", "kofte", K("domates 50, biber 20"))
D("tire_kofte", "Tire Köfte", "kofte", K("domates 40, biber 15"))
D("hasanpasa_kofte", "Hasanpaşa Köfte", "kofte", K("domates 40, tereyagi 5"))
D("eksili_kofte", "Ekşili Köfte", "kofte", "dana_kiyma 80, pirinc 15, un 8, yumurta 10, sogan 20, tereyagi 5, limon 5")
D("koroglu_kofte", "Köroğlu Köfte", "kofte", K("patlican 80, domates 40"))
D("sebzeli_kofte", "Sebzeli Köfte", "kofte", K("patates 40, havuc 30, kabak 40, biber 20"))
D("iskender_kofte", "İskender Köfte", "kofte", K("ekmek 50, domates 40, yogurt 50, tereyagi 10"))
D("sogurtmeli_kofte", "Söğürtmeli Köfte", "kofte", K("patlican 80, yogurt 30"))
D("misket_kofte", "Misket Köfte", "kofte", K("sivi_yag 5"))
D("kadinbudu_kofte", "Kadınbudu Köfte", "kofte", "dana_kiyma 80, pirinc 20, yumurta 25, un 15, sogan 10, sivi_yag 15")
D("odemis_kofte", "Ödemiş Köfte", "kofte", K("patates 40, domates 30"))
D("yogurtlu_kofte_kebabi", "Yoğurtlu Köfte Kebabı", "kofte", K("yogurt 80, ekmek 40, tereyagi 8, domates 30"))
D("canak_kofte", "Çanak Köfte", "kofte", K("domates 50, biber 20, kasar 15"))
D("mantarli_canak_kofte", "Mantarlı Çanak Köfte", "kofte", K("domates 50, biber 20, kasar 15, mantar 50"))
D("coban_kofte", "Çoban Köfte", "kofte", K("domates 50, biber 30"))
D("icli_kofte", "İçli Köfte", "kofte", "bulgur 40, dana_kiyma 50, sogan 20, sivi_yag 15, ceviz 5")

# ---- Etler
D("dana_haslama", "Dana Haşlama", "et_yemegi", "dana_et 100, havuc 40, patates 60, kereviz 20, sogan 20")
D("tavuk_haslama", "Tavuk Haşlama", "tavuk_yemegi", "tavuk_but 100, havuc 40, patates 60, kereviz 20, sogan 20")
D("et_doner", "Et Döner", "et_yemegi", "dana_et 110, sivi_yag 8")
D("et_tantuni", "Et Tantuni", "et_yemegi", "dana_et 80, ekmek 50, domates 40, biber 20, sogan 15, sivi_yag 8")
D("macar_gulas", "Macar Gulaş", "et_yemegi", "dana_et 100, patates 60, sogan 40, biber 30, domates 40, salca 10, havuc 20, sivi_yag 10")
D("macar_kebabi", "Macar Kebabı", "et_yemegi", "dana_et 100, biber 40, sogan 30, domates 50, mantar 20, sivi_yag 10")
D("dana_kavurma", "Dana Kavurma", "et_yemegi", "dana_et 100, sogan 40, biber 30, domates 40, sivi_yag 10")
D("coban_kavurma", "Çoban Kavurma", "et_yemegi", "dana_et 100, sogan 40, biber 40, domates 50, sivi_yag 10")
D("mersin_kavurma", "Mersin Kavurma", "et_yemegi", "dana_et 100, sogan 30, biber 30, salca 10, sivi_yag 10")
D("sac_kavurma", "Sac Kavurma", "et_yemegi", "dana_et 100, biber 40, domates 40, sogan 20, sivi_yag 8")
D("dana_yahni", "Dana Yahni", "et_yemegi", "dana_et 100, sogan 80, domates 30, salca 5, sivi_yag 10")
D("keskekli_dana_yahni", "Keşkekli Dana Yahni", "et_yemegi", "dana_et 80, bugday_dovme 40, sogan 20, tereyagi 8")
D("dana_et_sote", "Dana Et Sote", "et_yemegi", "dana_et 110, biber 40, domates 50, sogan 30, sivi_yag 10")
D("dana_rosto", "Dana Rosto", "et_yemegi", "dana_et 120, sogan 30, havuc 30, domates 30, sivi_yag 10")
D("pot_roast", "Pot Roast", "et_yemegi", "dana_et 120, havuc 40, sogan 30, kereviz 20, patates 60, domates 20, sivi_yag 8")
D("stroganoff", "Beef Stroganoff", "et_yemegi", "dana_et 100, mantar 50, sogan 20, krema 30, un 5, tereyagi 8")
D("dana_burginyon", "Dana Burginyon", "et_yemegi", "dana_et 110, mantar 40, sogan 30, havuc 30, un 8, tereyagi 8")
D("dana_fleminyon_mantarli", "Dana Fleminyon Mantarlı", "et_yemegi", "dana_et 120, mantar 60, tereyagi 8, krema 20")
D("dana_madalyon", "Dana Madalyon", "et_yemegi", "dana_et 120, sivi_yag 8")
D("dana_madalyon_mantar_soslu", "Dana Madalyon Mantar Soslu", "et_yemegi", "dana_et 120, sivi_yag 8, mantar 60, krema 20, un 5")
D("dana_biftek", "Dana Biftek", "et_yemegi", "dana_et 120, sivi_yag 8")
D("koylu_usulu_biftek", "Köylü Usulü Biftek", "et_yemegi", "dana_et 120, domates 50, biber 30, sogan 30, sivi_yag 10")
D("dana_emince", "Dana Emincé", "et_yemegi", "dana_et 100, mantar 30, sogan 20, krema 20, tereyagi 8")
D("dana_emense", "Dana Emense", "et_yemegi", "dana_et 100, patates 60, domates 40, biber 20, sogan 30, sivi_yag 8")
D("dana_mutancana", "Dana Mutancana", "et_yemegi", "dana_et 100, sogan 40, havuc 20, domates 30, uzum_kuru 15, sivi_yag 8")
D("dana_tandir", "Dana Tandır", "et_yemegi", "dana_et 120, sogan 20, sivi_yag 8")
D("hindi_tandir", "Hindi Tandır", "tavuk_yemegi", "hindi 120, sogan 20, sivi_yag 8")
D("kuzu_kizartma", "Kuzu Kızartma", "et_yemegi", "kuzu_et 130, sivi_yag 8")
D("arnavut_ciger", "Arnavut Ciğer", "et_yemegi", "ciger 100, un 15, sivi_yag 20")
D("tesrube", "Teşrübe", "et_yemegi", "dana_et 70, ekmek 40, nohut 15, sogan 20, domates 40, sivi_yag 8")
D("etli_taco", "Etli Taco", "et_yemegi", "un 40, dana_kiyma 70, domates 40, misir 15, kasar 15, yesillik 15, sivi_yag 5")
D("et_fajita", "Et Fajita", "et_yemegi", "dana_et 100, biber 50, sogan 40, domates 20, un 40, sivi_yag 10")
D("kayseri_yaglama", "Kayseri Yağlama", "et_yemegi", "un 50, dana_kiyma 60, domates 40, yogurt 60, tereyagi 10, sogan 20")

# ---- Kebaplar
def kebap(i, name, rec): D(i, name, "et_yemegi", rec)
kebap("orman_kebabi", "Orman Kebabı", "dana_et 100, patates 60, havuc 30, bezelye 30, sogan 20, domates 30, sivi_yag 10")
kebap("sebzeli_kebap", "Sebzeli Kebap", "dana_et 100, patates 50, havuc 30, kabak 40, biber 20, domates 30, sivi_yag 10")
kebap("sehzade_kebabi", "Şehzade Kebabı", "dana_et 100, patlican 120, domates 60, biber 20, sivi_yag 15, salca 5")
kebap("cokertme_kebabi", "Çökertme Kebabı", "dana_et 90, patates 100, yogurt 50, domates 40, sivi_yag 15, tereyagi 5")
kebap("taskebabi", "Taş Kebabı", "dana_et 100, sogan 40, domates 50, biber 25, salca 5, sivi_yag 10")
kebap("filiz_kebabi", "Filiz Kebabı", "dana_et 100, patates 60, biber 25, domates 40, sogan 20, sivi_yag 10")
kebap("abant_kebabi", "Abant Kebabı", "dana_et 100, patates 50, mantar 30, biber 20, kasar 20, sivi_yag 10")
kebap("bugu_kebabi", "Buğu Kebabı", "dana_et 100, patates 60, domates 40, biber 20, sogan 20, sivi_yag 5")
kebap("tepsi_kebabi", "Tepsi Kebabı", "dana_et 100, patates 60, biber 30, domates 50, sogan 30, sivi_yag 10")
kebap("saksi_kebabi", "Saksı Kebabı", "dana_et 100, patates 40, domates 40, biber 25, sogan 25, kasar 15, sivi_yag 8")
kebap("girit_kebabi", "Girit Kebabı", "dana_et 100, patates 50, domates 40, biber 20, sogan 20, sivi_yag 8")
kebap("ciftlik_kebabi", "Çiftlik Kebabı", "dana_et 90, patates 60, biber 25, domates 40, sogan 20, sivi_yag 10")
kebap("maras_tava", "Maraş Tava", "dana_et 100, patates 40, biber 30, domates 40, sogan 20, salca 10, sivi_yag 12")
kebap("belen_tava", "Dana Belen Tava", "dana_et 100, patates 50, biber 25, domates 40, sogan 20, sivi_yag 10")
kebap("bohca_kebabi", "Bohça Kebabı", "yufka 40, dana_et 70, mantar 30, kasar 20, sivi_yag 12")
kebap("yufkali_kebap", "Yufkalı Kebap", "yufka 50, dana_et 90, domates 40, biber 20, tereyagi 10, yogurt 50")
kebap("islim_kebabi", "İslim Kebabı", "dana_kiyma 80, patlican 100, domates 50, biber 20, sogan 20, sivi_yag 15")
kebap("patlican_kebabi", "Patlıcan Kebabı", "patlican 150, dana_kiyma 60, domates 40, biber 20, sivi_yag 20")
kebap("etsiz_patlican_kebabi", "Etsiz Patlıcan Kebabı", "patlican 200, domates 50, biber 20, sogan 20, sivi_yag 20")
kebap("adana_kebabi", "Adana Kebap", "dana_kiyma 100, sogan 15, kirmizi_biber 15, sivi_yag 8")
D("pilic_cokertme", "Piliç Çökertme", "tavuk_yemegi", "tavuk_gogus 90, patates 100, yogurt 50, domates 40, sivi_yag 15, tereyagi 5")

# ---- Piliç / tavuk
D("pilic_sis", "Piliç Şiş", "tavuk_yemegi", "tavuk_gogus 120, yogurt 20, sivi_yag 5")
D("pilic_fajita", "Piliç Fajita", "tavuk_yemegi", "tavuk_gogus 110, biber 50, sogan 40, domates 20, un 40, sivi_yag 10")
D("tavuk_baget", "Piliç Baget Fırın", "tavuk_yemegi", "tavuk_but 130, sivi_yag 5, salca 5")
D("sebzeli_tavuk_baget", "Sebzeli Fırın Tavuk Baget", "tavuk_yemegi", "tavuk_but 130, kabak 50, biber 30, havuc 30, patates 50, sivi_yag 8")
D("pilic_izgara", "Piliç Izgara", "tavuk_yemegi", "tavuk_gogus 120, sivi_yag 5")
D("tavuk_but_izgara", "Tavuk But Izgara", "tavuk_yemegi", "tavuk_but 130, sivi_yag 5")
D("susamli_pilic_roti", "Susamlı Piliç Roti", "tavuk_yemegi", "tavuk_but 130, susam 5, sivi_yag 5")
D("sebzeli_pilic_sote", "Sebzeli Piliç Sote", "tavuk_yemegi", "tavuk_gogus 100, kabak 50, havuc 30, mantar 30, biber 20, sivi_yag 8")
D("tavuk_sote", "Tavuk Sote", "tavuk_yemegi", "tavuk_gogus 110, biber 40, domates 40, sogan 20, sivi_yag 10")
D("pilic_topkapi", "Piliç Topkapı", "tavuk_yemegi", "tavuk_gogus 100, mantar 40, biber 20, kasar 20, krema 20, sivi_yag 8")
D("pilic_sarma", "Piliç Sarma", "tavuk_yemegi", "tavuk_gogus 110, kasar 20, mantar 20, un 8, sivi_yag 8")

# ---- Balık
D("ispanak_yataginda_balik", "Ispanak Yatağında Balık", "balik", "balik 120, ispanak 100, krema 20, tereyagi 5, limon 5")
D("cupra_firin", "Çupra Fırın", "balik", "balik 140, zeytinyagi 8, domates 30, limon 5")

# ---- Sebze / baklagil
D("musakka_patlican", "Patlıcan Musakka", "sebze_yemegi", "dana_kiyma 60, patlican 120, domates 60, biber 20, sogan 20, sivi_yag 15, salca 5")
D("musakka_patates", "Etli Patates Musakka", "sebze_yemegi", "patates 150, dana_kiyma 60, domates 50, sogan 20, sivi_yag 10")
D("musakka_karisik", "Karışık Musakka", "sebze_yemegi", "patlican 80, patates 50, kabak 40, biber 20, domates 50, dana_kiyma 60, sogan 20, sivi_yag 12, salca 5")
D("etli_biber_dolma", "Etli Biber Dolma", "sebze_yemegi", "biber 150, pirinc 25, dana_kiyma 50, sogan 30, domates 20, sivi_yag 8")
D("etli_karisik_dolma", "Etli Karışık Dolma", "sebze_yemegi", "biber 70, patlican 50, kabak 50, domates 30, pirinc 25, dana_kiyma 50, sogan 30, sivi_yag 8")
D("etli_sogan_dolma", "Etli Soğan Dolma", "sebze_yemegi", "sogan 180, pirinc 25, dana_kiyma 50, salca 5, sivi_yag 8")
D("etli_yaprak_sarma", "Etli Yaprak Sarma", "sebze_yemegi", "yesillik 50, pirinc 30, dana_kiyma 40, sogan 30, domates 20, sivi_yag 8")
D("etli_lahana_pohcasi", "Etli Lahana Pohçası", "sebze_yemegi", "lahana 150, dana_kiyma 60, pirinc 20, sogan 20, domates 30, sivi_yag 8")
D("karniyarik", "Karnıyarık", "sebze_yemegi", "patlican 180, dana_kiyma 70, sogan 25, domates 50, biber 25, sivi_yag 20, salca 5")
D("etsiz_mevsim_turlusu", "Etsiz Mevsim Türlüsü", "sebze_yemegi", "patates 60, havuc 40, kabak 40, taze_fasulye 40, bezelye 20, domates 30, sogan 20, kereviz 20, sivi_yag 10")
D("etli_mevsim_turlusu", "Etli Mevsim Türlüsü", "sebze_yemegi", "patates 60, havuc 40, kabak 40, taze_fasulye 40, bezelye 20, domates 30, sogan 20, kereviz 20, sivi_yag 10, dana_et 45")
D("kis_turlusu", "Kış Türlüsü", "sebze_yemegi", "dana_et 45, kereviz 40, havuc 40, patates 50, lahana 40, bezelye 20, sogan 20, sivi_yag 10")
D("etli_taze_fasulye", "Etli Taze Fasulye", "sebze_yemegi", "taze_fasulye 200, dana_et 40, sogan 25, domates 40, salca 5, sivi_yag 12")
D("etsiz_taze_fasulye", "Etsiz Taze Fasulye", "sebze_yemegi", "taze_fasulye 200, sogan 25, domates 40, salca 5, zeytinyagi 12")
D("sebze_graten", "Sebze Graten", "sebze_yemegi", "brokoli 50, havuc 40, kabak 40, patates 40, sut 100, un 12, tereyagi 8, kasar 30")
D("etli_sebze_graten", "Etli Sebze Graten", "sebze_yemegi", "brokoli 50, havuc 40, kabak 40, patates 40, dana_kiyma 50, sut 100, un 12, tereyagi 8, kasar 30")
D("ispanak_graten", "Ispanak Graten", "sebze_yemegi", "ispanak 150, sut 100, un 12, tereyagi 8, kasar 30")
D("mantarli_ispanak_graten", "Mantarlı Ispanak Graten", "sebze_yemegi", "ispanak 120, mantar 50, sut 100, un 12, tereyagi 8, kasar 30")
D("sebzeli_mantar_sote", "Sebzeli Mantar Sote", "sebze_yemegi", "mantar 100, kabak 50, biber 30, havuc 30, sivi_yag 10")
D("kori_sebzeli_sote", "Körili Mantar Soslu Sebzeli Sote", "sebze_yemegi", "mantar 60, kabak 50, biber 30, havuc 30, krema 30, sivi_yag 8")
D("karisik_sebze_sote", "Karışık Sebze Sote", "sebze_yemegi", "kabak 60, biber 40, patlican 50, havuc 30, mantar 30, sivi_yag 10")
D("soslu_patlican_kizartma", "Soslu Patlıcan Kızartma", "sebze_yemegi", "patlican 200, sivi_yag 25, domates 40, salca 5, sarimsak 3, biber 20")
D("soslu_karisik_kizartma", "Soslu Karışık Kızartma", "sebze_yemegi", "patlican 80, kabak 80, biber 40, sivi_yag 25, domates 40, sarimsak 3")
D("etli_kuru_fasulye", "Etli Kuru Fasulye", "baklagil", "kuru_fasulye 60, dana_et 40, sogan 20, salca 10, sivi_yag 10")
D("etsiz_kuru_fasulye", "Etsiz Kuru Fasulye", "baklagil", "kuru_fasulye 60, sogan 20, salca 10, sivi_yag 10")
D("gemici_kuru_fasulye", "Gemici Usulü Kuru Fasulye", "baklagil", "kuru_fasulye 60, dana_et 40, sogan 20, salca 10, domates 40, biber 20, sivi_yag 10")
D("etli_nohut", "Etli Nohut", "baklagil", "nohut 60, dana_et 45, sogan 30, domates 30, salca 5, sivi_yag 10")
D("nohut_yemegi", "Nohut Yemeği", "baklagil", "nohut 60, sogan 20, domates 30, sivi_yag 10")
D("tereyagli_nohut", "Tereyağlı Nohut", "baklagil", "nohut 60, tereyagi 12, sogan 10")
D("etli_barbunya", "Etli Barbunya", "baklagil", "barbunya 60, dana_et 40, sogan 20, salca 5, domates 30, sivi_yag 10")
D("barbunya", "Barbunya", "baklagil", "barbunya 60, sogan 25, havuc 20, domates 30, zeytinyagi 10")
D("yesil_mercimek_yemegi", "Yeşil Mercimek Yemeği", "baklagil", "yesil_mercimek 60, sogan 25, domates 30, salca 5, sivi_yag 10")

# ---- Hamur / pide
D("tirnakli_pide", "Tırnaklı Pide", "ekmek_hamur", "un 80, dana_et 40, domates 30, biber 15, kasar 15, sivi_yag 8")
D("etli_pide", "Etli Pide", "ekmek_hamur", "un 80, dana_kiyma 50, sogan 20, biber 15, sivi_yag 8")
D("kusbasili_kasarli_pide", "Kuşbaşılı Kaşarlı Pide", "ekmek_hamur", "un 80, dana_et 50, kasar 30, biber 15, sivi_yag 8")
D("pizza", "Pizza", "ekmek_hamur", "un 60, kasar 40, sosis 20, mantar 20, salca 10, biber 15")
D("hamburger", "Hamburger", "ekmek_hamur", "ekmek 80, dana_kiyma 80, domates 20, yesillik 10, ketcap 10, mayonez 5, sogan 10")
D("manti", "Mantı", "ekmek_hamur", "un 60, dana_kiyma 40, yogurt 80, tereyagi 8, sogan 10, salca 5")

# ---- Pilavlar
def pilav(i, name, rec): D(i, name, "pilav", rec)
pilav("pirinc_pilavi", "Pirinç Pilavı", "pirinc 65, tereyagi 8")
pilav("sehriyeli_pirinc_pilavi", "Şehriyeli Pirinç Pilavı", "pirinc 55, makarna 10, tereyagi 8")
pilav("meyane_pilavi", "Meyane Pilavı", "pirinc 60, havuc 20, bezelye 15, misir 15, biber 15, domates 20, tereyagi 8")
pilav("sebzeli_pirinc_pilavi", "Sebzeli Pirinç Pilavı", "pirinc 60, havuc 20, bezelye 15, biber 10, tereyagi 8")
pilav("misirli_pirinc_pilavi", "Mısırlı Pirinç Pilavı", "pirinc 60, misir 25, tereyagi 8")
pilav("nohutlu_pirinc_pilavi", "Nohutlu Pirinç Pilavı", "pirinc 55, nohut 20, tereyagi 8")
pilav("tavuklu_pirinc_pilavi", "Tavuklu Pirinç Pilavı", "pirinc 60, tavuk_gogus 40, tereyagi 8")
pilav("domatesli_pirinc_pilavi", "Domatesli Pirinç Pilavı", "pirinc 60, domates 60, salca 10, sivi_yag 8")
pilav("uzumlu_pirinc_pilavi", "Üzümlü Pirinç Pilavı", "pirinc 60, uzum_kuru 15, tereyagi 8")
pilav("ic_pilav", "İç Pilav", "pirinc 65, ciger 20, sogan 15, uzum_kuru 8, badem 5, tereyagi 8")
pilav("melek_pilavi", "Melek Pilavı", "pirinc 55, tavuk_gogus 30, mantar 20, tereyagi 8")
pilav("yayla_pilavi", "Yayla Pilavı", "pirinc 60, yogurt 40, tereyagi 5")
pilav("bulgur_pilavi", "Bulgur Pilavı", "bulgur 65, sivi_yag 8, sogan 10")
pilav("salcali_bulgur_pilavi", "Salçalı Bulgur Pilavı", "bulgur 65, sivi_yag 8, sogan 10, salca 15, domates 30, biber 15")
pilav("sehriyeli_bulgur_pilavi", "Şehriyeli Bulgur Pilavı", "bulgur 55, makarna 10, sivi_yag 8")
pilav("sebzeli_bulgur_pilavi", "Sebzeli Bulgur Pilavı", "bulgur 60, havuc 20, bezelye 15, biber 15, sivi_yag 8")
pilav("nohutlu_bulgur_pilavi", "Nohutlu Bulgur Pilavı", "bulgur 55, nohut 20, sivi_yag 8")
pilav("patlicanli_bulgur_pilavi", "Patlıcanlı Bulgur Pilavı", "bulgur 55, patlican 60, domates 30, salca 5, sivi_yag 8")
pilav("sehriye_pilavi", "Şehriye Pilavı", "makarna 65, tereyagi 8")
pilav("sebzeli_sehriye_pilavi", "Sebzeli Şehriye Pilavı", "makarna 60, havuc 20, bezelye 15, biber 10, tereyagi 8")
pilav("kuskus_pilavi", "Kuskus Pilavı", "kuskus 65, tereyagi 8, havuc 15")
pilav("firik_pilavi", "Firik Pilavı", "firik 65, tereyagi 8, sogan 10")
pilav("cevizli_eriste", "Cevizli Erişte", "eriste 80, tereyagi 8, ceviz 15")
pilav("eriste_kavurma", "Erişte Kavurma", "eriste 80, tereyagi 10")
pilav("peynirli_eriste_kavurma", "Peynirli Erişte Kavurma", "eriste 80, tereyagi 10, beyaz_peynir 25")
pilav("sebzeli_eriste", "Sebzeli Erişte", "eriste 70, havuc 20, bezelye 15, biber 15, domates 20, sivi_yag 8")
def mak(i, name, rec): D(i, name, "makarna", rec)
mak("makarna_sade", "Makarna", "makarna 80, tereyagi 8")
mak("peynirli_makarna", "Peynirli Makarna", "makarna 80, kasar 25, tereyagi 8")
mak("pesto_makarna", "Pesto Soslu Makarna", "makarna 80, maydanoz 15, zeytinyagi 15, kasar 10, ceviz 8")
mak("mantarli_pesto_makarna", "Mantarlı Pesto Soslu Makarna", "makarna 80, maydanoz 15, zeytinyagi 15, kasar 10, ceviz 8, mantar 50")
mak("arabiata_makarna", "Arabiatta Makarna", "makarna 80, domates 100, salca 10, sarimsak 3, kirmizi_biber 5, zeytinyagi 8")
mak("napoliten_makarna", "Napoliten Soslu Makarna", "makarna 80, domates 100, salca 10, sogan 20, zeytinyagi 8")
mak("karbonara_makarna", "Karbonara Makarna", "makarna 80, sosis 30, krema 40, yumurta 25, kasar 10")
mak("mantar_soslu_makarna", "Mantar Soslu Makarna", "makarna 80, mantar 70, krema 30, un 5, tereyagi 5")
mak("kori_mantar_makarna", "Mantarlı Köri Soslu Makarna", "makarna 80, mantar 50, krema 30, un 5, tereyagi 5")
mak("kori_soslu_makarna", "Köri Soslu Makarna", "makarna 80, krema 30, sogan 30, un 5, tereyagi 5")
mak("bolonez_makarna", "Bolonez Soslu Makarna", "makarna 80, dana_kiyma 50, domates 80, salca 10, sogan 20, sivi_yag 5")
mak("firin_makarna", "Fırın Makarna", "makarna 80, kasar 30, sut 50, yumurta 15, dana_kiyma 30, tereyagi 5")
mak("kiymali_lazanya", "Kıymalı Lazanya", "makarna 45, dana_kiyma 60, sut 80, un 10, tereyagi 8, kasar 30, domates 60, sogan 20")
mak("sebzeli_lazanya", "Sebzeli Lazanya", "makarna 45, kabak 50, mantar 40, ispanak 40, sut 80, un 10, tereyagi 8, kasar 30, domates 40")
D("su_boregi", "Su Böreği", "borek", "un 60, yumurta 20, beyaz_peynir 40, tereyagi 12, maydanoz 10")
D("kol_boregi_ogle", "Kol Böreği", "borek", "yufka 70, beyaz_peynir 40, yumurta 15, sut 30, sivi_yag 12")
D("gul_boregi", "Gül Böreği", "borek", "yufka 70, beyaz_peynir 35, yumurta 15, sivi_yag 12")
D("ispanakli_gul_boregi", "Ispanaklı Gül Böreği", "borek", "yufka 70, ispanak 50, beyaz_peynir 25, yumurta 15, sivi_yag 12")

# ------------------------------------------------------------------ aliases
ALIAS_TXT = r"""
@ : Yumurta
omlet : Omlet
menemen : Menemen
patates_pure : Püre; Patates Püresi; Patates Püre
kup_patates : Küp Patates; Patates
susamli_patates : Susamlı Patates; Susamlı Küp Patates
patates_tava : Patates Tava
kutuk_patates : Kütük Patates
baby_patates : Baby Patates
blonjor_patates : Blonjör Patates
patates_kizartmasi : Patates Kızartması
elma_dilim_patates : Elma Dilim Patates
kibrit_patates : Kibrit Patates
cips_patates : Cips Patates
yaprak_patates : Yaprak Patates
sogan_halkasi : Soğan Halka; Soğan Halkası
arpacik_sogan : Arpacık Soğan
havuc_garnitur : Havuç
lavas : Lavaş
pide : Pide
patlican_puresi : Patlıcan Püresi; Patlıcan Püre
bbq_sos : BBQ Sos
meksika_sos : Meksika Soslu
kendi_sosu : Kendi Sosu
izgara_kofte : Izgara Köfte
sis_kofte : Şiş Köfte
akhisar_kofte : Akhisar Köfte
doner_kofte : Döner Köfte
rosto_kofte : Rosto Köfte
rosto_kofte|patates_pure : Püreli Rosto Köfte
rosto_kofte|avci_sos : Avcı Soslu Rosto Köfte
sahan_kofte : Sahan Köfte
izmir_kofte : İzmir Köfte
kayseri_kofte : Kayseri Köfte
kayhan_kofte : Kayhan Köfte
tire_kofte : Tire Köfte
hasanpasa_kofte : Hasanpaşa Köfte
eksili_kofte : Ekşili Köfte
koroglu_kofte : Köroğlu Köfte
sebzeli_kofte : Sebzeli Köfte
iskender_kofte : İskender Köfte
sogurtmeli_kofte : Söğürtmeli Köfte
misket_kofte|mantar_sos : Mantar Soslu Misket Köfte
misket_kofte|mantar_sos|patates_pure : Püreli Mantar Soslu Misket Köfte
misket_kofte|avci_sos : Avcı Usulü Misket Köfte
misket_kofte|meksika_sos : Meksika Soslu Misket Köfte
kadinbudu_kofte : Kadınbudu Köfte
odemis_kofte : Ödemiş Köfte
yogurtlu_kofte_kebabi : Yoğurtlu Köfte Kebabı
izgara_kofte|patlican_puresi : Beğendili Kuru Köfte; Beğendili Köfte
canak_kofte : Çanak Köfte
mantarli_canak_kofte : Mantarlı Çanak Köfte
coban_kofte|patates_pure : Püreli Çoban Köfte
icli_kofte : İçli Köfte
dana_haslama : Dana Haşlama
tavuk_haslama : Tavuk Haşlama; Piliç Haşlama
et_doner : Et Döner
et_tantuni : Et Tantuni
macar_gulas : Dana Macar Gulaş; Macar Gulaş
macar_kebabi : Macar Kebabı
dana_kavurma : Dana Kavurma; Zerdeçallı Dana Kavurma
dana_kavurma|patates_pure : Püreli Dana Kavurma
coban_kavurma : Çoban Kavurma; Dana Çoban Kavurma
mersin_kavurma : Mersin Kavurma
mersin_kavurma|patates_pure : Püreli Mersin Kavurma
sac_kavurma : Sac Kavurma
dana_yahni : Dana Yahni; Soğanlı Dana Yahni
keskekli_dana_yahni : Keşkekli Dana Yahni
dana_et_sote : Dana Et Sote
dana_et_sote|patates_pure : Püreli Et Sote
dana_et_sote|kup_patates : Patates Garnitürlü Dana Et Sote
dana_rosto : Dana Rosto
dana_rosto|patates_pure : Püreli Dana Rosto
pot_roast : Pot Roast
stroganoff : Beef Stroganoff; Beef Stroganof; Dana Stroganoff; Dana Stroganof
dana_burginyon : Dana Burginyon
dana_fleminyon_mantarli : Dana Fleminyon Mantarlı; Mantarlı Dana Fleminyon
dana_madalyon : Dana Madalyon
dana_madalyon_mantar_soslu : Dana Madalyon Mantar Soslu
dana_madalyon|patlican_puresi : Patlıcan Beğendili Dana Madalyon
dana_biftek : Dana Biftek
dana_biftek|karamelize_sogan : Karamelize Soğanlı Biftek
dana_biftek|kendi_sosu : Dana Biftek Demi Glace Soslu
dana_biftek|meksika_sos : Meksika Soslu Dana Biftek
koylu_usulu_biftek : Köylü Usulü Biftek
dana_emince : Dana Emincé
dana_emense : Dana Emense
dana_mutancana : Dana Mutancana
dana_tandir : Dana Tandır
hindi_tandir : Hindi Tandır
kuzu_kizartma : Kuzu Kızartma
arnavut_ciger : Arnavut Ciğer
tesrube : Teşrübe
etli_taco : Etli Taco
et_fajita : Et Fajita
kayseri_yaglama : Kayseri Yağlama
orman_kebabi : Orman Kebap; Orman Kebabı
sebzeli_kebap : Sebzeli Kebap
sehzade_kebabi : Şehzade Kebabı
cokertme_kebabi : Çökertme Kebabı
pilic_cokertme : Piliç Çökertme; Tavuk Çökertme
taskebabi : Taskebap; Püreli Tas Kebabı; Püreli Tas Kebap; Püreli Taskebap
filiz_kebabi : Filiz Kebabı; Filiz Kebap
abant_kebabi : Abant Kebabı
bugu_kebabi : Buğu Kebabı
tepsi_kebabi : Tepsi Kebabı
saksi_kebabi : Saksı Kebabı
girit_kebabi : Girit Kebabı
ciftlik_kebabi : Çiftlik Kebabı
maras_tava : Maraş Tava
belen_tava : Dana Belen Tava
bohca_kebabi : Bohça Kebabı; Sultan Bohçası; Saray Bohçası
yufkali_kebap : Yufkalı Kebap; Yufkalı Saray Kebabı; Yufkalı Manisa Kebap; Yufkalı Manisa Kebabı
islim_kebabi : İslim Kebap; İslim Köfte
patlican_kebabi : Patlıcan Kebap
etsiz_patlican_kebabi : Etsiz Patlıcan Kebabı
adana_kebabi : Adana Kebap
dana_et_sote|patlican_puresi : Beğendili Kebap
pilic_sis : Piliç Şiş
pilic_fajita : Piliç Fajita
tavuk_baget : Piliç Baget Fırın
tavuk_baget|bbq_sos : Piliç Baget Barbekü Soslu; Barbekü Soslu Piliç Baget
sebzeli_tavuk_baget : Sebzeli Fırın Tavuk Baget
pilic_izgara|avci_sos : Avcı Soslu Piliç Izgara
pilic_izgara|bbq_sos : Barbekü Soslu Piliç Izgara; Barbekü Soslu Izgara Piliç
pilic_izgara|meksika_sos : Meksika Sos Piliç Izgara
tavuk_but_izgara : Tavuk But Izgara
susamli_pilic_roti|bbq_sos : B.B.Q Soslu Susamlı Piliç Roti
sebzeli_pilic_sote : Sebzeli Piliç
sebzeli_pilic_sote|beyaz_sos : Beyaz Soslu Sebzeli Piliç Sote; Beyaz Soslu Mantarlı Sebzeli Piliç Sote
tavuk_sote|patlican_puresi : Beğendili Tavuk Sote
pilic_topkapi : Piliç Topkapı
pilic_sarma|kup_patates : Küp Patates Eşliğinde Soslu Piliç Sarma
ispanak_yataginda_balik : Ispanak Yatağında Balık
cupra_firin : Çupra Fırın
musakka_patlican : Patlıcan Musakka; Etli Patlıcan Musakka
musakka_patates : Etli Patates Musakka
musakka_karisik : Ege Musakka; Etli Ege Musakka; Karışık Musakka; Etli Karışık Musakka
etli_biber_dolma : Etli Biber Dolma; Biber Dolma
etli_karisik_dolma : Etli Karışık Dolma; Karışık Dolma
etli_sogan_dolma : Etli Soğan Dolma
etli_yaprak_sarma : Etli Yaprak Sarma
etli_lahana_pohcasi : Etli Lahana Pohçası
karniyarik : Karnıyarık; Etli Karnıyarık; Eli Böğründe
etsiz_mevsim_turlusu : Etsiz Mevsim Türlü
etli_mevsim_turlusu : Etli Mevsim Türlü; Mevsim Türlü; Mevsim Türlüsü
kis_turlusu : Kış Türlüsü
etli_taze_fasulye : Etli Taze Fasulye
etsiz_taze_fasulye : Etsiz Taze Fasulye
sebze_graten : Sebze Graten
etli_sebze_graten : Etli Sebze Graten
ispanak_graten : Ispanak Graten
mantarli_ispanak_graten : Mantarlı Ispanak Graten
sebzeli_mantar_sote : Sebzeli Mantar Sote
kori_sebzeli_sote : Körili Mantar Soslu Sebzeli Sote
karisik_sebze_sote : Karışık Sebze Sote
soslu_patlican_kizartma : Soslu Patlıcan Kızartma
soslu_karisik_kizartma : Soslu Karışık Kızartma
etli_kuru_fasulye : Kuru Fasulye; Etli Kuru Fasulye
etsiz_kuru_fasulye : Etsiz Kuru Fasulye
gemici_kuru_fasulye : Gemici Usulü Kuru Fasulye
etli_nohut : Etli Nohut; Etli Nohut Yahni; Nohut Yahni; Gemici Usulü Nohut
nohut_yemegi : Nohut
tereyagli_nohut : Tereyağlı Nohut
nohut_yemegi|arpacik_sogan|beyaz_sos : Beyaz Soslu Arpacık Soğanlı Nohut
etli_barbunya : Kehribar Soslu Etli Barbunya
barbunya : Barbunya
yesil_mercimek_yemegi : Yeşil Mercimek Yemeği
tirnakli_pide : Tırnaklı Pide
etli_pide : Etli Pide
kusbasili_kasarli_pide : Kuşbaşılı Kaşarlı Pide
pizza : Pizza; Karışık Pizza
hamburger : Hamburger
manti : Mantı
pirinc_pilavi : Pirinç Pilavı; Tereyağlı Pirinç Pilavı; Zerdeçallı Pirinç Pilavı
sehriyeli_pirinc_pilavi : Şehriyeli Pirinç Pilavı; Arpa Şehriyeli Pirinç Pilavı
meyane_pilavi : Meyane Pilavı; Meyhane Pilavı
sebzeli_pirinc_pilavi : Sebzeli Pirinç Pilavı
misirli_pirinc_pilavi : Mısırlı Pirinç Pilavı
nohutlu_pirinc_pilavi : Nohutlu Pirinç Pilavı; Nohutlu Pilav
tavuklu_pirinc_pilavi : Tavuklu Pirinç Pilavı
domatesli_pirinc_pilavi : Domatesli Pirinç Pilavı; Salçalı Domatesli Pirinç Pilavı
uzumlu_pirinc_pilavi : Üzümlü Pirinç Pilavı
ic_pilav : İç Pilav
melek_pilavi : Melek Pilavı
yayla_pilavi : Yayla Pilavı
bulgur_pilavi : Bulgur Pilavı; Zerdeçallı Bulgur Pilavı
salcali_bulgur_pilavi : Salçalı Bulgur Pilavı
sehriyeli_bulgur_pilavi : Şehriyeli Bulgur Pilavı
sebzeli_bulgur_pilavi : Sebzeli Bulgur Pilavı
nohutlu_bulgur_pilavi : Nohutlu Bulgur Pilavı
patlicanli_bulgur_pilavi : Patlıcanlı Bulgur Pilavı
sehriye_pilavi : Arpa Şehriye Pilavı; Şehriye Pilavı
sebzeli_sehriye_pilavi : Sebzeli Şehriye Pilavı
kuskus_pilavi : Kuskus Pilavı
firik_pilavi : Firik Pilavı
cevizli_eriste : Cevizli Erişte; Erişte Cevizli; Cevizli Erişte Kavurma
eriste_kavurma : Erişte Kavurma; Erişte
peynirli_eriste_kavurma : Peynirli Erişte Kavurma
sebzeli_eriste : Sebzeli Erişte
makarna_sade : Makarna; Burgu Makarna; Spagetti
peynirli_makarna : Peynirli Makarna; Peynirli Burgu Makarna; Peynirli İnce Uzun Makarna; Peynirli Boncuk Makarna; Peynirli Penne Makarna
pesto_makarna : Pesto Soslu Spagetti; Pesto Soslu Penne Makarna; Pestolu İnce Uzun Makarna; Pesto Sos Spagetti; Pesto Sosu Kısa Kalem Makarna; Pesto Soslu Fettuccine Makarna; Pesto Soslu İnce Uzun Makarna
mantarli_pesto_makarna : Mantarlı Pestolu Fettucini
arabiata_makarna : Spagetti Arabiatta; Penne Arabiatta; Arabiatta Spagetti; Fetüçini Arabiatta; Füsuli Arabiatta; Spagetti Arrabbiata
napoliten_makarna : Napoliten Soslu Kısa Kalem Makarna; Napoliten Soslu Makarna; Napoliten Burgu Makarna; Napoliten Spagetti; Napoliten Sos Kısa Kalem Makarna; Napoliten Sos Burgu Makarna; Napoliten Soslu Burgu Makarna
karbonara_makarna : Spagetti Karbonara; Karbonara; Spagetti Carbonara
mantar_soslu_makarna : Mantar Soslu Spagetti; Mantar Soslu Penne Makarna; Mantar Soslu İnce Uzun Makarna; Fetüçini Mantar Soslu; Fettucine Mantarlı
kori_mantar_makarna : Mantarlı Köri Soslu Farfalle Makarna; Körili Mantar Sos Burgu Makarna; Mantarlı Köri Sos Burgu Makarna; Mantarlı Köri Soslu Burgu Makarna
kori_soslu_makarna : Köri Soslu İnce Uzun Makarna
bolonez_makarna : Bolonez Soslu Makarna
firin_makarna : Fırın Makarna
kiymali_lazanya : Kıymalı Lazanya
sebzeli_lazanya : Sebzeli Lazanya
su_boregi : Su Böreği; Peynirli Su Böreği
kol_boregi_ogle : Peynirli Kol Böreği; Kol Böreği
gul_boregi : Peynirli Gül Böreği; Gül Böreği
ispanakli_gul_boregi : Ispanaklı Peynirli Gül Böreği; Ispanaklı Gül Böreği
"""

def build():
    amap = {}
    for line in ALIAS_TXT.strip().splitlines():
        if not line.strip(): continue
        ids, raws = line.split(" : ", 1)
        ids = "" if ids == "@" else ids
        for r in raws.split(";"):
            r = r.strip()
            assert r not in amap, "dup alias " + r
            amap[r] = ids
    for ids in amap.values():
        for d in filter(None, ids.split("|")):
            assert d in DISHES, "bilinmeyen dish " + d
    return amap

def desc(rec):
    names = []
    for k, g in sorted(rec.items(), key=lambda kv: -kv[1]):
        names.append(ING[k].split(" (")[0].split(" /")[0].strip().lower())
    return ", ".join(names)

PORT = {"kofte": "1 porsiyon, ~100 g çiğ kıyma", "et_yemegi": "1 porsiyon", "tavuk_yemegi": "1 porsiyon",
        "pilav": "1 porsiyon pilav", "makarna": "1 porsiyon makarna", "sos": "1 servis kepçesi sos",
        "patates_garnitur": "1 porsiyon garnitür", "baklagil": "1 porsiyon", "sebze_yemegi": "1 porsiyon",
        "ekmek_hamur": "1 porsiyon", "borek": "1 dilim/porsiyon", "balik": "1 porsiyon balık",
        "kahvalti_yumurta": "2 yumurta"}

def main():
    amap = build()
    items = list(csv.DictReader(open(ROOT/"data"/"items_raw.csv", encoding="utf-8")))
    rows = [(r["comp"], r["raw"]) for r in items if r["comp"] in ("ana", "pilav")]
    missing = [r for c, r in rows if r not in amap]
    assert not missing, missing
    used = {r for c, r in rows}
    extra = [r for r in amap if r not in used]
    assert not extra, extra
    with open(N/"dishes_a.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["dish_id", "name_tr", "category", "portion_desc", "desc"])
        for i, (name, cat, rec) in DISHES.items():
            tot = round(sum(rec.values()))
            w.writerow([i, name, cat, f"{PORT.get(cat,'1 porsiyon')}, ~{tot} g (çiğ toplam)", desc(rec)])
    with open(N/"recipes_a.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["dish_id", "ingredient_id", "grams"])
        for i, (name, cat, rec) in DISHES.items():
            for k, g in rec.items(): w.writerow([i, k, f"{g:g}"])
    with open(N/"aliases_a.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["comp", "raw", "dish_ids"])
        for c, r in rows: w.writerow([c, r, amap[r]])
    print(len(DISHES), "dishes;", len(rows), "aliases")

main()
