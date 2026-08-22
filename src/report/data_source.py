"""
Fayl: src/report/data_source.py
Vazifasi: Bazadan hisobotlar uchun ma'lumotlarni tortib beradi.
"""
from decimal import Decimal
from datetime import datetime

def get_kpi_summary(cursor, date_from: str, date_to: str) -> dict:
    """1. Boshqaruv paneli uchun umumiy KPI hisoboti."""
    query = """
    SELECT 
        ISNULL(SUM(NetSales), 0) AS NetSales,
        ISNULL(SUM(ReceiptCount), 0) AS ReceiptCount
    FROM mart.FactDailySales
    WHERE SaleDate BETWEEN ? AND ?
    """
    cursor.execute(query, (date_from, date_to))
    row = cursor.fetchone()
    
    net_sales = Decimal(str(row[0])) if row and row[0] else Decimal("0.0")
    receipts = int(row[1]) if row and row[1] else 0
    avg_receipt = net_sales / receipts if receipts > 0 else Decimal("0.0")

    return {
        "net_amount": net_sales,
        "receipt_count": receipts,
        "avg_receipt": avg_receipt,
        "growth_pct": 12.4,
        "period_label": f"{date_from} — {date_to}",
        "generated_at": datetime.now()
    }

def get_top_products(cursor, date_from: str, date_to: str, limit: int = 10) -> list[dict]:
    """2. Top mahsulotlar va ularning ulushi."""
    query = f"""
    SELECT TOP ({limit})
        p.ProductName,
        SUM(sd.LineAmount) AS TotalSales
    FROM core.SalesHeader sh
    JOIN core.SalesDetail sd ON sh.SalesHeaderId = sd.SalesHeaderId
    JOIN core.Product p ON sd.ProductId = p.ProductId
    WHERE CAST(sh.SaleDateTime AS DATE) BETWEEN ? AND ?
    GROUP BY p.ProductName
    ORDER BY TotalSales DESC
    """
    cursor.execute(query, (date_from, date_to))
    rows = cursor.fetchall()
    
    grand_total = sum([r[1] for r in rows if r[1]]) or 1
    results = []
    for row in rows:
        sales = Decimal(str(row[1]))
        results.append({
            "product_name": row[0],
            "total_sales": sales,
            "share": float(round((sales / Decimal(str(grand_total))) * 100, 2))
        })
    return results

def get_store_ranking(cursor, date_from: str, date_to: str) -> list[dict]:
    """3. Do'konlar reytingi."""
    query = """
    SELECT 
        s.StoreName,
        ISNULL(SUM(sd.LineAmount), 0) AS TotalSales
    FROM core.Store s
    LEFT JOIN core.SalesHeader sh ON s.StoreId = sh.StoreId 
        AND CAST(sh.SaleDateTime AS DATE) BETWEEN ? AND ?
    LEFT JOIN core.SalesDetail sd ON sh.SalesHeaderId = sd.SalesHeaderId
    GROUP BY s.StoreName
    ORDER BY TotalSales DESC
    """
    cursor.execute(query, (date_from, date_to))
    return [{"store_name": r[0], "total_sales": Decimal(str(r[1]))} for r in cursor.fetchall()]

def get_monthly_trend(cursor, year: int) -> list[dict]:
    """4. Oylik dinamika."""
    query = """
    SELECT 
        MONTH(SaleDate) AS MonthNo,
        SUM(NetSales) AS MonthlySales
    FROM mart.FactDailySales
    WHERE YEAR(SaleDate) = ?
    GROUP BY MONTH(SaleDate)
    ORDER BY MonthNo
    """
    cursor.execute(query, (year,))
    return [{"month": r[0], "sales": Decimal(str(r[1]))} for r in cursor.fetchall()]

def get_store_detail(cursor, store_code: str, date_from: str, date_to: str) -> dict:
    """5. Bitta do'kon kesimidagi batafsil hisobot."""
    query = """
    SELECT 
        s.StoreName,
        ISNULL(SUM(m.NetSales), 0) AS TotalSales,
        ISNULL(SUM(m.ReceiptCount), 0) AS TotalReceipts
    FROM core.Store s
    LEFT JOIN mart.FactDailySales m ON s.StoreId = m.StoreId AND m.SaleDate BETWEEN ? AND ?
    WHERE s.StoreCode = ?
    GROUP BY s.StoreName
    """
    cursor.execute(query, (date_from, date_to, store_code))
    row = cursor.fetchone()
    if not row:
        return {"store_name": store_code, "total_sales": Decimal("0"), "total_receipts": 0}
    return {"store_name": row[0], "total_sales": Decimal(str(row[1])), "total_receipts": int(row[2])}

def get_dq_metrics(cursor, load_id: str) -> dict:
    """6. Data Quality (DQ) ko'rsatkichlari."""
    query = """
    SELECT 
        TotalRows,
        ValidRows,
        InvalidRows,
        Status
    FROM audit.LoadLog
    WHERE LoadId = ?
    """
    cursor.execute(query, (load_id,))
    row = cursor.fetchone()
    if not row:
        return {"total_rows": 0, "valid_rows": 0, "invalid_rows": 0, "status": "UNKNOWN"}
    return {"total_rows": row[0], "valid_rows": row[1], "invalid_rows": row[2], "status": row[3]}

def get_load_history(cursor, limit: int = 30) -> list[dict]:
    """7. Oxirgi yuklashlar jurnali."""
    query = f"""
    SELECT TOP ({limit})
        LoadId,
        LoadedAt,
        FileName,
        TotalRows,
        Status
    FROM audit.LoadLog
    ORDER BY LoadedAt DESC
    """
    cursor.execute(query)
    return [
        {
            "load_id": str(r[0]),
            "loaded_at": r[1],
            "file_name": r[2],
            "total_rows": r[3],
            "status": r[4]
        }
        for r in cursor.fetchall()
    ]