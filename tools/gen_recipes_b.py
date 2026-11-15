# -*- coding: utf-8 -*-
"""dishes_b / recipes_b / aliases_b uretici (bilesenler: corba, tatli, yogurt, salata, kahvaltilik, hamur, diger)."""
import csv, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
N = ROOT / "data" / "nutrition"
OWN = {"corba", "tatli", "yogurt", "salata", "kahvaltilik", "hamur", "diger"}

D = []  # (id, name, cat, portion, recipe)
def d(i, name, cat, portion, rec):
    D.append((i, name, cat, portion, rec))

BOWL = "1 kase, 250 ml"
def soup(i, name, rec): d(i, name, "corba", BOWL, rec)

# ---------------- CORBA ----------------
soup("mercimek_corba", "Mercimek Çorbası", "kirmizi_mercimek:30 sogan:15 havuc:20 un:3 tereyagi:8")
soup("krotonlu_mercimek_corba", "Krotonlu Mercimek Çorbası", "kirmizi_mercimek:30 sogan:15 havuc:20 un:3 tereyagi:8 ekmek:15")
soup("ezogelin_corba", "Ezogelin Çorbası", "kirmizi_mercimek:22 bulgur:10 pirinc:8 sogan:15 salca:10 tereyagi:8")
soup("tarhana_corba", "Tarhana Çorbası", "un:20 yogurt:30 domates:10 biber:5 sogan:5 salca:5 tereyagi:8")
soup("yayla_corba", "Yayla Çorbası", "yogurt:60 pirinc:15 un:5 yumurta:15 tereyagi:5")
soup("acem_corba", "Acem Çorbası", "kirmizi_mercimek:15 nohut:10 bulgur:10 domates:30 sogan:15 salca:5 tereyagi:8")
soup("domates_corba", "Domates Çorbası", "domates:120 salca:10 un:10 tereyagi:8 kasar:15 sut:40")
soup("kitir_ekmekli_domates_corba", "Kıtır Ekmekli Domates Çorbası", "domates:120 salca:10 un:10 tereyagi:8 kasar:10 sut:40 ekmek:20")
soup("brokoli_corba", "Brokoli Çorbası", "brokoli:100 patates:40 sogan:15 un:8 sut:60 tereyagi:5 krema:10")
soup("kremali_mantar_corba", "Kremalı Mantar Çorbası", "mantar:80 un:12 sut:100 krema:20 sogan:15 tereyagi:8")
soup("canakkale_corba", "Çanakkale Çorbası", "kirmizi_mercimek:20 patates:40 havuc:20 sogan:15 domates:20 tereyagi:8 kasar:10 un:4")
soup("andaloz_corba", "Andaloz Çorbası", "bulgur:15 nohut:15 kirmizi_mercimek:10 domates:30 sogan:15 salca:5 tereyagi:8 maydanoz:3")
soup("dugun_corba", "Düğün Çorbası", "dana_et:25 un:12 yumurta:20 limon:8 tereyagi:8")
soup("toyga_corba", "Toyga Çorbası", "yogurt:70 bugday_dovme:20 nohut:10 un:3 yumurta:10 tereyagi:8 sogan:10")
soup("dovme_corba", "Dövme (Naneli Buğday) Çorbası", "bugday_dovme:30 yogurt:50 nohut:8 un:3 tereyagi:8 sogan:10")
soup("yuksuk_corba", "Yüksük Çorbası", "un:25 dana_kiyma:15 nohut:10 yogurt:20 sogan:15 salca:8 tereyagi:8 yumurta:8")
soup("gemici_corba", "Gemici Çorbası", "dana_et:20 patates:40 havuc:20 sogan:15 salca:8 bulgur:10 tereyagi:8")
soup("kremali_tavuk_corba", "Kremalı Tavuk Çorbası", "tavuk_gogus:30 un:12 sut:100 krema:15 havuc:10 sogan:10 tereyagi:8")
soup("terbiyeli_tavuk_corba", "Terbiyeli Tavuk Çorbası", "tavuk_gogus:30 un:8 yumurta:20 limon:8 havuc:10 tereyagi:8")
soup("sehriyeli_tavuk_corba", "Şehriyeli Tavuk Çorbası", "tavuk_gogus:25 makarna:20 havuc:10 sogan:10 salca:5 tereyagi:8")
soup("tavuk_suyu_corba", "Tavuk Suyu Çorbası", "tavuk_gogus:30 havuc:20 patates:20 sogan:10 makarna:10 tereyagi:5")
soup("sehriye_corba", "Şehriye Çorbası", "makarna:25 domates:60 salca:8 sogan:10 tereyagi:8")
soup("salcali_koylu_corba", "Salçalı Köylü Çorbası", "bulgur:20 kirmizi_mercimek:10 salca:12 sogan:15 patates:30 tereyagi:8")
soup("kremali_tane_sebze_corba", "Kremalı Tane Sebze Çorbası", "havuc:25 patates:30 bezelye:15 misir:15 un:10 sut:80 krema:15 sogan:10 tereyagi:5")
soup("sebze_corba", "Sebze Çorbası", "patates:40 havuc:25 kabak:30 bezelye:15 domates:30 sogan:10 tereyagi:8")
soup("havuc_corba", "Havuç Çorbası", "havuc:100 patates:30 sogan:15 un:8 sut:60 krema:10 tereyagi:6")
soup("misir_corba", "Mısır Çorbası", "misir:80 patates:30 havuc:20 sogan:10 un:8 sut:60 krema:10 tereyagi:6")
soup("cennet_corba", "Cennet Çorbası", "patates:60 misir:40 havuc:15 sogan:10 un:8 sut:80 krema:10 tereyagi:6")
soup("ispanak_corba", "Ispanak Çorbası", "ispanak:100 patates:30 sogan:15 un:8 sut:80 yogurt:20 tereyagi:6")
soup("ayran_asi_corba", "Ayran Aşı Çorbası", "yogurt:100 bugday_dovme:20 nohut:10 un:3 tereyagi:5")
soup("alaca_corba", "Alaca Çorbası", "kirmizi_mercimek:15 yesil_mercimek:15 bulgur:10 domates:30 sogan:15 tereyagi:8")
soup("koz_patlican_corba", "Köz Patlıcan Çorbası", "patlican:100 un:10 sut:80 tereyagi:8 krema:10 sogan:10")
soup("mengen_corba", "Mengen Çorbası", "dana_et:25 pirinc:15 yogurt:40 un:5 yumurta:15 tereyagi:8")
soup("osmanli_corba", "Osmanlı Çorbası", "tavuk_gogus:25 yogurt:50 un:8 yumurta:15 sogan:10 havuc:10 tereyagi:8")
soup("supa_topceta_corba", "Supa Topçeta Çorbası", "dana_kiyma:25 pirinc:10 yumurta:10 un:8 domates:30 sogan:15 tereyagi:8 limon:5")
soup("cesminigar_corba", "Çeşminigar Çorbası", "dana_et:20 nohut:10 pirinc:10 yogurt:40 un:5 yumurta:10 sogan:10 tereyagi:8")
soup("mahluta_corba", "Mahluta (Dört Kaşık) Çorbası", "kirmizi_mercimek:12 nohut:8 bulgur:8 pirinc:8 kuru_fasulye:8 sogan:15 domates:20 salca:5 tereyagi:8")
soup("lebeniye_corba", "Lebeniye Çorbası", "yogurt:70 pirinc:15 nohut:10 un:5 yumurta:10 tereyagi:6")
soup("beyran_corba", "Beyran Çorbası", "kuzu_et:40 pirinc:25 sarimsak:3 tereyagi:8")
soup("tutmac_corba", "Tutmaç Çorbası", "eriste:25 yogurt:80 sogan:5 un:3 tereyagi:8")
soup("eristeli_yesil_mercimek_corba", "Erişteli Yeşil Mercimek Çorbası", "yesil_mercimek:25 eriste:15 sogan:15 havuc:10 salca:5 tereyagi:8")
soup("borc_corba", "Borç Çorbası", "lahana:50 havuc:20 patates:40 dana_et:20 salca:8 sogan:15")
soup("suleymaniye_corba", "Süleymaniye Çorbası", "dana_kiyma:20 pirinc:15 nohut:10 yumurta:10 domates:30 sogan:10 tereyagi:8 limon:5")
soup("muradiye_corba", "Muradiye Çorbası", "yogurt:50 bulgur:15 nohut:10 sogan:10 un:3 tereyagi:8")
soup("anadolu_corba", "Anadolu Çorbası", "kirmizi_mercimek:15 bulgur:10 nohut:8 yogurt:30 sogan:10 salca:5 un:3 tereyagi:8")
soup("sefin_corba", "Şefin (Aşçıbaşı) Çorbası", "tavuk_gogus:20 mantar:20 havuc:15 patates:30 un:8 sut:60 krema:10 tereyagi:6")
soup("safak_corba", "Şafak Çorbası", "kirmizi_mercimek:20 havuc:30 domates:40 patates:20 sogan:10 un:3 tereyagi:8")
soup("roman_corba", "Roman Çorbası", "tavuk_gogus:20 patates:30 havuc:20 sogan:10 domates:30 makarna:10 tereyagi:6")
soup("anali_kizli_corba", "Analı Kızlı Çorbası", "bulgur:25 dana_kiyma:20 nohut:10 domates:30 salca:5 sogan:15 un:5 tereyagi:8")
soup("yuvalama_corba", "Yuvalama Çorbası", "dana_kiyma:25 pirinc:20 yogurt:50 nohut:10 un:5 yumurta:10 tereyagi:8")
soup("meksika_corba", "Acılı Meksika Çorbası", "misir:40 barbunya:15 domates:50 salca:8 kirmizi_biber:20 sogan:15 tavuk_gogus:30 sivi_yag:5")
soup("kereviz_corba", "Kereviz Çorbası", "kereviz:100 patates:30 sogan:10 un:8 sut:60 krema:10 tereyagi:6")
soup("bal_kabagi_corba", "Bal Kabağı Çorbası", "balkabagi:150 patates:20 sogan:15 un:6 sut:60 krema:10 tereyagi:6")

