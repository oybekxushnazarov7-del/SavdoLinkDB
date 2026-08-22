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
                TRY_CONVERT(INT, ReturnId) AS ReturnId,
                TRY_CONVERT(INT, SalesHeaderId) AS SalesHeaderId,
                TRY_CONVERT(INT, ProductId) AS ProductId,
                TRY_CONVERT(DATETIME2(0), ReturnDateTime, 120) AS ReturnDateTime,
                TRY_CONVERT(INT, Qty) AS Qty,
                LTRIM(RTRIM(Reason)) AS Reason
            FROM stg.RawReturns
            WHERE LoadId = @LoadId AND ReturnId IS NOT NULL
        ) AS src
            ON tgt.ReturnId = src.ReturnId
        WHEN MATCHED THEN
            UPDATE SET 
                tgt.Qty = src.Qty,
                tgt.Reason = src.Reason
        WHEN NOT MATCHED THEN
            INSERT (ReturnId, SalesHeaderId, ProductId, ReturnDateTime, Qty, Reason, LoadId)
            VALUES (src.ReturnId, src.SalesHeaderId, src.ProductId, src.ReturnDateTime, src.Qty, src.Reason, @LoadId);

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