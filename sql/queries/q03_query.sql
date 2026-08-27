/* ------------------------------------------------------------------
   Fayl   : q03_above_avg_cashiers.sql
   Savol  : O'rtachadan yuqori savdo qilgan kassirlar
   Texnika: Skalyar Subquery
   Eslatma: core.Cashier yo'q — core.Employee (S-11 bilan mos)
   ------------------------------------------------------------------ */
WITH CashierSales AS (
    SELECT
        e.EmployeeId,
        e.FullName AS CashierName,
        ISNULL(SUM(sd.LineAmount), 0) AS TotalSales
    FROM core.Employee e
    LEFT JOIN core.SalesHeader sh ON sh.EmployeeId = e.EmployeeId
    LEFT JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
    WHERE e.Position IN ('Kassir', 'Sotuvchi')
    GROUP BY e.EmployeeId, e.FullName
)
SELECT
    CashierName,
    TotalSales
FROM CashierSales
WHERE TotalSales > (SELECT AVG(TotalSales) FROM CashierSales);