# ---------------- TATLI ----------------
def sh(i, name, rec, portion="1 porsiyon, ~100 g"): d(i, name, "serbetli_tatli", portion, rec)
def sl(i, name, rec, portion="1 porsiyon, ~150 g"): d(i, name, "sutlu_tatli", portion, rec)
def pk(i, name, rec, portion="1 dilim, ~100 g"): d(i, name, "pasta_kek", portion, rec)

d("meyve", "Meyve", "meyve", "1 porsiyon, 150 g", "meyve:150")
sh("baklava", "Baklava", "yufka:40 tereyagi:15 ceviz:12 antep_fistigi:8 seker:35", "3-4 dilim, ~80 g")
sh("kadayif", "Kadayıf (Burma/Tel)", "yufka:40 tereyagi:15 ceviz:15 seker:35", "1 porsiyon, ~90 g")
sh("saray_burma", "Saray Burma (Sarma)", "yufka:35 tereyagi:12 antep_fistigi:12 seker:35", "2 adet, ~90 g")
sh("kaymakli_ekmek_kadayifi", "Kaymaklı Ekmek Kadayıfı", "ekmek:35 seker:40 krema:30 ceviz:8", "1 porsiyon, ~120 g")
sh("sekerpare", "Şekerpare", "un:22 irmik:8 tereyagi:12 yumurta:10 seker:35 badem:3", "2 adet, ~80 g")
sh("kakaolu_sekerpare", "Kakaolu Şekerpare", "un:22 irmik:8 tereyagi:12 yumurta:10 seker:35 kakao:5", "2 adet, ~80 g")
sh("hashasli_sekerpare", "Haşhaşlı Şekerpare (Haşhaşpare)", "un:22 irmik:8 tereyagi:12 yumurta:10 seker:35 hashas:5", "2 adet, ~80 g")
sh("findikpare", "Fındıkpare", "un:20 irmik:8 tereyagi:12 yumurta:10 seker:35 findik:15", "2 adet, ~80 g")
sh("revani", "Revani", "irmik:22 un:10 yumurta:20 yogurt:20 sivi_yag:8 seker:40", "1 dilim, ~100 g")
sh("hashasli_revani", "Haşhaşlı Revani", "irmik:22 un:10 yumurta:20 yogurt:20 sivi_yag:8 seker:40 hashas:6", "1 dilim, ~100 g")
sh("tulumba", "Tulumba", "un:25 irmik:5 yumurta:15 sivi_yag:12 seker:35", "4 adet, ~90 g")
sh("sobiyet", "Şöbiyet", "yufka:35 tereyagi:12 sut:40 irmik:8 seker:35 antep_fistigi:8", "2 dilim, ~90 g")
sh("kalburabasti", "Kalburabastı", "un:22 irmik:10 tereyagi:15 yumurta:10 seker:35 ceviz:10", "2 adet, ~80 g")
sh("sam_tatlisi", "Şam Tatlısı", "irmik:30 yogurt:30 yumurta:20 sivi_yag:8 seker:40 antep_fistigi:5", "2 adet, ~100 g")
sh("kibris_tatlisi", "Kıbrıs Tatlısı", "un:18 irmik:12 tereyagi:15 yumurta:10 seker:38 ceviz:12", "1 porsiyon, ~100 g")
sh("arap_tatlisi", "Arap Tatlısı", "irmik:25 un:8 yumurta:15 sivi_yag:10 seker:38 hindistan_cevizi:8", "1 porsiyon, ~100 g")
sh("kemalpasa_tatlisi", "Kemalpaşa Tatlısı", "irmik:20 un:10 beyaz_peynir:30 yumurta:15 tereyagi:5 seker:40", "2 adet, ~100 g")
sh("balbadem", "Balbadem (Bal Badem)", "un:20 badem:15 tereyagi:12 yumurta:10 bal:25 seker:15", "2 adet, ~80 g")
sh("hanim_gobegi", "Hanım Göbeği", "un:25 yumurta:15 tereyagi:10 nisasta:5 seker:40", "3 adet, ~90 g")
sh("havuc_dilimi", "Havuç Dilimi", "havuc:60 un:20 yumurta:15 sivi_yag:10 seker:35 ceviz:8", "1 dilim, ~100 g")
sh("yogurt_tatlisi", "Yoğurt Tatlısı", "yogurt:60 un:20 irmik:10 yumurta:15 sivi_yag:10 seker:38", "1 dilim, ~100 g")
sh("peynir_tatlisi", "Peynir Tatlısı", "yufka:35 tereyagi:12 beyaz_peynir:35 seker:35", "1 porsiyon, ~100 g")
sh("tahinli_cevizli_peynir_tatlisi", "Tahinli Cevizli Peynir Tatlısı", "yufka:35 tereyagi:12 beyaz_peynir:35 seker:30 tahin:10 ceviz:12", "1 porsiyon, ~110 g")
sh("kabak_tatlisi", "Tahinli Cevizli Kabak Tatlısı", "balkabagi:150 seker:30 tahin:10 ceviz:12", "1 porsiyon, ~150 g")
sh("bakla_tatlisi", "Tahinli Cevizli Bakla Tatlısı", "kuru_fasulye:25 seker:30 tahin:10 ceviz:12", "1 porsiyon, ~120 g")
sh("hurma_tatlisi", "Hurma Tatlısı", "hurma:50 un:20 tereyagi:12 ceviz:10 seker:5", "1 porsiyon, ~100 g")
sh("ejder_tatlisi", "Ejder Tatlısı", "kek:50 krema:25 seker:20 cikolata:10", "1 dilim, ~100 g")
sh("soguk_kadayif", "Soğuk Kadayıf", "yufka:30 sut:100 krema:15 seker:25 ceviz:10", "1 porsiyon, ~150 g")
sh("asure", "Aşure", "bugday_dovme:15 nohut:6 kuru_fasulye:6 uzum_kuru:15 seker:22 ceviz:10 findik:5", "1 kase, ~200 g")
sh("cikolata_soslu_churros", "Çikolata Soslu Churros", "un:30 yumurta:10 sivi_yag:15 seker:10 cikolata:25", "4 adet, ~100 g")
d("islak_kek", "Islak Kek", "pasta_kek", "1 dilim, ~100 g", "un:25 kakao:5 yumurta:20 seker:30 sivi_yag:10 sut:40")

