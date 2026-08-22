CREATE OR ALTER VIEW mart.vw_StoreOverview AS
SELECT 
    s.StoreId,
    s.StoreName,
    s.City,
    r.RegionName,
    COUNT(DISTINCT sh.SalesHeaderId) AS TotalOrders,
    ISNULL(SUM(sd.LineAmount), 0) AS TotalRevenue
FROM core.Store s
LEFT JOIN core.Region r ON r.RegionId = s.RegionId
LEFT JOIN core.SalesHeader sh ON sh.StoreId = s.StoreId
LEFT JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
GROUP BY s.StoreId, s.StoreName, s.City, r.RegionName;
GO