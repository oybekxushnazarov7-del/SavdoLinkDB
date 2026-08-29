
IF OBJECT_ID('stg.RawSales','U') is null 
Begin
    CREATE TABLE stg.RawSales (
        RawSalesId    BIGINT IDENTITY(1,1) NOT NULL,
        LoadId        NVARCHAR(50)  NOT NULL,
        SourceFile    NVARCHAR(260) NOT NULL,
        RowNum        INT           NOT NULL,
        LoadedAt      DATETIME2(0)  NOT NULL CONSTRAINT DF_RawSales_LoadedAt DEFAULT SYSDATETIME(),

        ReceiptNo     NVARCHAR(200) NULL,
        StoreCode     NVARCHAR(200) NULL,
        CashierId     NVARCHAR(200) NULL,
        SaleDateTime  NVARCHAR(200) NULL,
        Sku           NVARCHAR(200) NULL,
        Qty           NVARCHAR(200) NULL,
        UnitPrice     NVARCHAR(200) NULL,
        DiscountPct   NVARCHAR(200) NULL,
        PaymentType   NVARCHAR(200) NULL,
        UnitPriceResolved NVARCHAR(200) NULL,
        PriceSource       NVARCHAR(20)  NULL,

        CONSTRAINT PK_RawSales PRIMARY KEY CLUSTERED (RawSalesId)
    );
End

IF OBJECT_ID('stg.RawStores','U') is null 
Begin
    CREATE TABLE stg.RawStores (
        RawStoreId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,
        SourceFile NVARCHAR(260) NOT NULL,
        RowNum INT NOT NULL,
        LoadedAt DATETIME2(0) NOT NULL CONSTRAINT DF_RawStores_LoadedAt DEFAULT SYSDATETIME(),

        StoreCode NVARCHAR(200) NULL,
        StoreName NVARCHAR(200) NULL,
        Region NVARCHAR(200) NULL,
        City NVARCHAR(200) NULL,
        OpenedDate NVARCHAR(200) NULL,
        AreaM2 NVARCHAR(200) NULL,

        CONSTRAINT PK_RawStores PRIMARY KEY CLUSTERED (RawStoreId)
    );
End

IF OBJECT_ID('stg.RawEmployees','U') is null 
Begin
    CREATE TABLE stg.RawEmployees (
        RawEmployeeId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,
        SourceFile NVARCHAR(260) NOT NULL,
        RowNum INT NOT NULL,
        LoadedAt DATETIME2(0) NOT NULL CONSTRAINT DF_RawEmployees_LoadedAt DEFAULT SYSDATETIME(),

        EmpCode NVARCHAR(200) NULL,
        FullName NVARCHAR(200) NULL,
        StoreCode NVARCHAR(200) NULL,
        Position NVARCHAR(200) NULL,
        Salary NVARCHAR(200) NULL,
        HiredDate NVARCHAR(200) NULL,
        ManagerCode NVARCHAR(200) NULL,
        IsActive NVARCHAR(200) NULL,

        CONSTRAINT PK_RawEmployees PRIMARY KEY CLUSTERED (RawEmployeeId)
    );
End

IF OBJECT_ID('stg.RawCategories','U') is null 
Begin
    CREATE TABLE stg.RawCategories (
        RawCategoryId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,
        SourceFile NVARCHAR(260) NOT NULL,
        RowNum INT NOT NULL,
        LoadedAt DATETIME2(0) NOT NULL CONSTRAINT DF_RawCategories_LoadedAt DEFAULT SYSDATETIME(),
        CategoryCode NVARCHAR(200) NULL,
        CategoryName NVARCHAR(200) NULL,
        ParentCategoryCode NVARCHAR(200) NULL,
        [Level] tinyint not null,
        CONSTRAINT PK_RawCategories PRIMARY KEY CLUSTERED (RawCategoryId)
    );
END

