-- S-12: audit.ProductHistory da OldPrice/NewPrice/ValidFrom yo'q;
-- core.Product da UnitPrice yo'q (narx ProductPrice da).
CREATE OR ALTER TRIGGER core.tr_Product_Audit
ON core.Product
AFTER UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- UPDATE (to'plamli: inserted/deleted — jadvallar)
    INSERT INTO audit.ProductHistory (ProductId, ChangeType, OldName, NewName)
    SELECT i.ProductId, 'UPDATE', d.ProductName, i.ProductName
    FROM inserted i
    JOIN deleted  d ON d.ProductId = i.ProductId
    WHERE ISNULL(i.ProductName, '') <> ISNULL(d.ProductName, '');

    -- DELETE
    INSERT INTO audit.ProductHistory (ProductId, ChangeType, OldName, NewName)
    SELECT d.ProductId, 'DELETE', d.ProductName, NULL
    FROM deleted d
    LEFT JOIN inserted i ON i.ProductId = d.ProductId
    WHERE i.ProductId IS NULL;
END;
GO