sl("firin_sutlac", "Fırın Sütlaç", "sut:150 pirinc:12 seker:22 yumurta:10")
sl("sutlu_irmik_tatlisi", "Sütlü İrmik Tatlısı", "sut:120 irmik:15 seker:20 tereyagi:5")
sl("kazandibi", "Kazandibi", "sut:150 seker:25 nisasta:8 pirinc_unu:8 tereyagi:3")
sl("tavuk_gogsu", "Tavuk Göğsü (Soslu Tavuk Göğsü)", "sut:130 seker:22 tavuk_gogus:15 pirinc_unu:10 nisasta:5 tereyagi:3")
sl("keskul", "Keşkül-ü Fukara", "sut:130 seker:22 badem:12 nisasta:8 pirinc_unu:5 yumurta:15 hindistan_cevizi:5")
sl("pannacotta", "Pannacotta", "krema:80 sut:50 seker:22")
sl("visneli_pannacotta", "Vişneli Pannacotta", "krema:80 sut:50 seker:28 visne:40")
sl("krem_karamel", "Krem Karamel", "sut:120 yumurta:40 seker:30")
sl("krem_brule", "Krem Brüle", "krema:100 yumurta:30 seker:25")
sl("supangle", "Supangle", "sut:130 seker:22 cikolata:15 kakao:5 nisasta:10")
sl("kekli_supangle", "Kekli Supangle", "sut:130 seker:18 cikolata:15 kakao:5 nisasta:10 kek:20")
sl("muhallebi", "Muhallebi (Sakızlı)", "sut:150 seker:22 nisasta:12")
sl("bademli_muhallebi", "Bademli Muhallebi", "sut:150 seker:22 nisasta:12 badem:10")
sl("muzlu_muhallebi", "Muzlu Muhallebi", "sut:150 seker:20 nisasta:12 muz:40")
sl("kuru_meyveli_muhallebi", "Kuru Meyveli Muhallebi", "sut:150 seker:15 nisasta:12 uzum_kuru:15")
sl("kestaneli_sutte", "Kestaneli Sütte", "sut:130 seker:25 hurma:25 nisasta:5")
sl("findikli_gullac", "Fındıklı Gullaç", "nisasta:20 sut:150 seker:20 findik:15")
sl("sut_dilimi", "Süt Dilimi", "sut:120 seker:22 nisasta:10 biskuvi:20")
sl("naz_tatlisi", "Naz Tatlısı", "sut:120 seker:25 nisasta:10 yumurta:10 ceviz:5 biskuvi:15")
sl("malaga", "Malaga", "sut:100 biskuvi:25 seker:20 nisasta:10 cikolata:12")
sl("magnolya", "Magnolya", "sut:120 nisasta:10 seker:20 biskuvi:20 muz:40")
sl("kabakli_magnolya", "Kabaklı Magnolya", "sut:120 nisasta:10 seker:20 biskuvi:20 balkabagi:50")
sl("tiramisu", "Tiramisu", "kek:40 krem_peynir:40 krema:30 seker:15 kakao:3 yumurta:15", "1 porsiyon, ~100 g")
sl("trilece", "Trileçe", "kek:40 sut:80 krema:40 seker:15", "1 dilim, ~120 g")

