Sprint 1: Loyiha Arxitekturasi va Muhitni Sozlash
SavdoLink loyihasining umumiy kataloglar tuzilmasi (config/, data/, sql/, src/, tests/) to'liq shakllantirildi.

Python virtual muhiti (venv) sozlanib, loyiha uchun zarur bo'lgan barcha kutubxonalar va bog'liqliklar o'rnatildi.

config/settings.json va src/load/db.py modullari orqali Microsoft SQL Server bazasiga ulanish o'rnatildi va SELECT @@VERSION so'rovi orqali aloqa muvaffaqiyatli tekshirildi.

Sprint 2: Data Profiling va Anomaliyalarni Tahlil Qilish
data/incoming/ papkasiga birlamchi manba bo'lgan Data Pack CSV fayllari joylashtirildi.

CSV fayllar tahlil qilinib, ulardagi tiplar nomuvofiqligi, ortiqcha belgi va bo'sh qiymatlar hamda noto'g'ri formatlangan ustunlar anomaliyalari ajratib olindi.

Avtomatlashtirilgan profilaktika uchun tools/profile_data.py skripti yozildi hamda aniqlangan 12 ta asosiy anomaliya uchun Yechimlar Rejasi docs/profiling.md faylida hujjatlashtirildi.

Sprint 3: DDL va Staging Arxitekturasi
MS SQL Server'da loyiha uchun kerakli sxemalar (stg, core, mart, audit) yaratildi.

Xom ma'lumotlarni qabul qiluvchi Staging jadvallari (stg.RawSales, stg.RawProducts, stg.RawStores, stg.RawEmployees) loyihalashtirildi.

Ma'lumotlar ombori uchun normalize qilingan Core jadvallari (core.Store, core.Product, core.SalesHeader, core.SalesDetail, core.Returns) va xatoliklarni qayd etuvchi audit.ErrorLog hamda audit.ProductHistory jadvallari qurildi.

Sprint 4: Python ETL Pipeline
Python'da ma'lumotlarni tozalash va standartlashtirish modullari (cleaners.py, parsers.py, enrichers.py) ishlab chiqildi.

Kiruvchi CSV ma'lumotlarini tekshiruvchi biznes-qoidalar (rules.py) hamda moliyaviy hisob-kitoblar uchun maxsus money.py moduli yaratildi.

ETL quvurini (pipeline.py) va fayllarni avtomatik o'quvchi extractor'larni sinash uchun pytest testlar to'plami yozildi va muvaffaqiyatli o'tkazildi.

Sprint 5: SQL Business Logic Layer
Tranzaksion Protseduralar: Staging'ni xavfsiz tozalash (usp_TruncateStaging), spravochnik va mahsulotlarni yuklash (usp_LoadDimensions, usp_LoadProducts), chek va qaytarishlarni MERGE qilish (usp_LoadSales, usp_LoadReturns) hamda kunlik faktlarni qayta hisoblash (usp_RefreshDailyFacts) protseduralari yozildi. Ularga ACID tranzaksiyalar, TRY...CATCH va audit.ErrorLog bilan ishlash mantiqlari kiritildi.

Yordamchi Funksiyalar va Triggerlar: Net-narxni hisoblash (fn_NetPrice), telefon raqamlarini niqoblash (fn_MaskPhone), mahsulot narxi va ma'lumotlari o'zgarganda audit tarixini yurituvchi trigger (tr_Product_Audit) hamda 50% dan yuqori noqonuniy chegirmalarni bloklovchi trigger (tr_SalesDetail_Guard) yaratildi.

Tahliliy Ko'rinishlar (Views): Hisobotlar va tahlillar uchun kerakli bo'lgan 5 ta asosiy ko'rinish (vw_AuditLogs, vw_CashierPerformance, vw_DailySalesSummary, vw_ProductPerformance, vw_StoreOverview) bazadagi DDL sxemasiga 100% moslab sozlandi va barcha ustun xatoliklari bartaraf etildi.
---
Tuzatish sessiyasi (qo'llanma v2): P-01..P-18, S-01..S-14, D-01..D-06, R-08/R-09.
Data Pack data/incoming/ ga chiqarildi; StagingLoader/LoadLog/SQL MERGE DDL ga moslandi; pytest 44 passed.

