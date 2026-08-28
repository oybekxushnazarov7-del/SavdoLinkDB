# Data Profiling — Data Pack v1 (haqiqiy o'lchov)

**Manba:** Data Pack v1, `sales_2026-01-01.csv` formati (tire bilan).

## Validator.stats (ETL dan keyin)

Quyidagi raqamlar `python main.py run` dan keyin logda chiqadi (`Qoidalar statistikasi`):

| Qoida | Taxminiy son | Izoh |
|---|---:|---|
| `PRICE_IS_NUMERIC` | ~2097 | Bo'sh yoki `n/a` narx — rad etiladi |
| `QTY_POSITIVE` | ~274 | Nol yoki manfiy miqdor |
| `DISCOUNT_RANGE` | ~142 | 0–100% dan tashqari chegirma |
| `PRICE_DEVIATION` | >0 | enrichers ulangach — katalogdan chetlashgan narxlar |

**Qaror (B-11):** Bo'sh narxli qatorlar katalogdan tiklanadi (`_price_source=catalog`), ogohlantirish sifatida `PRICE_DEVIATION` qo'llanishi mumkin. Rad etish o'rniga tiklash — chek raqami va SKU mavjud bo'lganda.

## Anomaliyalar jadvali

| # | Fayl / ustun | Anomaliya | Qaror |
|---|---|---|---|
| 1 | `returns.csv` / `store_code` | NULL (#28, #37) | Rad etish yoki to'ldirish |
| 2 | `sales_2026-01-01.csv` / `sale_datetime` | DD.MM.YYYY | `parse_datetime` normalizatsiya |
| 3 | `sales_*.csv` / `discount_pct` | NULL | 0 deb qabul (transform) |
| 4 | `sales_*.csv` / `unit_price` | NULL, `n/a`, `-` | Katalogdan tiklash (B-11) |
| 5 | `stores.csv` / `opened_date` | DD.MM.YYYY | `parse_datetime` |
| 6 | `suppliers.csv` / `country` | NULL (#19) | NULL qoldirish |

## Balans tekshiruvi

```
rows_read = rows_valid + rows_rejected + rows_duplicate
```

Data Pack v1: `63282 = 60052 + 2493 + 737` ✓

## core vs stg farqi

`usp_LoadSales` INNER JOIN tufayli yetim SKU (~227), noto'g'ri do'kon (~110) va boshqa havola xatolari `stg` da qoladi, `core` ga tushmaydi. Farq `audit.ErrorLog` da qayd etiladi (B-07).
