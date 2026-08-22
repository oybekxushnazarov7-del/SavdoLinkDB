CREATE OR ALTER FUNCTION mart.fn_StoreSalesByPeriod
(
    @StoreId  INT,
    @DateFrom DATE,
    @DateTo   DATE
)
RETURNS TABLE
AS
RETURN
(
    SELECT 
        sh.StoreId,
        p.ProductName,
        SUM(sd.Qty) AS TotalQty,
        SUM(sd.LineAmount) AS TotalRevenue
    FROM core.SalesHeader sh
    JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
    JOIN core.Product p ON p.ProductId = sd.ProductId
    WHERE sh.StoreId = @StoreId
      AND CAST(sh.SaleDateTime AS DATE) BETWEEN @DateFrom AND @DateTo
    GROUP BY sh.StoreId, p.ProductName
);
GO