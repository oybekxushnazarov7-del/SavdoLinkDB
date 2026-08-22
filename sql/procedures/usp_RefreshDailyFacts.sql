CREATE OR ALTER PROCEDURE mart.usp_RefreshDailyFacts
    @DateFrom DATE,
    @DateTo DATE
AS
BEGIN
    SET NOCOUNT ON;

    -- 1. Idempotentlikni ta'minlash: berilgan diapazondagi eski ma'lumotlarni o'chirish
    DELETE FROM mart.FactDailySales
    WHERE SaleDate BETWEEN @DateFrom AND @DateTo;

    -- 2. Savdo va qaytarish ma'lumotlarini agregatsiya qilish
    WITH SalesAgg AS (
        SELECT 
            CAST(sh.SaleDateTime AS DATE) AS SaleDate,
            sh.StoreId,
            p.CategoryId,
            COUNT(DISTINCT sh.SalesHeaderId) AS ReceiptCount,
            SUM(sd.Quantity) AS QtySold,
            SUM(sd.Quantity * sd.UnitPrice) AS GrossAmount,
            SUM(sd.LineAmount) AS NetAmount
        FROM core.SalesHeader sh
        JOIN core.SalesDetail sd ON sh.SalesHeaderId = sd.SalesHeaderId
        JOIN core.Product p ON p.ProductId = sd.ProductId
        WHERE CAST(sh.SaleDateTime AS DATE) BETWEEN @DateFrom AND @DateTo
        GROUP BY CAST(sh.SaleDateTime AS DATE), sh.StoreId, p.CategoryId
    ),
    ReturnsAgg AS (
        SELECT 
            CAST(r.ReturnDate AS DATE) AS ReturnDate,
            r.StoreId,
            p.CategoryId,
            COUNT(DISTINCT r.ReturnId) AS ReturnCount,
            SUM(rd.LineAmount) AS ReturnAmount
        FROM core.Returns r
        JOIN core.ReturnDetail rd ON r.ReturnId = rd.ReturnId
        JOIN core.Product p ON p.ProductId = rd.ProductId
        WHERE CAST(r.ReturnDate AS DATE) BETWEEN @DateFrom AND @DateTo
        GROUP BY CAST(r.ReturnDate AS DATE), r.StoreId, p.CategoryId
    )
    INSERT INTO mart.FactDailySales (
        SaleDate,
        StoreId,
        CategoryId,
        ReceiptCount,
        QtySold,
        GrossAmount,
        NetAmount,
        ReturnCount,
        ReturnAmount,
        NetSales
    )
    SELECT 
        s.SaleDate,
        s.StoreId,
        s.CategoryId,
        s.ReceiptCount,
        s.QtySold,
        s.GrossAmount,
        s.NetAmount,
        ISNULL(r.ReturnCount, 0) AS ReturnCount,
        ISNULL(r.ReturnAmount, 0) AS ReturnAmount,
        s.NetAmount - ISNULL(r.ReturnAmount, 0) AS NetSales
    FROM SalesAgg s
    LEFT JOIN ReturnsAgg r 
        ON s.SaleDate = r.ReturnDate 
       AND s.StoreId = r.StoreId 
       AND s.CategoryId = r.CategoryId;
END;