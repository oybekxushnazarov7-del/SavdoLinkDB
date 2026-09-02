# Normalizatsiya: 0NF → 1NF → 2NF → 3NF → mart denormalizatsiya

## 0. Normalizatsiyalanmagan holat

Manba fayl bitta "yassi" jadval: har qatorda do'kon nomi, kassir ismi va mahsulot nomi takrorlanadi.

| ReceiptNo | StoreName | CashierName | ProductName | Qty | Price |
|---|---|---|---|---:|---:|
| R-001 | SavdoLink Chilonzor | Karimov Aziz | Qaymoq 500ml | 2 | 18500 |
| R-001 | SavdoLink Chilonzor | Karimov Aziz | Non oq | 1 | 4200 |

**Anomaliyalar:** insert (do'kon qo'shish uchun har qatorni takrorlash), update (do'kon nomi o'zgarsa minglab qator), delete (bitta mahsulot o'chsa butun chek buzilishi).

---

## 1NF — takrorlanuvchi guruhlar ajratildi

**Qayerda:** `stg.*` jadvallar — barcha ustunlar `NVARCHAR`, xom matn saqlanadi.

**Yechim:** Har bir maydon atomik (bitta qiymat). `products.json` dagi `price_history` alohida `stg.RawPrices` jadvaliga ajratildi — mahsulot qatorida takrorlanuvchi narxlar yo'q.

**Bartaraf etilgan anomaliya:**
- *Insert:* narx tarixini alohida qator sifatida qo'shish mumkin
- *Update:* bitta narx o'zgarsa, faqat `RawPrices` qatori yangilanadi
- *Delete:* narx yozuvi o'chirilsa, mahsulot qatori buzilmaydi

---

## 2NF — to'liq bo'lmagan bog'liqlik olib tashlandi

**Qayerda:** `core.SalesHeader` + `core.SalesDetail` ajratildi.

**Yechim:** Chek sarlavhasi (`ReceiptNo`, `StoreId`, `EmployeeId`, `SaleDateTime`, `PaymentType`) `SalesHeader` da; qator tafsilotlari (`ProductId`, `Qty`, `UnitPrice`, `DiscountPct`) `SalesDetail` da.

**Bartaraf etilgan anomaliya:** *update anomaliyasi* — do'kon nomini o'zgartirish uchun minglab `SalesDetail` qatorini yangilash kerak edi; endi faqat `core.Store` yangilanadi.

---

## 3NF — tranzitiv bog'liqlik olib tashlandi

**Qayerda:** `core.Product` → `core.Category`, `core.Supplier`; `core.Store` → `core.Region`; `core.Employee` → `core.Store`.

**Yechim:** Spravochniklar alohida jadvallarga ajratildi. `core.ProductPrice` — mahsulot + sana + narx (kompozit kalit).

**Bartaraf etilgan anomaliya:** *insert* — yangi do'kon faqat `core.Store` ga qo'shiladi; *update* — hudud nomi o'zgarsa faqat `core.Region` yangilanadi; *delete* — FK cheklovi himoya qiladi.

---

## mart qatlami — ongli denormalizatsiya

`mart.FactDailySales` da `StoreName` va `CategoryName` **ataylab takrorlangan**.

**Sabab:** BI so'rovlarida (`dashboard`, `store` hisobotlari) har safar 4–5 ta JOIN qilmaslik uchun. `mart.usp_RefreshDailyFacts` bir marta agregatsiya qiladi, hisobotlar tez ochiladi.

**Narxi:** `Store` nomi o'zgarsa, mart qayta hisoblanishi kerak (`promote_to_mart`). Bu normalizatsiya qoidasini buzish, lekin o'qish tezligi uchun qabul qilingan kompromis — `ANALYSIS.md` Q20 da batafsil.

---

## Qo'shimcha: `core.ProductPrice` va `core.ExchangeRate`

- **ProductPrice:** bitta mahsulotda bir nechta narx — `Product` ichiga sig'dirsangiz 1NF buziladi
- **ExchangeRate:** tabiiy kompozit kalit (`RateDate`, `CurrencyCode`), surrogat emas — tarixiy kurslar uchun to'g'ri dizayn
