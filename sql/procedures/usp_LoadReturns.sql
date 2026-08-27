-- stg.RawReturns: ReturnId/ReceiptNo/StoreCode/Sku — core.Returns: ReturnCode + FK.
CREATE OR ALTER PROCEDURE core.usp_LoadReturns
    @LoadId     NVARCHAR(50),
    @RowsLoaded INT = 0 OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @LoadId IS NULL OR LTRIM(RTRIM(@LoadId)) = ''
        THROW 50001, 'LoadId ko''rsatilmagan', 1;

    BEGIN TRY
        BEGIN TRANSACTION;

        MERGE core.Returns AS tgt
        USING (
            SELECT
                LTRIM(RTRIM(rr.ReturnId)) AS ReturnCode,
                sh.SalesHeaderId,
                p.ProductId,
                TRY_CONVERT(INT, rr.Qty) AS Qty,
                LTRIM(RTRIM(rr.Reason)) AS Reason,
                COALESCE(
                    TRY_CONVERT(DATE, rr.ReturnDate, 23),
                    TRY_CONVERT(DATE, rr.ReturnDate, 104)
                ) AS ReturnDate
            FROM stg.RawReturns rr
            JOIN core.Store st ON st.StoreCode = LTRIM(RTRIM(rr.StoreCode))
            JOIN core.SalesHeader sh
                ON sh.ReceiptNo = LTRIM(RTRIM(rr.ReceiptNo))
               AND sh.StoreId = st.StoreId
            JOIN core.Product p ON p.Sku = LTRIM(RTRIM(rr.Sku))
            WHERE rr.LoadId = @LoadId
              AND NULLIF(LTRIM(RTRIM(rr.ReturnId)), '') IS NOT NULL
        ) AS src
            ON tgt.ReturnCode = src.ReturnCode
        WHEN MATCHED THEN
            UPDATE SET
                tgt.Qty = src.Qty,
                tgt.Reason = src.Reason,
                tgt.ReturnDate = src.ReturnDate
        WHEN NOT MATCHED AND src.ReturnDate IS NOT NULL AND src.Qty IS NOT NULL THEN
            INSERT (ReturnCode, SalesHeaderId, ProductId, Qty, Reason, ReturnDate)
            VALUES (src.ReturnCode, src.SalesHeaderId, src.ProductId, src.Qty, src.Reason, src.ReturnDate);

        SET @RowsLoaded = @@ROWCOUNT;

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
