"""Sentetik yemek veri seti — YALNIZCA embedding karşılaştırması için.

Besin değerleri standart porsiyon başına YAKLAŞIK değerlerdir (genel beslenme
bilgisine dayalı elle girildi). Asıl sistemde kullanılmayacak; asıl değerler
TürKomp + USDA FoodData Central üzerinden tarif ayrıştırma ile hesaplanacak.

Alanlar: ad, kategori, karbonhidrat(g), protein(g), yağ(g), lif(g), GI sınıfı (D/O/Y),
kısa malzeme açıklaması, eş adlar (menülerde görülen yazımlar).
"""
import random
import re

# (ad, kategori, carb, prot, yag, lif, gi, aciklama, [es_adlar])
DISHES = [
    # --- ekmek / hamur işi ---
    ("Beyaz Ekmek", "ekmek_hamur", 25, 4, 1, 1.4, "Y", "buğday unu, maya, tuz; 2 dilim", ["Ekmek", "Francala", "Somun Ekmek"]),
    ("Tam Buğday Ekmeği", "ekmek_hamur", 21, 4.5, 1.5, 3.5, "O", "tam buğday unu, kepek, maya", ["Kepekli Ekmek", "Tam Buğday Ekmek"]),
    ("Bazlama", "ekmek_hamur", 30, 5, 1.5, 1.5, "Y", "buğday unu, yoğurt, maya; sacda pişmiş yassı ekmek", ["Köy Bazlaması", "Bazlama Ekmeği"]),
    ("Lavaş", "ekmek_hamur", 27, 4.5, 1, 1.2, "Y", "buğday unu, su, tuz; ince yassı ekmek", ["Lavaş Ekmeği", "Tandır Lavaş"]),
    ("Pide Ekmeği", "ekmek_hamur", 31, 5, 1.5, 1.4, "Y", "buğday unu, maya, çörek otu, susam", ["Ramazan Pidesi", "Pide"]),
    ("Simit", "ekmek_hamur", 55, 10, 6, 2.5, "Y", "buğday unu, pekmez, susam", ["Susamlı Simit", "Gevrek"]),
    ("Poğaça", "ekmek_hamur", 30, 5, 12, 1, "Y", "un, tereyağı, yoğurt, peynir", ["Peynirli Poğaça", "Sade Poğaça"]),
    ("Açma", "ekmek_hamur", 32, 5, 14, 1, "Y", "un, margarin, süt, maya", ["Sade Açma", "Zeytinli Açma"]),
    ("Kol Böreği", "ekmek_hamur", 28, 8, 15, 1, "O", "yufka, beyaz peynir, yağ", ["Peynirli Kol Böreği", "Kol Böreği (Peynirli)"]),
    ("Sigara Böreği", "ekmek_hamur", 18, 6, 14, 0.7, "O", "yufka, beyaz peynir, maydanoz; kızartma", ["Peynirli Sigara Böreği", "Sigara Börek"]),
    ("Su Böreği", "ekmek_hamur", 30, 12, 16, 1, "O", "haşlanmış yufka, peynir, tereyağı", ["Peynirli Su Böreği"]),
    ("Gül Böreği", "ekmek_hamur", 27, 8, 15, 1, "O", "yufka, peynir veya ıspanak", ["Peynirli Gül Böreği", "Ispanaklı Gül Böreği"]),
    ("Kaşarlı Tost", "ekmek_hamur", 30, 14, 13, 1.5, "Y", "tost ekmeği, kaşar peyniri", ["Tost", "Karışık Tost"]),
    ("Gözleme", "ekmek_hamur", 45, 12, 14, 2, "Y", "yufka, peynir veya patates; sacda", ["Peynirli Gözleme", "Patatesli Gözleme"]),
    # --- kahvaltılık ---
    ("Beyaz Peynir", "kahvaltilik", 0.5, 5, 6, 0, "D", "inek sütü peyniri; 30 g", ["Peynir", "Ezine Peyniri"]),
    ("Kaşar Peyniri", "kahvaltilik", 0.5, 8, 9, 0, "D", "olgunlaştırılmış kaşar; 30 g", ["Kaşar", "Taze Kaşar"]),
    ("Zeytin", "kahvaltilik", 1.5, 0.4, 6, 1.3, "D", "siyah veya yeşil zeytin; 10 adet", ["Siyah Zeytin", "Yeşil Zeytin"]),
    ("Haşlanmış Yumurta", "kahvaltilik", 0.6, 6.5, 5, 0, "D", "1 adet haşlanmış yumurta", ["Yumurta", "Haşlama Yumurta"]),
    ("Omlet", "kahvaltilik", 1.5, 13, 15, 0, "D", "2 yumurta, tereyağı", ["Yumurta, Omlet", "Sade Omlet"]),
    ("Menemen", "kahvaltilik", 7, 13, 17, 2, "D", "yumurta, domates, biber, zeytinyağı", ["Yumurta, Menemen", "Domatesli Yumurta"]),
    ("Bal", "kahvaltilik", 16, 0, 0, 0, "Y", "süzme çiçek balı; 1 yemek kaşığı", ["Süzme Bal", "Çiçek Balı"]),
    ("Reçel", "kahvaltilik", 13, 0, 0, 0.2, "Y", "meyve ve şeker; 1 yemek kaşığı", ["Vişne Reçeli", "Çilek Reçeli"]),
    ("Tahin Pekmez", "kahvaltilik", 15, 3, 8, 1, "O", "susam ezmesi ve üzüm pekmezi", ["Tahin-Pekmez", "Tahinli Pekmez"]),
    ("Tereyağı", "kahvaltilik", 0, 0, 8, 0, "D", "10 g tereyağı", ["Tereyağ"]),
    ("Sosis", "kahvaltilik", 2, 6, 12, 0, "D", "piliç veya dana sosis; 2 adet", ["Sosis Kızartma", "Piliç Sosis"]),
    ("Patates Kızartması", "kahvaltilik", 35, 3.5, 15, 3, "Y", "kızartılmış patates; 100 g", ["Patates Kızartma", "Parmak Patates", "Elma Dilim Patates"]),
    ("Domates Salatalık", "kahvaltilik", 4, 1, 0.2, 1.3, "D", "çeri domates ve salatalık dilimleri", ["Çeri Domates", "Salatalık Domates"]),
    ("Fındık Ezmesi", "kahvaltilik", 11, 1.5, 6, 1, "O", "kakaolu fındık kreması; 20 g", ["Kakaolu Fındık Kreması", "Çikolata Kreması"]),
    # --- çorba (1 kase) ---
    ("Mercimek Çorbası", "corba", 20, 8, 5, 4, "O", "kırmızı mercimek, soğan, havuç, un", ["Ev Usulü Mercimek Çorba", "Mercimek Çorba", "Süzme Mercimek Çorbası"]),
    ("Ezogelin Çorbası", "corba", 22, 7, 5, 4, "O", "kırmızı mercimek, bulgur, pirinç, nane", ["Ezogelin Çorba", "Ezo Gelin Çorbası"]),
    ("Tarhana Çorbası", "corba", 18, 5, 5, 1.5, "O", "tarhana (un, yoğurt, sebze), salça", ["Tarhana Çorba", "Ev Tarhanası"]),
    ("Yayla Çorbası", "corba", 14, 6, 6, 0.5, "O", "yoğurt, pirinç, yumurta, nane", ["Yayla Çorba", "Yoğurtlu Pirinç Çorbası"]),
    ("Domates Çorbası", "corba", 14, 3, 6, 1.5, "O", "domates, un, süt, rendelenmiş kaşar", ["Kaşarlı Domates Çorbası", "Domates Çorba (Kaşarlı)"]),
    ("Şehriye Çorbası", "corba", 16, 4, 4, 1, "Y", "tel şehriye, domates, tavuk suyu", ["Domatesli Şehriye Çorba", "Tel Şehriye Çorbası"]),
    ("Mantar Çorbası", "corba", 10, 3, 8, 1, "D", "mantar, krema, un", ["Kremalı Mantar Çorbası"]),
    ("Sebze Çorbası", "corba", 12, 3, 5, 3, "D", "havuç, kabak, patates, bezelye", ["Kremalı Taneli Sebze Çorbası", "Taze Sebze Çorbası"]),
    ("Tavuk Suyu Çorbası", "corba", 10, 8, 4, 0.5, "O", "tavuk suyu, tavuk eti, şehriye, limon", ["Tavuk Çorbası", "Terbiyeli Tavuk Suyu Çorba"]),
    ("Düğün Çorbası", "corba", 8, 8, 7, 0.3, "D", "kuzu eti suyu, yoğurt, yumurta terbiyesi", ["Düğün Çorba"]),
    ("Acem Çorbası", "corba", 12, 6, 6, 1.5, "O", "et suyu, pirinç, nohut, havuç", ["Acem Çorba"]),
    ("İşkembe Çorbası", "corba", 6, 10, 8, 0, "D", "işkembe, sarımsak, sirke", ["İşkembe Çorba"]),
    ("Brokoli Çorbası", "corba", 10, 4, 7, 3, "D", "brokoli, krema, patates", ["Kremalı Brokoli Çorbası"]),
    ("Naneli Yoğurt Çorbası", "corba", 13, 6, 6, 0.5, "O", "yoğurt, buğday, nane", ["Yoğurt Çorbası", "Naneli Yoğurt Çorba"]),
    # --- et ana yemek ---
    ("Izgara Köfte", "et_ana", 6, 22, 18, 0.5, "D", "kıyma, ekmek içi, soğan; ızgara", ["Köfte", "Kasap Köfte", "Izgara Köfte (Piyazlı)"]),
    ("Sahan Köfte", "et_ana", 10, 20, 18, 1.5, "D", "kıyma, domates sos, biber", ["Sahanda Köfte"]),
    ("İzmir Köfte", "et_ana", 20, 18, 18, 3, "O", "kıyma, patates, domates, biber; fırında", ["İzmir Köfte (Patatesli)", "Fırında Patatesli Köfte"]),
    ("Dana Rosto", "et_ana", 4, 25, 12, 0.5, "D", "dana eti, sebze sosu", ["Rosto Dana", "Dana Fleminyon"]),
    ("Tas Kebabı", "et_ana", 10, 22, 14, 2, "D", "kuşbaşı dana, soğan, salça", ["Tas Kebap", "Tas Kebap (Püreli)"]),
    ("Et Sote", "et_ana", 6, 22, 13, 1.5, "D", "kuşbaşı et, biber, domates", ["Dana Sote", "Etli Sote"]),
    ("Hünkar Beğendi", "et_ana", 20, 22, 22, 2, "O", "kuzu yahni, patlıcanlı beşamel", ["Hünkar Beğendili Kebap"]),
    ("Karnıyarık", "et_ana", 14, 12, 20, 5, "D", "patlıcan, kıyma, domates", ["Karnı Yarık"]),
    ("Musakka", "et_ana", 15, 12, 18, 5, "D", "patlıcan, kıyma, domates", ["Patlıcan Musakka", "Karışık Musakka"]),
    ("Hamburger", "et_ana", 35, 20, 18, 2, "Y", "hamburger ekmeği, köfte, sos", ["Burger", "Hamburger Menü"]),
    ("Lahmacun", "et_ana", 40, 14, 10, 3, "Y", "ince hamur, kıyma, soğan, biber", ["Fındık Lahmacun"]),
    ("Mantı", "et_ana", 50, 15, 15, 2, "O", "hamur, kıyma, yoğurt, tereyağı", ["Kayseri Mantısı", "Yoğurtlu Mantı"]),
    ("Pizza", "et_ana", 55, 18, 18, 3, "Y", "hamur, domates sos, mozzarella, sucuk", ["Karışık Pizza", "Margarita Pizza"]),
    # --- tavuk ana yemek ---
    ("Tavuk Sote", "tavuk_ana", 8, 25, 10, 1.5, "D", "tavuk göğsü, biber, domates, mantar", ["Piliç Sote", "Sebzeli Piliç Sote"]),
    ("Izgara Tavuk", "tavuk_ana", 1, 30, 7, 0, "D", "ızgara tavuk göğsü", ["Piliç Izgara", "Tavuk Göğüs Izgara"]),
    ("Tavuk Şiş", "tavuk_ana", 3, 28, 9, 0.5, "D", "şişte tavuk, biber, soğan", ["Piliç Şiş", "Tavuk Şiş Kebap"]),
    ("Fırın Tavuk Baget", "tavuk_ana", 2, 26, 14, 0, "D", "fırında tavuk but", ["Fırında Tavuk But", "Piliç Baget"]),
    ("Tavuk Döner", "tavuk_ana", 3, 25, 12, 0.5, "D", "döner tavuk eti (ekmeksiz)", ["Piliç Döner"]),
    ("Tavuk Şinitzel", "tavuk_ana", 18, 24, 15, 1, "O", "galeta unlu pane tavuk; kızartma", ["Tavuk Schnitzel", "Pane Tavuk"]),
    ("Çıtır Tavuk", "tavuk_ana", 20, 18, 16, 1, "Y", "panelenmiş tavuk parçaları; kızartma", ["Tavuk Nugget", "Çıtır Piliç"]),
    # --- sebze ana yemek ---
    ("Taze Fasulye", "sebze_ana", 10, 2, 8, 4, "D", "yeşil fasulye, domates, zeytinyağı", ["Zeytinyağlı Taze Fasulye", "Etli Taze Fasulye"]),
    ("Ispanak Yemeği", "sebze_ana", 7, 4, 6, 3.5, "D", "ıspanak, soğan, pirinç", ["Ispanak", "Yoğurtlu Ispanak"]),
    ("Türlü", "sebze_ana", 12, 3, 8, 4.5, "D", "patlıcan, kabak, biber, fasulye, domates", ["Sebze Türlü", "Etli Türlü"]),
    ("Kabak Yemeği", "sebze_ana", 8, 2, 6, 2, "D", "kabak, soğan, pirinç", ["Zeytinyağlı Kabak"]),
    ("Patates Yemeği", "sebze_ana", 25, 4, 7, 3, "Y", "patates, soğan, salça", ["Etli Patates", "Patates Oturtma"]),
    ("Patates Püresi", "sebze_ana", 22, 3, 6, 2, "Y", "haşlanmış patates, süt, tereyağı", ["Püre", "Tereyağlı Püre"]),
    ("Bezelye Yemeği", "sebze_ana", 15, 6, 6, 5, "D", "bezelye, havuç, patates", ["Etli Bezelye"]),
    ("Yaprak Sarma", "sebze_ana", 30, 3, 10, 3, "O", "asma yaprağı, pirinç, zeytinyağı", ["Zeytinyağlı Yaprak Sarma", "Sarma"]),
    ("Biber Dolması", "sebze_ana", 20, 8, 10, 3, "O", "dolmalık biber, pirinç, kıyma", ["Etli Biber Dolma", "Dolma"]),
    ("Mücver", "sebze_ana", 12, 6, 12, 2, "O", "kabak, yumurta, un, dereotu", ["Kabak Mücver"]),
    # --- baklagil ---
    ("Kuru Fasulye", "baklagil", 25, 10, 7, 9, "D", "kuru beyaz fasulye, salça, et", ["Etli Kuru Fasulye", "Kuru Fasulye Yemeği"]),
    ("Nohut Yemeği", "baklagil", 27, 10, 8, 8, "D", "nohut, salça, et", ["Nohut Yahni", "Etli Nohut"]),
    ("Barbunya", "baklagil", 22, 8, 7, 8, "D", "barbunya fasulyesi, havuç, zeytinyağı", ["Zeytinyağlı Barbunya", "Barbunya Pilaki"]),
    ("Yeşil Mercimek Yemeği", "baklagil", 25, 11, 6, 8, "D", "yeşil mercimek, bulgur, soğan", ["Mercimek Yemeği", "Bulgurlu Yeşil Mercimek"]),
    ("Mercimek Köftesi", "baklagil", 30, 8, 5, 6, "O", "kırmızı mercimek, ince bulgur, yeşillik", ["Mercimek Köfte"]),
    # --- pilav / makarna ---
    ("Pirinç Pilavı", "pilav_makarna", 45, 4, 7, 0.5, "Y", "pirinç, tereyağı, tavuk suyu", ["Pilav", "Tereyağlı Pirinç Pilavı", "Şehriyeli Pirinç Pilavı"]),
    ("Bulgur Pilavı", "pilav_makarna", 35, 5, 5, 6, "O", "pilavlık bulgur, salça, soğan", ["Salçalı Bulgur Pilavı", "Zerdeçallı Bulgur Pilavı", "Domatesli Bulgur Pilavı"]),
    ("Şehriye Pilavı", "pilav_makarna", 40, 6, 6, 1.5, "Y", "arpa şehriye, tereyağı", ["Arpa Şehriye Pilavı", "Tel Şehriye Pilavı"]),
    ("Kuskus Pilavı", "pilav_makarna", 38, 6, 5, 2, "O", "kuskus, tereyağı, sebze", ["Kuskus", "Sebzeli Kuskus"]),
    ("Meyhane Pilavı", "pilav_makarna", 33, 5, 6, 6, "O", "bulgur, domates, biber, soğan", ["Meyane Pilavı"]),
    ("Domates Soslu Makarna", "pilav_makarna", 45, 8, 6, 2.5, "O", "makarna, domates sos", ["Spagetti (Napoliten)", "Penne Arabiata", "Makarna"]),
    ("Kremalı Makarna", "pilav_makarna", 45, 10, 15, 2, "O", "makarna, krema, mantar, parmesan", ["Spagetti Carbonara", "Fettucini Alfredo", "Mantarlı Fettucini"]),
    ("Erişte", "pilav_makarna", 42, 8, 6, 2, "O", "ev yapımı yumurtalı erişte, peynir", ["Peynirli Erişte", "Ev Eriştesi"]),
    ("Fırın Makarna", "pilav_makarna", 40, 14, 14, 2, "O", "makarna, beşamel, kaşar", ["Beşamel Soslu Fırın Makarna"]),
    # --- şerbetli tatlı ---
    ("Baklava", "tatli_serbetli", 50, 5, 20, 1.5, "Y", "yufka, ceviz/fıstık, tereyağı, şerbet", ["Fıstıklı Baklava", "Cevizli Baklava", "Şöbiyet"]),
    ("Şekerpare", "tatli_serbetli", 55, 4, 15, 0.5, "Y", "irmik, un, tereyağı, şerbet", ["Kakaolu Şekerpare"]),
    ("Revani", "tatli_serbetli", 50, 4, 10, 0.5, "Y", "irmik, yumurta, şerbet", ["Portakallı Revani"]),
    ("Tel Kadayıf", "tatli_serbetli", 55, 5, 18, 1.5, "Y", "tel kadayıf, ceviz, tereyağı, şerbet", ["Burma Kadayıf", "Kadayıf"]),
    ("Ekmek Kadayıfı", "tatli_serbetli", 60, 4, 15, 0.5, "Y", "kadayıf ekmeği, şerbet, kaymak", ["Kaymaklı Ekmek Kadayıfı"]),
    ("Tulumba Tatlısı", "tatli_serbetli", 45, 2, 15, 0.3, "Y", "hamur kızartması, şerbet", ["Tulumba"]),
    ("Şam Tatlısı", "tatli_serbetli", 50, 4, 14, 0.5, "Y", "irmikli hamur, şerbet, fındık", ["Şam Tatlı"]),
    ("İrmik Helvası", "tatli_serbetli", 40, 4, 14, 1, "Y", "irmik, tereyağı, süt, şeker", ["Helva", "İrmik Helva"]),
    # --- sütlü tatlı / pasta ---
    ("Sütlaç", "tatli_sutlu", 35, 6, 5, 0.2, "O", "süt, pirinç, şeker; fırında", ["Fırın Sütlaç", "Sütlaç (Fırında)"]),
    ("Kazandibi", "tatli_sutlu", 35, 5, 5, 0, "O", "süt, nişasta, şeker; karamelize", ["Kazan Dibi"]),
    ("Tavuk Göğsü Tatlısı", "tatli_sutlu", 33, 6, 5, 0, "O", "süt, tavuk göğsü lifi, şeker, nişasta", ["Tavuk Göğsü", "Tavukgöğsü"]),
    ("Muhallebi", "tatli_sutlu", 30, 5, 5, 0, "O", "süt, pirinç unu, şeker", ["Sakızlı Muhallebi"]),
    ("Profiterol", "tatli_sutlu", 35, 5, 15, 0.5, "Y", "choux hamuru, krema, çikolata sos", ["Profiterol Tatlısı"]),
    ("Puding", "tatli_sutlu", 32, 5, 5, 1, "O", "süt, kakao, nişasta, şeker", ["Kakaolu Puding", "Supangle"]),
    ("Magnolya", "tatli_sutlu", 35, 5, 15, 0.5, "O", "bisküvi, krema, muhallebi, meyve", ["Çilekli Magnolya"]),
    ("Trileçe", "tatli_sutlu", 40, 7, 12, 0, "Y", "pandispanya, üç çeşit süt, karamel", ["Trileçe Tatlısı"]),
    ("Tiramisu", "tatli_sutlu", 30, 6, 18, 0.5, "O", "kedi dili, mascarpone, kahve", ["Tremisu"]),
    ("Aşure", "tatli_sutlu", 45, 5, 4, 4, "O", "buğday, nohut, fasulye, kuru meyve, şeker", ["Aşure Tatlısı"]),
    ("Kek", "tatli_sutlu", 35, 4, 12, 0.5, "Y", "un, şeker, yumurta, yağ", ["Kakaolu Kek", "Havuçlu Kek"]),
    ("Yaş Pasta", "tatli_sutlu", 40, 5, 18, 0.5, "Y", "pandispanya, krema, meyve", ["Pasta", "Kardelen Pasta"]),
    # --- meyve ---
    ("Elma", "meyve", 20, 0.3, 0.3, 3.5, "D", "1 orta boy elma", ["Kırmızı Elma", "Yeşil Elma"]),
    ("Portakal", "meyve", 15, 1, 0.2, 3, "D", "1 orta boy portakal", ["Washington Portakal"]),
    ("Muz", "meyve", 27, 1.3, 0.4, 3, "O", "1 orta boy muz", ["Sarı Muz"]),
    ("Mandalina", "meyve", 18, 1.2, 0.3, 3, "D", "2 adet mandalina", ["Satsuma Mandalina"]),
    ("Üzüm", "meyve", 27, 1, 0.3, 1.4, "O", "1 su bardağı üzüm", ["Çekirdeksiz Üzüm"]),
    ("Karpuz", "meyve", 19, 1.5, 0.4, 1, "Y", "1 dilim karpuz", ["Karpuz Dilimi"]),
    ("Mevsim Meyvesi", "meyve", 18, 0.8, 0.3, 2.5, "D", "mevsimine göre tek porsiyon meyve", ["Meyve", "Meyve Tabağı"]),
    # --- süt ürünü ---
    ("Yoğurt", "sut_urun", 9, 7, 6, 0, "D", "200 g tam yağlı yoğurt", ["Ev Yoğurdu", "Kase Yoğurt"]),
    ("Ayran", "sut_urun", 6, 4, 3, 0, "D", "yoğurt, su, tuz; 200 ml", ["Yayık Ayranı"]),
    ("Süt", "sut_urun", 10, 6.5, 6, 0, "D", "200 ml tam yağlı süt", ["Sade Süt", "Günlük Süt"]),
    ("Cacık", "sut_urun", 6, 4, 4, 0.5, "D", "yoğurt, salatalık, sarımsak, nane", ["Cacık (Salatalıklı)"]),
    ("Kakaolu Süt", "sut_urun", 24, 6, 5, 1, "O", "süt, kakao, şeker; 200 ml", ["Çikolatalı Süt"]),
    # --- salata ---
    ("Mevsim Salata", "salata", 6, 1.5, 5, 2.5, "D", "marul, domates, salatalık, zeytinyağı", ["Salata", "Mevsim Yeşillikleri", "Çoban Salata"]),
    ("Piyaz", "salata", 20, 7, 8, 6, "D", "kuru fasulye, soğan, maydanoz, yumurta", ["Fasulye Piyazı"]),
    ("Patates Salatası", "salata", 25, 3, 7, 3, "Y", "haşlanmış patates, soğan, maydanoz", ["Patates Salata"]),
    ("Kısır", "salata", 30, 5, 7, 5, "O", "ince bulgur, salça, yeşillik", ["Bulgur Kısırı"]),
    ("Rus Salatası", "salata", 15, 3, 20, 2, "O", "patates, havuç, bezelye, mayonez", ["Amerikan Salatası"]),
    # --- içecek / ek ---
    ("Çay", "icecek", 0, 0, 0, 0, "D", "şekersiz demlik çay", ["Demleme Çay", "Siyah Çay"]),
    ("Şeker", "icecek", 10, 0, 0, 0, "Y", "2 küp kesme şeker", ["Kesme Şeker", "Toz Şeker"]),
    ("Meyve Suyu", "icecek", 22, 0.5, 0, 0.3, "Y", "200 ml paket meyve suyu", ["Portakal Suyu", "Vişne Suyu"]),
    ("Kola", "icecek", 26, 0, 0, 0, "Y", "250 ml şekerli gazlı içecek", ["Gazlı İçecek"]),
]

