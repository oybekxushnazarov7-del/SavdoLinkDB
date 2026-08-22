CREATE OR ALTER PROCEDURE mart.usp_GenerateStoreReports
    @DateFrom DATE,
    @DateTo   DATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @StoreId INT;
    DECLARE @StoreName NVARCHAR(100);
    DECLARE @TotalNet DECIMAL(18,2);

    -- Kursor mashqi (Solishtirish va tahlil uchun)
    DECLARE store_cursor CURSOR LOCAL FAST_FORWARD FOR
        SELECT StoreId, StoreName FROM core.Store WHERE IsActive = 1;

    OPEN store_cursor;
    FETCH NEXT FROM store_cursor INTO @StoreId, @StoreName;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SELECT @TotalNet = SUM(sd.LineAmount)
        FROM core.SalesHeader sh
        JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
        WHERE sh.StoreId = @StoreId
          AND CAST(sh.SaleDateTime AS DATE) BETWEEN @DateFrom AND @DateTo;

        PRINT 'Do''kon: ' + @StoreName + ' | Umumiysotuv: ' + CAST(ISNULL(@TotalNet, 0) AS NVARCHAR(30));

        FETCH NEXT FROM store_cursor INTO @StoreId, @StoreName;
    END;

    CLOSE store_cursor;
    DEALLOCATE store_cursor;
END
GO