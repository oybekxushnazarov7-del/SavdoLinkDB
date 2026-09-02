# Data Dictionary

Nomlash lug'ati: manba CSV → Python → `stg` → `core`.

| Manba CSV | Python | stg | core |
|---|---|---|---|
| `receipt_no` | `receipt_no` | `ReceiptNo` | `ReceiptNo` |
| `store_code` | `store_code` | `StoreCode` | → `StoreId` |
| `cashier_id` | `cashier_id` | `CashierId` | → `EmployeeId` |
| `sale_datetime` | `sale_datetime` | `SaleDateTime` | `SaleDateTime` |
| `sku` | `sku` | `Sku` | → `ProductId` |
| `qty` | `qty` | `Qty` | `Qty` |
| `unit_price` | `unit_price` | `UnitPrice` | `UnitPrice` |
| `discount_pct` | `discount_pct` | `DiscountPct` | `DiscountPct` |
| `payment_type` | `payment_type` | `PaymentType` | `PaymentType` |

---

## stg — staging jadvallar

Barcha `stg` jadvallarida umumiy ustunlar: `LoadId`, `SourceFile`, `RowNum`, `LoadedAt`. Ma'lumotlar `NVARCHAR` — transform oldidan xom holat.

### stg.RawSales — savdo qatorlari

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| RawSalesId | BIGINT IDENTITY | Yo'q | Surrogat kalit |
| LoadId | NVARCHAR(50) | Yo'q | Partiya identifikatori |
| SourceFile | NVARCHAR(260) | Yo'q | Manba fayl nomi |
| RowNum | INT | Yo'q | Fayldagi qator raqami |
| ReceiptNo … PaymentType | NVARCHAR(200) | Ha | Xom CSV ustunlari |
| UnitPriceResolved | NVARCHAR(200) | Ha | Katalogdan tiklangan narx |
| PriceSource | NVARCHAR(20) | Ha | `file` yoki `catalog` |

### stg.RawStores, RawEmployees, RawProducts, RawCategories, RawSuppliers, RawPrices, RawReturns, RawRates

Spravochnik va qo'shimcha fayllar uchun xuddi shu struktura — barcha biznes ustunlari `NVARCHAR(200)`.

---

## core — normalizatsiyalangan qatlam

### core.Region — hududlar

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| RegionId | INT IDENTITY | Yo'q | PK |
| RegionName | NVARCHAR(100) | Yo'q | UQ |

### core.Store — do'konlar

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| StoreId | INT IDENTITY | Yo'q | PK |
| StoreCode | NVARCHAR(10) | Yo'q | Biznes kalit (`ST-001`) |
| StoreName | NVARCHAR(150) | Yo'q | |
| RegionId | INT | Yo'q | FK → Region |
| City | NVARCHAR(100) | Yo'q | |
| OpenedDate | DATE | Ha | |
| AreaM2 | INT | Ha | m², >0 |
| IsActive | BIT | Yo'q | Default 1 |

