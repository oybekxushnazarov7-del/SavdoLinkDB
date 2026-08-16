CREATE OR ALTER PROCEDURE mart.sp_RefreshFactDailySales
AS
BEGIN
    SET NOCOUNT ON;

    -- Eski ma'lumotlarni tozalab, qayta hisoblash (Full Refresh yoki Incremental)
    TRUNCATE TABLE mart.FactDailySales;

    INSERT INTO mart.FactDailySales (
        SaleDate, StoreId, CategoryId, StoreName, CategoryName,
        ReceiptCount, QtySold, GrossAmount, NetAmount, ReturnAmount, RefreshedAt
    )
    SELECT 
        CAST(s.SaleDateTime AS DATE) AS SaleDate,
        s.StoreId,
        p.CategoryId,
        st.StoreName,
        c.CategoryName,
        COUNT(DISTINCT s.ReceiptNo) AS ReceiptCount,
        SUM(s.Qty) AS QtySold,
        SUM(s.Qty * s.UnitPrice) AS GrossAmount,
        SUM(s.NetAmount) AS NetAmount,
        ISNULL(SUM(r.ReturnAmount), 0) AS ReturnAmount,
        SYSDATETIME() AS RefreshedAt
    FROM core.Sales s
    JOIN core.Store st ON s.StoreId = st.StoreId
    JOIN core.Product p ON s.ProductId = p.ProductId
    JOIN core.Category c ON p.CategoryId = c.CategoryId
    LEFT JOIN core.Returns r ON s.ReceiptNo = r.ReceiptNo AND s.ProductId = r.ProductId
    GROUP BY 
        CAST(s.SaleDateTime AS DATE),
        s.StoreId,
        p.CategoryId,
        st.StoreName,
        c.CategoryName;
END;