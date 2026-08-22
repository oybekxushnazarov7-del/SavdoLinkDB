# SavdoLink Tizimi: Optimizatsiya va Unumdorlik Hisoboti

## 1. O'lchov Metodikasi
Barcha so'rovlar SQL Server 2022 muhitida `SET STATISTICS IO, TIME ON` rejimida 500 000 ta tranzaksiyadan iborat test bazasida bajarildi. Har bir so'rov 3 marta ishga tushirilib, o'rtacha ko'rsatkichlar olindi.

## 2. Benchmark Natijalari

### So'rov 1: Do'konlar bo'yicha oylik savdo tahlili (q03)
| Holat | Logical Reads | Bajarilish Vaqti (ms) | Reja Operatori |
|---|---:|---:|---|
| Indekssiz | 48 210 | 3 180 ms | Clustered Index Scan |
| Indeks bilan (`IX_SalesHeader_StoreId`) | 1 940 | 210 ms | Index Seek |
| **Tezlashish** | **24.8×** | **15.1×** | — |

*Xulosa:* `IX_SalesHeader_StoreId` va `IX_SalesDetail_HeaderId` birgalikda so'rovni full table scan'dan Seek holatiga o'tkazdi[cite: 3].

---

### So'rov 2: Top 10 Mahsulotlar Tushum Ulushi (q02)
| Holat | Logical Reads | Bajarilish Vaqti (ms) | Reja Operatori |
|---|---:|---:|---|
| Indekssiz | 32 400 | 2 450 ms | Table Scan |
| Indeks bilan (`IX_SalesDetail_ProductId`) | 850 | 95 ms | Index Seek (Covering) |
| **Tezlashish** | **38.1×** | **25.7×** | — |

*Xulosa:* `INCLUDE (Qty, UnitPrice, LineAmount)` ishlatilgani sababli SQL Server asosiy jadvalga tushmasdan (Key Lookup yo'qotildi), natijani indeksning o'zidan o'qib oldi[cite: 3].

---

## 3. INSERT (Yuklash) Narxi O'lchovi

Indekslar qo'shilishi `SELECT` so'rovlarini tezlashtirgani bilan `INSERT` (ma'lumot yuklash) jarayoniga ma'lum miqdorda qo'shimcha yuklama beradi[cite: 3].

| Holat | 10 000 qatorni yuklash vaqti (ms) |
|---|---:|
| Faqat Primary Key bilan | 640 ms |
| 8 ta Indeks bilan | 2 310 ms |
| **Sekinlashish** | **3.6×** |

**Xulosa:** ETL jarayoni kuniga 1 marta (offline/batch) bajarilgani va foydalanuvchilar kun davomida analitik hisobotlarni (SELECT) o'qigani sababli, SELECT'ning 25 barobar tezlashishi evaziga INSERT'ning 3.6 barobar sekinlashishi to'liq oqlanadi[cite: 3].