# Elle işaretlenmiş zor çiftler.
# label=1: kelime olarak benzemiyor ama besin değeri yakın  (modelin YAKIN bulması istenir)
# label=0: kelime olarak benziyor ama besin değeri farklı (modelin UZAK bulması istenir)
HARD_PAIRS = [
    ("Beyaz Ekmek", "Bazlama", 1), ("Beyaz Ekmek", "Lavaş", 1), ("Bazlama", "Pide Ekmeği", 1),
    ("Pirinç Pilavı", "Şehriye Pilavı", 1), ("Bulgur Pilavı", "Kuskus Pilavı", 1),
    ("Mercimek Çorbası", "Ezogelin Çorbası", 1), ("Baklava", "Tel Kadayıf", 1),
    ("Sütlaç", "Kazandibi", 1), ("Muhallebi", "Kazandibi", 1), ("Sütlaç", "Tavuk Göğsü Tatlısı", 1),
    ("Kuru Fasulye", "Nohut Yemeği", 1), ("Barbunya", "Kuru Fasulye", 1), ("Elma", "Portakal", 1),
    ("Yoğurt", "Ayran", 1), ("Omlet", "Haşlanmış Yumurta", 1), ("Beyaz Peynir", "Kaşar Peyniri", 1),
    ("Bal", "Reçel", 1), ("Izgara Tavuk", "Tavuk Şiş", 1), ("Erişte", "Domates Soslu Makarna", 1),
    ("Revani", "Şekerpare", 1), ("Meyve Suyu", "Kola", 1), ("Simit", "Gözleme", 1),
    ("Beyaz Ekmek", "Ekmek Kadayıfı", 0), ("Tavuk Göğsü Tatlısı", "Izgara Tavuk", 0),
    ("Kuru Fasulye", "Taze Fasulye", 0), ("Sütlaç", "Süt", 0), ("Patates Salatası", "Mevsim Salata", 0),
    ("Şehriye Çorbası", "Şehriye Pilavı", 0), ("Mercimek Köftesi", "Izgara Köfte", 0),
    ("Domates Çorbası", "Domates Salatalık", 0), ("Kakaolu Süt", "Süt", 0),
    ("Tavuk Suyu Çorbası", "Izgara Tavuk", 0), ("Kaşarlı Tost", "Kaşar Peyniri", 0),
    ("Şeker", "Şekerpare", 0), ("Patates Kızartması", "Elma", 0), ("Naneli Yoğurt Çorbası", "Ayran", 0),
    ("Pide Ekmeği", "Lahmacun", 0), ("Mercimek Çorbası", "Mercimek Köftesi", 0),
]

