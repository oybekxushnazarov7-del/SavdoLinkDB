CREATE OR ALTER TRIGGER core.tr_Product_Audit
ON core.Product
AFTER UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- UPDATE amallari auditi
    INSERT INTO audit.ProductHistory (ProductId, ChangeType, OldName, NewName, OldPrice, NewPrice, ValidFrom)
    SELECT 
        i.ProductId,
        'UPDATE',
        d.ProductName,
        i.ProductName,
        d.UnitPrice,
        i.UnitPrice,
        SYSDATETIME()
    FROM inserted i
    JOIN deleted d ON d.ProductId = i.ProductId
    WHERE ISNULL(i.ProductName, '') <> ISNULL(d.ProductName, '')
       OR ISNULL(i.UnitPrice, 0) <> ISNULL(d.UnitPrice, 0);

    -- DELETE amallari auditi
    INSERT INTO audit.ProductHistory (ProductId, ChangeType, OldName, NewName, OldPrice, NewPrice, ValidFrom)
    SELECT 
        d.ProductId,
        'DELETE',
        d.ProductName,
        NULL,
        d.UnitPrice,
        NULL,
        SYSDATETIME()
    FROM deleted d
    LEFT JOIN inserted i ON i.ProductId = d.ProductId
    WHERE i.ProductId IS NULL;
END;
GO