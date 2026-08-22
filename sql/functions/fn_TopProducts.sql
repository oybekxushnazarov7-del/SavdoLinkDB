CREATE OR ALTER FUNCTION mart.fn_TopProducts
(
    @TopN     INT,
    @DateFrom DATE,
    @DateTo   DATE
)
RETURNS TABLE
AS
RETURN
(
    SELECT TOP (@TopN)
        p.ProductId,
        p.ProductName,
        SUM(sd.Qty) AS QtySold,
        SUM(sd.LineAmount) AS TotalRevenue
    FROM core.SalesDetail sd
    JOIN core.SalesHeader sh ON sh.SalesHeaderId = sd.SalesHeaderId
    JOIN core.Product p ON p.ProductId = sd.ProductId
    WHERE CAST(sh.SaleDateTime AS DATE) BETWEEN @DateFrom AND @DateTo
    GROUP BY p.ProductId, p.ProductName
    ORDER BY TotalRevenue DESC
);
GO