TR_UP = str.maketrans("ıi", "Iİ")
TR_LO = str.maketrans("Iİ", "ıi")
ASCII = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
SUFFIX = [("Çorbası", "Çorba"), ("Pilavı", "Pilav"), ("Böreği", "Börek"), ("Tatlısı", "Tatlı"),
          ("Yemeği", "Yemek"), ("Kebabı", "Kebap"), ("Ekmeği", "Ekmek"), ("Köftesi", "Köfte"),
          ("Salatası", "Salata"), ("Helvası", "Helva")]
GARNISH = [" (Yoğurtlu)", " (Salata ile)", " (Ev Usulü)", " (Mevsim Sebzeli)", " (Porsiyon)"]


def tr_lower(s):
    return s.translate(TR_LO).lower()


def tr_upper(s):
    return s.translate(TR_UP).upper()


def toggle_suffix(s):
    for a, b in SUFFIX:
        if s.endswith(a):
            return s[: -len(a)] + b
        if s.endswith(b):
            return s[: -len(b)] + a
    return None


def typo(s, rng):
    letters = [i for i, c in enumerate(s) if c.isalpha() and 0 < i < len(s) - 1]
    if len(letters) < 3:
        return None
    i = rng.choice(letters)
    if rng.random() < 0.5:
        return s[:i] + s[i + 1:]
    if s[i + 1].isalpha():
        return s[:i] + s[i + 1] + s[i] + s[i + 2:]
    return s[:i] + s[i + 1:]


