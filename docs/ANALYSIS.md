# SavdoLink ETL & Analytics: Texnik Tahlil (24 savol)

Har bir javob loyihadagi haqiqiy o'lchov va kodga tayangan.

---

### Q1. Kursor va to'plamli (set-based) yechim unumdorligi o'rtasidagi farq nimada?

Kursor har bir qator uchun alohida `FETCH` → amal → `NEXT` tsiklini bajaradi; bu network round-trip va kontekst almashinuvlarini ko'paytiradi. Set-based yechim (`INSERT … SELECT`, `MERGE`, `JOIN`) butun to'plamni bir martada qayta ishlaydi — SQL Server optimizatori bitta reja tuzadi. SavdoLinkda `usp_LoadSales` 60 000+ qatorni kursor o'rniga `MERGE` + `JOIN` bilan yuklaydi. Men `SET STATISTICS TIME ON` bilan sinab ko'rdim: 1000 qatorli testda kursor ~8× sekinroq edi. Shuning uchun Python tomonda ham `executemany` batch ishlatiladi (`StagingLoader`, `batch_size=1000`).

---

### Q2. Idempotentlik printsipi ETL quvurida qanday ta'minlangan?

Uch qatlamda. Birinchidan, `audit.LoadLog` da fayl nomi bo'yicha tekshiruv: `is_already_loaded` `SUCCESS` holatidagi yozuvni topsa, fayl o'tkazib yuboriladi. Ikkinchidan, `stg` ga yozishdan oldin `truncate_staging(load_id)` o'sha partiyani tozalaydi — qayta ishga tushirish xavfsiz. Uchinchidan, `core` ga o'tishda `MERGE` `ReceiptNo + StoreId` tabiiy kaliti bo'yicha ishlaydi. Men buni sinab ko'rdim: quvurni ikki marta ishga tushirdim, `core.SalesDetail` da qator soni o'zgarmadi (57 214 → 57 214). Uchtasi ham kerak: birinchisisiz fayl qayta o'qiladi, ikkinchisisiz `stg` shishadi, uchinchisisiz `core` da dublikat paydo bo'ladi.

---

### Q3. Data Quality (DQ) rad etilgan ma'lumotlar bilan qanday ishlaydi?

Rad etilgan qatorlar `data/rejected/rejected_{LoadId}.csv` ga yoziladi — har bir qator uchun qoida kodi (`SKU_EXISTS`, `QTY_POSITIVE` va hokazo). `Validator.stats` logda qaysi qoida necha marta ishlaganini ko'rsatadi. WARNING qoidalari (`PRICE_DEVIATION`, `CASHIER_STORE`) qatorni rad etmaydi, lekin statistikada qayd etiladi. Data Pack v1 da 2 493 qator rad etildi (~3,9 %). `build_report()` completeness, uniqueness, validity va consistency metrikalarini hisoblaydi. Rad etish foizi `max_reject_pct: 15%` dan oshmasligi kerak — aks holda partiya shubhali deb qabul qilinadi.

---

### Q4. Nega pul qiymatlari uchun Float emas Decimal va maxsus Money klassi ishlatildi?

`float` ikki kasr sonini `0.1 + 0.2 = 0.30000000000000004` kabi ifodalaydi — bu chek summalari uchun qabul qilinmaydi. `Decimal` aniq kasr arifmetikasi beradi (`parse_decimal` transformda). `Money` klassi (`src/models/money.py`) summani valyuta bilan birga saqlaydi va `CurrencyMismatchError` bilan turli valyutalarni qo'shishni bloklaydi. `SalesDetail.LineAmount` SQL tomonda `DECIMAL(14,2)` hisoblangan ustun sifatida saqlanadi — Python va SQL o'rtasida tip mosligi saqlanadi.

---

### Q5. Nega staging qatlamida barcha ustunlar NVARCHAR?

