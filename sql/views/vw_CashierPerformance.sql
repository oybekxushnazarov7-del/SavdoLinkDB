CREATE OR ALTER VIEW mart.vw_CashierPerformance AS
SELECT 
    c.CashierId,
    c.CashierName,
    s.StoreName,
    COUNT(DISTINCT sh.SalesHeaderId) AS TotalTransactions,
    ISNULL(SUM(sd.LineAmount), 0) AS TotalSales,
    ROUND(ISNULL(SUM(sd.LineAmount), 0) / NULLIF(COUNT(DISTINCT sh.SalesHeaderId), 0), 2) AS AvgReceiptValue
FROM core.Cashier c
JOIN core.SalesHeader sh ON sh.CashierId = c.CashierId
JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
JOIN core.Store s ON s.StoreId = sh.StoreId
GROUP BY c.CashierId, c.CashierName, s.StoreName;
GO