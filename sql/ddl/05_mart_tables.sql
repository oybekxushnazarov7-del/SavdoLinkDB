IF OBJECT_ID('mart.FactDailySales', 'U') IS NOT NULL DROP TABLE mart.FactDailySales;
GO

CREATE TABLE mart.FactDailySales (
    FactId BIGINT IDENTITY(1,1) NOT NULL,
    SaleDate DATE NOT NULL,
    StoreId INT NOT NULL,
    CategoryId INT NOT NULL,
    
    -- Denormalizatsiya (JOIN kamaytirish uchun ataylab takrorlangan ustunlar)
    StoreName NVARCHAR(150) NOT NULL,
    CategoryName NVARCHAR(150) NOT NULL,
    
    -- Metrikalar (Agregatsiyalangan ko'rsatkichlar)
    ReceiptCount INT NOT NULL,
    QtySold INT NOT NULL,
    GrossAmount DECIMAL(16,2) NOT NULL,
    NetAmount DECIMAL(16,2) NOT NULL,
    ReturnAmount DECIMAL(16,2) NOT NULL,
    
    RefreshedAt DATETIME2(0) NOT NULL CONSTRAINT DF_FactDailySales_RefreshedAt DEFAULT SYSDATETIME(),

    CONSTRAINT PK_FactDailySales PRIMARY KEY CLUSTERED (FactId)
);

SELECT * FROM mart.FactDailySales;