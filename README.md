# SavdoLink — O'rnatish va Ishga Tushirish

SavdoLink — chakana savdo tarmog'ining operatsion ma'lumotlarini (CSV/JSON) yig'uvchi, tozalovchi, Data Quality validsiyasidan o'tkazuvchi va SQL Server dWH hamda HTML hisobotlarini shakllantiruvchi ETL quvuri.

**Arxitektura:** `CSV/JSON` → `Extract` → `Transform & DQ` → `Load (stg)` → `core (protseduralar)` → `mart` → `HTML hisobotlar`

---

## Talablar

- Python 3.10+
- Microsoft SQL Server 2019+ (yoki Express)
- **ODBC Driver 17 yoki 18** for SQL Server
- Data Pack v1 (o'qituvchi bergan arxiv)

---

## 1. Muhit

```bash
git clone <repo-url> SavdoLink
cd SavdoLink
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

`config/settings.json` da SQL Server ulanishini tekshiring:

```json
{
  "db": {
    "driver": "ODBC Driver 17 for SQL Server",
    "server": ".\\SQLEXPRESS",
    "database": "SavdoLinkDB_v2",
    "trusted_connection": true
  }
}
```

---

## 2. Baza (SSMS — shu tartibda)

```
sql/ddl/00_database.sql
sql/ddl/01_schemas.sql
sql/ddl/02_core_tables.sql
sql/ddl/03_stg_tables.sql
sql/ddl/04_audit_tables.sql
sql/ddl/05_mart_tables.sql
sql/ddl/06_indexes.sql
sql/functions/*.sql
sql/views/*.sql
sql/procedures/*.sql
sql/triggers/*.sql
```

To'liq qayta boshlash: avval `sql/ddl/99_drop_all.sql`, keyin yuqoridagi tartib.

---

## 3. Ma'lumot

Data Pack v1 ni `data/incoming/` ga chiqaring. Kerakli fayllar:

- `stores.csv`, `employees.json`, `categories.csv`, `suppliers.csv`
- `products.json`
- `sales_*.csv`, `returns.csv` (ixtiyoriy)

---

## 4. To'liq ETL sikli

```bash
python main.py run
```

Kutilgan log:

```
Balans: 63282 = 63282 ✓
Qoidalar statistikasi: {...}
core.usp_LoadDimensions bajarildi [manbada ... qator]
mart.usp_RefreshDailyFacts bajarildi [2026-01-01 — 2026-03-01]
```

**Bitta fayl** (masalan faqat do'konlar):

```bash
python main.py run --file data/incoming/stores.csv
```

Bu holatda `promote_to_core` faqat manbasi bo'lgan protseduralarni chaqiradi — yiqilmaydi.

**Alohida bosqichlar:**

```bash
python main.py run --stage load          # faqat stg
python main.py run --stage core --load-id LOAD-20260828-120000
python main.py run --stage mart --month 2026-01
```

`--stage core` va `--stage mart` uchun `--load-id` yoki avval `--stage all` bajarilgan bo'lishi kerak.

**Sinov (bazaga yozmasdan):**

```bash
python main.py run --dry-run
```

---

## 5. Hisobotlar

```bash
python main.py report --type dashboard
python main.py report --type store --store ST-001
python main.py report --type load_log
python main.py report --type dq --load-id LOAD-20260828-120000
```

Natija `reports/` papkasida HTML fayl sifatida saqlanadi.

---

## 6. Testlar

```bash
python -m pytest tests/ -q
```

52 ta test (validatsiya, pipeline, loader, parserlar).

---

## 7. Loyiha tuzilmasi

```
SavdoLink/
├── config/           # settings.json, validation_rules.json
├── data/
│   ├── incoming/     # kiruvchi fayllar
│   ├── archive/      # yuklangan fayllar
│   └── rejected/     # rad etilgan qatorlar
├── docs/             # hujjatlar (ANALYSIS, profiling, ...)
├── logs/             # LoadId bo'yicha log fayllar
├── reports/          # HTML hisobotlar
├── sql/              # DDL, protseduralar, so'rovlar
├── src/              # Python ETL kodi
├── tests/
├── tools/            # scale_data.py, benchmark_perf.py
└── main.py           # CLI kirish nuqtasi
```

---

## 8. Muammolarni bartaraf etish

| Muammo | Yechim |
|---|---|
| `pyodbc` ulanmaydi | ODBC Driver 17/18 o'rnatilganini tekshiring |
| `core.SalesHeader bo'sh` | `audit.ErrorLog` ni ko'ring; stg da savdo bormi? |
| `logs/` bo'sh | `get_logger` endi `logger.handlers` tekshiradi — qayta ishga tushiring |
| `pip install` xato | `requirements.txt` UTF-8 bo'lishi kerak |

---

## 9. Katta hajmda sinov (S7)

```bash
python tools/scale_data.py --days 400 --seed 42 --start-date 2025-01-01 --out data/scaled
python tools/benchmark_perf.py
```

Batafsil: `docs/performance.md`
