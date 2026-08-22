CREATE OR ALTER PROCEDURE core.usp_LoadProducts
    @LoadId        NVARCHAR(50),
    @RowsInserted INT = 0 OUTPUT,
    @RowsUpdated  INT = 0 OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @LoadId IS NULL OR LTRIM(RTRIM(@LoadId)) = ''
        THROW 50001, 'LoadId ko''rsatilmagan', 1;

    DECLARE @Changes TABLE (ChangeAction NVARCHAR(10));

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Vaqtinchalik jadvalga xavfsiz tip o'girish orqali ma'lumot yig'ish
        SELECT DISTINCT
            TRY_CONVERT(INT, ProductId) AS ProductId,
            LTRIM(RTRIM(SKU)) AS SKU,
            LTRIM(RTRIM(ProductName)) AS ProductName,
            LTRIM(RTRIM(Category)) AS Category,
            TRY_CONVERT(DECIMAL(12,2), REPLACE(UnitPrice, ',', '.')) AS UnitPrice
        INTO #TempProducts
        FROM stg.RawProducts
        WHERE LoadId = @LoadId AND ProductId IS NOT NULL;

        -- Product Dimension 'ga MERGE qilish
        MERGE core.Product AS tgt
        USING #TempProducts AS src
            ON tgt.ProductId = src.ProductId
        WHEN MATCHED AND (
            tgt.ProductName <> src.ProductName OR
            tgt.Category <> src.Category OR
            tgt.UnitPrice <> src.UnitPrice
        ) THEN
            UPDATE SET 
                tgt.ProductName = src.ProductName,
                tgt.Category = src.Category,
                tgt.UnitPrice = src.UnitPrice
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (ProductId, SKU, ProductName, Category, UnitPrice)
            VALUES (src.ProductId, src.SKU, src.ProductName, src.Category, src.UnitPrice)
        OUTPUT $action INTO @Changes;

        -- LEAD() yordamida narxlar tarixining amal qilish muddatini (ValidTo) qayta hisoblash
        WITH ProductHistoryCalculated AS (
            SELECT 
                HistoryId,
                ValidFrom,
                LEAD(ValidFrom) OVER (PARTITION BY ProductId ORDER BY ValidFrom) AS NewValidTo
            FROM audit.ProductHistory
        )
        UPDATE ph
        SET ph.ValidTo = phc.NewValidTo
        FROM audit.ProductHistory ph
        JOIN ProductHistoryCalculated phc ON ph.HistoryId = phc.HistoryId
        WHERE ph.ValidTo IS NULL OR ph.ValidTo <> phc.NewValidTo;

        SELECT @RowsInserted = COUNT(*) FROM @Changes WHERE ChangeAction = 'INSERT';
        SELECT @RowsUpdated  = COUNT(*) FROM @Changes WHERE ChangeAction = 'UPDATE';

        DROP TABLE #TempProducts;
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