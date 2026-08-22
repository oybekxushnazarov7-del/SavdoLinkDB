SELECT 
    s.StoreName,
    DATEPART(YEAR, sh.SaleDateTime) AS SaleYear,
    DATEPART(MONTH, sh.SaleDateTime) AS SaleMonth,
    SUM(sd.LineAmount) AS TotalSales,
    COUNT(DISTINCT sh.SalesHeaderId) AS TotalOrders
FROM core.SalesHeader sh
JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
JOIN core.Store s ON s.StoreId = sh.StoreId
GROUP BY s.StoreName, DATEPART(YEAR, sh.SaleDateTime), DATEPART(MONTH, sh.SaleDateTime)
ORDER BY SaleYear, SaleMonth, s.StoreName;