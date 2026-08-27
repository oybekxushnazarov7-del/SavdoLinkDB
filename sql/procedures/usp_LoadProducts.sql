-- S-09: stg.RawProducts da ProductId/Category/UnitPrice yo'q.
-- MERGE tabiiy kalit Sku bo'yicha; CategoryId/SupplierId JOIN orqali.
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

        SELECT DISTINCT
            LTRIM(RTRIM(Sku))                        AS Sku,
            LTRIM(RTRIM(ProductName))                AS ProductName,
            LTRIM(RTRIM(CategoryCode))               AS CategoryCode,
            LTRIM(RTRIM(SupplierInn))                AS SupplierInn,
            LOWER(LTRIM(RTRIM(Unit)))                AS Unit,
            LTRIM(RTRIM(Barcode))                    AS Barcode,
            TRY_CONVERT(BIT, IsActive)               AS IsActive
        INTO #TempProducts
        FROM stg.RawProducts
        WHERE LoadId = @LoadId
          AND NULLIF(LTRIM(RTRIM(Sku)), '') IS NOT NULL;

        MERGE core.Product AS tgt
        USING (
            SELECT t.Sku, t.ProductName, c.CategoryId, s.SupplierId,
                   t.Unit, t.Barcode, ISNULL(t.IsActive, 1) AS IsActive
            FROM #TempProducts t
            JOIN core.Category c ON c.CategoryCode = t.CategoryCode
            JOIN core.Supplier s ON s.Inn          = t.SupplierInn
        ) AS src
            ON tgt.Sku = src.Sku
        WHEN MATCHED AND (
                tgt.ProductName <> src.ProductName
             OR tgt.CategoryId  <> src.CategoryId
             OR tgt.SupplierId  <> src.SupplierId
             OR ISNULL(tgt.Barcode,'') <> ISNULL(src.Barcode,'')
             OR tgt.IsActive <> src.IsActive
        ) THEN
            UPDATE SET tgt.ProductName = src.ProductName,
                       tgt.CategoryId  = src.CategoryId,
                       tgt.SupplierId  = src.SupplierId,
                       tgt.Barcode     = src.Barcode,
                       tgt.Unit        = src.Unit,
                       tgt.IsActive    = src.IsActive
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (Sku, ProductName, CategoryId, SupplierId, Unit, Barcode, IsActive)
            VALUES (src.Sku, src.ProductName, src.CategoryId, src.SupplierId,
                    src.Unit, src.Barcode, src.IsActive)
        OUTPUT $action INTO @Changes;

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