pk("browni_kek", "Browni (Brownie)", "un:20 seker:30 cikolata:20 kakao:5 tereyagi:20 yumurta:20 ceviz:8")
pk("mozaik_pasta", "Mozaik Pasta", "biskuvi:50 kakao:6 seker:15 tereyagi:12 sut:20 cikolata:10")
pk("aglayan_pasta", "Ağlayan Pasta", "kek:50 sut:50 kakao:6 seker:20 cikolata:15")
pk("elmali_tart", "Elmalı Tart", "un:25 tereyagi:15 seker:20 meyve:80 yumurta:10")
pk("kostebek_pasta", "Köstebek Pasta", "kek:45 muz:40 krema:25 kakao:5 seker:12 cikolata:10")
pk("kardelen_pasta", "Kardelen Pasta", "kek:55 krema:30 hindistan_cevizi:8 seker:15")
pk("latte_pasta", "Latte Pasta", "kek:55 sut:40 krema:25 seker:15")
pk("visneli_pasta", "Vişneli Pasta", "kek:55 krema:25 visne:40 seker:15")
pk("ispanakli_pasta", "Ispanaklı Pasta", "un:25 ispanak:30 seker:25 yumurta:20 sivi_yag:15 krema:15")
pk("akdeniz_gulu", "Akdeniz Gülü", "kek:50 krema:25 seker:15 meyve:30")
d("dondurma", "Dondurma", "sutlu_tatli", "2 top, ~80 g", "dondurma:80")
d("bal", "Bal", "tatlandirici", "1 porsiyon, 20 g", "bal:20")
d("recel", "Reçel", "tatlandirici", "1 porsiyon, 20 g", "recel:20")

