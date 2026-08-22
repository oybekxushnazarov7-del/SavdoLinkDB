# SavdoLink — Retail ETL & Analytical Reporting System

SavdoLink — chakana savdo tarmog'ining operatsion ma'lumotlarini (CSV/JSON formatdagi cheklar va qaytarishlar) yig'uvchi, tozalovchi, Data Quality validsiyasidan o'tkazuvchi va SQL Server dWH hamda HTML analitik panellarini shakllantiruvchi ETL quvuri[cite: 3].

## Tizim Arxitekturasi
`CSV/JSON Data Sources` ➔ `Extract (Python)` ➔ `Transform & DQ Validation` ➔ `Load (MS SQL Server Core)` ➔ `Mart Aggregation (Stored Procedures)` ➔ `Jinja2 HTML Reports & Dashboard`[cite: 3]

---

## Talablar
* Python 3.10+
* Microsoft SQL Server 2019+
* ODBC Driver 17 or 18 for SQL Server

---

## O'rnatish va Sozlash

1. **Repozitoriyani klon qiling va virtual muhitni ishga tushiring:**
```bash
git clone [https://github.com/user/savdolink.git](https://github.com/user/savdolink.git)
cd savdolink
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt