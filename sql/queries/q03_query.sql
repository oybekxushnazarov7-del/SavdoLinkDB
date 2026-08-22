/* ------------------------------------------------------------------
   Fayl   : q03_above_avg_cashiers.sql
   Savol  : O'rtachadan yuqori savdo qilgan kassirlar
   Texnika: Skalyar Subquery
   ------------------------------------------------------------------ */
WITH CashierSales AS (
    SELECT 
        c.CashierId,
        c.CashierName,
        ISNULL(SUM(sd.LineAmount), 0) AS TotalSales
    FROM core.Cashier c
    LEFT JOIN core.SalesHeader sh ON sh.CashierId = c.CashierId
    LEFT JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
    GROUP BY c.CashierId, c.CashierName
)
SELECT 
    CashierName,
    TotalSales
FROM CashierSales
WHERE TotalSales > (SELECT AVG(TotalSales) FROM CashierSales);