# ---------------- YOGURT / SALATA / KAHVALTILIK / HAMUR / DIGER ----------------
d("yogurt", "Yoğurt", "sut_urunu", "1 kase, 150 g", "yogurt:150")
d("sut", "Süt", "icecek", "1 bardak, 200 ml", "sut:200")
d("salata_zeytinyagli", "Salata ve Zeytinyağlı Sebze", "salata", "1 küçük salata + 1 küçük zeytinyağlı, ~160 g",
  "yesillik:30 domates:25 salatalik:25 zeytinyagi:13 taze_fasulye:40 havuc:20 pirinc:5")
d("mevsim_yesillik", "Mevsim Yeşillikleri", "salata", "1 porsiyon, 30 g", "yesillik:30")
d("ceri_domates", "Çeri Domates", "kahvaltilik", "1 porsiyon, 50 g", "domates:50")
d("salatalik_dilim", "Salatalık", "kahvaltilik", "1 porsiyon, 50 g", "salatalik:50")
d("zeytin_kahvalti", "Zeytin", "kahvaltilik", "1 porsiyon, 25 g", "zeytin:25")
d("tereyagi_kahvalti", "Tereyağı", "kahvaltilik", "1 porsiyon, 10 g", "tereyagi:10")
d("beyaz_peynir_kahvalti", "Beyaz Peynir", "kahvaltilik", "1 porsiyon, 30 g", "beyaz_peynir:30")
d("kasar_kahvalti", "Kaşar Peyniri", "kahvaltilik", "1 porsiyon, 30 g", "kasar:30")
d("tahin_pekmez", "Tahin Pekmez", "kahvaltilik", "1 porsiyon, 35 g", "tahin:15 pekmez:20")

