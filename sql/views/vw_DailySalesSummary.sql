CREATE OR ALTER VIEW mart.vw_DailySalesSummary AS
SELECT 
    CAST(sh.SaleDateTime AS DATE) AS SaleDate,
    COUNT(DISTINCT sh.SalesHeaderId) AS TotalReceipts,
    SUM(sd.Qty) AS TotalItemsSold,
    SUM(sd.LineAmount) AS GrossRevenue
FROM core.SalesHeader sh
JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
GROUP BY CAST(sh.SaleDateTime AS DATE);
GO