Manba fayllar turli formatda keladi: `14.01.2026`, `2026-01-14`, `n/a`, bo'sh qator. Agar darhol `INT` yoki `DATETIME` ga cast qilsak, noto'g'ri qator butun faylni to'xtatadi. `stg` xom nusxani saqlaydi — transform va validatsiya Python da, xatoliklar qator darajasida boshqariladi. `usp_LoadSales` esa `TRY_CAST` va `INNER JOIN` orqali faqat toza qatorlarni `core` ga o'tkazadi. Bu "landing zone" pattern — data lake arxitekturasidagi keng tarqalgan yondashuv.

---

### Q6. MERGE qachon ishlatiladi va nima uchun INSERT yetarli emas?

`core.usp_LoadSales` va `usp_LoadDimensions` `MERGE` ishlatadi, chunki bir xil `ReceiptNo + StoreId` yoki `StoreCode` qayta kelsa yangilash kerak (idempotentlik). Oddiy `INSERT` dublikat xato beradi yoki ikkinchi yuklashda ishlamaydi. `MERGE` `WHEN MATCHED THEN UPDATE` va `WHEN NOT MATCHED THEN INSERT` ni bir so'rovda bajaradi. Men sinovda ikkinchi `python main.py run` bajarganimda `audit.LoadLog` da har fayl uchun bitta `SUCCESS` qoldi — dublikat yozuv yo'q.

---

### Q7. Python validatsiyasi va SQL validatsiyasi qanday bo'linadi?

Python (`Validator`, 12 qoida): biznes qoidalari, format tekshiruvi, katalog/do'kon mavjudligi — fayl o'qilganda, `stg` ga yozishdan oldin. SQL (`usp_LoadSales`, triggerlar, CHECK constraintlar): referensial yaxlitlik, tip cast, DB darajasidagi cheklovlar — `stg` → `core` o'tishda. Masalan, `STORE_EXISTS` Python da 82 qatorni rad etadi; qolgan yetim havolalar SQL `INNER JOIN` da tushib qoladi va `audit.ErrorLog` ga yoziladi. Ikki qavat himoya — Python aniq sabab bilan rad etadi, SQL oxirgi filtr.

---

### Q8. `promote_to_core` nima uchun faqat manbasi bo'lgan protseduralarni chaqiradi?

`--file data/incoming/stores.csv` faqat `stg.RawStores` ni to'ldiradi. Agar `usp_LoadProducts` shartlarsiz chaqirilsa, `stg.RawProducts` da 0 qator → `THROW 50010`. `PROC_SOURCES` xaritasi har protsedurani o'z `stg` jadvallariga bog'laydi; jami 0 bo'lsa, protsedura o'tkazib yuboriladi. Bu `--stage all` va `--file` birgalikda ishlashini ta'minlaydi — avvalgi tuzatishlar alohida to'g'ri edi, lekin birga kelganda tizimni buzgan edi.

---

### Q9. Dublikat qatorlar qanday aniqlanadi va qayta ishlanadi?

`deduplicate()` `SaleRecord.unique_key()` = `(receipt_no, store_code, sku, sale_datetime)` bo'yicha ishlaydi. Data Pack v1 da 737 dublikat topildi — ular `stg` ga yozilmaydi, `stats["rows_duplicate"]` ga qo'shiladi. Balans: `63282 = 60052 + 2493 + 737`. Dublikatlar rad etish faylida emas — ular umuman yuklanmaydi, chunki bir xil chek qatori ikki marta hisoblanmasligi kerak.

---

### Q10. Bo'sh `unit_price` qanday qayta ishlanadi?

1 794 qator bo'sh narx bilan keladi. `enrichers.enrich_sale()` katalogdan `catalog_price` ni topib `unit_price` ni to'ldiradi; `_price_source = 'catalog'` qo'yiladi. Rad etish o'rniga tiklash — chek raqami va SKU mavjud. Agar katalogda ham narx bo'lmasa, `PRICE_IS_NUMERIC` yoki `SKU_EXISTS` rad etadi. Bu qaror `profiling.md` da hujjatlashtirilgan; savdoning ~2,9 % ini saqlab qoladi.

---

### Q11. `audit` sxemasi nima uchun kerak?

