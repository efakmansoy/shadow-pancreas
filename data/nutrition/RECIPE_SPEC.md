# Tarif ayrıştırma şartnamesi

Amaç: yemekhane menüsündeki her yemek yazımını standart bir yemeğe bağlamak ve her standart yemek için
**bir servis porsiyonunun** malzeme gramajını yazmak. Besin değerleri `data/nutrition/ingredients.csv` (USDA SR Legacy, 100 g başına)
üzerinden hesaplanır. Bu, diyetisyenlerin kullandığı standart tarif ayrıştırma (recipe decomposition) yöntemidir.

## Girdi
- `data/items_raw.csv` — sütunlar `comp,raw,n` (bileşen, menüde görünen yazım, kaç kez geçtiği). Bileşenler:
  corba, ana, pilav, yogurt, salata, tatli, kahvaltilik, hamur, diger.
- `data/nutrition/ingredients.csv` — kullanılabilecek TEK malzeme listesi (`ingredient_id`). Yeni malzeme UYDURMA; en yakın olanı kullan.

## Çıktı (her ajan kendi dosya önekine yazar: `<onek>` = sana verilen önek)
1. `data/nutrition/dishes_<onek>.csv` — `dish_id,name_tr,category,portion_desc,desc`
   - `dish_id`: küçük harf ascii snake_case, benzersiz (ör. `mercimek_corba`, `rosto_kofte`).
   - `category`: şunlardan biri: `corba, et_yemegi, tavuk_yemegi, balik, kofte, sebze_yemegi, baklagil, patates_garnitur,
     ekmek_hamur, pilav, makarna, borek, serbetli_tatli, sutlu_tatli, pasta_kek, meyve, kahvaltilik, kahvalti_yumurta,
     icecek, sos, salata, sut_urunu, tatlandirici`.
   - `portion_desc`: Türkçe kısa porsiyon tanımı (ör. "1 kase, 250 ml", "1 porsiyon, ~120 g çiğ et").
   - `desc`: malzeme açıklaması, Türkçe, tek satır, virgüllerle ("kırmızı mercimek, soğan, havuç, tereyağı, un"). Embedding için kullanılacak.
2. `data/nutrition/recipes_<onek>.csv` — `dish_id,ingredient_id,grams`
   - grams = bir servis porsiyonundaki malzemenin **çiğ/kullanıldığı haldeki** ağırlığı (pirinç çiğ, makarna kuru, et çiğ, mercimek kuru).
     Su yazılmaz. Tuz/baharat yazılmaz.
3. `data/nutrition/aliases_<onek>.csv` — `comp,raw,dish_ids`
   - `items_raw.csv`'deki SANA AİT bileşenlerin **her satırı** için bir satır (eksiksiz). `dish_ids` `|` ile ayrılmış bir veya birden fazla dish_id.
     Örnekler: `Püreli Rosto Köfte` → `rosto_kofte|patates_pure`; `Kaşarlı Domates Çorbası` → `kasarli_domates_corba`;
     `Patates Garnitürlü Dana Et Sote` → `dana_et_sote|kup_patates`.
   - Yazım farkları, ek farkları ("Çorba"/"Çorbası", "Kebap"/"Kebabı", "Stroganof"/"Stroganoff", "Tremisu"/"Tiramisu") aynı dish_id'ye gider.
   - Gerçekten farklı tarifler ayrı dish_id alır (Kaşarlı Domates Çorba ≠ Domates Çorba değil; ikisi tek dish olabilir, kaşar az fark eder —
     karar senin, ama besin farkı < %10 ise birleştir).
   - Besin etkisi olmayan etiket kalemleri için `dish_ids` boş bırakılır (ör. kahvaltıdaki `Yumurta` kalemi yalnızca "yumurta yemeği" başlığıdır,
     her kahvaltıda Omlet veya Menemen ile birlikte gelir → boş; `Çay` → boş).

