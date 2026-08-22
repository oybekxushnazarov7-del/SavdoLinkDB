CREATE OR ALTER TRIGGER core.tr_Store_PreventDelete
ON core.Store
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- O'chirish o'rniga soft-delete (IsActive = 0) qilish
    UPDATE s
    SET s.IsActive = 0
    FROM core.Store s
    JOIN deleted d ON d.StoreId = s.StoreId;
END;
GO