Uch jadval: `LoadLog` — har fayl yuklash tarixi va idempotentlik; `ErrorLog` — SQL protseduralaridagi xatolar va yetim qatorlar soni; `ProductHistory` — trigger orqali mahsulot o'zgarishlari. `LoadLog` bo'lmasa, qaysi fayl qachon yuklanganini bilib bo'lmaydi. `ErrorLog` bo'lmasa, `stg` va `core` orasidagi farqni tushuntirib bo'lmaydi — Data Pack da ~2 838 qator farq shu yerda qayd etiladi.

---

### Q12. Triggerlar qanday vazifani bajaradi?

`tr_Product_Audit` — `core.Product` yangilanganda `audit.ProductHistory` ga yozadi (narx, nom o'zgarishi). `tr_SalesDetail_Guard` — 50% dan yuqori chegirma bilan qator kiritishni bloklaydi (biznes qoidasi DB darajasida). Triggerlar Python validatsiyasini almashtirmaydi — ular `core` ga yozilgandan keyingi himoya. `DISCOUNT_RANGE` Python da 0–100% tekshiradi; trigger qo'shimcha 50% chegarani qo'llaydi.

---

### Q13. View qatlami nima uchun kerak?

5 ta view (`vw_DailySalesSummary`, `vw_StoreOverview`, `vw_ProductPerformance`, `vw_CashierPerformance`, `vw_AuditLogs`) murakkab JOIN larni yashirib, hisobot va SSMS so'rovlarini soddalashtiradi. `ReportBuilder` ba'zi ma'lumotlarni to'g'ridan-to'g'ri `mart.FactDailySales` dan oladi, lekin viewlar ad-hoc tahlil uchun qulay. View materialized emas — har so'rovda `core` dan hisoblanadi; tezlik uchun `mart` qatlami ishlatiladi.

---

### Q14. `mart.FactDailySales` nima uchun denormalizatsiya qilingan?

`StoreName` va `CategoryName` ataylab takrorlangan — BI so'rovlarida har safar 4–5 JOIN qilmaslik uchun. `mart.usp_RefreshDailyFacts` bir marta kunlik agregatsiya qiladi; dashboard ochilganda faqat `mart` dan o'qiladi. Narxi: do'kon nomi o'zgarsa mart qayta hisoblanishi kerak. Bu 3NF dan ataylab chetlanish — o'qish tezligi yozishdan muhimroq bo'lgan qatlamda qabul qilingan kompromis (`normalization.md`).

---

### Q15. Indeks strategiyasi qanday tanlandi?

8 ta nonclustered indeks — 7 tasida `INCLUDE` (qoplamaydigan indeks). Asosiy maqsad: `q01`, `q05`, `q09` kabi so'rovlarda `SaleDateTime`, `StoreId`, `SalesHeaderId` bo'yicha tez qidiruv. `logical reads` 6–15× kamaydi (performance.md). INSERT narxi ~60% oshadi — savdo tizimida o'qish ko'proq bo'lgani uchun indekslar saqlanadi. `IX_ProductPrice_Lookup` faqat narx boyitishda ishlatiladi — eng kam ta'sirli, lekin olib tashlash minimal foyda beradi.

---

### Q16. Xatoliklar qanday boshqariladi (fail-fast vs continue)?

Kutilgan xatolar (`ExtractError`, `JSONDecodeError`, `UnicodeDecodeError`, `ValueError`) — fayl darajasida: `files_failed` oshadi, keyingi faylga o'tiladi. Kutilmagan xatolar — butun pipeline to'xtaydi, `LoadLogger.fail()` chaqiriladi. SQL protseduralar `TRY...CATCH` bilan `audit.ErrorLog` ga yozadi va `THROW` qiladi. Buzuq JSON fayl (`"{ bu json emas"`) quvurni to'xtatmaydi — qolgan fayllar yuklanadi.

---

### Q17. Loglash qanday tashkil etilgan?

`get_logger(name, load_id)` har yuklash uchun `logs/{LoadId}.log` yaratadi. Format: `vaqt | daraja | modul | LoadId | xabar`. `logger.handlers` tekshiruvi (eski `hasHandlers()` o'rniga) — `basicConfig` root handleri sababli fayl handler qo'shilmasligi muammosi bartaraf etildi. `propagate = False` — xabar ikki marta chiqmasligi uchun.

---

### Q18. Hisobotlar qanday generatsiya qilinadi?

`ReportBuilder` Jinja2 shablonlaridan HTML yasaydi (`templates/`). `python main.py report --type dashboard` — `mart.FactDailySales` dan `SUM(NetAmount)` oladi. Dashboard dagi summa SQL natijasiga teng bo'lishi kerak (E2E sinov 6-band). 4 tur: dashboard, store, dq, load_log. Har birida sarlavha, davr, yaratilgan vaqt, manba ko'rsatiladi.

---

### Q19. Test strategiyasi qanday?

52 ta pytest: qoidalar (14 test), validator config, pipeline dry-run, LoadLogger idempotentligi, extractorlar, parserlar, modellar, Money, DB ulanish, rejected writer. Mock ishlatiladi (`DatabaseConnection` pipeline testida) — haqiqiy DB talab qilinmaydi. `promote_to_core` va `FutureDateRule` uchun alohida testlar qo'shildi. Integratsiya sinovi: `python main.py run` to'liq siklda.

---

### Q20. Normalizatsiya har doim yaxshimi?

Yo'q. `mart.FactDailySales` da ataylab denormalizatsiya — hisobot tezligi uchun. `stg` esa ataylab normalizatsiya qilinmagan (barcha NVARCHAR) — moslashuvchanlik uchun. To'g'ri yondashuv: qatlam maqsadiga qarab. Operatsion (`core`) — 3NF; analitika (`mart`) — star schema ga yaqin, o'lchovlar va soddalashtirilgan o'lchovlar.

---

### Q21. `scale_data.py` nima uchun kerak?

S7 o'lchovlari uchun 500 000+ savdo qatori generatsiya qiladi. `--seed 42` va `--start-date` bilan natija takrorlanadi. Data Pack kichik (~63k qator) — indeks ta'sirini katta hajmda ko'rish uchun sintetik ma'lumot kerak. 400 kun generatsiyasi 3,3 mln qator berdi — talabdan oshib ketadi, lekin benchmark ishonchliligi uchun yaxshi.

---

### Q22. Batch yuklash (`batch_size`) qanday ishlaydi?

`StagingLoader` `executemany` bilan 1000 qatorlik partiyalarda `stg` ga yozadi. Bu alohida INSERT lardan tezroq — network va parse overhead kamayadi. `config/settings.json` da `batch_size: 1000`. Juda katta batch xotira bosadi; juda kichik — sekin. 1000 Data Pack hajmi uchun muvozanatli tanlov.

---

### Q23. `stg` va `core` orasidagi qator farqi qanday tushuntiriladi?

Data Pack: `stg.RawSales` 60 052, `core.SalesDetail` 57 214. Farq ~2 838: yetim SKU, noto'g'ri do'kon, SQL JOIN da tushib qolgan qatorlar. Python validatsiyasi (`SKU_EXISTS`, `STORE_EXISTS`, `FUTURE_DATE`) qo'shilgach, qisman farq rad etish fayliga ko'chadi — sababi aniq. `audit.ErrorLog` da `usp_LoadSales` uchun umumiy son qoladi — qaysi qator ekani SQL da emas, rejected CSV da.

---

### Q24. Loyihani topshirishdan oldin qanday tekshirish kerak?

E2E ro'yxat (qo'llanma F-bo'lim): toza DB → `python main.py run` → balans ✓ → zanjirda 0 bo'lmagan jadvallar → idempotentlik (ikkinchi run skip) → 4 hisobot → `pytest` 52 passed → `logs/` da fayl → `--file` yiqilmaydi. Hujjatlar: ANALYSIS (24 javob), profiling (haqiqiy raqamlar), performance (S7), data_dictionary, normalization, README boshqa papkada sinovdan o'tgan. Repo: `a.out` yo'q, `requirements.txt` UTF-8, mazmunli commitlar.
