

-- 1. SalesHeader
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SalesHeader_SaleDate' AND object_id = OBJECT_ID('core.SalesHeader'))
    CREATE NONCLUSTERED INDEX IX_SalesHeader_SaleDate
        ON core.SalesHeader (SaleDateTime)
        INCLUDE (StoreId, EmployeeId);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SalesHeader_StoreId' AND object_id = OBJECT_ID('core.SalesHeader'))
    CREATE NONCLUSTERED INDEX IX_SalesHeader_StoreId
        ON core.SalesHeader (StoreId, SaleDateTime);
GO

-- 2. SalesDetail (S-04: Quantity → Qty)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SalesDetail_HeaderId' AND object_id = OBJECT_ID('core.SalesDetail'))
    CREATE NONCLUSTERED INDEX IX_SalesDetail_HeaderId
        ON core.SalesDetail (SalesHeaderId)
        INCLUDE (ProductId, Qty, LineAmount);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_SalesDetail_ProductId' AND object_id = OBJECT_ID('core.SalesDetail'))
    CREATE NONCLUSTERED INDEX IX_SalesDetail_ProductId
        ON core.SalesDetail (ProductId)
        INCLUDE (Qty, UnitPrice, LineAmount);
GO

-- 3. Product
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Product_CategoryId' AND object_id = OBJECT_ID('core.Product'))
    CREATE NONCLUSTERED INDEX IX_Product_CategoryId
        ON core.Product (CategoryId)
        INCLUDE (Sku, ProductName);
GO

-- 4. Employee
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Employee_StoreId' AND object_id = OBJECT_ID('core.Employee'))
    CREATE NONCLUSTERED INDEX IX_Employee_StoreId
        ON core.Employee (StoreId)
        INCLUDE (EmpCode, FullName);
GO

-- 5. Returns (S-04: Quantity → Qty)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Returns_HeaderId' AND object_id = OBJECT_ID('core.Returns'))
    CREATE NONCLUSTERED INDEX IX_Returns_HeaderId
        ON core.Returns (SalesHeaderId, ProductId)
        INCLUDE (Qty);
GO

-- 6. ProductPrice
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ProductPrice_Lookup' AND object_id = OBJECT_ID('core.ProductPrice'))
    CREATE NONCLUSTERED INDEX IX_ProductPrice_Lookup
        ON core.ProductPrice (ProductId, ValidFrom)
        INCLUDE (Price);
GO
