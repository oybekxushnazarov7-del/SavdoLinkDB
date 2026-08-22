CREATE OR ALTER VIEW mart.vw_ProductPerformance AS
SELECT 
    p.ProductId,
    p.ProductName,
    ISNULL(SUM(sd.Qty), 0) AS TotalQtySold,
    ISNULL(SUM(sd.LineAmount), 0) AS TotalRevenue,
    ISNULL(SUM(r.Qty), 0) AS TotalQtyReturned
FROM core.Product p
LEFT JOIN core.SalesDetail sd ON sd.ProductId = p.ProductId
LEFT JOIN core.Returns r ON r.ProductId = p.ProductId
GROUP BY p.ProductId, p.ProductName;
GO