CREATE OR ALTER PROCEDURE stg.usp_TruncateStaging
    @LoadId NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- Parametr tekshiruvi
    IF @LoadId IS NULL OR LTRIM(RTRIM(@LoadId)) = ''
        THROW 50001, 'LoadId ko''rsatilmagan', 1;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Muayyan LoadId ga tegishli staging ma'lumotlarini o'chirish
        DELETE FROM stg.RawSales WHERE LoadId = @LoadId;
        DELETE FROM stg.RawProducts WHERE LoadId = @LoadId;
        DELETE FROM stg.RawStores WHERE LoadId = @LoadId;
        DELETE FROM stg.RawCashiers WHERE LoadId = @LoadId;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;

        INSERT INTO audit.ErrorLog
            (LoadId, ErrorNumber, ErrorMessage, ErrorLine, ErrorProcedure)
        VALUES
            (@LoadId, ERROR_NUMBER(), ERROR_MESSAGE(), ERROR_LINE(), ERROR_PROCEDURE());

        THROW;
    END CATCH
END
GO