def hm(i, name, rec, portion, cat="ekmek_hamur"): d(i, name, cat, portion, rec)
hm("simit", "Simit", "un:70 susam:6", "1 adet, ~90 g")
hm("pogaca", "Poğaça", "un:40 sivi_yag:10 yogurt:15 yumurta:10 kabartma:1", "1 adet, ~70 g")
hm("kasarli_pogaca", "Kaşarlı Poğaça", "un:40 sivi_yag:10 yogurt:15 yumurta:10 kasar:15 kabartma:1", "1 adet, ~85 g")
hm("acma", "Açma", "un:45 sut:15 tereyagi:10 seker:4 yumurta:8", "1 adet, ~70 g")
hm("zeytinli_acma", "Zeytinli Açma", "un:45 sut:15 tereyagi:10 seker:4 yumurta:8 zeytin:15", "1 adet, ~85 g")
hm("peynirli_gul_boregi", "Peynirli Gül Böreği", "yufka:60 beyaz_peynir:30 yumurta:10 sivi_yag:12 sut:20", "1 porsiyon, ~100 g", "borek")
hm("sigara_boregi", "Sigara Böreği", "yufka:50 beyaz_peynir:30 maydanoz:3 sivi_yag:15 yumurta:5", "3 adet, ~100 g", "borek")
hm("kol_boregi", "Kol Böreği", "yufka:55 beyaz_peynir:25 ispanak:30 sivi_yag:12 yumurta:10 sut:20", "1 dilim, ~110 g", "borek")
d("patates_kizartma", "Patates Kızartma", "patates_garnitur", "1 porsiyon, 80 g", "patates_kizartma:80")
d("sosis", "Sosis", "kahvaltilik", "1 porsiyon, 50 g", "sosis:50")

# ---------------- ALIASES ----------------
ALIAS = {}
CORBA = {
 "Mercimek": "mercimek_corba", "Ev Usulü Mercimek": "mercimek_corba", "Süzme Mercimek": "mercimek_corba",
 "Krotonlu Mercimek": "krotonlu_mercimek_corba", "Krotonlu Ev Usulü Mercimek": "krotonlu_mercimek_corba",
 "Krotonlu Terbiyeli Mercimek": "krotonlu_mercimek_corba",
 "Ezogelin": "ezogelin_corba", "Tarhana": "tarhana_corba",
 "Yayla": "yayla_corba", "Naneli Yoğurt": "yayla_corba", "Yoğurt": "yayla_corba",
 "Acem": "acem_corba", "Kaşarlı Domates": "domates_corba", "Domates": "domates_corba", "Mantarlı Domates": "domates_corba",
 "Kıtır Ekmekli Domates": "kitir_ekmekli_domates_corba", "Krotonlu Domates": "kitir_ekmekli_domates_corba",
 "Brokoli": "brokoli_corba", "Kremalı Mantar": "kremali_mantar_corba", "Mantar": "kremali_mantar_corba",
 "Çanakkale": "canakkale_corba", "Andaloz": "andaloz_corba", "Andoloz": "andaloz_corba", "Maydanozlu Andaloz": "andaloz_corba",
 "Düğün": "dugun_corba", "Çeşminigar": "cesminigar_corba", "Çeşmi Nigar": "cesminigar_corba", "Çeşminigâr": "cesminigar_corba",
 "Yüksük": "yuksuk_corba", "Toyga": "toyga_corba", "Gemici": "gemici_corba",
 "Naneli Dövme": "dovme_corba", "Dövme": "dovme_corba", "Naneli Buğday": "dovme_corba", "Buğday": "dovme_corba",
 "Kremalı Tavuk": "kremali_tavuk_corba", "Terbiyeli Tavuk": "terbiyeli_tavuk_corba", "Terbiyeli Tavuk Suyu": "terbiyeli_tavuk_corba",
 "Şehriyeli Tavuk": "sehriyeli_tavuk_corba", "Salçalı Şehriyeli Tavuk": "sehriyeli_tavuk_corba",
 "Tavuk Suyu": "tavuk_suyu_corba", "Sebzeli Tavuk Suyu": "tavuk_suyu_corba",
 "Domatesli Şehriye": "sehriye_corba", "Şehriye": "sehriye_corba", "Salçalı Şehriye": "sehriye_corba",
 "Maydanozlu Şehriye": "sehriye_corba", "Terbiyeli Şehriye": "sehriye_corba",
 "Salçalı Köylü": "salcali_koylu_corba", "Salçalı Köylü Usulü": "salcali_koylu_corba",
 "Kremalı Tane Sebze": "kremali_tane_sebze_corba", "Kremalı Sebze Tane": "kremali_tane_sebze_corba",
 "Taneli Kremalı Sebze": "kremali_tane_sebze_corba", "Kremalı Taneli Sebze": "kremali_tane_sebze_corba",
 "Sebze": "sebze_corba", "Sebze Tane": "sebze_corba",
 "Havuç": "havuc_corba", "Kremalı Havuç": "havuc_corba", "Sütlü Havuç": "havuc_corba",
 "Kremalı Havuçlu Mısır": "misir_corba", "Dereotlu Mısır": "misir_corba",
 "Cennet": "cennet_corba", "Patatesli Mısırlı Cennet": "cennet_corba", "Ispanak": "ispanak_corba",
 "Ayran Aşı": "ayran_asi_corba", "Alaca": "alaca_corba", "Köz Patlıcan": "koz_patlican_corba",
 "Mengen": "mengen_corba", "Osmanlı": "osmanli_corba", "Supa Topçeta": "supa_topceta_corba",
 "Mahluta": "mahluta_corba", "Dört Kaşık": "mahluta_corba", "Lebeniye": "lebeniye_corba",
 "Beyran": "beyran_corba", "Tutmaç": "tutmac_corba",
 "Yeşil Mercimekli Erişte": "eristeli_yesil_mercimek_corba", "Erişteli Yeşil Mercimek": "eristeli_yesil_mercimek_corba",
 "Şehriyeli Yeşil Mercimek": "eristeli_yesil_mercimek_corba",
 "Borç": "borc_corba", "Süleymaniye": "suleymaniye_corba", "Muradiye": "muradiye_corba", "Anadolu": "anadolu_corba",
 "Şefin": "sefin_corba", "Aşçıbaşı": "sefin_corba", "Şafak": "safak_corba", "Roman": "roman_corba",
 "Analı Kızlı": "anali_kizli_corba", "Yuvalama": "yuvalama_corba", "Acılı Meksika": "meksika_corba",
 "Kereviz": "kereviz_corba", "Bal Kabağı": "bal_kabagi_corba",
}
for k, v in CORBA.items():
    ALIAS[("corba", k)] = v
