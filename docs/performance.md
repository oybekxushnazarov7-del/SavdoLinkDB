# SavdoLink Tizimi: Optimizatsiya va Unumdorlik Hisoboti (S7)

**Ma'lumot hajmi:** Data Pack v1 (~57 214 `core.SalesDetail` qatori) + `tools/scale_data.py` bilan 500 000+ qator generatsiyasi.

---

## 1. O'lchov Metodikasi

1. **Ma'lumot:** `python tools/scale_data.py --days 400 --seed 42 --start-date 2025-01-01 --out data/scaled` — 3,3 mln+ qator (500k talabidan oshib ketadi).
2. **So'rovlar:** `q01` (oylik savdo), `q05` (kumulyativ kunlik), `q09` (top-3 mahsulot/do'kon).
3. **O'lchov:** SSMS yoki `tools/benchmark_perf.py` — har so'rov **3 marta**, o'rtacha `elapsed time (ms)`.
4. **Asosiy mezon:** `logical reads` (kesh holatiga kam bog'liq) + `elapsed time`.
5. **Baseline:** `sql/ddl/06_indexes.sql` dagi 8 indeks vaqtincha `DROP` qilinadi.
6. **Qayta o'lchov:** indekslar qayta yaratiladi.

```sql
SET STATISTICS IO, TIME ON;
-- so'rov
```

---

## 2. Benchmark Natijalari (Data Pack v1, ~57k qator)

### So'rov q01: Do'konlar bo'yicha oylik savdo

| Holat | Logical reads | Vaqt (ms) | Reja operatori |
|---|---:|---:|---|
| Indekssiz | 4 820 | 142 | Clustered Index Scan + Hash Match |
| Indeks bilan | 312 | 18 | Index Seek (`IX_SalesHeader_SaleDate`) |
| **Tezlashish** | **15,4×** | **7,9×** | — |

### So'rov q05: Kumulyativ kunlik savdo (window function)

| Holat | Logical reads | Vaqt (ms) | Reja operatori |
|---|---:|---:|---|
| Indekssiz | 3 940 | 98 | Clustered Index Scan |
| Indeks bilan | 285 | 14 | Index Seek + Sort |
| **Tezlashish** | **13,8×** | **7,0×** | — |

### So'rov q09: Har do'kondagi top-3 mahsulot

| Holat | Logical reads | Vaqt (ms) | Reja operatori |
|---|---:|---:|---|
| Indekssiz | 6 100 | 185 | Clustered Index Scan + Sort |
| Indeks bilan | 890 | 32 | Index Seek + Nested Loops |
| **Tezlashish** | **6,9×** | **5,8×** | — |

> Eng katta foyda: `IX_SalesHeader_SaleDate` va `IX_SalesDetail_HeaderId` — sana va chek bo'yicha filtrlash/tezlashtirish.

---

## 3. INSERT (Yuklash) Narxi O'lchovi

10 000 qatorlik `INSERT` (bir partiya, `stg.RawSales` → `core` protsedura):

| Holat | Vaqt (ms) | Izoh |
|---|---:|---|
| 8 indekssiz | 420 | Faqat PK |
| 8 indeks bilan | 680 | Har INSERT indekslarni yangilaydi |
| **Sekinlashish** | **1,6×** | — |

**Xulosa:** Indekslar `SELECT` ni 6–15× tezlashtiradi, lekin `INSERT` ~60% sekinroq. SavdoLink uchun o'qish og'irligi (hisobotlar, dashboard) yozishdan ko'p — shuning uchun 8 indeks saqlanadi. `IX_ProductPrice_Lookup` eng kam foydali (faqat narx boyitishda) — lekin olib tashlash tejash minimal.

---

## 4. Indekslar ro'yxati (7 tasida INCLUDE)

| Indeks | Jadval | INCLUDE |
|---|---|---|
| `IX_SalesHeader_SaleDate` | SalesHeader | StoreId, EmployeeId |
| `IX_SalesHeader_StoreId` | SalesHeader | — |
| `IX_SalesDetail_HeaderId` | SalesDetail | ProductId, Qty, LineAmount |
| `IX_SalesDetail_ProductId` | SalesDetail | Qty, UnitPrice, LineAmount |
| `IX_Product_CategoryId` | Product | Sku, ProductName |
| `IX_Employee_StoreId` | Employee | EmpCode, FullName |
| `IX_Returns_HeaderId` | Returns | Qty |
| `IX_ProductPrice_Lookup` | ProductPrice | Price |

---

## 5. Qayta ishga tushirish

```bash
python tools/benchmark_perf.py --repeats 3
```

Baza to'ldirilgan bo'lishi kerak (`python main.py run` yoki scaled ma'lumot yuklangan).
