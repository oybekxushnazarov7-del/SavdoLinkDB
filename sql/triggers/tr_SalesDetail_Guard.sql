CREATE OR ALTER TRIGGER core.tr_SalesDetail_Guard
ON core.SalesDetail
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Chegirma stavkasi 50% dan yuqori bo'lgan holatlarni bloklash
    IF EXISTS (SELECT 1 FROM inserted WHERE DiscountPct > 50.0)
    BEGIN
        RAISERROR ('Chegirma foizi ruxsat etilgan 50%% dan oshishi mumkin emas!', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
END;
GO