TATLI = {
 "Meyve": "meyve", "Bal": "bal", "Reçel": "recel", "Baklava": "baklava", "Cevizli Baklava": "baklava", "Cimcik Baklava": "baklava",
 "Haşhaşlı Revani": "hashasli_revani", "Revani": "revani", "Portakallı Revani": "revani", "Limonlu Revani": "revani",
 "Burma Kadayıf": "kadayif", "Kadayıf": "kadayif", "Tel Kadayıf": "kadayif", "Saray Burma": "saray_burma", "Saray Sarma": "saray_burma",
 "Şekerpare": "sekerpare", "Kakaolu Şekerpare": "kakaolu_sekerpare", "Haşhaşlı Şekerpare": "hashasli_sekerpare",
 "Haşhaşpare": "hashasli_sekerpare", "Fındıkpare": "findikpare",
 "Kalburabastı": "kalburabasti", "Havuç Dilimi": "havuc_dilimi", "Mozaik Pasta": "mozaik_pasta", "Kıbrıs Tatlısı": "kibris_tatlisi",
 "Browni Kek": "browni_kek", "Brownie": "browni_kek", "Fırın Sütlaç": "firin_sutlac", "Şöbiyet": "sobiyet", "Şam Tatlı": "sam_tatlisi",
 "Tavuk Göğsü": "tavuk_gogsu", "Tavuk Göğsü Tatlısı": "tavuk_gogsu", "Soslu Tavuk Göğsü": "tavuk_gogsu",
 "Tremisu": "tiramisu", "Tiramisu": "tiramisu", "Tramisu": "tiramisu", "Kedi Dili Tremisu": "tiramisu",
 "Köstebek Pasta": "kostebek_pasta", "Kazandibi": "kazandibi", "Pannacotta": "pannacotta", "Panacotta": "pannacotta",
 "Vişneli Panacotta": "visneli_pannacotta", "Vişneli Panna Cotta": "visneli_pannacotta",
 "Trileçe": "trilece", "Islak Kek": "islak_kek", "Arap Tatlısı": "arap_tatlisi",
 "Kaymaklı Ekmek Kadayıfı": "kaymakli_ekmek_kadayifi", "Kaymaklı Vişneli Ekmek Kadayıfı": "kaymakli_ekmek_kadayifi",
 "Keşkül-ü Fukara": "keskul", "Keskül Fukara": "keskul", "Kemalpaşa Tatlısı": "kemalpasa_tatlisi", "Kemalpaşa": "kemalpasa_tatlisi",
 "Balbadem": "balbadem", "Bal Badem": "balbadem", "Krem Karamel": "krem_karamel", "Krem Brüle": "krem_brule",
 "Ağlayan Pasta": "aglayan_pasta", "Tulumba": "tulumba", "Osmanlı Tulumba Tatlısı": "tulumba",
 "Kabaklı Magnolya": "kabakli_magnolya", "Magnolya": "magnolya", "Magnolia": "magnolya", "Aşure": "asure", "Kardelen Pasta": "kardelen_pasta",
 "Tahinli Cevizli Kabak Tatlısı": "kabak_tatlisi", "Bademli Muhallebi": "bademli_muhallebi", "Dondurma": "dondurma",
 "Ejder Tatlısı": "ejder_tatlisi", "Fındıklı Gullaç": "findikli_gullac", "Hanım Göbeği": "hanim_gobegi",
 "Elmalı Tart": "elmali_tart", "Hurma Tatlısı": "hurma_tatlisi", "Kekli Supangle": "kekli_supangle", "Supangle": "supangle",
 "Naz Tatlısı": "naz_tatlisi", "Kuru Meyveli Muhallebi": "kuru_meyveli_muhallebi", "Muzlu Muhallebi": "muzlu_muhallebi",
 "Sakızlı Muhallebi": "muhallebi", "Peynir Tatlısı": "peynir_tatlisi", "Tahinli Cevizli Peynir Tatlısı": "tahinli_cevizli_peynir_tatlisi",
 "Kestaneli Sütte": "kestaneli_sutte", "Latte Pasta": "latte_pasta", "Tahinli Cevizli Bakla Tatlısı": "bakla_tatlisi",
 "Süt Dilimi": "sut_dilimi", "Ispanaklı Pasta": "ispanakli_pasta", "Sütlü İrmik Tatlısı": "sutlu_irmik_tatlisi",
 "Malaga": "malaga", "Çikolata Soslu Churros": "cikolata_soslu_churros", "Akdeniz Gülü": "akdeniz_gulu",
 "Vişneli Pasta": "visneli_pasta", "Yoğurt Tatlısı": "yogurt_tatlisi", "Soğuk Kadayıf": "soguk_kadayif",
}
for k, v in TATLI.items():
    ALIAS[("tatli", k)] = v
