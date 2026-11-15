/* DiyaLife Menü Hafızası / Menu Memory — client (vanilla JS, offline, EN + TR) */
(function () {
  'use strict';

  // ================================================================ I18N
  // Every visible UI string lives here. {name} placeholders are filled by t().
  var I18N = {
    en: {
      doc_title: 'Shadow Pancreas',
      skip: 'Skip to content',
      brand_sub: 'Your Pancreas Has a Memory',
      lang_group: 'Language',
      tabs_label: 'Sections',
      tab_bugun: 'Today', tab_gecmis: 'History', tab_model: 'Model', tab_hakkinda: 'About',
      theme_to_light: 'Switch to light theme', theme_to_dark: 'Switch to dark theme',
      llm_loading: 'Checking status…', llm_on: 'Local LLM · {m}', llm_on_title: 'Local language model is running: {m}',
      llm_off: 'Local LLM off', llm_off_title: 'Local language model is not running; summaries come from a template.',
      server_down: 'Server not responding',

      bugun_h1: 'What happened the last times I ate a meal like this?',
      bugun_intro: 'Enter today’s menu and your pre-meal glucose. You’ll see your most similar past meals from your own log: how many units of insulin you injected and where your glucose was 2 hours later. These are past facts, not predictions, and no dose is ever suggested.',
      step1: 'Choose the meal', step2: 'Today’s menu', step3: 'Your reading',
      date: 'Date', meal: 'Meal', today_btn: 'Back to today', today_word: 'today',
      meal_kahvalti: 'Breakfast', meal_ogle: 'Lunch', meal_aksam: 'Dinner',
      meal_long_kahvalti: 'breakfast', meal_long_ogle: 'lunch', meal_long_aksam: 'dinner',
      meal_cap_kahvalti: 'Breakfast', meal_cap_ogle: 'Lunch', meal_cap_aksam: 'Dinner',
      aclik_label: 'Pre-meal glucose', aclik_ph: 'e.g. 110', aclik_hint: 'Reading right before the meal (20–600).',
      err_required: 'Enter your pre-meal glucose.', err_nan: 'Enter a number.', err_range: 'Value must be between 20 and 600 mg/dL.',
      show_btn: 'Show similar meals', showing: 'Searching…', need_menu: 'Save today’s menu first (step 2).',

      menu_title: 'Menu', menu_note: 'Tap a dish to see its recipe and USDA sources.',
      src_menu: 'Menu file', src_kullanici: 'Saved by you', edit: 'Edit',
      menu_failed: 'Could not load menu', retry: 'Try again',
      menu_none_title: 'No menu for this meal yet.', menu_none_text: 'Type what you are about to eat; pick each dish from the list.',
      menu_empty: 'Menu is empty', menu_empty_text: 'No dishes recorded for this meal.',
      on_menu: 'written as “{raw}”', no_match: 'No matching dish', component: 'Component',
      comp_carb_title: 'Total carbohydrate of this component', g_carb_short: '{v} g carbs',
      dish_aria: '{name}, {carb} grams of carbohydrate, {gi}. Show recipe',
      comp_corba: 'Soup', comp_ana: 'Main dish', comp_pilav: 'Rice / pasta', comp_yogurt: 'Yogurt / milk', comp_salata: 'Salad',
      comp_tatli: 'Dessert / fruit', comp_kahvaltilik: 'Breakfast plate', comp_hamur: 'Pastry', comp_diger: 'Other',
      gi_none: 'GI —', gi_none_title: 'Very little carbohydrate; GI not meaningful',
      gi_low: 'low', gi_mid: 'medium', gi_high: 'high', gi_prefix: 'GI {c}',
      gi_title: 'Glycemic index {v} ({c})',
      protein: 'Protein', fat: 'Fat', carbs: 'carbs', menu_total: 'Menu total',

      ed_comp: 'Component', ed_dish: 'Dish', ed_ph: 'Start typing a dish…', ed_add: 'Add dish', ed_remove: 'Remove this dish',
      ed_quick: 'Quick add', ed_save: 'Save menu', ed_saving: 'Saving…', ed_cancel: 'Cancel',
      ed_unknown: 'Not a known dish. Pick the closest:', ed_matching: 'Looking for matching dishes…', ed_nomatch: 'No match found; try another spelling.',
      ed_need_pick: 'Pick a dish from the list for every row (or remove the row).', ed_empty: 'Add at least one dish.',
      ed_saved: 'Menu saved.', ed_failed: 'Could not save menu', ed_dishes_failed: 'The dish list could not be loaded; suggestions come from name matching.',
      ed_total: '{n} dishes · {c} g carbs', ed_matched: 'matched', ed_unresolved: 'pick a dish',

      results_label: 'Results',
      res_empty_title: 'Enter your pre-meal glucose and press “Show similar meals”.',
      res_empty_text: 'Your most similar past meals, the insulin you injected and your post-meal glucose will appear here.',
      stats_title: 'Your similar past meals in numbers',
      stats_of: 'Of {n} similar past meals:', stats_hedef: '{n} in range', stats_hiper: '{n} high', stats_hipo: '{n} low',
      ss_ins: 'Insulin, pre-meal within ±{r}', ss_ins_avg: '{n} of these meals', ss_tok: 'Post-meal (2 h), pre-meal within ±{r}', ss_none: 'no similar-menu meal with a pre-meal value within ±{r}', ss_now: 'Your pre-meal now',
      cases_title: 'Most similar past meals', cases_intro: 'From your own log, closest in pre-meal glucose and menu nutrition. Every value is what actually happened.',
      c_date: 'Date', c_meal: 'Meal', c_pre: 'Pre-meal', c_ins: 'Insulin', c_post: 'Post-meal (2 h)', c_carb: 'Carbs', c_why: 'Why similar · menu',
      lbl_aclik: 'pre-meal', lbl_tokluk: 'post-meal', lbl_ins: 'insulin', u: 'u',
      ekdoz: '+{v} {u} correction', ekdoz_short: '+{v} corr.',
      why_aclik: 'pre-meal Δ <b>{v}</b>', why_carb: 'carbs Δ <b>{v} g</b>', why_carb_abs: 'carbs <b>{v} g</b>', why_shared: 'same dish: <b>{v}</b>', why_family: 'similar: <b>{v}</b>', why_match: '<b>{a}/{b}</b> dishes identical',
      case_aria: '{d}, {m}: pre-meal {a}, insulin {i}, post-meal {b} mg/dL, {s}',
      show_more: 'Show {n} more', show_less: 'Show fewer',
      sim_none: 'No similar past meals found.', sim_menu: 'Menu',
      st_hipo: 'low', st_hedef: 'in range', st_hiper: 'high', st_bilinmiyor: 'not recorded',

      sum_title: 'Summary', sum_loading: 'Preparing summary…', sum_failed: 'Could not get a summary.', sum_none: 'No summary produced.',
      badge_ok: 'Local LLM · passed the check', badge_rej: 'Template summary · LLM output failed the check', badge_off: 'Template summary · LLM off',
      why_rejected: 'Why was it rejected?', rejected_text: 'Rejected LLM text:', details: 'Details',
      llm_unreachable: 'Could not reach the local language model; the summary was generated from a template.',
      sum_note: 'The summary only describes your past records; it never suggests a dose.',
      chk_none: 'No check details.', chk_failed: 'Check failed (no details).', yes: 'yes',
      chk_bad_numbers: 'Numbers not in the input', chk_bad_language: 'Forbidden phrases', chk_missing_hipo: 'Hypo mention missing',
      chk_hipo_first: 'Hypo in first sentence', chk_too_long: 'Too long', chk_length: 'Length', chk_words: 'Word count',

      rec_title: 'Save this meal’s result', rec_sub: 'insulin now, post-meal later',
      rec_intro: 'After you eat, record what you injected for {m} on {d} (pre-meal {a} mg/dL). The post-meal reading is optional; you can save again later to add it.',
      rec_ins: 'Insulin injected', rec_tok: 'Post-meal glucose (2 h)', rec_ins_ph: 'e.g. 12', rec_tok_ph: 'e.g. 150', rec_tok_hint: 'Optional. You can add it later.',
      rec_save: 'Save', rec_saving: 'Saving…', rec_saved: 'Saved. It now appears in History.', rec_failed: 'Could not save', rec_open_hist: 'Open History',
      err_ins_req: 'Enter the insulin you injected.', err_ins_range: 'Value must be between 0 and 100 units.',

      calc_failed: 'Could not find similar meals',
      err_server: 'Server error ({s})', err_notfound: 'Not found for this date and meal.', err_invalid: 'Invalid request.',
      err_net: 'Could not reach the server. Is the local server running?',

      hist_h1: 'Your meal log',
      hist_intro: 'Every recorded meal: pre-meal glucose, the insulin you injected and the 2-hour post-meal reading. Tap a day to see its menus.',
      hist_month: 'Month', all: 'All', hist_search: 'Search dishes', hist_search_ph: 'e.g. mercimek',
      hist_legend: 'Each meal: pre-meal → insulin → post-meal (2 h).',
      hist_loading: 'Loading your log…', hist_failed: 'Could not load history', hist_none: 'No days match.',
      hist_found: '{n} days with “{q}” (all months)', hist_capped: ' · first {n} shown',
      hist_sum: '{n} post-meal readings', spark_aria: 'Post-meal readings this month: {n} values, {h} in range, {y} high, {l} low.',
      hist_ins_sum: 'insulin per meal {a}–{b} {u}',
      yatis: 'Bedtime', lantus: 'Lantus (basal)', src_user_rec: 'added by you', no_menu_rec: 'No menu recorded',
      cell_none: 'no record',

      dlg_eyebrow: 'Where did these values come from?', close: 'Close', dish: 'Dish',
      recipe_loading: 'Loading recipe…', recipe_failed: 'Could not load recipe',
      flow_aria: 'Calculation path', flow1: 'Menu name', flow2: 'Standard dish', flow3: 'Portion recipe', flow4: 'USDA ingredient', flow5: 'Nutrients',
      portion: 'Portion:', carbohydrate: 'Carbohydrate', protein_fat: 'Protein · fat {v} g', fiber_kcal: 'Fibre · {v} kcal',
      ingredients_cap: 'Ingredients (one portion)', ingredient: 'Ingredient', grams: 'Grams', carb_s: 'Carbs', prot_s: 'Prot.', total: 'Total',
      no_ingredients: 'No ingredient breakdown for this dish.',
      recipe_note: 'Ingredient values come from USDA FoodData Central SR Legacy (CC0) records: grams × value per 100 g. GI values are assigned from the literature by dish category.',
      model_h1: 'How good is the model?',
      model_intro: 'All numbers were measured on months the model never saw (leave-one-month-out cross-validation). Baselines are shown in grey: if a new method can’t beat them, it isn’t useful.',
      report_failed: 'Could not load report', no_report: 'No report', no_report_text: 'No evaluation files on the server.',
      findings: 'Findings', model_used: 'Model used in the app', inner_mae: ' Inner validation MAE: {v} mg/dL.', k_neigh: ' k = {v} neighbours.',
      g_base: 'baseline', g_model: 'model', g_abl: 'ablation', g_info: 'info only', g_final: 'selected',
      cv_title: 'Leave-one-month-out cross-validation', cv_intro: 'Each month was held out in turn; the model predicted it without ever seeing it.',
      mae_chart_title: 'MAE per model with 95% confidence interval', all_metrics: 'All metrics',
      tbl_aria: 'Model comparison table (scrolls horizontally)',
      th_model: 'Model', th_mae: 'MAE<br>(95% CI)', th_cov: 'Coverage', th_width: 'Interval<br>width', th_caught: 'Caught', th_missed: 'Missed', th_false: 'False<br>alarms',
      th_hiper: 'Hyper &gt;180', th_hipo: 'Hypo &lt;70',
      tbl_note: 'MAE: mean absolute error (mg/dL, lower is better). Coverage: share of real values inside the 80% interval (target ≈ 80%). “Caught”: the estimate is on the correct side of the threshold.',
      n_meals: ' n = {v} meals.',
      diffs: 'Paired differences (bootstrap 95% CI)', th_cmp: 'Comparison (MAE difference)', th_ci: '95% CI', th_result: 'Result',
      sig: 'significant', nosig: 'no difference', diffs_note: 'If the interval excludes 0 the difference is significant. Positive: the first model is worse.',
      groups: 'MAE by subgroup', dim_ogun: 'Meal', dim_aclik: 'Pre-meal', dim_ay: 'Month',
      test_title: 'October test set (never touched)', test_intro: 'October was locked away during development and measured once after model selection.',
      bo_title: 'Local LLM comparison', bo_intro: 'Each model’s summary for the same inputs went through the faithfulness/safety check.', bo_aria: 'LLM comparison table',
      th_pass: 'Passed<br>check', th_numfaith: 'Number<br>faithfulness', th_forbid: 'Forbidden<br>language', th_hipofirst: 'Hypo in first<br>sentence',
      th_words: 'Avg.<br>words', th_time: 'Time<br>(s)', th_vram: 'VRAM<br>(MB)',
      me_title: 'Menu name matching', me_intro: 'Can real menu spellings be linked to the right standard dish when their own label is hidden?',
      th_method: 'Method', th_acc1: 'Top-1 correct', th_rec5: 'In top 5', me_errs: 'Mismatch examples ({n})', th_query: 'Written on menu', th_true: 'Correct', th_pred: 'Predicted',
      nv_title: 'Nutrient value validation', nv_intro: 'Carbohydrate from recipe decomposition compared with USDA’s analysis of the cooked/prepared dish.',
      nv_n: 'dishes', nv_mae: 'mean absolute difference', nv_rel: 'median relative error', nv_bias: 'systematic bias',
      nv_rows: 'Per-dish comparison', th_dish: 'Dish', th_recipe: 'Recipe', th_ref: 'USDA ref.', th_diff: 'Diff.', th_usda: 'USDA record',
      ret_title: 'Similar-case retrieval evaluation', ret_intro: 'Do the retrieved past cases actually have similar outcomes?',
      ragas_title: 'Summary faithfulness (RAGAS)', ragas_intro: 'Faithfulness and relevance of LLM summaries to the retrieved cases.',
      method: 'Method',
      mae_aria: 'MAE (mg/dL) per model with 95% confidence interval. {list}',
      mae_note: 'Dot: MAE (mg/dL, further left is better). Line: 95% bootstrap confidence interval. Dashed line: selected model. Grey: baselines.',
      base_prefix: '[baseline] ',

      about_h1: 'How does it work?',
      about_intro: 'A person with type 1 diabetes eats a known menu every day. Before a meal, Shadow Pancreas answers “what happened the last times I ate something like this, with a similar pre-meal glucose?” straight from their own log.',
      pipe_title: 'Pipeline',
      p1k: 'Today’s menu', p1d: 'Taken from the menu file, or typed in by the user and saved.',
      p2k: 'Dish matching', p2d: 'Each written name (“Fettucine Mantarlı”) is linked to a standard dish: TF-IDF character n-grams + bge-m3 embeddings.',
      p3k: 'Recipe decomposition', p3d: 'Each dish maps to a portion recipe, and each recipe to raw ingredients.',
      p4k: 'USDA nutrient vector', p4d: 'Ingredients are multiplied by USDA FoodData Central records: carbohydrate, sugar, fibre, fat, protein, GI/GL.',
      p5k: 'Similar past meals', p5d: 'Weighted kNN finds the past meals closest in pre-meal glucose and menu nutrition.',
      p6k: 'Your own records', p6d: 'For each similar meal, the app shows the insulin you injected and the post-meal glucose that followed — facts from your log, not predictions.',
      p7k: 'Local LLM summary', p7d: 'Gemma 4 E4B running on the device with llama.cpp writes a short summary of those cases; no data leaves the machine.',
      p8k: 'Faithfulness check', p8d: 'Every number in the summary must appear in the input, and phrases such as dose advice are rejected. If it fails, a template summary is shown.',
      safe_title: 'Safety rules',
      safe1: '<strong>Never recommends an insulin dose.</strong> It only shows what you yourself injected in similar past meals.',
      safe2: 'Past values are shown <strong>as facts from your own log</strong>; there are no predictions or probabilities.',
      safe3: 'Summaries only <strong>describe past cases</strong>; they never say “do this”.',
      safe4: 'If the LLM output fails the faithfulness check, a template text is used and this is stated clearly.',
      safe5: 'Everything runs locally: your log, the matcher and the language model stay on this device.',
      data_title: 'Data sources', src1k: 'Personal log', src1d: 'Pre-meal glucose, insulin injected and 2-hour post-meal readings.', n_events: '{n} meals on this device.',
      src2k: 'Menu file', src2d: 'Monthly cafeteria menus, plus menus you enter yourself.', src3d: 'SR Legacy dataset, CC0 licence (public domain).',
      tools: 'Tools', chip_knn: 'weighted kNN',
      sys_title: 'Status on this device', sys_status: 'Status', sys_unreach: 'Could not reach the server.',
      sys_model: 'Similarity method', sys_events: 'Past meals', sys_events_v: '{n} meals with readings',
      sys_llm: 'Local LLM', sys_llm_on: 'On · {m}', sys_llm_off: 'Off — summaries come from a template',
      sys_days: 'Logged days', sys_days_v: '{n} days · {a} – {b}'
    },

    tr: {
      doc_title: 'Shadow Pancreas',
      skip: 'İçeriğe geç',
      brand_sub: 'Pankreasının Bir Hafızası Var',
      lang_group: 'Dil',
      tabs_label: 'Bölümler',
      tab_bugun: 'Bugün', tab_gecmis: 'Geçmiş', tab_model: 'Model', tab_hakkinda: 'Hakkında',
      theme_to_light: 'Açık temaya geç', theme_to_dark: 'Koyu temaya geç',
      llm_loading: 'Durum yükleniyor…', llm_on: 'Yerel LLM · {m}', llm_on_title: 'Yerel dil modeli çalışıyor: {m}',
      llm_off: 'Yerel LLM kapalı', llm_off_title: 'Yerel dil modeli çalışmıyor; özetler hazır şablondan üretilir.',
      server_down: 'Sunucu yanıt vermiyor',

      bugun_h1: 'Buna benzer bir öğün yediğimde ne olmuştu?',
      bugun_intro: 'Bugünkü menüyü ve açlık şekerini gir. Kendi kaydından en benzer geçmiş öğünlerini görürsün: o zaman kaç ünite insülin yaptığını ve 2 saat sonra şekerinin nerede olduğunu. Bunlar tahmin değil, geçmişte olanlardır; hiçbir zaman doz önerilmez.',
      step1: 'Öğünü seç', step2: 'Bugünkü menü', step3: 'Ölçümün',
      date: 'Tarih', meal: 'Öğün', today_btn: 'Bugüne dön', today_word: 'bugün',
      meal_kahvalti: 'Kahvaltı', meal_ogle: 'Öğle', meal_aksam: 'Akşam',
      meal_long_kahvalti: 'kahvaltı', meal_long_ogle: 'öğle yemeği', meal_long_aksam: 'akşam yemeği',
      meal_cap_kahvalti: 'Kahvaltı', meal_cap_ogle: 'Öğle yemeği', meal_cap_aksam: 'Akşam yemeği',
      aclik_label: 'Açlık şekeri', aclik_ph: 'örn. 110', aclik_hint: 'Yemekten hemen önceki ölçüm (20–600).',
      err_required: 'Açlık şekerini gir.', err_nan: 'Sayı gir.', err_range: 'Değer 20–600 mg/dL arasında olmalı.',
      show_btn: 'Benzer öğünleri göster', showing: 'Aranıyor…', need_menu: 'Önce bugünkü menüyü kaydet (2. adım).',

      menu_title: 'Menü', menu_note: 'Bir yemeğe dokun: tarifini ve USDA kaynaklarını gör.',
      src_menu: 'Menü dosyası', src_kullanici: 'Senin kaydın', edit: 'Düzenle',
      menu_failed: 'Menü yüklenemedi', retry: 'Tekrar dene',
      menu_none_title: 'Bu öğün için henüz menü yok.', menu_none_text: 'Ne yiyeceğini yaz; her yemeği listeden seç.',
      menu_empty: 'Menü boş', menu_empty_text: 'Bu öğün için yemek kaydı yok.',
      on_menu: '“{raw}” olarak yazıldı', no_match: 'Eşleşen yemek yok', component: 'Bileşen',
      comp_carb_title: 'Bileşenin toplam karbonhidratı', g_carb_short: '{v} g karb.',
      dish_aria: '{name}, {carb} gram karbonhidrat, {gi}. Tarifi göster',
      comp_corba: 'Çorba', comp_ana: 'Ana yemek', comp_pilav: 'Pilav / makarna', comp_yogurt: 'Yoğurt / süt', comp_salata: 'Salata',
      comp_tatli: 'Tatlı / meyve', comp_kahvaltilik: 'Kahvaltılık', comp_hamur: 'Hamur işi', comp_diger: 'Diğer',
      gi_none: 'GI —', gi_none_title: 'Karbonhidratı çok az; GI anlamlı değil',
      gi_low: 'düşük', gi_mid: 'orta', gi_high: 'yüksek', gi_prefix: 'GI {c}',
      gi_title: 'Glisemik indeks {v} ({c})',
      protein: 'Protein', fat: 'Yağ', carbs: 'karbonhidrat', menu_total: 'Menü toplamı',

      ed_comp: 'Bileşen', ed_dish: 'Yemek', ed_ph: 'Yemek adı yazmaya başla…', ed_add: 'Yemek ekle', ed_remove: 'Bu yemeği kaldır',
      ed_quick: 'Hızlı ekle', ed_save: 'Menüyü kaydet', ed_saving: 'Kaydediliyor…', ed_cancel: 'Vazgeç',
      ed_unknown: 'Bilinen bir yemek değil. En yakınını seç:', ed_matching: 'Eşleşen yemekler aranıyor…', ed_nomatch: 'Eşleşme bulunamadı; başka bir yazım dene.',
      ed_need_pick: 'Her satır için listeden bir yemek seç (ya da satırı kaldır).', ed_empty: 'En az bir yemek ekle.',
      ed_saved: 'Menü kaydedildi.', ed_failed: 'Menü kaydedilemedi', ed_dishes_failed: 'Yemek listesi yüklenemedi; öneriler ad eşleştirmeden gelir.',
      ed_total: '{n} yemek · {c} g karbonhidrat', ed_matched: 'eşleşti', ed_unresolved: 'yemek seç',

      results_label: 'Sonuçlar',
      res_empty_title: 'Açlık şekerini gir ve “Benzer öğünleri göster”e bas.',
      res_empty_text: 'En benzer geçmiş öğünlerin, yaptığın insülin ve tokluk şekerin burada görünecek.',
      stats_title: 'Benzer geçmiş öğünlerin, sayılarla',
      stats_of: '{n} benzer geçmiş öğünden:', stats_hedef: '{n} hedefte', stats_hiper: '{n} yüksek', stats_hipo: '{n} düşük',
      ss_ins: 'İnsülin, açlığı ±{r} içinde olanlar', ss_ins_avg: 'bu öğünlerden {n} tanesi', ss_tok: 'Tokluk (2 sa), açlığı ±{r} içinde olanlar', ss_none: 'açlığı ±{r} içinde benzer menülü öğün yok', ss_now: 'Şu anki açlığın',
      cases_title: 'En benzer geçmiş öğünler', cases_intro: 'Kendi kaydından; açlık değeri ve menünün besin profili en yakın olanlar. Her değer gerçekte olandır.',
      c_date: 'Tarih', c_meal: 'Öğün', c_pre: 'Açlık', c_ins: 'İnsülin', c_post: 'Tokluk (2 sa)', c_carb: 'Karb.', c_why: 'Neden benzer · menü',
      lbl_aclik: 'açlık', lbl_tokluk: 'tokluk', lbl_ins: 'insülin', u: 'ü',
      ekdoz: '+{v} {u} ek doz', ekdoz_short: '+{v} ek',
      why_aclik: 'açlık farkı <b>{v}</b>', why_carb: 'karb. farkı <b>{v} g</b>', why_carb_abs: 'karb. <b>{v} g</b>', why_shared: 'aynı yemek: <b>{v}</b>', why_family: 'benzer: <b>{v}</b>', why_match: '<b>{a}/{b}</b> yemek birebir aynı',
      case_aria: '{d}, {m}: açlık {a}, insülin {i}, tokluk {b} mg/dL, {s}',
      show_more: '{n} tane daha göster', show_less: 'Daha az göster',
      sim_none: 'Benzer geçmiş öğün bulunamadı.', sim_menu: 'Menü',
      st_hipo: 'düşük', st_hedef: 'hedefte', st_hiper: 'yüksek', st_bilinmiyor: 'kayıt yok',

      sum_title: 'Özet', sum_loading: 'Özet hazırlanıyor…', sum_failed: 'Özet alınamadı.', sum_none: 'Özet üretilemedi.',
      badge_ok: 'Yerel LLM · kontrolden geçti', badge_rej: 'Şablon özet · LLM çıktısı kontrolden geçemedi', badge_off: 'Şablon özet · LLM kapalı',
      why_rejected: 'Neden reddedildi?', rejected_text: 'Reddedilen LLM metni:', details: 'Ayrıntı',
      llm_unreachable: 'Yerel dil modeline bağlanılamadı; özet hazır şablondan üretildi.',
      sum_note: 'Özet yalnızca geçmiş kayıtlarını anlatır; doz önermez.',
      chk_none: 'Kontrol ayrıntısı yok.', chk_failed: 'Kontrol başarısız (ayrıntı yok).', yes: 'evet',
      chk_bad_numbers: 'Girdide olmayan sayılar', chk_bad_language: 'Yasaklı ifadeler', chk_missing_hipo: 'Hipo bilgisi eksik',
      chk_hipo_first: 'Hipo ilk cümlede', chk_too_long: 'Çok uzun', chk_length: 'Uzunluk', chk_words: 'Kelime sayısı',

      rec_title: 'Bu öğünün sonucunu kaydet', rec_sub: 'insülin şimdi, tokluk sonra',
      rec_intro: 'Yemekten sonra {d} {m} için yaptığın insülini kaydet (açlık {a} mg/dL). Tokluk ölçümü isteğe bağlı; sonra tekrar kaydedip ekleyebilirsin.',
      rec_ins: 'Yapılan insülin', rec_tok: 'Tokluk şekeri (2 sa)', rec_ins_ph: 'örn. 12', rec_tok_ph: 'örn. 150', rec_tok_hint: 'İsteğe bağlı. Sonra da ekleyebilirsin.',
      rec_save: 'Kaydet', rec_saving: 'Kaydediliyor…', rec_saved: 'Kaydedildi. Artık Geçmiş’te görünüyor.', rec_failed: 'Kaydedilemedi', rec_open_hist: 'Geçmiş’i aç',
      err_ins_req: 'Yaptığın insülini gir.', err_ins_range: 'Değer 0–100 ünite arasında olmalı.',

      calc_failed: 'Benzer öğünler bulunamadı',
      err_server: 'Sunucu hatası ({s})', err_notfound: 'Bu tarih ve öğün için kayıt yok.', err_invalid: 'Geçersiz istek.',
      err_net: 'Sunucuya ulaşılamadı. Yerel sunucu çalışıyor mu?',

      hist_h1: 'Öğün kaydın',
      hist_intro: 'Kayıtlı her öğün: açlık şekeri, yaptığın insülin ve 2 saat sonraki tokluk ölçümü. Menüleri görmek için bir güne dokun.',
      hist_month: 'Ay', all: 'Tümü', hist_search: 'Yemek ara', hist_search_ph: 'örn. mercimek',
      hist_legend: 'Her öğün: açlık → insülin → tokluk (2 sa).',
      hist_loading: 'Kayıt yükleniyor…', hist_failed: 'Geçmiş yüklenemedi', hist_none: 'Eşleşen gün yok.',
      hist_found: '“{q}” geçen {n} gün (tüm aylar)', hist_capped: ' · ilk {n} tanesi gösteriliyor',
      hist_sum: '{n} tokluk ölçümü', spark_aria: 'Bu ayki tokluk ölçümleri: {n} değer, {h} hedefte, {y} yüksek, {l} düşük.',
      hist_ins_sum: 'öğün başı insülin {a}–{b} {u}',
      yatis: 'Yatış', lantus: 'Lantus (bazal)', src_user_rec: 'senin eklediğin', no_menu_rec: 'Menü kaydı yok',
      cell_none: 'kayıt yok',

      dlg_eyebrow: 'Bu değerler nereden geldi?', close: 'Kapat', dish: 'Yemek',
      recipe_loading: 'Tarif yükleniyor…', recipe_failed: 'Tarif yüklenemedi',
      flow_aria: 'Hesaplama yolu', flow1: 'Menü adı', flow2: 'Standart yemek', flow3: 'Porsiyon tarifi', flow4: 'USDA malzeme', flow5: 'Besin değeri',
      portion: 'Porsiyon:', carbohydrate: 'Karbonhidrat', protein_fat: 'Protein · yağ {v} g', fiber_kcal: 'Lif · {v} kcal',
      ingredients_cap: 'Malzemeler (bir porsiyon)', ingredient: 'Malzeme', grams: 'Gram', carb_s: 'Karb.', prot_s: 'Prot.', total: 'Toplam',
      no_ingredients: 'Bu yemeğin malzeme dökümü yok.',
      recipe_note: 'Malzeme değerleri USDA FoodData Central SR Legacy (CC0) kayıtlarından, gram × 100 g başına değer olarak hesaplanır. GI değerleri literatürden yemek kategorisine göre atanır.',
      model_h1: 'Model ne kadar iyi?',
      model_intro: 'Tüm sayılar, modelin hiç görmediği aylar üzerinde ölçüldü (ay-dışarıda çapraz doğrulama). Taban çizgiler gri gösterilir: yeni bir yöntem bunları geçemiyorsa işe yaramıyordur.',
      report_failed: 'Rapor yüklenemedi', no_report: 'Rapor yok', no_report_text: 'Sunucuda değerlendirme dosyası bulunamadı.',
      findings: 'Bulgular', model_used: 'Uygulamada kullanılan model', inner_mae: ' İç doğrulama MAE: {v} mg/dL.', k_neigh: ' k = {v} komşu.',
      g_base: 'taban', g_model: 'model', g_abl: 'ablasyon', g_info: 'yalnız bilgi', g_final: 'seçilen',
      cv_title: 'Ay-dışarıda çapraz doğrulama', cv_intro: 'Her ay sırayla dışarıda bırakıldı; model o ayı hiç görmeden tahmin etti.',
      mae_chart_title: 'Model başına MAE ve %95 güven aralığı', all_metrics: 'Tüm ölçüler',
      tbl_aria: 'Model karşılaştırma tablosu (yatay kaydırılabilir)',
      th_model: 'Model', th_mae: 'MAE<br>(%95 GA)', th_cov: 'Kapsama', th_width: 'Aralık<br>genişliği', th_caught: 'Yakalanan', th_missed: 'Kaçan', th_false: 'Yanlış<br>alarm',
      th_hiper: 'Hiper &gt;180', th_hipo: 'Hipo &lt;70',
      tbl_note: 'MAE: ortalama mutlak hata (mg/dL, düşük daha iyi). Kapsama: gerçek değerin %80 aralığa düştüğü oran (hedef ≈ %80). “Yakalanan”: tahmin eşiğin doğru tarafında.',
      n_meals: ' n = {v} öğün.',
      diffs: 'Eşleştirilmiş farklar (bootstrap %95 GA)', th_cmp: 'Karşılaştırma (MAE farkı)', th_ci: '%95 GA', th_result: 'Sonuç',
      sig: 'anlamlı', nosig: 'fark yok', diffs_note: 'Aralık 0’ı içermiyorsa fark anlamlıdır. Pozitif: ilk model daha kötü.',
      groups: 'Alt gruplara göre MAE', dim_ogun: 'Öğün', dim_aclik: 'Açlık', dim_ay: 'Ay',
      test_title: 'Ekim test seti (hiç dokunulmamış)', test_intro: 'Ekim ayı geliştirme boyunca kilitli tutuldu; model seçimi bittikten sonra bir kez ölçüldü.',
      bo_title: 'Yerel LLM karşılaştırması', bo_intro: 'Aynı girdilerle her modelin özeti sadakat/güvenlik kontrolünden geçirildi.', bo_aria: 'LLM karşılaştırma tablosu',
      th_pass: 'Kontrolden<br>geçen', th_numfaith: 'Sayı<br>sadakati', th_forbid: 'Yasak<br>dil', th_hipofirst: 'Hipo ilk<br>cümlede',
      th_words: 'Ort.<br>kelime', th_time: 'Süre<br>(s)', th_vram: 'VRAM<br>(MB)',
      me_title: 'Menü adı eşleştirme', me_intro: 'Gerçek menü yazımları, kendi etiketi gizlenerek doğru standart yemeğe bağlanabiliyor mu?',
      th_method: 'Yöntem', th_acc1: 'İlk tahmin doğru', th_rec5: 'İlk 5’te', me_errs: 'Hatalı eşleşme örnekleri ({n})', th_query: 'Menüde yazan', th_true: 'Doğrusu', th_pred: 'Tahmin',
      nv_title: 'Besin değeri doğrulaması', nv_intro: 'Tarif ayrıştırmasıyla hesaplanan karbonhidrat, USDA’nın hazır/pişmiş yemek analiziyle karşılaştırıldı.',
      nv_n: 'yemek', nv_mae: 'ortalama mutlak fark', nv_rel: 'medyan bağıl hata', nv_bias: 'sistematik sapma',
      nv_rows: 'Yemek bazında karşılaştırma', th_dish: 'Yemek', th_recipe: 'Tarif', th_ref: 'USDA ref.', th_diff: 'Fark', th_usda: 'USDA kaydı',
      ret_title: 'Benzer vaka getirme değerlendirmesi', ret_intro: 'Getirilen geçmiş vakaların gerçekten benzer sonuçlara sahip olup olmadığı.',
      ragas_title: 'Özet sadakati (RAGAS)', ragas_intro: 'LLM özetlerinin getirilen vakalara sadakati ve ilgisi.',
      method: 'Yöntem',
      mae_aria: 'Model başına MAE (mg/dL) ve %95 güven aralığı. {list}',
      mae_note: 'Nokta: MAE (mg/dL, sola doğru daha iyi). Çizgi: %95 bootstrap güven aralığı. Kesikli çizgi: seçilen model. Gri: taban çizgiler.',
      base_prefix: '[taban] ',

      about_h1: 'Nasıl çalışıyor?',
      about_intro: 'Tip 1 diyabetli birinin her gün yediği menü belli. Menü Hafızası yemekten önce “buna benzer bir şeyi, benzer bir açlık şekeriyle yediğimde ne olmuştu?” sorusunu doğrudan kendi kaydından yanıtlar.',
      pipe_title: 'Akış',
      p1k: 'Bugünkü menü', p1d: 'Menü dosyasından gelir ya da kullanıcı yazıp kaydeder.',
      p2k: 'Yemek eşleştirme', p2d: 'Yazılan her ad (“Fettucine Mantarlı”) standart bir yemeğe bağlanır: TF-IDF harf n-gram + bge-m3 gömme.',
      p3k: 'Tarif ayrıştırma', p3d: 'Her yemek bir porsiyon tarifine, tarif çiğ malzemelere ayrılır.',
      p4k: 'USDA besin vektörü', p4d: 'Malzemeler USDA FoodData Central kayıtlarıyla çarpılır: karbonhidrat, şeker, lif, yağ, protein, GI/GL.',
      p5k: 'Benzer geçmiş öğünler', p5d: 'Ağırlıklı kNN, açlık değeri ve menünün besin profili en yakın geçmiş öğünleri bulur.',
      p6k: 'Kendi kayıtların', p6d: 'Her benzer öğün için yaptığın insülin ve ardından gelen tokluk şekeri gösterilir — tahmin değil, kaydındaki gerçekler.',
      p7k: 'Yerel LLM özeti', p7d: 'Cihazda llama.cpp ile çalışan Gemma 4 E4B bu vakaların kısa bir özetini yazar; veri dışarı çıkmaz.',
      p8k: 'Sadakat kontrolü', p8d: 'Özetteki her sayı girdide var mı, doz önerisi gibi ifadeler var mı kontrol edilir. Geçemezse şablon özet gösterilir.',
      safe_title: 'Güvenlik kuralları',
      safe1: '<strong>Asla insülin dozu önermez.</strong> Yalnızca benzer geçmiş öğünlerde senin yaptığın insülini gösterir.',
      safe2: 'Geçmiş değerler <strong>kendi kaydındaki gerçekler</strong> olarak gösterilir; tahmin ya da olasılık yoktur.',
      safe3: 'Özetler yalnızca <strong>geçmiş vakaları anlatır</strong>; “şunu yap” demez.',
      safe4: 'LLM çıktısı sadakat kontrolünden geçemezse hazır şablon metin kullanılır ve bu açıkça belirtilir.',
      safe5: 'Her şey yerelde çalışır: kaydın, eşleştirici ve dil modeli bu cihazda kalır.',
      data_title: 'Veri kaynakları', src1k: 'Kişisel kayıt', src1d: 'Açlık şekeri, yapılan insülin ve 2 saat sonraki tokluk ölçümleri.', n_events: 'Bu cihazda {n} öğün.',
      src2k: 'Menü dosyası', src2d: 'Yemekhanenin aylık yemek listeleri ve senin girdiğin menüler.', src3d: 'SR Legacy veri seti, CC0 lisanslı (kamu malı).',
      tools: 'Araçlar', chip_knn: 'ağırlıklı kNN',
      sys_title: 'Bu cihazdaki durum', sys_status: 'Durum', sys_unreach: 'Sunucuya ulaşılamadı.',
      sys_model: 'Benzerlik yöntemi', sys_events: 'Geçmiş öğün sayısı', sys_events_v: 'ölçümlü {n} öğün',
      sys_llm: 'Yerel LLM', sys_llm_on: 'Açık · {m}', sys_llm_off: 'Kapalı — özetler şablondan üretiliyor',
      sys_days: 'Kayıtlı günler', sys_days_v: '{n} gün · {a} – {b}'
    }
  };

  // Rapor dosyalarındaki Türkçe model/yöntem adlarının İngilizce karşılıkları (sıra önemli).
  var TERM_EN = [
    ['yalnız menü embedding', 'menu embedding only'], ['yalnız karbonhidrat', 'carbs only'], ['menü embedding', 'menu embedding'],
    ['öğün medyanı', 'meal median'], ['besin vektörü', 'nutrient vector'], ['yalnız bilgi', 'info only'],
    ['ortalama', 'mean'], ['prototip', 'prototype'], ['yemeksiz', 'no food'], ['besin', 'nutrients'], ['insülin', 'insulin'], ['harf', 'char']
  ];

  // ================================================================ helpers
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode etc. */ } }
  };

  var LANG = store.get('dl-lang') === 'tr' ? 'tr' : 'en';
  function loc() { return LANG === 'tr' ? 'tr-TR' : 'en-GB'; }
  function t(key, vars) {
    var s = I18N[LANG][key];
    if (s == null) s = I18N.en[key];
    if (s == null) s = key;
    if (vars) s = s.replace(/\{(\w+)\}/g, function (m, k) { return vars[k] != null ? vars[k] : m; });
    return s;
  }
  function term(s) {
    s = String(s == null ? '' : s);
    if (LANG !== 'en') return s;
    TERM_EN.forEach(function (p) { s = s.split(p[0]).join(p[1]); });
    return s;
  }

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function isNum(v) { return typeof v === 'number' && isFinite(v); }
  var NF = {};
  function fmt(v, d) {
    if (!isNum(v)) return '—';
    d = d == null ? 0 : d;
    var k = LANG + d;
    if (!NF[k]) NF[k] = new Intl.NumberFormat(loc(), { minimumFractionDigits: d, maximumFractionDigits: d });
    return NF[k].format(v);
  }
  function signed(v, d) { if (!isNum(v)) return '—'; return (v > 0 ? '+' : v < 0 ? '−' : '±') + fmt(Math.abs(v), d); }
  function pnum(n) { return LANG === 'tr' ? '%' + n : n + '%'; }           // n already formatted
  function pct(v, d) { return isNum(v) ? pnum(fmt(v * 100, d == null ? 1 : d)) : '—'; }  // v is 0..1
  function pctInt(v) { return isNum(v) ? pnum(fmt(v, 0)) : '—'; }          // v is 0..100
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

  function mealShort(m) { return I18N.en['meal_' + m] ? t('meal_' + m) : (m || ''); }
  function mealLong(m) { return I18N.en['meal_long_' + m] ? t('meal_long_' + m) : (m || ''); }
  function mealCap(m) { return I18N.en['meal_cap_' + m] ? t('meal_cap_' + m) : (m || ''); }

  function parseDate(s) { var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s || ''); return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null; }
  function fmtDate(s, opts) {
    var d = parseDate(s);
    if (!d) return String(s || '—');
    return d.toLocaleDateString(loc(), opts || { day: 'numeric', month: 'long', year: 'numeric' });
  }
  function weekday(s) { var d = parseDate(s); return d ? d.toLocaleDateString(loc(), { weekday: 'long' }) : ''; }
  function cap1(s) { s = String(s || ''); return s.charAt(0).toLocaleUpperCase(loc()) + s.slice(1); }

  function glucoseStatus(v) { if (!isNum(v)) return 'bilinmiyor'; return v < 70 ? 'hipo' : v > 180 ? 'hiper' : 'hedef'; }
  function statusChip(st) {
    var s = ['hipo', 'hedef', 'hiper'].indexOf(st) >= 0 ? st : 'bilinmiyor';
    return '<span class="st st-' + s + '">' + esc(t('st_' + s)) + '</span>';
  }
  var GI_KEY = { dusuk: 'gi_low', orta: 'gi_mid', yuksek: 'gi_high' };
  var GI_FROM_TR = { 'düşük': 'dusuk', orta: 'orta', 'yüksek': 'yuksek' };
  function giInfo(gi, serverClass) {
    if (!isNum(gi) || gi <= 0) return { cls: 'yok', word: '—', label: t('gi_none'), title: t('gi_none_title') };
    var cls = GI_FROM_TR[serverClass] || (gi < 55 ? 'dusuk' : gi < 70 ? 'orta' : 'yuksek');
    var word = t(GI_KEY[cls]);
    return { cls: cls, word: word, label: t('gi_prefix', { c: word }), title: t('gi_title', { v: fmt(gi), c: word }) };
  }
  function giBadge(gi) { var g = giInfo(gi); return '<span class="badge gi-' + g.cls + '" title="' + esc(g.title) + '">' + esc(g.label) + '</span>'; }
  function compTitle(c) { return I18N.en['comp_' + c.comp] ? t('comp_' + c.comp) : (c.title || c.comp || t('component')); }

  function api(path, opts) {
    opts = opts || {};
    var init = { method: opts.method || 'GET', headers: {}, signal: opts.signal };
    if (opts.body !== undefined) { init.headers['Content-Type'] = 'application/json'; init.body = JSON.stringify(opts.body); }
    return fetch(path, init).then(function (r) {
      return r.text().then(function (txt) {
        var data = null;
        try { data = txt ? JSON.parse(txt) : null; } catch (e) { data = null; }
        if (!r.ok) {
          var det = data && data.detail, msg = typeof det === 'string' ? det : (det && typeof det.message === 'string' ? det.message : '');
          var err = new Error(msg); err.code = det && det.code;
          err.status = r.status; throw err;
        }
        return data;
      });
    });
  }
  function netMsg(e) {
    if (e && e.name === 'AbortError') return null;
    if (e && e.status) {
      if (e.message && (LANG === 'tr' || e.code)) return e.message;   // structured errors come in the requested language
      if (e.status === 404) return t('err_notfound');
      if (e.status === 422 || e.status === 400) return t('err_invalid');
      return t('err_server', { s: e.status });
    }
    return t('err_net');
  }
  function withLang(path) { return path + (path.indexOf('?') >= 0 ? '&' : '?') + 'lang=' + LANG; }
  function stateBox(title, text, retryId) {
    return '<div class="state" role="status"><strong>' + esc(title) + '</strong>' + (text ? esc(text) : '') +
      (retryId ? '<div><button class="btn sm" type="button" id="' + retryId + '">' + esc(t('retry')) + '</button></div>' : '') + '</div>';
  }
  function loadingLine(key) { return '<div class="loading-line"><span class="spin" aria-hidden="true"></span>' + esc(t(key)) + '</div>'; }
  var ICON = {
    warn: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.5 2.5 20h19z"/><path d="M12 10v4.5M12 17.5v.01"/></svg>',
    up: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 17l6-6 4 4 6-7"/><path d="M15 8h5v5"/></svg>',
    arrow: '<svg class="arr" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7"/></svg>',
    off: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M6 18 18 6"/></svg>'
  };
  ICON.edit = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/></svg>';
  ICON.x = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  ICON.plus = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>';
  ICON.chev = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';

  // Turkish-insensitive folding (length-preserving): ı/i, ş/s, ç/c, ğ/g, ö/o, ü/u.
  var TR_FOLD = { 'ı': 'i', 'ş': 's', 'ç': 'c', 'ğ': 'g', 'ö': 'o', 'ü': 'u', 'â': 'a', 'î': 'i', 'û': 'u' };
  function fold(s) { return String(s == null ? '' : s).toLocaleLowerCase('tr-TR').replace(/[ışçğöüâîû]/g, function (c) { return TR_FOLD[c]; }); }
  function markFold(text, q) {
    text = String(text == null ? '' : text);
    var qq = fold(q).trim(); if (!qq) return esc(text);
    var f = fold(text), i = f.indexOf(qq);
    if (i < 0 || f.length !== text.length) return esc(text);
    return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + qq.length)) + '</mark>' + esc(text.slice(i + qq.length));
  }
  function fmtIns(v) { return isNum(v) ? (Math.abs(v - Math.round(v)) < 1e-9 ? fmt(v) : fmt(v, 1)) : '—'; }
  function localISO(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function mealByClock() { var n = new Date(), m = n.getHours() * 60 + n.getMinutes(); return m < 630 ? 'kahvalti' : m < 960 ? 'ogle' : 'aksam'; }
  function stOf(st, tok) { return { hipo: 1, hedef: 1, hiper: 1 }[st] ? st : (isNum(tok) ? glucoseStatus(tok) : 'bilinmiyor'); }
  function monthLabel(ym) { var m = /^(\d{4})-(\d{2})/.exec(ym || ''); return m ? cap1(new Date(+m[1], +m[2] - 1, 1).toLocaleDateString(loc(), { month: 'long', year: 'numeric' })) : String(ym || ''); }
  function setErr(el, msg) { el.textContent = msg || ''; el.hidden = !msg; }

  // ================================================================ state
  var MEALS = ['kahvalti', 'ogle', 'aksam'];
  var S = {
    status: null, statusFailed: false, tab: 'bugun',
    today: null, date: null, meal: null,
    menu: null, menuReq: 0, ed: null, edSeq: 0,
    dishes: null, dishById: {}, dishesP: null, dishesFailed: false,
    result: null, lastAclik: null, showAll: false, summary: null, summaryCtrl: null, queryCtrl: null,
    hist: null, histP: null, histMonth: null, histMeal: 'all', histQ: '', histOpen: {}, spark: null,
    report: null, modelLoading: false, recipe: null
  };

  // ================================================================ static text / language
  function applyStatic() {
    document.documentElement.lang = LANG;
    document.title = t('doc_title');
    $$('[data-i18n]').forEach(function (el) { el.textContent = t(el.getAttribute('data-i18n')); });
    $$('[data-i18n-html]').forEach(function (el) { el.innerHTML = t(el.getAttribute('data-i18n-html')); });   // dictionary-only HTML
    $$('[data-i18n-ph]').forEach(function (el) { el.setAttribute('placeholder', t(el.getAttribute('data-i18n-ph'))); });
    $$('[data-i18n-aria]').forEach(function (el) { el.setAttribute('aria-label', t(el.getAttribute('data-i18n-aria'))); });
    $$('.lang-sw button').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.lang === LANG ? 'true' : 'false'); });
    syncThemeBtn();
    renderPill();
    setBusy(!!S.queryCtrl);
  }

  function setLang(l) {
    if (l === LANG || !I18N[l]) return;
    LANG = l; store.set('dl-lang', l);
    applyStatic();
    renderDateInfo();
    if (S.ed) renderEditor(); else if (S.menu) renderMenuCard();
    if (S.result) { renderResult(true); if (S.result.context) streamSummary(S.result.context); }
    var g = $('#goErr'); if (!g.hidden) setErr(g, t('need_menu'));
    if (S.hist) renderHistory();
    if (S.report) renderModel(S.report);
    renderSys();
    if (dlg.open && S.recipe) renderRecipe(S.recipe);
    var inp = $('#aclikIn');
    if (inp.getAttribute('aria-invalid') === 'true') readAclik();
  }
  $$('.lang-sw button').forEach(function (b) { b.addEventListener('click', function () { setLang(b.dataset.lang); }); });

  // ================================================================ theme
  function currentTheme() {
    var th = document.documentElement.getAttribute('data-theme');
    if (th) return th;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function syncThemeBtn() {
    var lbl = currentTheme() === 'dark' ? t('theme_to_light') : t('theme_to_dark');
    $('#themeBtn').setAttribute('aria-label', lbl);
    $('#themeBtn').title = lbl;
  }
  $('#themeBtn').addEventListener('click', function () {
    var next = currentTheme() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    store.set('dl-theme', next);
    syncThemeBtn();
  });

  // ================================================================ tabs
  var TABS = ['bugun', 'gecmis', 'model', 'hakkinda'];
  function showTab(name, focus) {
    if (TABS.indexOf(name) < 0) name = 'bugun';
    S.tab = name;
    TABS.forEach(function (x) {
      var b = $('#tab-' + x), p = $('#panel-' + x), on = x === name;
      b.setAttribute('aria-selected', on ? 'true' : 'false');
      b.tabIndex = on ? 0 : -1;
      p.hidden = !on;
    });
    if (focus) $('#tab-' + name).focus();
    if (name === 'gecmis') loadHistory();
    if (name === 'model') { loadModel(); requestAnimationFrame(drawMaeChart); }
    if (name === 'hakkinda') { renderSys(); if (!S.hist) loadHistory(); }
  }
  $$('.tabs [role="tab"]').forEach(function (b) {
    b.addEventListener('click', function () { showTab(b.dataset.tab); window.scrollTo({ top: 0 }); });
    b.addEventListener('keydown', function (e) {
      var i = TABS.indexOf(b.dataset.tab), n = null;
      if (e.key === 'ArrowRight') n = TABS[(i + 1) % TABS.length];
      else if (e.key === 'ArrowLeft') n = TABS[(i + TABS.length - 1) % TABS.length];
      else if (e.key === 'Home') n = TABS[0];
      else if (e.key === 'End') n = TABS[TABS.length - 1];
      if (n) { e.preventDefault(); showTab(n, true); }
    });
  });

  // ================================================================ status / LLM
  function loadStatus() {
    return api('/api/status').then(function (s) { S.status = s || {}; renderPill(); renderSys(); })
      .catch(function () { S.statusFailed = true; renderPill(); renderSys(); });
  }
  function llmName(s) { var m = (s.llm && s.llm.model) || 'LLM'; m = String(m).split(/[\\/]/).pop().replace(/\.gguf$/i, ''); return m || 'LLM'; }
  function renderPill() {
    var pill = $('#llmPill'), txt = $('.llm-text', pill), s = S.status;
    if (!s && !S.statusFailed) { pill.className = 'llm-pill'; txt.textContent = t('llm_loading'); pill.title = ''; return; }
    if (!s) { pill.className = 'llm-pill off'; txt.textContent = t('server_down'); pill.title = ''; return; }
    if (s.llm) {
      var m = llmName(s);
      pill.className = 'llm-pill on'; txt.textContent = t('llm_on', { m: m }); pill.title = t('llm_on_title', { m: m });
    } else {
      pill.className = 'llm-pill off'; txt.textContent = t('llm_off'); pill.title = t('llm_off_title');
    }
  }
  function renderSys() {
    var s = S.status, body = $('#sysBody');
    if (!s) { body.innerHTML = '<dt>' + esc(t('sys_status')) + '</dt><dd>' + esc(S.statusFailed ? t('sys_unreach') : t('llm_loading')) + '</dd>'; return; }
    var llm = s.llm ? t('sys_llm_on', { m: llmName(s) }) : t('sys_llm_off');
    var hd = S.hist && S.hist.days.length ? S.hist.days : null;
    var days = hd ? t('sys_days_v', { n: fmt(hd.length), a: fmtDate(hd[hd.length - 1].date), b: fmtDate(hd[0].date) }) : '—';
    body.innerHTML =
      '<dt>' + esc(t('sys_model')) + '</dt><dd>' + esc(t('chip_knn')) + '</dd>' +
      '<dt>' + esc(t('sys_events')) + '</dt><dd class="tnum">' + esc(t('sys_events_v', { n: fmt(s.n_events) })) + '</dd>' +
      '<dt>' + esc(t('sys_llm')) + '</dt><dd>' + esc(llm) + '</dd>' +
      '<dt>' + esc(t('sys_days')) + '</dt><dd class="tnum">' + esc(days) + '</dd>';
    $('#nEvents').textContent = isNum(s.n_events) ? t('n_events', { n: fmt(s.n_events) }) : '';
  }

  // ================================================================ TODAY: date + meal
  function renderDateInfo() {
    var info = $('#dateInfo');
    info.textContent = S.date ? cap1(weekday(S.date)) + (S.date === S.today ? ' · ' + t('today_word') : '') : '';
    $('#todayBtn').hidden = !S.today || S.date === S.today;
  }
  function setDate(v) {
    if (!parseDate(v) || v === S.date) return;
    S.date = v; $('#dateIn').value = v; renderDateInfo(); loadMenu();
  }
  $('#dateIn').addEventListener('change', function () { setDate(this.value); });
  $('#todayBtn').addEventListener('click', function () { setDate(S.today); $('#dateIn').focus(); });

  function syncMealSeg() {
    $$('#mealSeg button').forEach(function (b) {
      var on = b.dataset.meal === S.meal;
      b.setAttribute('aria-checked', on ? 'true' : 'false');
      b.tabIndex = on ? 0 : -1;
    });
  }
  function setMeal(m) { if (!m || m === S.meal) return; S.meal = m; syncMealSeg(); loadMenu(); }
  $$('#mealSeg button').forEach(function (b) {
    b.addEventListener('click', function () { setMeal(b.dataset.meal); });
    b.addEventListener('keydown', function (e) {
      if (['ArrowRight', 'ArrowLeft', 'ArrowDown', 'ArrowUp'].indexOf(e.key) < 0) return;
      e.preventDefault();
      var btns = $$('#mealSeg button'), i = btns.indexOf(b), d = (e.key === 'ArrowRight' || e.key === 'ArrowDown') ? 1 : -1;
      var n = btns[(i + d + btns.length) % btns.length];
      setMeal(n.dataset.meal); n.focus();
    });
  });

  // ================================================================ TODAY: menu card
  function menuSub() { return S.date ? fmtDate(S.date) + ' · ' + cap1(weekday(S.date)) + ' · ' + mealShort(S.meal) : ''; }
  var msgT = null;
  function setMenuMsg(s) { var el = $('#menuMsg'); el.textContent = s || ''; clearTimeout(msgT); if (s) msgT = setTimeout(function () { el.textContent = ''; }, 5000); }

  function loadMenu() {
    clearResult();
    S.menu = null; S.ed = null; setMenuMsg('');
    setErr($('#goErr'), '');
    if (!S.date || !S.meal) return;
    var req = ++S.menuReq, body = $('#menuBody');
    $('#menuSub').textContent = menuSub();
    $('#menuTools').innerHTML = '';
    body.setAttribute('aria-busy', 'true');
    body.innerHTML = '<div class="menu-grid"><div class="skel skel-card"></div><div class="skel skel-card"></div></div>';
    api(withLang('/api/menu?date=' + encodeURIComponent(S.date) + '&meal=' + encodeURIComponent(S.meal))).then(function (m) {
      if (req !== S.menuReq) return;
      S.menu = m || {}; renderMenuCard();
    }).catch(function (e) {
      if (req !== S.menuReq) return;
      if (e && e.status === 404) { openEditor(null); return; }
      body.innerHTML = stateBox(t('menu_failed'), netMsg(e), 'retryMenu');
      var b = $('#retryMenu'); if (b) b.onclick = loadMenu;
    }).then(function () { if (req === S.menuReq) body.setAttribute('aria-busy', 'false'); });
  }

  function srcKey(s) { s = fold(s); return s === 'menu' || s === 'okul' || s === 'school' ? 'menu' : (s === 'kullanici' || s === 'user' ? 'kullanici' : ''); }
  function compHtml(c) {
    var dishes = Array.isArray(c.dishes) ? c.dishes : [];
    var rows = dishes.map(function (d) {
      var raw = d.raw && d.name && fold(d.raw) !== fold(d.name) ? '<span class="dish-raw">' + esc(t('on_menu', { raw: d.raw })) + '</span>' : '';
      var gi = giInfo(d.gi);
      return '<button type="button" class="dish" data-dish="' + esc(d.dish_id || '') + '"' + (d.dish_id ? '' : ' disabled') +
        ' aria-label="' + esc(t('dish_aria', { name: d.name || d.raw || t('dish'), carb: fmt(d.carb), gi: gi.label })) + '">' +
        '<span class="dish-name" lang="tr">' + esc(d.name || d.raw || '—') + raw + '</span>' +
        giBadge(d.gi) +
        '<span class="dish-carb">' + fmt(d.carb) + '<small> g</small></span></button>';
    }).join('');
    if (!rows) rows = '<p class="muted small" style="padding:8px 4px">' + esc((Array.isArray(c.raw) ? c.raw.join(', ') : '') || t('no_match')) + '</p>';
    return '<article class="comp"><div class="comp-head"><span class="comp-title">' + esc(compTitle(c)) + '</span>' +
      '<span class="comp-carb" title="' + esc(t('comp_carb_title')) + '">' + esc(t('g_carb_short', { v: fmt(c.carb) })) + '</span></div>' + rows + '</article>';
  }
  function renderMenuCard() {
    var m = S.menu || {}, sk = srcKey(m.source);
    $('#menuSub').textContent = menuSub();
    $('#menuTools').innerHTML = (sk ? '<span class="chip src-' + sk + '">' + esc(t('src_' + sk)) + '</span>' : '') +
      '<button type="button" class="btn sm" id="editMenuBtn">' + ICON.edit + esc(t('edit')) + '</button>';
    $('#editMenuBtn').onclick = function () { openEditor(S.menu); var i = $('#menuBody .ed-in'); if (i) i.focus(); };
    var comps = Array.isArray(m.components) ? m.components : [];
    var html = comps.length ? '<div class="menu-grid">' + comps.map(compHtml).join('') + '</div>' : stateBox(t('menu_empty'), t('menu_empty_text'));
    var tt = m.total || {};
    html += '<div class="menu-total" aria-label="' + esc(t('menu_total')) + '"><span class="mt-k">' + esc(t('menu_total')) + '</span>' +
      '<span class="mt-carb"><b>' + fmt(tt.carb) + '</b> g ' + esc(t('carbs')) + '</span>' +
      '<span>' + esc(t('protein')) + ' <b>' + fmt(tt.protein) + ' g</b></span>' +
      '<span>' + esc(t('fat')) + ' <b>' + fmt(tt.fat) + ' g</b></span></div>' +
      '<p class="muted small sec-note">' + esc(t('menu_note')) + '</p>';
    $('#menuBody').innerHTML = html;
  }

  // ================================================================ TODAY: menu editor
  var COMPS = ['corba', 'ana', 'pilav', 'salata', 'yogurt', 'tatli', 'kahvaltilik', 'hamur', 'diger'];
  var QUICK = [{ k: 'Salata / Zeytinyağlı', comp: 'salata' }, { k: 'Yoğurt', comp: 'yogurt' }, { k: 'Meyve', comp: 'tatli' }];

  function loadDishes() {
    if (S.dishes) return Promise.resolve();
    if (S.dishesP) return S.dishesP;
    S.dishesP = api('/api/dishes').then(function (list) {
      S.dishes = (Array.isArray(list) ? list : []).filter(function (d) { return d && d.dish_id && d.name; });
      S.dishes.forEach(function (d) { d._f = fold(d.name); S.dishById[d.dish_id] = d; });
      S.dishesFailed = false; S.dishesP = null;
      if (S.ed) S.ed.rows.forEach(function (r) { syncRow(r); });
    }).catch(function () {
      S.dishesFailed = true; S.dishesP = null;
      var n = $('#edDishNote'); if (n) n.hidden = false;
    });
    return S.dishesP;
  }
  function defaultComp() { return S.meal === 'kahvalti' ? 'kahvaltilik' : 'ana'; }
  function newRow(comp, text, dishId, name, raw) {
    return { id: 'r' + (++S.edSeq), comp: comp || defaultComp(), compAuto: !comp, text: text || '', dish_id: dishId || null,
      name: name || '', raw: raw || '', sugg: null, matching: false, invalid: false, carb: null };
  }
  function openEditor(menu) {
    loadDishes();
    var rows = [];
    if (menu && Array.isArray(menu.components)) {
      menu.components.forEach(function (c) {
        (Array.isArray(c.dishes) ? c.dishes : []).forEach(function (d) {
          var r = d.dish_id ? newRow(d.comp || c.comp, d.name || d.raw, d.dish_id, d.name || d.raw, d.raw || d.name)
            : newRow(d.comp || c.comp, d.raw || d.name || '');
          r.compAuto = false; r.carb = isNum(d.carb) ? d.carb : null;
          rows.push(r);
        });
      });
    }
    if (!rows.length) rows.push(newRow());
    S.ed = { rows: rows, err: '', saving: false, hadMenu: !!menu };
    setMenuMsg('');
    renderEditor();
  }
  function rowCarb(r) { var d = r.dish_id && S.dishById[r.dish_id]; return d && isNum(d.carb) ? d.carb : r.carb; }
  function stateHtml(r) {
    if (r.dish_id) { var c = rowCarb(r); return '<span class="ed-ok" title="' + esc(t('ed_matched')) + '">' + ICON.check + (isNum(c) ? fmt(c) + ' g' : '') + '</span>'; }
    if (r.matching) return '<span class="spin" aria-hidden="true"></span>';
    if (r.text.trim()) return '<span class="ed-warn" title="' + esc(t('ed_unresolved')) + '">' + ICON.warn + '</span>';
    return '';
  }
  function suggHtml(r) {
    if (r.matching) return '<span class="muted small">' + esc(t('ed_matching')) + '</span>';
    if (r.sugg) {
      if (!r.sugg.length) return '<span class="small ed-warn-t">' + esc(t('ed_nomatch')) + '</span>';
      return '<span class="small ed-warn-t">' + esc(t('ed_unknown')) + '</span>' + r.sugg.map(function (s) {
        var d = S.dishById[s.dish_id], c = d && isNum(d.carb) ? ' <span class="muted">' + fmt(d.carb) + ' g</span>' : '';
        return '<button type="button" class="chip chip-btn" data-pick="' + esc(s.dish_id) + '" data-name="' + esc(s.name || (d && d.name) || s.dish_id) + '" lang="tr">' + esc(s.name || (d && d.name) || s.dish_id) + c + '</button>';
      }).join('');
    }
    if (r.dish_id && r.raw && fold(r.raw) !== fold(r.name)) return '<span class="muted small">' + esc(t('on_menu', { raw: r.raw })) + '</span>';
    return '';
  }
  function rowHtml(r) {
    var lb = 'lb-' + r.id;
    return '<div class="ed-row' + (r.invalid ? ' invalid' : '') + '" data-row="' + r.id + '">' +
      '<div class="select-wrap sm ed-c"><select class="ed-comp" aria-label="' + esc(t('ed_comp')) + '">' +
        COMPS.map(function (c) { return '<option value="' + c + '"' + (c === r.comp ? ' selected' : '') + '>' + esc(t('comp_' + c)) + '</option>'; }).join('') + '</select></div>' +
      '<div class="ac"><input type="text" class="ed-in" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="' + lb + '" autocomplete="off" spellcheck="false" lang="tr"' +
        ' aria-label="' + esc(t('ed_dish')) + '" placeholder="' + esc(t('ed_ph')) + '" value="' + esc(r.text) + '" aria-invalid="' + (r.invalid ? 'true' : 'false') + '" aria-describedby="sg-' + r.id + '">' +
        '<span class="ed-state">' + stateHtml(r) + '</span>' +
        '<ul class="ac-list" role="listbox" id="' + lb + '" aria-label="' + esc(t('ed_dish')) + '" hidden></ul></div>' +
      '<button type="button" class="icon-btn ed-del" aria-label="' + esc(t('ed_remove')) + '" title="' + esc(t('ed_remove')) + '">' + ICON.x + '</button>' +
      '<div class="ed-sugg" id="sg-' + r.id + '" aria-live="polite">' + suggHtml(r) + '</div></div>';
  }
  function edTotalText() {
    var n = 0, c = 0;
    S.ed.rows.forEach(function (r) { if (r.dish_id) { n++; var x = rowCarb(r); if (isNum(x)) c += x; } });
    return n ? t('ed_total', { n: fmt(n), c: fmt(c) }) : '';
  }
  function renderEditor() {
    var ed = S.ed;
    $('#menuSub').textContent = menuSub();
    $('#menuTools').innerHTML = '';
    $('#menuBody').innerHTML =
      (ed.hadMenu ? '' : '<div class="ed-intro"><strong>' + esc(t('menu_none_title')) + '</strong> ' + esc(t('menu_none_text')) + '</div>') +
      '<div class="ed-head" aria-hidden="true"><span>' + esc(t('ed_comp')) + '</span><span>' + esc(t('ed_dish')) + '</span></div>' +
      '<div class="ed-rows" id="edRows">' + ed.rows.map(rowHtml).join('') + '</div>' +
      '<div class="ed-actions"><button type="button" class="btn sm" id="edAdd">' + ICON.plus + esc(t('ed_add')) + '</button>' +
        '<span class="ed-quick"><span class="muted small">' + esc(t('ed_quick')) + ':</span>' +
        QUICK.map(function (q, i) { return '<button type="button" class="chip chip-btn" data-quick="' + i + '" lang="tr">+ ' + esc(q.k) + '</button>'; }).join('') + '</span></div>' +
      '<p class="note" id="edDishNote"' + (S.dishesFailed ? '' : ' hidden') + '>' + esc(t('ed_dishes_failed')) + '</p>' +
      '<p class="err" id="edErr" role="alert"' + (ed.err ? '' : ' hidden') + '>' + esc(ed.err) + '</p>' +
      '<div class="ed-foot"><span class="ed-total small" id="edTotal">' + esc(edTotalText()) + '</span><span class="ed-btns">' +
        (ed.hadMenu ? '<button type="button" class="btn ghost" id="edCancel">' + esc(t('ed_cancel')) + '</button>' : '') +
        '<button type="button" class="btn primary" id="edSave"' + (ed.saving ? ' disabled' : '') + '>' + esc(ed.saving ? t('ed_saving') : t('ed_save')) + '</button></span></div>';
  }
  function rowById(id) { return S.ed ? S.ed.rows.filter(function (r) { return r.id === id; })[0] : null; }
  function rowEl(r) { return $('#menuBody [data-row="' + r.id + '"]'); }
  // Updates one row in place without replacing its input (keeps focus/caret/IME).
  function syncRow(r, focus) {
    var el = rowEl(r); if (!el) return;
    var inp = $('.ed-in', el);
    if (inp.value !== r.text) inp.value = r.text;
    inp.setAttribute('aria-invalid', r.invalid ? 'true' : 'false');
    el.classList.toggle('invalid', !!r.invalid);
    $('.ed-comp', el).value = r.comp;
    $('.ed-state', el).innerHTML = stateHtml(r);
    $('.ed-sugg', el).innerHTML = suggHtml(r);
    if (focus) inp.focus();
    var tot = $('#edTotal'); if (tot) tot.textContent = edTotalText();
  }
  function edError(msg) { if (S.ed) S.ed.err = msg || ''; var e = $('#edErr'); if (e) setErr(e, msg); }

  function pick(r, id, name, raw, focus) {
    r.dish_id = id; r.name = name; r.text = name; r.raw = raw || name; r.sugg = null; r.matching = false; r.invalid = false;
    var d = S.dishById[id]; r.carb = d && isNum(d.carb) ? d.carb : null;
    if (r.compAuto && d && COMPS.indexOf(d.category) >= 0) r.comp = d.category;
    acClose(); syncRow(r, focus);
    if (S.ed && !S.ed.rows.some(function (x) { return x.invalid; })) edError('');
  }
  function exactDish(q) { var fq = fold(q).trim(); return S.dishes ? S.dishes.filter(function (d) { return d._f === fq; })[0] : null; }
  function resolveTyped(r, autoPick) {
    var q = r.text.trim(); if (!q || r.dish_id) return;
    var ex = exactDish(q);
    if (ex) { pick(r, ex.dish_id, ex.name, q, rowEl(r) && rowEl(r).contains(document.activeElement)); return; }
    r.matching = true; r.sugg = null; syncRow(r);
    api('/api/match?q=' + encodeURIComponent(q)).then(function (list) {
      if (!rowById(r.id) || r.text.trim() !== q || r.dish_id) return;
      r.matching = false;
      var s = (Array.isArray(list) ? list : []).filter(function (x) { return x && x.dish_id; }).slice(0, 5);
      if (autoPick && s.length) { pick(r, s[0].dish_id, s[0].name || s[0].dish_id, q); return; }
      r.sugg = s; syncRow(r);
    }).catch(function () {
      if (!rowById(r.id) || r.text.trim() !== q) return;
      r.matching = false; r.sugg = []; syncRow(r);
    });
  }

  // ---- autocomplete (combobox + listbox)
  var AC = { row: null, items: [], active: -1, inp: null };
  function acFilter(q) {
    var toks = fold(q).trim().split(/\s+/).filter(Boolean);
    if (!toks.length || !S.dishes) return [];
    var out = [];
    S.dishes.forEach(function (d) {
      var f = d._f;
      if (!toks.every(function (tk) { return f.indexOf(tk) >= 0; })) return;
      var i = f.indexOf(toks[0]);
      out.push({ d: d, sc: i === 0 ? 0 : (/[\s(\/-]/.test(f.charAt(i - 1)) ? 1 : 2) });
    });
    out.sort(function (a, b) { return a.sc - b.sc || a.d.name.length - b.d.name.length || (a.d.name < b.d.name ? -1 : 1); });
    return out.slice(0, 8).map(function (x) { return x.d; });
  }
  function acOpen(inp, r) {
    var list = $('#lb-' + r.id); if (!list) return;
    var items = acFilter(inp.value);
    if (AC.inp && AC.inp !== inp) acClose();
    AC = { row: r, items: items, active: -1, inp: inp };
    if (!items.length) { list.hidden = true; list.innerHTML = ''; inp.setAttribute('aria-expanded', 'false'); inp.removeAttribute('aria-activedescendant'); return; }
    list.innerHTML = items.map(function (d, i) {
      return '<li role="option" id="lb-' + r.id + '-' + i + '" data-i="' + i + '" aria-selected="false"><span lang="tr">' + markFold(d.name, inp.value) + '</span>' +
        '<span class="ac-carb">' + fmt(d.carb) + ' g</span></li>';
    }).join('');
    list.hidden = false; inp.setAttribute('aria-expanded', 'true'); inp.removeAttribute('aria-activedescendant');
  }
  function acClose() {
    if (AC.inp) {
      AC.inp.setAttribute('aria-expanded', 'false'); AC.inp.removeAttribute('aria-activedescendant');
      var l = AC.row && $('#lb-' + AC.row.id); if (l) { l.hidden = true; l.innerHTML = ''; }
    }
    AC = { row: null, items: [], active: -1, inp: null };
  }
  function acMove(d) {
    if (!AC.items.length) return;
    AC.active = (AC.active + d + AC.items.length) % AC.items.length;
    var list = $('#lb-' + AC.row.id);
    $$('li', list).forEach(function (li, i) { li.setAttribute('aria-selected', i === AC.active ? 'true' : 'false'); });
    var cur = $('#lb-' + AC.row.id + '-' + AC.active);
    AC.inp.setAttribute('aria-activedescendant', cur.id);
    cur.scrollIntoView({ block: 'nearest' });
  }
  function acPick(i) { var d = AC.items[i], r = AC.row; if (d && r) pick(r, d.dish_id, d.name, d.name, true); }

  function quickAdd(i) {
    var q = QUICK[i], ed = S.ed; if (!q || !ed) return;
    var r = ed.rows.filter(function (x) { return !x.text.trim(); })[0];
    if (r) { r.comp = q.comp; r.text = q.k; } else { r = newRow(q.comp, q.k); ed.rows.push(r); }
    r.compAuto = false;
    renderEditor();
    var b = $('#menuBody [data-quick="' + i + '"]'); if (b) b.focus();
    resolveTyped(r, true);
  }

  function saveMenu() {
    var ed = S.ed; if (!ed || ed.saving) return;
    acClose();
    var rows = ed.rows.filter(function (r) { return r.text.trim(); });
    if (!rows.length) { edError(t('ed_empty')); var f = $('#menuBody .ed-in'); if (f) f.focus(); return; }
    var bad = rows.filter(function (r) { return !r.dish_id; });
    ed.rows.forEach(function (r) { r.invalid = !r.dish_id && !!r.text.trim(); syncRow(r); });
    if (bad.length) {
      edError(t('ed_need_pick'));
      bad.forEach(function (r) { if (!r.sugg && !r.matching) resolveTyped(r); });
      var el = rowEl(bad[0]); if (el) $('.ed-in', el).focus();
      return;
    }
    ed.saving = true; ed.err = ''; renderEditor();
    var body = { date: S.date, meal: S.meal, items: rows.map(function (r) { return { comp: r.comp, raw: r.raw || r.name || r.text.trim(), dish_id: r.dish_id }; }) };
    var req = S.menuReq;
    api(withLang('/api/menu'), { method: 'PUT', body: body }).then(function (m) {
      if (req !== S.menuReq) return;
      S.menu = m || {}; S.ed = null; S.hist = null;
      clearResult(); renderMenuCard(); setMenuMsg(t('ed_saved'));
      setErr($('#goErr'), '');
      var a = $('#aclikIn'); if (!a.value) a.focus(); else $('#goBtn').focus();
    }).catch(function (e) {
      if (req !== S.menuReq || !S.ed) return;
      S.ed.saving = false; S.ed.err = t('ed_failed') + (netMsg(e) ? ': ' + netMsg(e) : '');
      renderEditor(); $('#edSave').focus();
    });
  }

  // ---- editor + menu events (delegated)
  var mb = $('#menuBody');
  mb.addEventListener('input', function (e) {
    var inp = e.target.closest('.ed-in'); if (!inp) return;
    var r = rowById(inp.closest('[data-row]').dataset.row); if (!r) return;
    r.text = inp.value;
    if (r.dish_id && fold(inp.value) !== fold(r.name)) { r.dish_id = null; r.name = ''; r.raw = ''; r.carb = null; }
    r.sugg = null; r.matching = false; if (r.invalid && !r.text.trim()) r.invalid = false;
    syncRow(r);
    acOpen(inp, r);
  });
  mb.addEventListener('keydown', function (e) {
    var inp = e.target.closest('.ed-in'); if (!inp) return;
    var r = rowById(inp.closest('[data-row]').dataset.row); if (!r) return;
    var open = AC.inp === inp && AC.items.length;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (!open) { acOpen(inp, r); if (AC.items.length) acMove(e.key === 'ArrowDown' ? 1 : -1); } else acMove(e.key === 'ArrowDown' ? 1 : -1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (open && AC.active >= 0) acPick(AC.active);
      else if (open && AC.items.length === 1) acPick(0);
      else { acClose(); resolveTyped(r); }
    } else if (e.key === 'Escape') { if (open) { e.preventDefault(); acClose(); } }
  });
  mb.addEventListener('focusout', function (e) {
    var inp = e.target.closest && e.target.closest('.ed-in'); if (!inp) return;
    var r = rowById(inp.closest('[data-row]').dataset.row);
    if (AC.inp === inp) acClose();
    if (r && r.text.trim() && !r.dish_id && !r.sugg && !r.matching) resolveTyped(r);
  });
  mb.addEventListener('mousedown', function (e) { if (e.target.closest('.ac-list li')) e.preventDefault(); });
  mb.addEventListener('change', function (e) {
    var sel = e.target.closest('.ed-comp'); if (!sel) return;
    var r = rowById(sel.closest('[data-row]').dataset.row); if (r) { r.comp = sel.value; r.compAuto = false; }
  });
  mb.addEventListener('click', function (e) {
    var el;
    if ((el = e.target.closest('.dish'))) { if (el.dataset.dish) openDish(el.dataset.dish, el); return; }
    if ((el = e.target.closest('.ac-list li'))) { acPick(+el.dataset.i); return; }
    if ((el = e.target.closest('[data-pick]'))) {
      var r = rowById(el.closest('[data-row]').dataset.row);
      if (r) pick(r, el.dataset.pick, el.dataset.name, r.text.trim(), true);
      return;
    }
    if ((el = e.target.closest('.ed-del'))) {
      var id = el.closest('[data-row]').dataset.row, ed = S.ed, idx = -1;
      ed.rows.forEach(function (x, i) { if (x.id === id) idx = i; });
      if (idx < 0) return;
      ed.rows.splice(idx, 1);
      if (!ed.rows.length) ed.rows.push(newRow());
      acClose(); renderEditor();
      var rowsEl = $$('#menuBody .ed-row'), tgt = rowsEl[Math.min(idx, rowsEl.length - 1)];
      if (tgt) $('.ed-in', tgt).focus();
      return;
    }
    if (e.target.closest('#edAdd')) {
      var nr = newRow(); S.ed.rows.push(nr); renderEditor();
      var ne = rowEl(nr); if (ne) $('.ed-in', ne).focus();
      return;
    }
    if ((el = e.target.closest('[data-quick]'))) { quickAdd(+el.dataset.quick); return; }
    if (e.target.closest('#edSave')) { saveMenu(); return; }
    if (e.target.closest('#edCancel')) { S.ed = null; renderMenuCard(); $('#editMenuBtn').focus(); }
  });

  // ================================================================ validation
  function readNum(input, errEl, o) {
    var raw = input.value.trim();
    var show = function (msg) { setErr(errEl, msg); input.setAttribute('aria-invalid', msg ? 'true' : 'false'); };
    if (!raw) { if (o.required) { show(t(o.req)); return NaN; } show(''); return null; }
    var v = Number(raw.replace(',', '.'));
    if (!isFinite(v)) { show(t('err_nan')); return NaN; }
    if (v < o.min || v > o.max) { show(t(o.range)); return NaN; }
    show(''); return o.dec ? Math.round(v * 10) / 10 : Math.round(v);
  }
  function readAclik() { return readNum($('#aclikIn'), $('#aclikErr'), { required: true, min: 20, max: 600, req: 'err_required', range: 'err_range' }); }
  $('#aclikIn').addEventListener('input', function () { if (this.getAttribute('aria-invalid') === 'true') readAclik(); });

  // ================================================================ similar meals query
  function clearResult() {
    S.result = null; S.summary = null; S.showAll = false;
    if (S.summaryCtrl) { S.summaryCtrl.abort(); S.summaryCtrl = null; }
    if (S.queryCtrl) { S.queryCtrl.abort(); S.queryCtrl = null; }
    $('#emptyResult').hidden = false;
    var r = $('#resStack'); if (r) r.remove();
    setBusy(false);
  }
  function setBusy(on) {
    var b = $('#goBtn');
    b.disabled = on;
    $('.btn-label', b).textContent = on ? t('showing') : t('show_btn');
    var a = $('.btn-arrow', b), s = $('.spin', b);
    if (on && !s) { s = document.createElement('span'); s.className = 'spin'; s.setAttribute('aria-hidden', 'true'); b.appendChild(s); }
    if (!on && s) s.remove();
    if (a) a.style.display = on ? 'none' : '';
  }

  $('#queryForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var aclik = readAclik();
    if (isNaN(aclik)) { $('#aclikIn').focus(); return; }
    if (!S.menu || S.ed) {
      setErr($('#goErr'), t('need_menu'));
      var i = $('#menuBody .ed-in') || $('#editMenuBtn'); if (i) i.focus();
      return;
    }
    setErr($('#goErr'), '');
    runQuery(aclik);
  });

  function runQuery(aclik) {
    clearResult();
    setBusy(true);
    S.lastAclik = aclik;
    var ctrl = new AbortController(); S.queryCtrl = ctrl;
    var q0 = { date: S.date, meal: S.meal };
    api('/api/similar', { method: 'POST', body: { date: S.date, meal: S.meal, aclik: aclik, lang: LANG }, signal: ctrl.signal }).then(function (q) {
      if (S.queryCtrl !== ctrl) return;
      S.queryCtrl = null;
      S.result = q || {};
      S.result._q = { date: q0.date, meal: q0.meal, aclik: aclik };
      if (q && q.menu && !S.ed) { S.menu = q.menu; renderMenuCard(); }
      renderResult();
      if (q && q.context) streamSummary(q.context);
      else renderFinal({ text: '', source: 'şablon' });
      var top = $('#results').getBoundingClientRect().top + window.scrollY - 110;
      window.scrollTo({ top: top, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    }).catch(function (e) {
      if (S.queryCtrl !== ctrl) return;
      S.queryCtrl = null;
      var msg = netMsg(e); if (msg === null) return;
      $('#emptyResult').hidden = true;
      var div = document.createElement('div');
      div.id = 'resStack'; div.className = 'res-stack';
      div.innerHTML = '<div class="notice err" role="alert">' + ICON.warn + '<div><h3>' + esc(t('calc_failed')) + '</h3><p>' + esc(msg) + '</p></div></div>';
      $('#results').appendChild(div);
    }).then(function () { if (!S.queryCtrl) setBusy(false); });
  }

  // ================================================================ result rendering
  function statsHtml(st, sims) {
    st = st || {};
    var n = isNum(st.n) ? st.n : sims.length;
    var cnt = { hedef: st.hedefte, hiper: st.hiper, hipo: st.hipo };
    if (!isNum(cnt.hedef) && sims.length) { cnt = { hedef: 0, hiper: 0, hipo: 0 }; sims.forEach(function (s) { var k = stOf(s.status, s.tokluk); if (cnt[k] != null) cnt[k]++; }); }
    var chips = ['hedef', 'hiper', 'hipo'].filter(function (k) { return isNum(cnt[k]) && cnt[k] > 0; })
      .map(function (k) { return '<span class="st st-' + k + '">' + esc(t('stats_' + k, { n: fmt(cnt[k]) })) + '</span>'; }).join('');
    var u = esc(t('u'));
    var insV = isNum(st.insulin_min) && isNum(st.insulin_max)
      ? (st.insulin_min === st.insulin_max ? fmtIns(st.insulin_min) : fmtIns(st.insulin_min) + '–' + fmtIns(st.insulin_max)) : '—';
    return '<section class="card stats-card" aria-labelledby="statsTitle"><h2 class="sr-only" id="statsTitle">' + esc(t('stats_title')) + '</h2>' +
      '<p class="ss-lead">' + esc(t('stats_of', { n: '\u0000' })).replace('\u0000', '<b class="tnum">' + fmt(n) + '</b>') + ' ' + chips + '</p>' +
      '<div class="ss-row">' +
        '<div class="ss ss-ins"><span class="k">' + esc(t('ss_ins', { r: st.yakin_aralik || 30 })) + '</span><span class="v">' + insV + '<small> ' + u + '</small></span>' +
          '<span class="s">' + esc(isNum(st.yakin_n) && st.yakin_n > 0 ? t('ss_ins_avg', { n: st.yakin_n }) : t('ss_none', { r: st.yakin_aralik || 30 })) + '</span></div>' +
        '<div class="ss"><span class="k">' + esc(t('ss_tok', { r: st.yakin_aralik || 30 })) + '</span><span class="v">' +
          (isNum(st.tokluk_min) ? (st.tokluk_min === st.tokluk_max ? fmt(st.tokluk_min) : fmt(st.tokluk_min) + '–' + fmt(st.tokluk_max)) : '—') + '<small> mg/dL</small></span></div>' +
        '<div class="ss"><span class="k">' + esc(t('ss_now')) + '</span><span class="v">' + fmt(S.result._q.aclik) + '<small> mg/dL</small></span></div>' +
      '</div></section>';
  }
  function insHtml(s, big) {
    var u = esc(t('u'));
    var main = isNum(s.insulin) ? '<span class="ins-pill' + (big ? ' big' : '') + '"><b>' + fmtIns(s.insulin) + '</b><small>' + u + '</small></span>' : '<span class="muted">—</span>';
    var ek = isNum(s.ekdoz) && s.ekdoz > 0 ? '<span class="ek">' + esc(t('ekdoz', { v: fmtIns(s.ekdoz), u: t('u') })) + '</span>' : '';
    return main + ek;
  }
  function whyHtml(s) {
    var why = '';
    if (isNum(s.eslesen) && isNum(s.toplam)) why += '<span class="why hl">' + t('why_match', { a: esc(String(s.eslesen)), b: esc(String(s.toplam)) }) + '</span>';
    var common = Array.isArray(s.ortak_yemek) ? s.ortak_yemek : [];
    if (common.length) why += '<span class="why hl" lang="tr">' + t('why_shared', { v: esc(common.join(', ')) }) + '</span>';
    var fam = Array.isArray(s.benzer_yemek) ? s.benzer_yemek : [];
    if (fam.length) why += '<span class="why" lang="tr">' + t('why_family', { v: esc(fam.join(', ')) }) + '</span>';
    if (isNum(s.aclik_fark)) why += '<span class="why">' + t('why_aclik', { v: esc(signed(s.aclik_fark)) }) + '</span>';
    return why;
  }
  function menuLine(s) {
    var common = Array.isArray(s.ortak_yemek) ? s.ortak_yemek : [], menu = Array.isArray(s.menu) ? s.menu : [];
    return menu.map(function (n) { return common.indexOf(n) >= 0 ? '<mark>' + esc(n) + '</mark>' : esc(n); }).join(', ');
  }
  function caseAria(s, st) {
    return t('case_aria', { d: fmtDate(s.date) + ' ' + weekday(s.date), m: mealShort(s.meal), a: fmt(s.aclik),
      i: isNum(s.insulin) ? fmtIns(s.insulin) + ' ' + t('u') + (isNum(s.ekdoz) && s.ekdoz > 0 ? ' ' + t('ekdoz', { v: fmtIns(s.ekdoz), u: t('u') }) : '') : '—',
      b: fmt(s.tokluk), s: t('st_' + st) });
  }
  function casesHtml(sims) {
    if (!sims.length) return '<p class="muted">' + esc(t('sim_none')) + '</p>';
    var shown = S.showAll ? sims : sims.slice(0, 8);
    var rows = '', cards = '';
    shown.forEach(function (s) {
      var st = stOf(s.status, s.tokluk), menu = menuLine(s), why = whyHtml(s);
      var dateS = fmtDate(s.date, { day: 'numeric', month: 'short', year: 'numeric' });
      rows += '<tr><td class="c-date"><b>' + esc(dateS) + '</b><span>' + esc(weekday(s.date)) + '</span></td>' +
        '<td class="c-l">' + esc(mealShort(s.meal)) + '</td>' +
        '<td class="c-num">' + fmt(s.aclik) + '</td>' +
        '<td class="c-ins">' + insHtml(s) + '</td>' +
        '<td class="c-post"><span class="c-num">' + fmt(s.tokluk) + '</span> ' + statusChip(st) + '</td>' +
        '<td>' + (isNum(s.carb) ? fmt(s.carb) + ' g' : '—') + '</td>' +
        '<td class="c-why">' + (why ? '<div class="sim-why">' + why + '</div>' : '') + (menu ? '<p class="sim-menu" lang="tr">' + menu + '</p>' : '') + '</td></tr>';
      cards += '<article class="case" aria-label="' + esc(caseAria(s, st)) + '">' +
        '<div class="case-top"><span class="case-date"><b>' + esc(dateS) + '</b> · ' + esc(weekday(s.date)) + '</span><span class="chip">' + esc(mealShort(s.meal)) + '</span></div>' +
        '<div class="case-flow" aria-hidden="true">' +
          '<div class="cf"><span class="lbl">' + esc(t('lbl_aclik')) + '</span><span class="v">' + fmt(s.aclik) + '</span></div>' + ICON.arrow +
          '<div class="cf cf-ins"><span class="lbl">' + esc(t('lbl_ins')) + '</span><span class="v">' + fmtIns(s.insulin) + '<small> ' + esc(t('u')) + '</small></span>' +
            (isNum(s.ekdoz) && s.ekdoz > 0 ? '<span class="ek">' + esc(t('ekdoz_short', { v: fmtIns(s.ekdoz) })) + '</span>' : '') + '</div>' + ICON.arrow +
          '<div class="cf"><span class="lbl">' + esc(t('lbl_tokluk')) + '</span><span class="v">' + fmt(s.tokluk) + '</span>' + statusChip(st) + '</div>' +
        '</div>' +
        '<div class="sim-why">' + (isNum(s.carb) ? '<span class="why">' + t('why_carb_abs', { v: esc(fmt(s.carb)) }) + '</span>' : '') + why + '</div>' +
        (menu ? '<p class="sim-menu"><span class="muted">' + esc(t('sim_menu')) + ': </span><span lang="tr">' + menu + '</span></p>' : '') + '</article>';
    });
    var more = sims.length > 8 ? '<div class="more-row"><button type="button" class="btn sm" id="moreBtn" aria-expanded="' + (S.showAll ? 'true' : 'false') + '">' +
      esc(S.showAll ? t('show_less') : t('show_more', { n: fmt(sims.length - 8) })) + '</button></div>' : '';
    return '<div class="cases-table table-wrap"><table class="cases"><thead><tr>' +
        ['c_date', 'c_meal', 'c_pre', 'c_ins', 'c_post', 'c_carb', 'c_why'].map(function (k) { return '<th scope="col">' + esc(t(k)) + '</th>'; }).join('') +
        '</tr></thead><tbody>' + rows + '</tbody></table></div>' +
      '<div class="case-cards">' + cards + '</div>' + more;
  }
  function recordHtml(p) {
    var q = S.result._q;
    return '<details class="card rec-card" id="recBox"' + (p.open ? ' open' : '') + '><summary><span class="card-title">' + esc(t('rec_title')) + '</span><span class="muted small">' + esc(t('rec_sub')) + '</span></summary>' +
      '<form id="recForm" novalidate><p class="muted small rec-intro">' + esc(t('rec_intro', { d: fmtDate(q.date), m: mealLong(q.meal), a: fmt(q.aclik) })) + '</p>' +
      '<div class="rec-grid"><div class="field"><label for="recIns">' + esc(t('rec_ins')) + ' <span class="unit">(' + esc(t('u')) + ')</span></label>' +
        '<div class="num-wrap"><input id="recIns" type="number" inputmode="decimal" min="0" max="100" step="0.5" placeholder="' + esc(t('rec_ins_ph')) + '" aria-describedby="recInsErr" required value="' + esc(p.ins || '') + '"><span class="num-unit" aria-hidden="true">' + esc(t('u')) + '</span></div>' +
        '<p class="err" id="recInsErr" role="alert" hidden></p></div>' +
      '<div class="field"><label for="recTok">' + esc(t('rec_tok')) + ' <span class="unit">mg/dL</span></label>' +
        '<div class="num-wrap"><input id="recTok" type="number" inputmode="numeric" min="20" max="600" step="1" placeholder="' + esc(t('rec_tok_ph')) + '" aria-describedby="recTokHint recTokErr" value="' + esc(p.tok || '') + '"><span class="num-unit" aria-hidden="true">mg/dL</span></div>' +
        '<p class="hint" id="recTokHint">' + esc(t('rec_tok_hint')) + '</p><p class="err" id="recTokErr" role="alert" hidden></p></div></div>' +
      '<button class="btn primary" type="submit" id="recBtn">' + esc(t('rec_save')) + '</button>' +
      '<div id="recMsg" class="rec-msg" role="status" aria-live="polite"></div></form></details>';
  }
  function renderResult(keep) {
    var q = S.result, sims = Array.isArray(q.similar) ? q.similar : [];
    var prev = { open: false, ins: '', tok: '' };
    if (keep) { var rb = $('#recBox'); if (rb) prev = { open: rb.open, ins: $('#recIns').value, tok: $('#recTok').value }; }
    var old = $('#resStack'); if (old) old.remove();
    $('#emptyResult').hidden = true;
    var stack = document.createElement('div');
    stack.id = 'resStack'; stack.className = 'res-stack';
    stack.innerHTML = (sims.length ? statsHtml(q.stats, sims) : '') +
      '<section class="card" aria-labelledby="simTitle"><h2 class="card-title" id="simTitle">' + esc(t('cases_title')) + '</h2>' +
        (sims.length ? '<p class="muted small" style="margin:-8px 0 12px">' + esc(t('cases_intro')) + '</p>' : '') +
        '<div id="casesBody">' + casesHtml(sims) + '</div></section>' +
      '<section class="card" aria-labelledby="sumTitle"><h2 class="card-title" id="sumTitle">' + esc(t('sum_title')) + '</h2>' +
        '<div class="sum-text" id="sumText" aria-live="polite">' + loadingLine('sum_loading') + '</div>' +
        '<div class="sum-meta" id="sumMeta"></div><div id="sumWhy"></div></section>' +
      recordHtml(prev);
    $('#results').appendChild(stack);
    if (keep && S.summary && !S.summaryCtrl) renderFinal(S.summary);
    $('#recForm').addEventListener('submit', submitRecord);
  }
  $('#results').addEventListener('click', function (e) {
    if (e.target.closest('#moreBtn')) {
      S.showAll = !S.showAll;
      $('#casesBody').innerHTML = casesHtml(Array.isArray(S.result.similar) ? S.result.similar : []);
      $('#moreBtn').focus();
    }
    if (e.target.closest('#recHistBtn')) { showTab('gecmis'); window.scrollTo({ top: 0 }); $('#tab-gecmis').focus(); }
  });

  // ================================================================ save result
  function submitRecord(e) {
    e.preventDefault();
    var ins = readNum($('#recIns'), $('#recInsErr'), { required: true, min: 0, max: 100, req: 'err_ins_req', range: 'err_ins_range', dec: true });
    var tok = readNum($('#recTok'), $('#recTokErr'), { required: false, min: 20, max: 600, range: 'err_range' });
    if (isNaN(ins)) { $('#recIns').focus(); return; }
    if (isNaN(tok)) { $('#recTok').focus(); return; }
    var q = S.result._q, btn = $('#recBtn'), msg = $('#recMsg');
    btn.disabled = true; btn.textContent = t('rec_saving'); msg.innerHTML = '';
    api(withLang('/api/record'), { method: 'POST', body: { date: q.date, meal: q.meal, aclik: q.aclik, insulin: ins, tokluk: tok } }).then(function () {
      S.hist = null;
      msg.innerHTML = '<div class="rec-ok">' + ICON.check + '<span>' + esc(t('rec_saved')) + '</span> <button type="button" class="btn sm" id="recHistBtn">' + esc(t('rec_open_hist')) + '</button></div>';
    }).catch(function (er) {
      msg.innerHTML = '<p class="err">' + esc(t('rec_failed') + (netMsg(er) ? ': ' + netMsg(er) : '')) + '</p>';
    }).then(function () { if (document.contains(btn)) { btn.disabled = false; btn.textContent = t('rec_save'); } });
  }

  // ================================================================ recipe dialog
  var dlg = $('#dishDlg'), lastFocus = null;
  function openDish(id, btn) {
    if (!id) return;
    lastFocus = btn || document.activeElement;
    S.recipe = null;
    var nm = btn && $('.dish-name', btn) ? $('.dish-name', btn).firstChild.textContent : t('dish');
    $('#dlgTitle').textContent = nm;
    $('#dlgBody').innerHTML = loadingLine('recipe_loading');
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    $('#dlgClose').focus();
    api('/api/recipe/' + encodeURIComponent(id)).then(function (r) {
      S.recipe = r || {};
      renderRecipe(S.recipe);
    }).catch(function (e) {
      $('#dlgBody').innerHTML = stateBox(t('recipe_failed'), netMsg(e) || '');
    });
  }
  function renderRecipe(r) {
    $('#dlgTitle').textContent = r.name || t('dish');
    $('#dlgTitle').setAttribute('lang', 'tr');
    var ings = Array.isArray(r.ingredients) ? r.ingredients : [];
    var sum = { g: 0, c: 0, p: 0, f: 0 };
    var rows = ings.map(function (x) {
      if (isNum(x.grams)) sum.g += x.grams; if (isNum(x.carb)) sum.c += x.carb; if (isNum(x.protein)) sum.p += x.protein; if (isNum(x.fat)) sum.f += x.fat;
      var u = String(x.usda || ''), mm = /^\s*(FDC\s*\d+)\s*:?\s*(.*)$/i.exec(u);
      var usda = mm ? '<span class="fdc">' + esc(mm[1]) + '</span><span class="usda-n" lang="en">' + esc(mm[2]) + '</span>' : (u ? '<span class="usda-n">' + esc(u) + '</span>' : '<span class="muted">—</span>');
      return '<tr><td lang="tr">' + esc(x.ingredient || '—') + '</td><td>' + fmt(x.grams) + '</td><td>' + fmt(x.carb, 1) + '</td><td>' + fmt(x.protein, 1) + '</td><td>' + fmt(x.fat, 1) + '</td><td class="usda">' + usda + '</td></tr>';
    }).join('');
    var g = giInfo(r.gi, r.gi_class);
    $('#dlgBody').innerHTML =
      '<div class="flow" aria-label="' + esc(t('flow_aria')) + '"><b>' + esc(t('flow1')) + '</b>→<b>' + esc(t('flow2')) + '</b>→<b>' + esc(t('flow3')) + '</b>→<b>' + esc(t('flow4')) + '</b>→<b>' + esc(t('flow5')) + '</b></div>' +
      (r.portion || r.desc ? '<p class="dlg-desc" lang="tr">' + (r.portion ? '<strong>' + esc(t('portion')) + '</strong> ' + esc(r.portion) : '') + (r.desc ? (r.portion ? ' · ' : '') + esc(r.desc) : '') + '</p>' : '') +
      '<div class="stat-row" style="margin-bottom:16px">' +
        '<div class="stat"><div class="v">' + fmt(r.carb, 1) + ' g</div><div class="k">' + esc(t('carbohydrate')) + '</div></div>' +
        '<div class="stat"><div class="v">' + fmt(r.protein, 1) + ' g</div><div class="k">' + esc(t('protein_fat', { v: fmt(r.fat, 1) })) + '</div></div>' +
        '<div class="stat"><div class="v">' + fmt(r.fiber, 1) + ' g</div><div class="k">' + esc(t('fiber_kcal', { v: fmt(r.kcal) })) + '</div></div>' +
        '<div class="stat"><div class="v">' + fmt(r.gi) + '</div><div class="k">GI · <span class="badge gi-' + g.cls + '">' + esc(g.word) + '</span></div></div>' +
      '</div>' +
      (rows ? '<div class="table-wrap"><table><caption class="mini-title" style="text-align:left;margin-top:0">' + esc(t('ingredients_cap')) + '</caption>' +
        '<thead><tr><th scope="col">' + esc(t('ingredient')) + '</th><th scope="col">' + esc(t('grams')) + '</th><th scope="col">' + esc(t('carb_s')) + '</th><th scope="col">' + esc(t('prot_s')) + '</th><th scope="col">' + esc(t('fat')) + '</th><th scope="col" style="text-align:left">USDA FoodData Central</th></tr></thead>' +
        '<tbody>' + rows + '</tbody><tfoot><tr><td>' + esc(t('total')) + '</td><td>' + fmt(sum.g) + '</td><td>' + fmt(sum.c, 1) + '</td><td>' + fmt(sum.p, 1) + '</td><td>' + fmt(sum.f, 1) + '</td><td></td></tr></tfoot></table></div>'
        : '<p class="muted">' + esc(t('no_ingredients')) + '</p>') +
      '<p class="note">' + esc(t('recipe_note')) + '</p>';
  }
  function closeDlg() { if (dlg.open) { if (typeof dlg.close === 'function') dlg.close(); else dlg.removeAttribute('open'); } }
  dlg.addEventListener('close', function () { if (lastFocus && document.contains(lastFocus)) lastFocus.focus(); });
  $('#dlgClose').addEventListener('click', closeDlg);
  dlg.addEventListener('click', function (e) { if (e.target === dlg) closeDlg(); });

  // ================================================================ summary stream
  function streamSummary(ctx) {
    if (S.summaryCtrl) S.summaryCtrl.abort();
    var ctrl = new AbortController(); S.summaryCtrl = ctrl;
    var textEl = $('#sumText'), got = '', finalSeen = false;
    var alive = function () { return S.summaryCtrl === ctrl && document.contains(textEl); };

    function onToken(tok) {
      if (!alive()) return;
      if (!got) { textEl.innerHTML = ''; textEl.classList.add('streaming'); }
      got += tok; textEl.textContent = got;
    }
    function onFinal(f) {
      finalSeen = true;
      if (!alive()) return;
      S.summaryCtrl = null;
      renderFinal(f || {});
    }
    function fallback(err) {
      if (!alive() || finalSeen) return;
      api(withLang('/api/summary'), { method: 'POST', body: ctx, signal: ctrl.signal }).then(onFinal).catch(function (e) {
        if (!alive()) return;
        S.summaryCtrl = null;
        textEl.classList.remove('streaming');
        textEl.innerHTML = '<span class="muted">' + esc(t('sum_failed')) + ' ' + esc(netMsg(e) || netMsg(err) || '') + '</span>';
        $('#sumMeta').innerHTML = '<button type="button" class="btn sm" id="sumRetry">' + esc(t('retry')) + '</button>';
        $('#sumRetry').onclick = function () { $('#sumMeta').innerHTML = ''; textEl.innerHTML = loadingLine('sum_loading'); streamSummary(ctx); };
      });
    }

    fetch(withLang('/api/summary/stream'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(ctx), signal: ctrl.signal })
      .then(function (r) {
        if (!r.ok || !r.body || !r.body.getReader) throw new Error('stream');
        var reader = r.body.getReader(), dec = new TextDecoder('utf-8'), buf = '';
        function handle(block) {
          var ev = 'message', data = [];
          block.split('\n').forEach(function (ln) {
            if (ln.indexOf('event:') === 0) ev = ln.slice(6).trim();
            else if (ln.indexOf('data:') === 0) data.push(ln.slice(5).replace(/^ /, ''));
          });
          if (!data.length) return;
          var payload; try { payload = JSON.parse(data.join('\n')); } catch (e) { return; }
          if (ev === 'token' && typeof payload === 'string') onToken(payload);
          else if (ev === 'final') onFinal(payload);
        }
        function pump() {
          return reader.read().then(function (res) {
            if (res.done) {
              buf += dec.decode();
              if (buf.trim()) handle(buf.replace(/\r\n?/g, '\n'));
              if (!finalSeen) fallback();
              return;
            }
            buf += dec.decode(res.value, { stream: true });
            buf = buf.replace(/\r\n?/g, '\n');
            var i;
            while ((i = buf.indexOf('\n\n')) >= 0) { handle(buf.slice(0, i)); buf = buf.slice(i + 2); }
            return pump();
          });
        }
        return pump();
      })
      .catch(function (e) { if (e && e.name === 'AbortError') return; fallback(e); });
  }

  function renderFinal(f) {
    var textEl = $('#sumText'), meta = $('#sumMeta'), why = $('#sumWhy');
    if (!textEl) return;
    S.summary = f;
    textEl.classList.remove('streaming');
    textEl.textContent = f.text || t('sum_none');
    var chk = f.check, badge, detail = '';
    if (f.source === 'llm' && (!chk || chk.ok !== false)) {
      badge = '<span class="src-badge ok">' + ICON.check + esc(t('badge_ok')) + '</span>';
    } else if (f.rejected != null || (chk && chk.ok === false)) {
      badge = '<span class="src-badge rej">' + ICON.warn + esc(t('badge_rej')) + '</span>';
      detail = '<details class="why-rej"><summary>' + esc(t('why_rejected')) + '</summary><div class="rej-body">' + checkReasons(chk) +
        (f.rejected ? '<div class="small muted" style="margin-top:10px">' + esc(t('rejected_text')) + '</div><blockquote>' + esc(f.rejected) + '</blockquote>' : '') + '</div></details>';
    } else {
      badge = '<span class="src-badge">' + ICON.off + esc(t('badge_off')) + '</span>';
      if (f.error) detail = '<details class="why-rej"><summary>' + esc(t('details')) + '</summary><div class="rej-body small muted">' + esc(t('llm_unreachable')) + ' <span lang="en">(' + esc(f.error) + ')</span></div></details>';
    }
    meta.innerHTML = badge + '<span class="small muted">' + esc(t('sum_note')) + '</span>';
    why.innerHTML = detail;
  }
  function checkReasons(chk) {
    if (!chk || typeof chk !== 'object') return '<p class="small">' + esc(t('chk_none')) + '</p>';
    var out = '';
    Object.keys(chk).forEach(function (k) {
      if (k === 'ok') return;
      var v = chk[k];
      if (v == null || v === false || (Array.isArray(v) && !v.length)) return;
      var val = Array.isArray(v) ? v.map(function (x) { return '<span class="chip">' + esc(typeof x === 'object' ? JSON.stringify(x) : x) + '</span>'; }).join(' ')
        : (v === true ? esc(t('yes')) : esc(typeof v === 'object' ? JSON.stringify(v) : v));
      var name = I18N.en['chk_' + k] ? t('chk_' + k) : k.replace(/_/g, ' ');
      out += '<div style="margin:4px 0"><strong>' + esc(name) + ':</strong> ' + val + '</div>';
    });
    return out || '<p class="small">' + esc(t('chk_failed')) + '</p>';
  }

  // ================================================================ HISTORY
  function hasData(x) { return !!x && (isNum(x.aclik) || isNum(x.insulin) || isNum(x.tokluk) || (Array.isArray(x.menu) && x.menu.length > 0)); }
  function normHist(h) {
    var days = Array.isArray(h && h.days) ? h.days.filter(function (d) { return d && d.date; }) : [];
    days.sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : 0; });
    var ms = {};
    days.forEach(function (d) {
      d._m = String(d.date).slice(0, 7); ms[d._m] = 1;
      d.meals = d.meals || {};
      d._f = {};
      MEALS.forEach(function (m) { var x = d.meals[m]; d._f[m] = x && Array.isArray(x.menu) ? fold(x.menu.join(' | ')) : ''; });
    });
    var months = Array.isArray(h && h.months) && h.months.length ? h.months.slice() : Object.keys(ms);
    months.sort(); months.reverse();
    return { months: months, days: days };
  }
  function loadHistory() {
    if (S.hist) { renderHistory(); return Promise.resolve(); }
    if (S.histP) return S.histP;
    $('#histBody').innerHTML = loadingLine('hist_loading');
    S.histP = api(withLang('/api/history')).then(function (h) {
      S.histP = null;
      S.hist = normHist(h);
      if (!S.histMonth || S.hist.months.indexOf(S.histMonth) < 0) S.histMonth = S.hist.months[0] || null;
      renderHistory(); renderSys();
    }).catch(function (e) {
      S.histP = null;
      $('#histBody').innerHTML = stateBox(t('hist_failed'), netMsg(e), 'retryHist');
      var b = $('#retryHist'); if (b) b.onclick = loadHistory;
    });
    return S.histP;
  }
  function syncHistSeg() {
    $$('#histMealSeg button').forEach(function (b) {
      var on = b.dataset.hmeal === S.histMeal;
      b.setAttribute('aria-checked', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1;
    });
  }
  function cellAria(x, m) {
    if (!hasData(x)) return mealShort(m) + ': ' + t('cell_none') + '.';
    var st = stOf(x.status, x.tokluk);
    return mealShort(m) + ': ' + t('lbl_aclik') + ' ' + fmt(x.aclik) + ', ' + t('lbl_ins') + ' ' + fmtIns(x.insulin) + ' ' + t('u') +
      (isNum(x.ekdoz) && x.ekdoz > 0 ? ' (' + t('ekdoz', { v: fmtIns(x.ekdoz), u: t('u') }) + ')' : '') +
      ', ' + t('lbl_tokluk') + ' ' + fmt(x.tokluk) + (st !== 'bilinmiyor' ? ' ' + t('st_' + st) : '') + '.';
  }
  function cellHtml(x, m) {
    var head = '<span class="hc-m">' + esc(mealShort(m)) + (x && srcKey(x.source) === 'kullanici' ? ' <i class="hc-user" title="' + esc(t('src_user_rec')) + '"></i>' : '') + '</span>';
    if (!hasData(x)) return '<span class="hc hc-empty">' + head + '<span class="hc-none">—</span></span>';
    if (!isNum(x.aclik) && !isNum(x.insulin) && !isNum(x.tokluk)) return '<span class="hc hc-empty">' + head + '<span class="hc-none">' + esc(t('sim_menu')) + '</span></span>';
    var st = stOf(x.status, x.tokluk);
    return '<span class="hc">' + head + '<span class="hc-flow">' +
      '<span class="hc-pre">' + fmt(x.aclik) + '</span>' + ICON.arrow +
      '<span class="hc-ins">' + (isNum(x.insulin) ? fmtIns(x.insulin) + '<small>' + esc(t('u')) + '</small>' : '—') +
        (isNum(x.ekdoz) && x.ekdoz > 0 ? '<sup>+' + fmtIns(x.ekdoz) + '</sup>' : '') + '</span>' + ICON.arrow +
      (isNum(x.tokluk) ? '<span class="st st-' + st + ' hc-post">' + fmt(x.tokluk) + '</span>' : '<span class="hc-post muted">—</span>') +
      '</span></span>';
  }
  function dayBody(d, meals, q) {
    var h = '';
    meals.forEach(function (m) {
      var x = d.meals[m]; if (!hasData(x)) return;
      var menu = Array.isArray(x.menu) ? x.menu : [];
      var facts = [];
      if (isNum(x.aclik)) facts.push(t('lbl_aclik') + ' ' + fmt(x.aclik));
      if (isNum(x.insulin)) facts.push(t('lbl_ins') + ' ' + fmtIns(x.insulin) + ' ' + t('u') + (isNum(x.ekdoz) && x.ekdoz > 0 ? ' (' + t('ekdoz', { v: fmtIns(x.ekdoz), u: t('u') }) + ')' : ''));
      if (isNum(x.tokluk)) facts.push(t('lbl_tokluk') + ' ' + fmt(x.tokluk));
      h += '<div class="hb-meal"><span class="hb-k">' + esc(mealCap(m)) + (srcKey(x.source) === 'kullanici' ? ' <span class="chip src-kullanici">' + esc(t('src_user_rec')) + '</span>' : '') + '</span>' +
        '<div><div class="hb-menu" lang="tr">' + (menu.length ? menu.map(function (n) { return markFold(n, q); }).join(', ') : '<span class="muted">' + esc(t('no_menu_rec')) + '</span>') + '</div>' +
        (facts.length ? '<div class="hb-facts muted small tnum">' + esc(facts.join(' · ')) + '</div>' : '') + '</div></div>';
    });
    var ex = [];
    if (isNum(d.yatis)) ex.push(esc(t('yatis')) + ' <b>' + fmt(d.yatis) + '</b> mg/dL');
    if (isNum(d.lantus)) ex.push(esc(t('lantus')) + ' <b>' + fmtIns(d.lantus) + '</b> ' + esc(t('u')));
    if (ex.length) h += '<div class="hb-extra tnum">' + ex.join('<span class="sep" aria-hidden="true">·</span>') + '</div>';
    return h || '<p class="muted small">—</p>';
  }
  function dayHtml(d, meals, q) {
    var open = Object.prototype.hasOwnProperty.call(S.histOpen, d.date) ? S.histOpen[d.date] : !!q;
    var id = 'hd-' + d.date;
    var label = fmtDate(d.date) + ', ' + weekday(d.date) + '. ' + meals.map(function (m) { return cellAria(d.meals[m], m); }).join(' ');
    return '<article class="hday' + (meals.length === 1 ? ' one' : '') + '"><button type="button" class="hday-head" aria-expanded="' + (open ? 'true' : 'false') + '" aria-controls="' + id + '" data-day="' + esc(d.date) + '" aria-label="' + esc(label) + '">' +
      '<span class="hd-date"><b>' + esc(fmtDate(d.date, { day: 'numeric', month: 'short' })) + '</b><span>' + esc(weekday(d.date)) + '</span></span>' +
      '<span class="hd-cells">' + meals.map(function (m) { return cellHtml(d.meals[m], m); }).join('') + '</span>' + ICON.chev + '</button>' +
      '<div class="hday-body" id="' + id + '"' + (open ? '' : ' hidden') + '>' + dayBody(d, meals, q) + '</div></article>';
  }
  function renderHistory() {
    var H = S.hist; if (!H) return;
    var q = fold(S.histQ).trim(), meals = S.histMeal === 'all' ? MEALS : [S.histMeal];
    var sel = $('#histMonth');
    sel.innerHTML = H.months.map(function (m) { return '<option value="' + esc(m) + '"' + (m === S.histMonth ? ' selected' : '') + '>' + esc(monthLabel(m)) + '</option>'; }).join('');
    sel.disabled = !!q || !H.months.length;
    syncHistSeg();
    var days = q ? H.days.filter(function (d) { return meals.some(function (m) { return d._f[m].indexOf(q) >= 0; }); })
      : H.days.filter(function (d) { return d._m === S.histMonth; });
    if (S.histMeal !== 'all') days = days.filter(function (d) { return hasData(d.meals[S.histMeal]); });
    var total = days.length, CAP = 120, capped = q && total > CAP;
    if (capped) days = days.slice(0, CAP);
    // summary
    var pts = [], c = { hedef: 0, hiper: 0, hipo: 0 }, insMin = Infinity, insMax = -Infinity;
    days.forEach(function (d) {
      meals.forEach(function (m) {
        var x = d.meals[m]; if (!x) return;
        if (isNum(x.insulin)) { insMin = Math.min(insMin, x.insulin); insMax = Math.max(insMax, x.insulin); }
        if (isNum(x.tokluk)) { var st = stOf(x.status, x.tokluk); if (c[st] != null) c[st]++; pts.push({ date: d.date, mi: MEALS.indexOf(m), v: x.tokluk, st: st }); }
      });
    });
    var chips = ['hedef', 'hiper', 'hipo'].filter(function (k) { return c[k] > 0; }).map(function (k) { return '<span class="st st-' + k + '">' + esc(t('stats_' + k, { n: fmt(c[k]) })) + '</span>'; }).join('');
    var head = q ? esc(t('hist_found', { n: fmt(total), q: S.histQ.trim() })) + (capped ? esc(t('hist_capped', { n: fmt(CAP) })) : '')
      : '<b>' + esc(monthLabel(S.histMonth)) + '</b> · ' + esc(t('hist_sum', { n: fmt(pts.length) }));
    $('#histSummary').innerHTML = '<div class="card hsum"><div class="hsum-row"><span>' + head + '</span>' + chips +
      (insMin <= insMax ? '<span class="muted small tnum">' + esc(t('hist_ins_sum', { a: fmtIns(insMin), b: fmtIns(insMax), u: t('u') })) + '</span>' : '') + '</div>' +
      (!q ? '<div id="spark"></div>' : '') + '</div>';
    S.spark = !q ? { pts: pts, month: S.histMonth, c: c } : null;
    drawSpark();
    $('#histBody').innerHTML = days.length ? '<div class="hlist">' + days.map(function (d) { return dayHtml(d, meals, q); }).join('') + '</div>' : stateBox(t('hist_none'), '');
  }
  function drawSpark() {
    var host = $('#spark'), sp = S.spark;
    if (!host || !sp || $('#panel-gecmis').hidden) return;
    if (sp.pts.length < 2) { host.innerHTML = ''; return; }
    var W = Math.max(260, host.clientWidth), H = 96, L = 32, R = 8, T = 6, B = 18;
    var m = /^(\d{4})-(\d{2})/.exec(sp.month), dim = m ? new Date(+m[1], +m[2], 0).getDate() : 31;
    var hiV = Math.max(300, Math.max.apply(null, sp.pts.map(function (p) { return p.v; })) + 10), loV = 40;
    var xf = function (p) { return L + ((+p.date.slice(8, 10) - 1) + (p.mi + 1) / 4) / dim * (W - L - R); };
    var yf = function (v) { return T + (1 - (clamp(v, loV, hiV) - loV) / (hiV - loV)) * (H - T - B); };
    var pts = sp.pts.slice().sort(function (a, b) { return xf(a) - xf(b); });
    var s = '<rect class="zone" x="' + L + '" y="' + yf(180) + '" width="' + (W - L - R) + '" height="' + (yf(70) - yf(180)) + '"/>';
    [70, 180].forEach(function (v) { s += '<line class="gl" x1="' + L + '" x2="' + (W - R) + '" y1="' + yf(v) + '" y2="' + yf(v) + '"/><text x="' + (L - 5) + '" y="' + (yf(v) + 3.5) + '" text-anchor="end">' + v + '</text>'; });
    [1, 10, 20, dim].forEach(function (dd) { s += '<text x="' + (L + (dd - 0.5) / dim * (W - L - R)) + '" y="' + (H - 4) + '" text-anchor="middle">' + dd + '</text>'; });
    s += '<polyline class="ln" points="' + pts.map(function (p) { return xf(p).toFixed(1) + ',' + yf(p.v).toFixed(1); }).join(' ') + '"/>';
    pts.forEach(function (p) { s += '<circle class="d-' + p.st + '" cx="' + xf(p).toFixed(1) + '" cy="' + yf(p.v).toFixed(1) + '" r="3"/>'; });
    host.innerHTML = '<svg class="spark" role="img" viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" style="width:100%;height:auto" aria-label="' +
      esc(t('spark_aria', { n: fmt(sp.pts.length), h: fmt(sp.c.hedef), y: fmt(sp.c.hiper), l: fmt(sp.c.hipo) })) + '">' + s + '</svg>';
  }
  $('#histMonth').addEventListener('change', function () { S.histMonth = this.value; S.histOpen = {}; renderHistory(); });
  $$('#histMealSeg button').forEach(function (b) {
    b.addEventListener('click', function () { S.histMeal = b.dataset.hmeal; renderHistory(); });
    b.addEventListener('keydown', function (e) {
      if (['ArrowRight', 'ArrowLeft', 'ArrowDown', 'ArrowUp'].indexOf(e.key) < 0) return;
      e.preventDefault();
      var btns = $$('#histMealSeg button'), i = btns.indexOf(b), d = (e.key === 'ArrowRight' || e.key === 'ArrowDown') ? 1 : -1;
      var n = btns[(i + d + btns.length) % btns.length];
      S.histMeal = n.dataset.hmeal; renderHistory(); n.focus();
    });
  });
  var hqT = null;
  $('#histQ').addEventListener('input', function () {
    var v = this.value; clearTimeout(hqT);
    hqT = setTimeout(function () { S.histQ = v; S.histOpen = {}; renderHistory(); }, 140);
  });
  $('#histBody').addEventListener('click', function (e) {
    var b = e.target.closest('.hday-head'); if (!b) return;
    var open = b.getAttribute('aria-expanded') !== 'true';
    b.setAttribute('aria-expanded', open ? 'true' : 'false');
    S.histOpen[b.dataset.day] = open;
    var body = document.getElementById(b.getAttribute('aria-controls')); if (body) body.hidden = !open;
  });

  // ================================================================ model report
  var MAE_ROWS = [];
  function groupOf(name) {
    var n = String(name);
    if (/^B\d/.test(n)) return { key: 'base', tag: t('g_base') };
    if (/^M\d/.test(n)) return { key: 'model', tag: t('g_model') };
    if (/^A:/.test(n)) return { key: 'abl', tag: t('g_abl') };
    if (/^i:/.test(n)) return { key: 'info', tag: t('g_info') };
    return { key: 'other', tag: '' };
  }
  function cleanName(n) { return term(String(n).replace(/^(A|i):\s*/, '')); }

  function loadModel() {
    if (S.report || S.modelLoading) return;
    S.modelLoading = true;
    var body = $('#modelBody');
    body.innerHTML = '<div class="card"><div class="skel skel-lg"></div><div class="skel"></div><div class="skel"></div><div class="skel"></div></div>';
    api('/api/report').then(function (r) { S.modelLoading = false; S.report = r || {}; renderModel(S.report); }).catch(function (e) {
      S.modelLoading = false;
      body.innerHTML = stateBox(t('report_failed'), netMsg(e), 'retryModel');
      var b = $('#retryModel'); if (b) b.onclick = loadModel;
    });
  }

  function sectionHead(id, title, intro) {
    return '<section class="card" aria-labelledby="' + id + '"><h2 class="card-title" id="' + id + '">' + esc(title) + '</h2>' +
      (intro ? '<p class="muted small" style="margin:-8px 0 14px">' + esc(intro) + '</p>' : '');
  }

  function metricTable(res, finalLabel) {
    var names = Object.keys(res || {});
    if (!names.length) return '';
    var vals = names.map(function (n) { return res[n] || {}; });
    var bestMae = Math.min.apply(null, vals.map(function (v) { return isNum(v.mae) ? v.mae : Infinity; }).concat([Infinity]));
    var rows = names.map(function (n) {
      var v = res[n] || {}, g = groupOf(n), isFinal = finalLabel && n === finalLabel;
      var ci = Array.isArray(v.mae_ci95) && v.mae_ci95.length === 2 ? '<div class="ci">' + fmt(v.mae_ci95[0], 1) + '–' + fmt(v.mae_ci95[1], 1) + '</div>' : '';
      var hiperMiss = isNum(v.hiper_kacan) ? v.hiper_kacan : (isNum(v.hiper_gercek) && isNum(v.hiper_yakalanan) ? v.hiper_gercek - v.hiper_yakalanan : null);
      var cls = (g.key === 'base' ? 'g-base' : g.key === 'info' ? 'g-info' : '') + (isFinal ? ' is-final' : '');
      return '<tr class="' + cls.trim() + '"><td>' + (isFinal ? '<span class="gtag final">' + esc(t('g_final')) + '</span>' : (g.tag ? '<span class="gtag">' + esc(g.tag) + '</span>' : '')) + esc(cleanName(n)) + '</td>' +
        '<td' + (v.mae === bestMae ? ' class="best"' : '') + '>' + fmt(v.mae, 1) + ci + '</td>' +
        '<td>' + pct(v.kapsama) + '</td><td>' + fmt(v.aralik_genislik) + '</td>' +
        '<td>' + fmt(v.hiper_yakalanan) + (isNum(v.hiper_gercek) ? '<span class="ci">/' + fmt(v.hiper_gercek) + '</span>' : '') + '</td><td>' + fmt(hiperMiss) + '</td><td>' + fmt(v.hiper_yanlis_alarm) + '</td>' +
        '<td>' + fmt(v.hipo_yakalanan) + (isNum(v.hipo_gercek) ? '<span class="ci">/' + fmt(v.hipo_gercek) + '</span>' : '') + '</td><td>' + fmt(v.hipo_yanlis_alarm) + '</td></tr>';
    }).join('');
    var n0 = vals[0] && isNum(vals[0].n) ? vals[0].n : null;
    return '<div class="table-wrap" tabindex="0" role="region" aria-label="' + esc(t('tbl_aria')) + '"><table>' +
      '<thead><tr class="grp"><th></th><th colspan="3"></th><th colspan="3" scope="colgroup">' + t('th_hiper') + '</th><th colspan="2" scope="colgroup">' + t('th_hipo') + '</th></tr>' +
      '<tr><th scope="col">' + t('th_model') + '</th><th scope="col">' + t('th_mae') + '</th><th scope="col">' + t('th_cov') + '</th><th scope="col">' + t('th_width') + '</th>' +
      '<th scope="col">' + t('th_caught') + '</th><th scope="col">' + t('th_missed') + '</th><th scope="col">' + t('th_false') + '</th><th scope="col">' + t('th_caught') + '</th><th scope="col">' + t('th_false') + '</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table></div>' +
      '<p class="note">' + esc(t('tbl_note') + (n0 ? t('n_meals', { v: fmt(n0) }) : '')) + '</p>';
  }

  function diffTable(fk) {
    if (!fk || typeof fk !== 'object' || !Object.keys(fk).length) return '';
    return '<details class="more"><summary>' + esc(t('diffs')) + '</summary><div class="table-wrap"><table><thead><tr><th scope="col">' + esc(t('th_cmp')) + '</th><th scope="col">' + esc(t('th_ci')) + '</th><th scope="col">' + esc(t('th_result')) + '</th></tr></thead><tbody>' +
      Object.keys(fk).map(function (k) {
        var a = fk[k]; if (!Array.isArray(a) || a.length < 2 || !isNum(a[0]) || !isNum(a[1])) return '';
        var sig = a[0] > 0 || a[1] < 0;
        return '<tr><td>' + esc(term(k)) + '</td><td>' + fmt(a[0], 1) + ' … ' + fmt(a[1], 1) + '</td><td>' + (sig ? '<strong>' + esc(t('sig')) + '</strong>' : '<span class="muted">' + esc(t('nosig')) + '</span>') + '</td></tr>';
      }).join('') + '</tbody></table></div><p class="note">' + esc(t('diffs_note')) + '</p></details>';
  }

  function pickFindings(r) {
    var f = r.findings || (r.results_cv && r.results_cv.findings);
    if (!f || typeof f !== 'object') return null;
    if (f[LANG] && typeof f[LANG] === 'object') return f[LANG];
    if (f.en || f.tr) return f.en || f.tr;
    return f;
  }

  function renderModel(r) {
    var html = '', fm = r.final_model || {}, finalLabel = fm.label;
    var f = pickFindings(r);
    if (f && (f.title || (Array.isArray(f.bullets) && f.bullets.length))) {
      html += '<section class="card findings"><h2 class="card-title">' + esc(f.title || t('findings')) + '</h2>' +
        (Array.isArray(f.bullets) ? '<ul>' + f.bullets.map(function (b) { return '<li>' + esc(b) + '</li>'; }).join('') + '</ul>' : '') + '</section>';
    }
    if (fm && fm.label) {
      html += '<section class="card"><div class="eyebrow plain">' + esc(t('model_used')) + '</div><h2 class="card-title" style="font-size:1.3rem;margin-bottom:6px">' + esc(term(fm.label)) + '</h2>' +
        '<p class="muted small">' + (LANG === 'tr' && fm.note ? esc(fm.note) : '') + (isNum(fm.inner_mae) ? esc(t('inner_mae', { v: fmt(fm.inner_mae, 1) })) : '') +
        (fm.knn && isNum(fm.knn.k) ? esc(t('k_neigh', { v: fmt(fm.knn.k) })) : '') + '</p></section>';
    }

    var cv = r.results_cv && r.results_cv.cv;
    MAE_ROWS = [];
    if (cv && typeof cv === 'object' && Object.keys(cv).length) {
      MAE_ROWS = Object.keys(cv).map(function (n) { return { name: n, v: cv[n] || {}, g: groupOf(n), final: n === finalLabel }; })
        .filter(function (x) { return isNum(x.v.mae); });
      html += sectionHead('cvTitle', t('cv_title'), t('cv_intro')) +
        '<h3 class="mini-title" style="margin-top:0">' + esc(t('mae_chart_title')) + '</h3><div id="maeChart"></div>' +
        '<h3 class="mini-title">' + esc(t('all_metrics')) + '</h3>' + metricTable(cv, finalLabel) + diffTable(r.results_cv.farklar);
      var gr = r.results_cv.gruplar;
      if (gr && typeof gr === 'object' && Object.keys(gr).length) {
        var gnames = Object.keys(gr);
        var dims = [['ogun', t('dim_ogun'), function (k) { return mealShort(k); }], ['aclik', t('dim_aclik'), function (k) { return k + ' mg/dL'; }],
          ['ay', t('dim_ay'), function (k) { var d = new Date(2026, (+k || 1) - 1, 1); return cap1(d.toLocaleDateString(loc(), { month: 'long' })); }]];
        html += '<details class="more"><summary>' + esc(t('groups')) + '</summary>';
        dims.forEach(function (dm) {
          var keys = {};
          gnames.forEach(function (g) { Object.keys((gr[g] || {})[dm[0]] || {}).forEach(function (k) { keys[k] = 1; }); });
          var ks = Object.keys(keys); if (!ks.length) return;
          html += '<h3 class="mini-title">' + esc(dm[1]) + '</h3><div class="table-wrap"><table><thead><tr><th scope="col">' + t('th_model') + '</th>' + ks.map(function (k) { return '<th scope="col">' + esc(dm[2](k)) + '</th>'; }).join('') + '</tr></thead><tbody>' +
            gnames.map(function (g) { var row = (gr[g] || {})[dm[0]] || {}; return '<tr class="' + (groupOf(g).key === 'base' ? 'g-base' : '') + (g === finalLabel ? ' is-final' : '') + '"><td>' + esc(cleanName(g)) + '</td>' + ks.map(function (k) { return '<td>' + fmt(row[k], 1) + '</td>'; }).join('') + '</tr>'; }).join('') +
            '</tbody></table></div>';
        });
        html += '</details>';
      }
      html += '</section>';
    }

    var test = r.results_test && (r.results_test.test || r.results_test);
    if (test && typeof test === 'object') {
      var tclean = {}; Object.keys(test).forEach(function (k) { if (test[k] && isNum(test[k].mae)) tclean[k] = test[k]; });
      if (Object.keys(tclean).length) {
        html += sectionHead('testTitle', t('test_title'), t('test_intro')) + metricTable(tclean, finalLabel) + diffTable(r.results_test.farklar) + '</section>';
      }
    }

    var bo = r.llm_bakeoff;
    var boRes = bo && typeof bo === 'object' ? (bo.sonuc || bo.models || bo) : null;
    if (boRes && typeof boRes === 'object') {
      var bnames = Object.keys(boRes).filter(function (k) { return boRes[k] && typeof boRes[k] === 'object' && !Array.isArray(boRes[k]); });
      if (bnames.length) {
        var ratio = function (v) { return isNum(v) ? (v <= 1 ? pct(v, 0) : fmt(v, 1)) : (v != null && v !== '' ? esc(v) : '—'); };
        html += sectionHead('boTitle', t('bo_title'), t('bo_intro')) +
          '<div class="table-wrap" tabindex="0" role="region" aria-label="' + esc(t('bo_aria')) + '"><table><thead><tr><th scope="col">' + t('th_model') + '</th><th scope="col">' + t('th_pass') + '</th><th scope="col">' + t('th_numfaith') + '</th><th scope="col">' + t('th_forbid') + '</th><th scope="col">' + t('th_hipofirst') + '</th><th scope="col">' + t('th_words') + '</th><th scope="col">' + t('th_time') + '</th><th scope="col">token/s</th><th scope="col">' + t('th_vram') + '</th></tr></thead><tbody>' +
          bnames.map(function (n) {
            var v = boRes[n];
            return '<tr><td>' + esc(n) + '</td><td><strong>' + ratio(v.gecen_oran) + '</strong></td><td>' + ratio(v.sayi_sadakati) + '</td><td>' + ratio(v.yasak_dil_orani) + '</td><td>' + ratio(v.hipo_ilk_cumle) + '</td><td>' + fmt(v.ort_kelime) + '</td><td>' + fmt(v.ort_sure_s, 1) + '</td><td>' + fmt(v.tok_per_s, 1) + '</td><td>' + fmt(v.vram_mb) + '</td></tr>';
          }).join('') + '</tbody></table></div></section>';
      }
    }

    var me = r.matcher_eval;
    if (me && me.sonuc && typeof me.sonuc === 'object' && Object.keys(me.sonuc).length) {
      var mk = Object.keys(me.sonuc);
      html += sectionHead('meTitle', t('me_title'), t('me_intro')) +
        '<div class="table-wrap"><table><thead><tr><th scope="col">' + esc(t('th_method')) + '</th><th scope="col">n</th><th scope="col">' + esc(t('th_acc1')) + '</th><th scope="col">' + esc(t('th_rec5')) + '</th><th scope="col">MRR</th></tr></thead><tbody>' +
        mk.map(function (k) { var v = me.sonuc[k] || {}; return '<tr><td>' + esc(term(k)) + '</td><td>' + fmt(v.n) + '</td><td><strong>' + pct(v.acc1) + '</strong></td><td>' + pct(v.recall5) + '</td><td>' + fmt(v.mrr, 3) + '</td></tr>'; }).join('') +
        '</tbody></table></div>';
      var errs = me.hatalar && me.hatalar[mk[0]];
      if (Array.isArray(errs) && errs.length) {
        html += '<details class="more"><summary>' + esc(t('me_errs', { n: fmt(errs.length) })) + '</summary><div class="table-wrap"><table lang="tr"><thead><tr><th scope="col">' + esc(t('th_query')) + '</th><th scope="col" style="text-align:left">' + esc(t('th_true')) + '</th><th scope="col" style="text-align:left">' + esc(t('th_pred')) + '</th></tr></thead><tbody>' +
          errs.map(function (x) { return '<tr><td>' + esc(x.sorgu) + '</td><td style="text-align:left">' + esc(x.dogru) + '</td><td style="text-align:left" class="muted">' + esc(x.tahmin) + '</td></tr>'; }).join('') + '</tbody></table></div></details>';
      }
      html += '</section>';
    }

    var nv = r.nutrition_validation;
    if (nv && (isNum(nv.mae_g) || Array.isArray(nv.satirlar))) {
      html += sectionHead('nvTitle', t('nv_title'), t('nv_intro')) +
        '<div class="stat-row"><div class="stat"><div class="v">' + fmt(nv.n) + '</div><div class="k">' + esc(t('nv_n')) + '</div></div><div class="stat"><div class="v">' + fmt(nv.mae_g, 1) + ' g</div><div class="k">' + esc(t('nv_mae')) + '</div></div>' +
        '<div class="stat"><div class="v">' + pct(nv.medyan_bagil_hata, 0) + '</div><div class="k">' + esc(t('nv_rel')) + '</div></div><div class="stat"><div class="v">' + signed(nv.bias_g, 1) + ' g</div><div class="k">' + esc(t('nv_bias')) + '</div></div></div>';
      if (Array.isArray(nv.satirlar) && nv.satirlar.length) {
        html += '<details class="more"><summary>' + esc(t('nv_rows')) + '</summary><div class="table-wrap"><table><thead><tr><th scope="col">' + esc(t('th_dish')) + '</th><th scope="col">' + esc(t('th_recipe')) + '</th><th scope="col">' + esc(t('th_ref')) + '</th><th scope="col">' + esc(t('th_diff')) + '</th><th scope="col" style="text-align:left">' + esc(t('th_usda')) + '</th></tr></thead><tbody>' +
          nv.satirlar.map(function (x) { return '<tr><td lang="tr">' + esc(x.yemek) + '</td><td>' + fmt(x.tarif_karb, 1) + '</td><td>' + fmt(x.referans_karb, 1) + '</td><td>' + signed(x.fark, 1) + '</td><td class="usda"><span class="usda-n" lang="en">' + esc(x.usda || '') + '</span></td></tr>'; }).join('') +
          '</tbody></table></div>' + (LANG === 'tr' && nv.yontem ? '<p class="note">' + esc(nv.yontem) + '</p>' : '') + '</details>';
      }
      html += '</section>';
    }

    html += genericSection('retEvalTitle', t('ret_title'), t('ret_intro'), r.retrieval_eval);
    html += genericSection('ragasTitle', t('ragas_title'), t('ragas_intro'), r.ragas);

    if (!html) html = stateBox(t('no_report'), t('no_report_text'));
    $('#modelBody').innerHTML = html;
    drawMaeChart();
  }

  // Defensive renderer for report sections whose shape is not fixed.
  function gnum(v) {
    if (!isNum(v)) return v == null ? '—' : esc(typeof v === 'object' ? JSON.stringify(v) : v);
    if (Number.isInteger(v)) return fmt(v);
    return Math.abs(v) <= 1 ? fmt(v, 3) : fmt(v, 1);
  }
  function genericSection(id, title, desc, obj) {
    if (!obj || typeof obj !== 'object') return '';
    var root = obj;
    if (obj[LANG] && typeof obj[LANG] === 'object') root = obj[LANG];
    ['sonuc', 'results', 'metrics', 'sonuclar'].forEach(function (k) { if (root[k] && typeof root[k] === 'object' && !Array.isArray(root[k])) root = root[k]; });
    var notes = [], flat = {}, rows = {};
    Object.keys(root).forEach(function (k) {
      var v = root[k];
      if (isNum(v)) flat[k] = v;
      else if (typeof v === 'string') notes.push(v);
      else if (v && typeof v === 'object' && !Array.isArray(v) && Object.keys(v).some(function (x) { return isNum(v[x]); })) rows[k] = v;
    });
    if (root !== obj) Object.keys(obj).forEach(function (k) { if (typeof obj[k] === 'string') notes.push(obj[k]); });
    var rk = Object.keys(rows), fk = Object.keys(flat);
    if (!rk.length && !fk.length) return '';
    var h = sectionHead(id, title, desc);
    if (fk.length) h += '<div class="stat-row" style="margin-bottom:' + (rk.length ? '14px' : '0') + '">' + fk.map(function (k) { return '<div class="stat"><div class="v">' + gnum(flat[k]) + '</div><div class="k">' + esc(term(k.replace(/_/g, ' '))) + '</div></div>'; }).join('') + '</div>';
    if (rk.length) {
      var cols = [];
      rk.forEach(function (r) { Object.keys(rows[r]).forEach(function (c) { if (isNum(rows[r][c]) && cols.indexOf(c) < 0) cols.push(c); }); });
      h += '<div class="table-wrap" tabindex="0" role="region" aria-label="' + esc(title) + '"><table><thead><tr><th scope="col"></th>' + cols.map(function (c) { return '<th scope="col">' + esc(term(c.replace(/_/g, ' '))) + '</th>'; }).join('') + '</tr></thead><tbody>' +
        rk.map(function (r) { return '<tr><td>' + esc(term(r)) + '</td>' + cols.map(function (c) { return '<td>' + gnum(rows[r][c]) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
    }
    if (notes.length) h += '<details class="more"><summary>' + esc(t('method')) + '</summary><p class="note" style="white-space:pre-wrap">' + esc(notes.join('\n\n')) + '</p></details>';
    return h + '</section>';
  }

  function drawMaeChart() {
    var host = $('#maeChart');
    if (!host || !MAE_ROWS.length || $('#panel-model').hidden) return;
    var W = Math.max(280, host.clientWidth), rows = MAE_ROWS;
    var lo = Infinity, hi = -Infinity;
    rows.forEach(function (r) { var c = Array.isArray(r.v.mae_ci95) ? r.v.mae_ci95 : [r.v.mae, r.v.mae]; lo = Math.min(lo, c[0], r.v.mae); hi = Math.max(hi, c[1], r.v.mae); });
    lo = Math.floor(lo - 1); hi = Math.ceil(hi + 1);
    var wide = W >= 640, labW = wide ? 250 : 0, L = labW + 8, R = 14, rowH = wide ? 26 : 38, top = 8;
    var H = top + rows.length * rowH + 30;
    var x = function (v) { return L + (v - lo) / (hi - lo) * (W - L - R); };
    var s = '';
    var step = (hi - lo) > 12 ? 4 : 2;
    for (var tk = Math.ceil(lo / step) * step; tk <= hi; tk += step) {
      s += '<line class="grid" x1="' + x(tk) + '" x2="' + x(tk) + '" y1="' + top + '" y2="' + (H - 22) + '"/><text class="ax" x="' + x(tk) + '" y="' + (H - 8) + '" text-anchor="middle">' + fmt(tk) + '</text>';
    }
    var fin = rows.filter(function (r) { return r.final; })[0];
    if (fin) s += '<line class="ref" x1="' + x(fin.v.mae) + '" x2="' + x(fin.v.mae) + '" y1="' + top + '" y2="' + (H - 22) + '"/>';
    rows.forEach(function (r, i) {
      var c = Array.isArray(r.v.mae_ci95) ? r.v.mae_ci95 : [r.v.mae, r.v.mae];
      var cy = top + i * rowH + (wide ? rowH / 2 : rowH - 10);
      var cls = r.final ? 'r-final' : r.g.key === 'base' ? 'r-base' : '';
      var nm = (r.g.key === 'base' ? t('base_prefix') : r.final ? '★ ' : '') + cleanName(r.name);
      s += '<g class="' + cls + '"><text x="' + (wide ? labW : L) + '" y="' + (wide ? cy + 4 : cy - 10) + '" text-anchor="' + (wide ? 'end' : 'start') + '">' + esc(nm) + '</text>' +
        '<line class="ci-l" x1="' + x(c[0]) + '" x2="' + x(c[1]) + '" y1="' + cy + '" y2="' + cy + '"/>' +
        '<circle class="dot" cx="' + x(r.v.mae) + '" cy="' + cy + '" r="' + (r.final ? 5.5 : 4.5) + '"/></g>';
    });
    host.innerHTML = '<svg class="mae-chart" role="img" viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" style="width:100%;height:auto" aria-label="' +
      esc(t('mae_aria', { list: rows.map(function (r) { return cleanName(r.name) + ' ' + fmt(r.v.mae, 1); }).join('; ') })) + '">' + s + '</svg>' +
      '<p class="note">' + esc(t('mae_note')) + '</p>';
  }
  var rT = null;
  window.addEventListener('resize', function () { clearTimeout(rT); rT = setTimeout(function () { drawMaeChart(); drawSpark(); }, 120); });

  // ================================================================ start
  applyStatic();
  showTab('bugun');
  renderSys();
  loadStatus();
  loadDishes();
  S.meal = mealByClock(); syncMealSeg();
  api('/api/today').then(function (d) { var sn = document.getElementById('synNote'); if (sn && d && d.synthetic) sn.hidden = false; S.today = d && d.date ? String(d.date).slice(0, 10) : localISO(new Date()); })
    .catch(function () { S.today = localISO(new Date()); })
    .then(function () { S.date = S.today; $('#dateIn').value = S.date; renderDateInfo(); loadMenu(); });
})();
