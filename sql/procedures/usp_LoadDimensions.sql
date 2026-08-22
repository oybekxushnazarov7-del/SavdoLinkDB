CREATE OR ALTER PROCEDURE core.usp_LoadDimensions
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

        -- 1. Region Dimension
        ;WITH src_region AS (
            SELECT DISTINCT LTRIM(RTRIM(Region)) AS RegionName
            FROM stg.RawStores
            WHERE LoadId = @LoadId AND NULLIF(LTRIM(RTRIM(Region)), '') IS NOT NULL
        )
        MERGE core.Region AS tgt
        USING src_region AS src
            ON tgt.RegionName = src.RegionName
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (RegionName) VALUES (src.RegionName)
        OUTPUT $action INTO @Changes;

        -- 2. Store Dimension
        ;WITH src_store AS (
            SELECT DISTINCT 
                TRY_CONVERT(INT, StoreId) AS StoreId,
                LTRIM(RTRIM(StoreName)) AS StoreName,
                LTRIM(RTRIM(City)) AS City,
                TRY_CONVERT(DECIMAL(10,2), REPLACE(AreaM2, ',', '.')) AS AreaM2
            FROM stg.RawStores
            WHERE LoadId = @LoadId AND StoreId IS NOT NULL
        )
        MERGE core.Store AS tgt
        USING src_store AS src
            ON tgt.StoreId = src.StoreId
        WHEN MATCHED AND (
            tgt.StoreName <> src.StoreName OR
            tgt.City <> src.City OR
            ISNULL(tgt.AreaM2, -1) <> ISNULL(src.AreaM2, -1)
        ) THEN
            UPDATE SET 
                tgt.StoreName = src.StoreName,
                tgt.City = src.City,
                tgt.AreaM2 = src.AreaM2
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (StoreId, StoreName, City, AreaM2)
            VALUES (src.StoreId, src.StoreName, src.City, src.AreaM2)
        OUTPUT $action INTO @Changes;

        -- 3. Cashier Dimension
        ;WITH src_cashier AS (
            SELECT DISTINCT 
                TRY_CONVERT(INT, CashierId) AS CashierId,
                LTRIM(RTRIM(CashierName)) AS CashierName
            FROM stg.RawCashiers
            WHERE LoadId = @LoadId AND CashierId IS NOT NULL
        )
        MERGE core.Cashier AS tgt
        USING src_cashier AS src
            ON tgt.CashierId = src.CashierId
        WHEN MATCHED AND tgt.CashierName <> src.CashierName THEN
            UPDATE SET tgt.CashierName = src.CashierName
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (CashierId, CashierName)
            VALUES (src.CashierId, src.CashierName)
        OUTPUT $action INTO @Changes;

        -- Statistika hisoblash
        SELECT @RowsInserted = COUNT(*) FROM @Changes WHERE ChangeAction = 'INSERT';
        SELECT @RowsUpdated  = COUNT(*) FROM @Changes WHERE ChangeAction = 'UPDATE';

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