IF OBJECT_ID('stg.RawSuppliers','U') is null 
Begin
    CREATE TABLE stg.RawSuppliers (
        RawSupplierId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,
        SourceFile NVARCHAR(260) NOT NULL,
        RowNum INT NOT NULL,
        LoadedAt DATETIME2(0) NOT NULL CONSTRAINT DF_RawSuppliers_LoadedAt DEFAULT SYSDATETIME(),

        Inn NVARCHAR(200) NULL,
        SupplierName NVARCHAR(200) NULL,
        Country NVARCHAR(200) NULL,
        ContractDate NVARCHAR(200) NULL,

        CONSTRAINT PK_RawSuppliers PRIMARY KEY CLUSTERED (RawSupplierId)
    );
END

IF OBJECT_ID('stg.RawProducts','U') is null 
Begin
    CREATE TABLE stg.RawProducts (
        RawProductId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,
        SourceFile NVARCHAR(260) NOT NULL,
        RowNum INT NOT NULL,
        LoadedAt DATETIME2(0) NOT NULL CONSTRAINT DF_RawProducts_LoadedAt DEFAULT SYSDATETIME(),

        Sku NVARCHAR(200) NULL,
        ProductName NVARCHAR(200) NULL,
        CategoryCode NVARCHAR(200) NULL,
        SupplierInn NVARCHAR(200) NULL,
        Unit NVARCHAR(200) NULL,
        Barcode NVARCHAR(200) NULL,
        IsActive NVARCHAR(200) NULL,

        CONSTRAINT PK_RawProducts PRIMARY KEY CLUSTERED (RawProductId)
    );
END

IF OBJECT_ID('stg.RawPrices','U') is null 
Begin
    CREATE TABLE stg.RawPrices (
        RawPriceId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,
        SourceFile NVARCHAR(260) NOT NULL,
        RowNum INT NOT NULL,
        LoadedAt DATETIME2(0) NOT NULL CONSTRAINT DF_RawPrices_LoadedAt DEFAULT SYSDATETIME(),

        Sku NVARCHAR(200) NULL,
        ValidFrom NVARCHAR(200) NULL,
        ValidTo NVARCHAR(200) NULL,
        Price NVARCHAR(200) NULL,

        CONSTRAINT PK_RawPrices PRIMARY KEY CLUSTERED (RawPriceId)
    );
END

IF OBJECT_ID('stg.RawReturns','U') is null 
Begin
    CREATE TABLE stg.RawReturns (
        RawReturnId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,
        SourceFile NVARCHAR(260) NOT NULL,
        RowNum INT NOT NULL,
        LoadedAt DATETIME2(0) NOT NULL CONSTRAINT DF_RawReturns_LoadedAt DEFAULT SYSDATETIME(),

        ReturnId NVARCHAR(200) NULL,
        ReceiptNo NVARCHAR(200) NULL,
        StoreCode NVARCHAR(200) NULL,
        Sku NVARCHAR(200) NULL,
        Qty NVARCHAR(200) NULL,
        Reason NVARCHAR(200) NULL,
        ReturnDate NVARCHAR(200) NULL,

        CONSTRAINT PK_RawReturns PRIMARY KEY CLUSTERED (RawReturnId)
    );
END

-- S-03: nusxa xatosi — IF RawEmployees edi, CREATE RawRates; RawRates hech qachon yaratilmas edi
IF OBJECT_ID('stg.RawRates','U') is null 
Begin
    CREATE TABLE stg.RawRates (
        RawRateId BIGINT IDENTITY(1,1) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,
        SourceFile NVARCHAR(260) NOT NULL,
        RowNum INT NOT NULL,
        LoadedAt DATETIME2(0) NOT NULL CONSTRAINT DF_RawRates_LoadedAt DEFAULT SYSDATETIME(),

        RateDate NVARCHAR(200) NULL,
        CurrencyCode NVARCHAR(200) NULL,
        Rate NVARCHAR(200) NULL,

        CONSTRAINT PK_RawRates PRIMARY KEY CLUSTERED (RawRateId)
    );
END

-- Migratsiya: mavjud bazalarga tiklangan narx ustunlari
IF COL_LENGTH('stg.RawSales', 'UnitPriceResolved') IS NULL
    ALTER TABLE stg.RawSales ADD UnitPriceResolved NVARCHAR(200) NULL;
IF COL_LENGTH('stg.RawSales', 'PriceSource') IS NULL
    ALTER TABLE stg.RawSales ADD PriceSource NVARCHAR(20) NULL;