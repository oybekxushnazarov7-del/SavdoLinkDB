CREATE OR ALTER PROCEDURE core.usp_LoadSales
    @LoadId        NVARCHAR(50),
    @HeadersLoaded INT = 0 OUTPUT,
    @DetailsLoaded INT = 0 OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @LoadId IS NULL OR LTRIM(RTRIM(@LoadId)) = ''
        THROW 50001, 'LoadId ko''rsatilmagan', 1;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- 1. Vaqtinchalik jadvalga xatolar va tiplardan tozalangan ma'lumotni olish
        SELECT 
            LTRIM(RTRIM(ReceiptNo)) AS ReceiptNo,
            TRY_CONVERT(INT, StoreId) AS StoreId,
            TRY_CONVERT(INT, CashierId) AS CashierId,
            TRY_CONVERT(DATETIME2(0), SaleDateTime, 120) AS SaleDateTime,
            TRY_CONVERT(INT, ProductId) AS ProductId,
            TRY_CONVERT(INT, Qty) AS Qty,
            TRY_CONVERT(DECIMAL(12,2), REPLACE(UnitPrice, ',', '.')) AS UnitPrice,
            TRY_CONVERT(DECIMAL(5,2), REPLACE(DiscountPct, ',', '.')) AS DiscountPct
        INTO #TempSales
        FROM stg.RawSales
        WHERE LoadId = @LoadId
          AND ReceiptNo IS NOT NULL 
          AND StoreId IS NOT NULL 
          AND ProductId IS NOT NULL;

        -- 2. Header (Sarlavha) qatlamini MERGE qilish
        MERGE core.SalesHeader AS tgt
        USING (
            SELECT DISTINCT ReceiptNo, StoreId, CashierId, SaleDateTime
            FROM #TempSales
        ) AS src
            ON tgt.ReceiptNo = src.ReceiptNo AND tgt.StoreId = src.StoreId
        WHEN NOT MATCHED THEN
            INSERT (ReceiptNo, StoreId, CashierId, SaleDateTime, LoadId)
            VALUES (src.ReceiptNo, src.StoreId, src.CashierId, src.SaleDateTime, @LoadId);

        SET @HeadersLoaded = @@ROWCOUNT;

        -- 3. Detail (Tafsilot) qatlamini MERGE qilish
        MERGE core.SalesDetail AS tgt
        USING (
            SELECT 
                sh.SalesHeaderId,
                ts.ProductId,
                ts.Qty,
                ts.UnitPrice,
                ts.DiscountPct,
                ROUND(ts.Qty * ts.UnitPrice * (1 - ISNULL(ts.DiscountPct, 0) / 100.0), 2) AS LineAmount
            FROM #TempSales ts
            JOIN core.SalesHeader sh ON sh.ReceiptNo = ts.ReceiptNo AND sh.StoreId = ts.StoreId
        ) AS src
            ON tgt.SalesHeaderId = src.SalesHeaderId AND tgt.ProductId = src.ProductId
        WHEN MATCHED THEN
            UPDATE SET 
                tgt.Qty = src.Qty,
                tgt.UnitPrice = src.UnitPrice,
                tgt.DiscountPct = src.DiscountPct,
                tgt.LineAmount = src.LineAmount
        WHEN NOT MATCHED THEN
            INSERT (SalesHeaderId, ProductId, Qty, UnitPrice, DiscountPct, LineAmount)
            VALUES (src.SalesHeaderId, src.ProductId, src.Qty, src.UnitPrice, src.DiscountPct, src.LineAmount);

        SET @DetailsLoaded = @@ROWCOUNT;

        DROP TABLE #TempSales;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        INSERT INTO audit.ErrorLog (LoadId, ErrorNumber, ErrorMessage, ErrorLine, ErrorProcedure)
        VALUES (@LoadId, ERROR_NUMBER(), ERROR_MESSAGE(), ERROR_LINE(), ERROR_PROCEDURE());
        THROW;
    END CATCH
END
GO