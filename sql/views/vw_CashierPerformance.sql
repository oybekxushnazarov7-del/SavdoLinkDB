-- S-11: core.Cashier yo'q — core.Employee; sh.CashierId emas sh.EmployeeId
CREATE OR ALTER VIEW mart.vw_CashierPerformance AS
SELECT
    e.EmployeeId,
    e.EmpCode,
    e.FullName,
    s.StoreName,
    COUNT(DISTINCT sh.SalesHeaderId)                AS TotalTransactions,
    ISNULL(SUM(sd.LineAmount), 0)                   AS TotalSales,
    ROUND(ISNULL(SUM(sd.LineAmount), 0)
          / NULLIF(COUNT(DISTINCT sh.SalesHeaderId), 0), 2) AS AvgReceiptValue
FROM core.Employee e
JOIN core.SalesHeader sh ON sh.EmployeeId    = e.EmployeeId
JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
JOIN core.Store       s  ON s.StoreId        = sh.StoreId
WHERE e.Position IN ('Kassir', 'Sotuvchi')
GROUP BY e.EmployeeId, e.EmpCode, e.FullName, s.StoreName;
GO
