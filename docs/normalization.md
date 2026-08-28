# Normalizatsiya: 1NF → 2NF → 3NF

## 1NF (Birinchi normal shakl)

**Anomaliya:** Takrorlanuvchi guruhlar va atomik bo'lmagan qiymatlar.

**Qayerda:** `stg.*` jadvallar — barcha ustunlar `NVARCHAR`, xom matn saqlanadi.

**Yechim:** Har bir maydon atomik (bitta qiymat). `products.json` dagi `price_history` alohida `stg.RawPrices` jadvaliga ajratildi — mahsulot qatorida takrorlanuvchi narxlar yo'q.

**Bartaraf etilgan anomaliyalar:**
- *Insert:* narx tarixini alohida qator sifatida qo'shish mumkin
- *Update:* bitta narx o'zgarsa, faqat `RawPrices` qatori yangilanadi
- *Delete:* narx yozuvi o'chirilsa, mahsulot qatori buzilmaydi

## 2NF (Ikkinchi normal shakl)

**Anomaliya:** Qisman bog'liqlik — kompozit kalitning bir qismiga bog'liq maydonlar.

**Qayerda:** `core.SalesHeader` + `core.SalesDetail` ajratildi.

**Yechim:** Chek sarlavhasi (`ReceiptNo`, `StoreId`, `EmployeeId`, `SaleDateTime`, `PaymentType`) `SalesHeader` da; qator tafsilotlari (`ProductId`, `Qty`, `UnitPrice`, `DiscountPct`) `SalesDetail` da. `SalesDetail` kaliti: `(SalesHeaderId, ProductId)`.

**Bartaraf etilgan anomaliyalar:**
- *Insert:* yangi chek qatori sarlavhasiz qo'shilmaydi
- *Update:* to'lov turi o'zgarsa, faqat `SalesHeader` yangilanadi
- *Delete:* bitta mahsulot qatori o'chirilsa, chek sarlavhasi saqlanadi

## 3NF (Uchinchi normal shakl)

**Anomaliya:** Tranzitiv bog'liqlik — kalit bo'lmagan maydon boshqa kalit bo'lmagan maydonga bog'liq.

**Qayerda:** `core.Product` → `core.Category`, `core.Supplier`; `core.Store` → `core.Region`; `core.Employee` → `core.Store`.

**Yechim:** Spravochniklar alohida jadvallarga ajratildi. `core.ProductPrice` — mahsulot + sana + narx (kompozit kalit, surrogat emas).

**Buzilgan qoida (ataylab):** `mart.FactDailySales` da `StoreName` va `CategoryName` denormalizatsiya qilingan — BI so'rovlarida JOIN kamaytirish uchun.

**Bartaraf etilgan anomaliyalar:**
- *Insert:* yangi do'kon — faqat `core.Store` ga qo'shiladi
- *Update:* hudud nomi o'zgarsa, faqat `core.Region` yangilanadi
- *Delete:* kategoriya o'chirilsa, FK cheklovi himoya qiladi

## Qo'shimcha: `core.ProductPrice`

Bitta mahsulotda bir nechta narx bo'ladi. Ularni `Product` ichiga sig'dirsangiz 1NF buziladi — shuning uchun alohida jadval.

`core.ExchangeRate` — tabiiy kompozit kalit (`RateDate`, `CurrencyCode`), surrogat emas.
