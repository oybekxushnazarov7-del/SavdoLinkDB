# Data Profiling — Data Pack v1 (haqiqiy o'lchov)

**Manba:** Data Pack v1, `sales_*.csv` (tire bilan sana formati).

## Validator.stats (ETL dan keyin)

`python main.py run` dan keyin logda chiqadigan `Qoidalar statistikasi` (12 ta faol qoida):

| Qoida | Taxmin (profiling) | Haqiqat (ETL log) | Izoh |
|---|---:|---:|---|
| `PRICE_DEVIATION` | ~1000 | 1123 | Katalogdan >50% chetlashgan narxlar — WARNING |
| `CASHIER_STORE` | ~600 | 656 | Kassir boshqa do'konda savdo qilgan |
| `QTY_POSITIVE` | ~250 | 274 | Nol yoki manfiy miqdor |
| `DISCOUNT_RANGE` | ~140 | 142 | 0–100% dan tashqari chegirma |
| `PRICE_IS_NUMERIC` | ~2000 | 6* | Bo'sh narx katalogdan tiklanadi, shuning uchun kam |
| `SKU_EXISTS` | ~200 | ~204 | Katalogda yo'q SKU |
| `STORE_EXISTS` | ~80 | ~82 | Mavjud bo'lmagan do'kon kodi |
| `FUTURE_DATE` | ~80 | ~82 | 2027 yilidagi sanalar |

\* `PRICE_IS_NUMERIC` kam chiqishi — `enrichers.py` bo'sh narxni katalogdan to'ldiradi (B-11 qarori).

## Anomaliyalar jadvali

| # | Fayl / ustun | Anomaliya | Profiling taxmini | Haqiqat | Qaror | Sabab |
|---|---|---|---:|---:|---|---|
| 1 | `returns.csv` / `store_code` | NULL (#28, #37) | 2 | 2 | Rad etish | FK to'ldirish mumkin emas |
| 2 | `sales_*.csv` / `sale_datetime` | DD.MM.YYYY | ~500 | 0 (transform) | Normalizatsiya | `parse_datetime` barcha formatlarni qabul qiladi |
| 3 | `sales_*.csv` / `discount_pct` | NULL | ~3000 | 0 (transform) | 0 deb qabul | Chegirma ixtiyoriy maydon |
| 4 | `sales_*.csv` / `unit_price` | NULL, `n/a` | ~1794 | ~1794 tiklangan | Katalogdan tiklash | Chek+SKU mavjud, faqat narx yo'q |
| 5 | `stores.csv` / `opened_date` | DD.MM.YYYY | 12 | 0 | Normalizatsiya | `parse_datetime` |
| 6 | `suppliers.csv` / `country` | NULL | 1 | 1 | NULL qoldirish | Mamlakat ixtiyoriy |
| 7 | `sales_*.csv` / `store_code` | Noto'g'ri kod | ~80 | ~82 | Rad etish (`STORE_EXISTS`) | Python bosqichida ushlanadi |
| 8 | `sales_*.csv` / `sku` | Katalogda yo'q | ~200 | ~204 | Rad etish (`SKU_EXISTS`) | core ga yetim tushmasin |
| 9 | `sales_*.csv` / `sale_datetime` | Kelajak (2027) | ~80 | ~82 | Rad etish (`FUTURE_DATE`) | Biznes qoidasi |

### B-11 qarori: bo'sh `unit_price`

**1 794 qator** bo'sh narx bilan keladi. Rad etish o'rniga katalogdan tiklashni tanladim, chunki chek raqami va mahsulot ma'lum — faqat narx tushib qolgan. `PriceSource = 'catalog'` sifatida qayd etiladi (`stg.RawSales.PriceSource`), shuning uchun keyinchalik ajratib ko'rish mumkin. Rad etsam savdoning ~2,9 % i hisobotdan tushib qolardi.

## Balans tekshiruvi

```
rows_read = rows_valid + rows_rejected + rows_duplicate
```

Data Pack v1: **63 282 = 60 052 + 2 493 + 737** ✓

## core vs stg farqi

`usp_LoadSales` INNER JOIN tufayli yetim SKU (~204), noto'g'ri do'kon (~82) va boshqa havola xatolari `stg` da qoladi, `core` ga tushmaydi. Farq `audit.ErrorLog` da qayd etiladi.

| Ko'rsatkich | Son |
|---|---:|
| `stg.RawSales` | 60 052 |
| `core.SalesDetail` | 57 214 |
| Farq (yetim/dublikat) | ~2 838 |

Python validatsiyasi (`SKU_EXISTS`, `STORE_EXISTS`, `FUTURE_DATE`) qo'shilgach, bu qatorlar rad etish faylida (`data/rejected/rejected_LOAD-*.csv`) aniq sabab bilan yoziladi — `audit.ErrorLog` dagi umumiy son kamayadi.

## DQ metrikalari

`build_report()` chiqishi (Data Pack v1):

- **Completeness:** >95% (majburiy maydonlar to'ldirilgan)
- **Uniqueness:** dublikatlar `deduplicate()` da ajratiladi (737 ta)
- **Validity:** qoidalar bo'yicha rad etish ~3,9%
- **Consistency:** kassir-do'kon mosligi WARNING sifatida qayd etiladi