### core.Employee — xodimlar

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| EmployeeId | INT IDENTITY | Yo'q | PK |
| EmpCode | NVARCHAR(10) | Yo'q | `E-0101` |
| FullName | NVARCHAR(150) | Yo'q | |
| StoreId | INT | Yo'q | FK → Store |
| Position | NVARCHAR(50) | Yo'q | Kassir, Menejer, … |
| Salary | DECIMAL(12,2) | Yo'q | ≥0 |
| HiredDate | DATE | Yo'q | |
| ManagerId | INT | Ha | FK → Employee (o'ziga) |
| IsActive | BIT | Yo'q | |

### core.Category — mahsulot kategoriyalari

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| CategoryId | INT IDENTITY | Yo'q | PK |
| CategoryCode | NVARCHAR(20) | Yo'q | |
| CategoryName | NVARCHAR(150) | Yo'q | |
| ParentCategoryId | INT | Ha | Ierarxiya |
| Level | TINYINT | Yo'q | 1–3 |

### core.Supplier — yetkazib beruvchilar

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| SupplierId | INT IDENTITY | Yo'q | PK |
| Inn | NVARCHAR(9) | Yo'q | 9 raqam, UQ |
| SupplierName | NVARCHAR(150) | Yo'q | |
| Country | NVARCHAR(50) | Ha | |
| ContractDate | DATE | Yo'q | |

### core.Product — mahsulotlar

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| ProductId | INT IDENTITY | Yo'q | PK |
| Sku | NVARCHAR(15) | Yo'q | UQ |
| ProductName | NVARCHAR(200) | Yo'q | |
| CategoryId | INT | Yo'q | FK |
| SupplierId | INT | Yo'q | FK |
| Unit | NVARCHAR(10) | Yo'q | dona, kg, litr, quti |
| Barcode | NVARCHAR(13) | Ha | |
| IsActive | BIT | Yo'q | |

### core.ProductPrice — narx tarixi

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| ProductPriceId | INT IDENTITY | Yo'q | PK |
| ProductId | INT | Yo'q | FK |
| ValidFrom | DATE | Yo'q | UQ (ProductId, ValidFrom) |
| ValidTo | DATE | Ha | |
| Price | DECIMAL(12,2) | Yo'q | >0 |

### core.SalesHeader — chek sarlavhasi

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| SalesHeaderId | INT IDENTITY | Yo'q | PK |
| ReceiptNo | NVARCHAR(15) | Yo'q | |
| StoreId | INT | Yo'q | FK |
| EmployeeId | INT | Yo'q | FK (kassir) |
| SaleDateTime | DATETIME2(0) | Yo'q | |
| PaymentType | NVARCHAR(10) | Yo'q | CASH, CARD, TRANSFER |
| LoadId | NVARCHAR(50) | Yo'q | Qaysi partiyadan |

**Noyoblik kaliti:** `ReceiptNo + StoreId` — idempotentlik shunga tayanadi (`MERGE`).

### core.SalesDetail — chek qatorlari

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| SalesDetailId | INT IDENTITY | Yo'q | PK |
| SalesHeaderId | INT | Yo'q | FK |
| ProductId | INT | Yo'q | FK |
| Qty | INT | Yo'q | >0 |
| UnitPrice | DECIMAL(12,2) | Yo'q | >0 |
| DiscountPct | DECIMAL(5,2) | Yo'q | 0–100 |
| LineAmount | DECIMAL(14,2) | — | Hisoblangan: `Qty * UnitPrice * (1 - DiscountPct/100)` |

### core.Returns — qaytarishlar

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| ReturnId | INT IDENTITY | Yo'q | PK |
| ReturnCode | NVARCHAR(15) | Yo'q | UQ |
| SalesHeaderId | INT | Yo'q | FK |
| ProductId | INT | Yo'q | FK |
| Qty | INT | Yo'q | >0 |
| Reason | NVARCHAR(200) | Ha | |
| ReturnDate | DATE | Yo'q | |

### core.ExchangeRate — valyuta kurslari

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| RateDate | DATE | Yo'q | PK (RateDate, CurrencyCode) |
| CurrencyCode | CHAR(3) | Yo'q | USD, EUR, RUB |
| Rate | DECIMAL(12,4) | Yo'q | >0 |

---

## mart — analitika qatlami

### mart.FactDailySales — kunlik fakt jadvali

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| FactId | BIGINT IDENTITY | Yo'q | PK |
| SaleDate | DATE | Yo'q | |
| StoreId | INT | Yo'q | |
| CategoryId | INT | Yo'q | |
| StoreName | NVARCHAR(150) | Yo'q | Denormalizatsiya |
| CategoryName | NVARCHAR(150) | Yo'q | Denormalizatsiya |
| ReceiptCount | INT | Yo'q | Kunlik cheklar soni |
| QtySold | INT | Yo'q | Sotilgan dona |
| GrossAmount | DECIMAL(16,2) | Yo'q | Chegirmasiz |
| NetAmount | DECIMAL(16,2) | Yo'q | Chegirma bilan |
| ReturnAmount | DECIMAL(16,2) | Yo'q | Qaytarishlar |
| RefreshedAt | DATETIME2(0) | Yo'q | Oxirgi yangilanish |

---

## audit — audit jadvallar

### audit.LoadLog — fayl yuklash jurnali

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| LoadLogId | BIGINT IDENTITY | Yo'q | PK |
| LoadId | NVARCHAR(50) | Yo'q | |
| SourceFile | NVARCHAR(260) | Yo'q | Idempotentlik tekshiruvi |
| StartedAt / FinishedAt | DATETIME2(0) | | Vaqt oralig'i |
| RowsRead … RowsLoaded | INT | Ha | Statistika |
| Status | NVARCHAR(20) | Yo'q | RUNNING, SUCCESS, FAILED |
| Message | NVARCHAR(1000) | Ha | Xato matni |

### audit.ErrorLog — SQL xatolari

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| ErrorLogId | BIGINT IDENTITY | Yo'q | PK |
| LoadId | NVARCHAR(50) | Ha | |
| ErrorNumber / ErrorLine | INT | Ha | |
| ErrorMessage | NVARCHAR(2000) | Ha | |
| ErrorProcedure | NVARCHAR(200) | Ha | masalan `core.usp_LoadSales` |
| LoggedAt | DATETIME2(0) | Yo'q | |

### audit.ProductHistory — mahsulot o'zgarishlari (trigger)

| Ustun | Tip | NULL | Izoh |
|---|---|---|---|
| HistoryId | BIGINT IDENTITY | Yo'q | PK |
| ProductId | INT | Yo'q | |
| ChangeType | NVARCHAR(10) | Yo'q | UPDATE, DELETE |
| OldName / NewName | NVARCHAR(200) | Ha | |
| OldUnitPrice / NewUnitPrice | DECIMAL(18,2) | Ha | |
| ChangedAt | DATETIME2(0) | Yo'q | |