## Porsiyon kuralları (toplu beslenme / TÜBER porsiyon ölçüleriyle uyumlu, yetişkin gençler)
- Çorba: 1 kase ~250 ml. Mercimek çorbası ~30–35 g kuru mercimek; un/tereyağı/sebze ile. Kremalı çorbalarda ~20 ml krema, ~10 g un.
- Ana yemek et/tavuk: ~100–120 g çiğ et/tavuk; köfte ~100 g kıyma + ~10 g galeta/ekmek.
- Sebze yemeği (etli/etsiz): ~200 g sebze, etliyse ~40–50 g et, ~10–15 g yağ.
- Baklagil (kuru fasulye, nohut): ~60 g kuru tane.
- Pilav: ~65 g çiğ pirinç veya bulgur + ~8 g yağ/tereyağı. Şehriyeli pirinç: 55 g pirinç + 10 g şehriye.
- Makarna: ~80 g kuru makarna + sos.
- Patates garnitür (püre, kızartma, elma dilim): ~120 g çiğ patates (+ yağ / süt / tereyağı); patates kızartması hazır ise `patates_kizartma` ~100 g.
- Pide/lavaş garnitür: ~50 g `ekmek`.
- Hamur işi (simit ~90 g, poğaça ~70 g, açma ~70 g, börek ~100 g): un/yağ/süt/yumurta/peynir olarak ayrıştır, ya da yufka kullan.
- Şerbetli tatlılar (baklava 3–4 dilim ~80 g, revani ~100 g, şekerpare 2 adet ~80 g, kadayıf ~90 g): yufka/un/irmik + yağ + şeker (şerbet şekeri dahil, ~30–40 g şeker) + ceviz/fıstık.
- Sütlü tatlılar (sütlaç, muhallebi, kazandibi, tavuk göğsü, keşkül): ~150 g; ~120 ml süt, ~20–25 g şeker, ~10–15 g pirinç unu/nişasta/pirinç.
- Pasta/kek/magnolya/tiramisu: ~100 g; kek/bisküvi + krema + şeker.
- Meyve: 150 g `meyve`. Yoğurt: 150 g `yogurt`. Süt: 200 g `sut`.
- Salata / Zeytinyağlı (her öğle/akşamda var): küçük salata (~80 g yeşillik/domates/salatalık + 5 g zeytinyağı) + küçük zeytinyağlı sebze (~80 g sebze + 8 g zeytinyağı + 5 g pirinç).
- Kahvaltılık: beyaz peynir 30 g, kaşar 30 g, zeytin 25 g, çeri domates 50 g, salatalık 50 g, tereyağı 10 g,
  tahin-pekmez 15 g tahin + 20 g pekmez, bal 20 g, reçel 20 g, mevsim yeşillikleri 30 g.
- Omlet: 2 yumurta + 5 g yağ (+ peynir varsa). Menemen: 2 yumurta + 100 g domates + 40 g biber + 8 g yağ.
- Diğer (her kahvaltıda): `Patates Kızartma` → 80 g `patates_kizartma`; `Sosis` → 50 g `sosis`; `Çay` → boş; `Şeker` → boş
  (Tip 1 diyabetli kişi çaya şeker eklemiyor varsayımı).

## Kontrol
- Yazdıktan sonra `python src/check_recipes.py <onek>` çalıştır. Her yemeğin porsiyon karbonhidratını, proteinini, yağını ve kcal'ini yazdırır;
  aliases kapsamasını (items_raw'daki her satır var mı) ve bilinmeyen ingredient_id/dish_id kontrollerini yapar.
- Karbonhidratları Türk karbonhidrat sayımı değişim listeleriyle karşılaştır, bariz sapma varsa düzelt
  (yaklaşık referans: 1 kase mercimek çorbası ~20 g; 1 porsiyon pirinç pilavı ~50 g; 1 porsiyon makarna ~60 g;
  4 dilim baklava ~50–60 g; 1 simit ~55 g; 1 meyve ~20 g; 150 g yoğurt ~7 g; 1 porsiyon kuru fasulye ~35 g).