ALIAS.update({
 ("yogurt", "Yoğurt"): "yogurt", ("yogurt", "Süt"): "sut",
 ("salata", "Salata / Zeytinyağlı"): "salata_zeytinyagli", ("salata", "Mevsim Yeşillikleri"): "mevsim_yesillik",
 ("kahvaltilik", "Çeri Domates"): "ceri_domates", ("kahvaltilik", "Salatalık"): "salatalik_dilim",
 ("kahvaltilik", "Zeytin"): "zeytin_kahvalti", ("kahvaltilik", "Tereyağı"): "tereyagi_kahvalti",
 ("kahvaltilik", "Beyaz Peynir"): "beyaz_peynir_kahvalti", ("kahvaltilik", "Kaşar Peynir"): "kasar_kahvalti",
 ("kahvaltilik", "Kaşar Peyniri"): "kasar_kahvalti", ("kahvaltilik", "Tahin Pekmez"): "tahin_pekmez",
 ("hamur", "Simit"): "simit", ("hamur", "Poğaça"): "pogaca", ("hamur", "Açma"): "acma",
 ("hamur", "Peynirli Gül Böreği"): "peynirli_gul_boregi", ("hamur", "Sigara Böreği"): "sigara_boregi",
 ("hamur", "Kol Böreği"): "kol_boregi", ("hamur", "Zeytinli Açma"): "zeytinli_acma", ("hamur", "Kaşarlı Poğaça"): "kasarli_pogaca",
 ("diger", "Patates Kızartma"): "patates_kizartma", ("diger", "Sosis"): "sosis", ("diger", "Çay"): "", ("diger", "Şeker"): "",
})

def corba_key(raw):
    return re.sub(r"\s+Çorba(sı)?$", "", raw).strip()

def main():
    ing = {r["ingredient_id"]: r["name_tr"] for r in csv.DictReader(open(N / "ingredients.csv", encoding="utf-8"))}
    def trl(s): return s.replace("I", "ı").replace("İ", "i").lower()
    def short(i):
        return trl(re.split(r" \(| /", ing[i])[0])
    ids = [x[0] for x in D]; assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
    with open(N / "dishes_b.csv", "w", encoding="utf-8", newline="") as fd, open(N / "recipes_b.csv", "w", encoding="utf-8", newline="") as fr:
        wd = csv.writer(fd); wr = csv.writer(fr)
        wd.writerow(["dish_id", "name_tr", "category", "portion_desc", "desc"]); wr.writerow(["dish_id", "ingredient_id", "grams"])
        for i, name, cat, portion, rec in D:
            agg = {}
            for tok in rec.split():
                k, g = tok.split(":"); assert k in ing, (i, k); agg[k] = agg.get(k, 0) + float(g)
            for k, g in agg.items(): wr.writerow([i, k, f"{g:g}"])
            wd.writerow([i, name, cat, portion, ", ".join(short(k) for k in agg)])
    n = 0; missing = []
    with open(N / "aliases_b.csv", "w", encoding="utf-8", newline="") as fa:
        wa = csv.writer(fa); wa.writerow(["comp", "raw", "dish_ids"])
        for r in csv.DictReader(open(ROOT / "data" / "items_raw.csv", encoding="utf-8")):
            c, raw = r["comp"], r["raw"]
            if c not in OWN: continue
            key = (c, corba_key(raw)) if c == "corba" else (c, raw)
            if key not in ALIAS: missing.append(key); continue
            wa.writerow([c, raw, ALIAS[key]]); n += 1
    assert not missing, missing
    valid = set(ids)
    bad = [v for v in ALIAS.values() if v and v not in valid]
    assert not bad, bad
    print("dishes", len(D), "aliases", n)

if __name__ == "__main__":
    main()