def build(seed=42):
    """Döndürür: dishes (list[dict]), queries (list[dict]), pairs (list[dict])."""
    rng = random.Random(seed)
    dishes = []
    for i, (name, cat, carb, prot, fat, fib, gi, desc, aliases) in enumerate(DISHES):
        dishes.append(dict(id=i, name=name, category=cat, carb=carb, protein=prot, fat=fat,
                           fiber=fib, gi=gi, desc=desc, aliases=aliases))
    names_norm = {tr_lower(d["name"]): d["id"] for d in dishes}

    queries = []

    def add(text, d, kind):
        key = tr_lower(text).strip()
        owner = names_norm.get(key)
        if owner is not None:  # birebir bir yemeğin adı ise (kendisi ya da başkası) sorgu olarak alma
            return
        queries.append(dict(query=text, target_id=d["id"], kind=kind))

    for d in dishes:
        for a in d["aliases"]:
            add(a, d, "es_ad")
        base = d["name"]
        add(base.translate(ASCII), d, "ascii")
        ts = toggle_suffix(base)
        if ts:
            add(ts, d, "ek_degisimi")
        t = typo(base, rng)
        if t:
            add(t, d, "yazim_hatasi")
        add(base + rng.choice(GARNISH), d, "garnitur")
        if d["aliases"]:
            a = rng.choice(d["aliases"])
            t2 = typo(a.translate(ASCII), rng)
            if t2:
                add(t2, d, "es_ad+ascii+hata")

    # aynı (sorgu, hedef) tekrarlarını temizle
    seen, uniq = set(), []
    for q in queries:
        k = (tr_lower(q["query"]), q["target_id"])
        if k not in seen:
            seen.add(k)
            uniq.append(q)

    by_name = {d["name"]: d["id"] for d in dishes}
    pairs = [dict(a=by_name[a], b=by_name[b], label=l) for a, b, l in HARD_PAIRS]
    return dishes, uniq, pairs


if __name__ == "__main__":
    d, q, p = build()
    import collections
    print(len(d), "yemek |", len(q), "sorgu |", len(p), "zor çift")
    print(collections.Counter(x["kind"] for x in q))
    print(collections.Counter(x["category"] for x in d))
