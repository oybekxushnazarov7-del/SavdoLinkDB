-- Vazifasi: Analitik so'rovlar va JOIN operatsiyalarini optimizatsiya qilish uchun indekslar.

USE SavdoLinkDB;
GO

-- 1. SalesHeader: Sana va Do'kon bo'yicha filtrlar uchun
CREATE NONCLUSTERED INDEX IX_SalesHeader_SaleDate 
    ON core.SalesHeader (SaleDateTime) 
    INCLUDE (StoreId, EmployeeId);

CREATE NONCLUSTERED INDEX IX_SalesHeader_StoreId 
    ON core.SalesHeader (StoreId, SaleDateTime);

-- 2. SalesDetail: Covering index (JOIN lar uchun asosiy jadvalga tushmaslikni ta'minlaydi)
CREATE NONCLUSTERED INDEX IX_SalesDetail_HeaderId 
    ON core.SalesDetail (SalesHeaderId) 
    INCLUDE (ProductId, Quantity, LineAmount);

CREATE NONCLUSTERED INDEX IX_SalesDetail_ProductId 
    ON core.SalesDetail (ProductId) 
    INCLUDE (Quantity, UnitPrice, LineAmount);

-- 3. Product: Kategoriya va Sku bo'yicha tezkor qidirish
CREATE NONCLUSTERED INDEX IX_Product_CategoryId 
    ON core.Product (CategoryId) 
    INCLUDE (Sku, ProductName);

-- 4. Employee: Do'konlar bo'yicha hodimlarni guruhlash
CREATE NONCLUSTERED INDEX IX_Employee_StoreId 
    ON core.Employee (StoreId) 
    INCLUDE (EmpCode, FullName);

-- 5. Returns: Qaytarishlarni hisoblash uchun
CREATE NONCLUSTERED INDEX IX_Returns_HeaderId 
    ON core.Returns (SalesHeaderId, ProductId) 
    INCLUDE (Quantity);

-- 6. ProductPrice: Sana bo'yicha narx variantlarini aniqlash
CREATE NONCLUSTERED INDEX IX_ProductPrice_Lookup 
    ON core.ProductPrice (ProductId, ValidFrom) 
    INCLUDE (Price);
GO