

IF OBJECT_ID('core.Region', 'U') IS NULL
BEGIN
    CREATE TABLE core.Region (
        RegionId INT IDENTITY(1,1) NOT NULL,
        RegionName NVARCHAR(100) NOT NULL,
        CreatedAt DATETIME2(0) NOT NULL CONSTRAINT DF_Region_CreatedAt DEFAULT SYSDATETIME(),

        CONSTRAINT PK_Region PRIMARY KEY CLUSTERED (RegionId),
        CONSTRAINT UQ_Region_Name UNIQUE (RegionName)
    );
END;

IF OBJECT_ID('core.Store', 'U') IS NULL 
Begin
    create table core.Store (
        StoreId int identity(1,1) not null,
        StoreCode nvarchar(10) not null,
        StoreName nvarchar (150) not null,
        RegionId int not null,
        City nvarchar(100) not null,
        OpenedDate date null,
        AreaM2 int null,
        IsActive bit not null constraint DF_Store_IsActive default 1,
        CreatedAt DATETIME2(0) not null constraint DF_Store_CreatedAt DEFAULT SYSDATETIME(),

        CONSTRAINT PK_Store PRIMARY KEY CLUSTERED (StoreId),
        CONSTRAINT UQ_Store_Code UNIQUE (StoreCode),
        CONSTRAINT FK_Store_Region FOREIGN KEY (RegionId) REFERENCES core.Region(RegionId),
        CONSTRAINT CK_Store_OpenedDate CHECK (OpenedDate <= CAST(SYSDATETIME() AS DATE)),
        CONSTRAINT CK_Store_AreaM2 CHECK (AreaM2 > 0)
    )
End

IF OBJECT_ID ('core.Employee', 'U') is null 
Begin
    create table core.Employee (
        EmployeeId int identity(1,1) not null, 
        EmpCode nvarchar(10) not null,
        FullName nvarchar(150) not null,
        StoreId int not null,
        Position nvarchar(50) not null, 
        Salary decimal(12,2) not null,
        HiredDate date not null, 
        ManagerId int null,
        IsActive bit not null constraint DF_Employee_IsActive DEFAULT 1,

        CONSTRAINT PK_Employee_EmployeeId PRIMARY KEY CLUSTERED (EmployeeId),
        CONSTRAINT UQ_Employee_EmpCode UNIQUE (EmpCode),
        CONSTRAINT FK_Employee_StoreId FOREIGN KEY (StoreId) REFERENCES core.Store(StoreId),
        CONSTRAINT FK_Employee_Manager FOREIGN KEY (ManagerId) REFERENCES core.Employee(EmployeeId),
        CONSTRAINT CK_Employee_Salary CHECK (Salary >= 0),
        CONSTRAINT CK_Employee_Position CHECK (Position IN ('Kassir', 'Menejer', 'Direktor', 'Sotuvchi'))
    )
End

IF OBJECT_ID('core.Category','U') is null 
Begin
    create table core.Category (
        CategoryId int identity(1,1) not null,
        CategoryCode nvarchar(20) not null,
        CategoryName nvarchar(150) not null,
        ParentCategoryId int null,
        Level tinyint not null,

        constraint PK_Category_CategoryId primary key clustered (CategoryId),
        constraint UQ_Category_CategoryCode UNIQUE (CategoryCode),
        constraint FK_Category_ParentCategoryId foreign key (ParentCategoryId) references core.Category(CategoryId),
        constraint CK_Category_Level check (level between 1 and 3)
    );
End 

IF OBJECT_ID('core.Supplier','U') is null
Begin
    create table core.Supplier (
        SupplierId int identity(1,1) not null,
        Inn nvarchar(9) not null,
        SupplierName nvarchar(150) not null,
        Country nvarchar(50) null,
        ContractDate date not null,

        constraint PK_Supplier_SupplierId primary key clustered (SupplierId),
        constraint UQ_Supplier_Inn unique (Inn),
        constraint CK_Supplier_Inn check(len(Inn)=9),
        constraint CK_Supplier_ContractDate check(ContractDate <= cast(sysdatetime() as date))
    );
End

IF OBJECT_ID('core.Product','U') is null 
BEGIN
    create table core.Product (
        ProductId int identity(1,1) not null,
        Sku nvarchar(15) not null,
        ProductName nvarchar(200) not null,
        CategoryId int not null,
        SupplierId int not null,
        Unit nvarchar(10) not null,
        Barcode nvarchar(13) null, 
        IsActive bit not null constraint DF_Product_IsActive default 1,

        CONSTRAINT PK_Product PRIMARY KEY CLUSTERED (ProductId),
        constraint UQ_Product_Sku unique(Sku),
        constraint FK_Product_CategoryId Foreign key (CategoryId) references core.Category(CategoryId),
        constraint FK_Product_SupplierId Foreign key (SupplierId) references core.Supplier(SupplierId),
        constraint CK_Product_Unit Check (Unit in ('dona','kg','litr','quti'))
    )
End 

IF OBJECT_ID('core.ProductPrice','U') is NULL
Begin
    CREATE TABLE core.ProductPrice (
        ProductPriceId INT IDENTITY(1,1) NOT NULL,
        ProductId INT NOT NULL,
        ValidFrom DATE NOT NULL,
        ValidTo DATE NULL,
        Price DECIMAL(12,2) NOT NULL,

        CONSTRAINT PK_ProductPrice PRIMARY KEY CLUSTERED (ProductPriceId),
        CONSTRAINT FK_ProductPrice_Product FOREIGN KEY (ProductId) REFERENCES core.Product(ProductId),
        CONSTRAINT UQ_ProductPrice_Product_ValidFrom UNIQUE (ProductId, ValidFrom),
        CONSTRAINT CK_ProductPrice_Price CHECK (Price > 0)
    );
End

IF OBJECT_ID('core.SalesHeader','U') is null 
Begin 
    CREATE TABLE core.SalesHeader (
        SalesHeaderId INT IDENTITY(1,1) NOT NULL,
        ReceiptNo NVARCHAR(15) NOT NULL,
        StoreId INT NOT NULL,
        EmployeeId INT NOT NULL,
        SaleDateTime DATETIME2(0) NOT NULL,
        PaymentType NVARCHAR(10) NOT NULL,
        LoadId NVARCHAR(50) NOT NULL,

        CONSTRAINT PK_SalesHeader PRIMARY KEY CLUSTERED (SalesHeaderId),
        CONSTRAINT FK_SalesHeader_Store FOREIGN KEY (StoreId) REFERENCES core.Store(StoreId),
        CONSTRAINT FK_SalesHeader_Employee FOREIGN KEY (EmployeeId) REFERENCES core.Employee(EmployeeId),
        CONSTRAINT UQ_SalesHeader_ReceiptNo_StoreId UNIQUE (ReceiptNo, StoreId),
        CONSTRAINT CK_SalesHeader_SaleDateTime CHECK (SaleDateTime <= SYSDATETIME()),
        CONSTRAINT CK_SalesHeader_PaymentType CHECK (PaymentType IN ('CASH', 'CARD', 'TRANSFER'))
    );
End

IF OBJECT_ID('core.SalesDetail','U') is null
Begin
    CREATE TABLE core.SalesDetail (
        SalesDetailId INT IDENTITY(1,1) NOT NULL,
        SalesHeaderId INT NOT NULL,
        ProductId INT NOT NULL,
        Qty INT NOT NULL,
        UnitPrice DECIMAL(12,2) NOT NULL,
        DiscountPct DECIMAL(5,2) NOT NULL CONSTRAINT DF_SalesDetail_DiscountPct DEFAULT 0,
        LineAmount AS CAST(Qty * UnitPrice * (1 - DiscountPct / 100.0) AS DECIMAL(14,2)) PERSISTED,

        CONSTRAINT PK_SalesDetail PRIMARY KEY CLUSTERED (SalesDetailId),
        CONSTRAINT FK_SalesDetail_SalesHeader FOREIGN KEY (SalesHeaderId) REFERENCES core.SalesHeader(SalesHeaderId),
        CONSTRAINT FK_SalesDetail_Product FOREIGN KEY (ProductId) REFERENCES core.Product(ProductId),
        CONSTRAINT CK_SalesDetail_Qty CHECK (Qty > 0),
        CONSTRAINT CK_SalesDetail_UnitPrice CHECK (UnitPrice > 0),
        CONSTRAINT CK_SalesDetail_DiscountPct CHECK (DiscountPct BETWEEN 0 AND 100)
    );
END

IF OBJECT_ID('core.Returns','U') is null
Begin
    CREATE TABLE core.Returns (
        ReturnId INT IDENTITY(1,1) NOT NULL,
        ReturnCode NVARCHAR(15) NOT NULL,
        SalesHeaderId INT NOT NULL,
        ProductId INT NOT NULL,
        Qty INT NOT NULL,
        Reason NVARCHAR(200) NULL,
        ReturnDate DATE NOT NULL,

        CONSTRAINT PK_Returns PRIMARY KEY CLUSTERED (ReturnId),
        CONSTRAINT UQ_Returns_ReturnCode UNIQUE (ReturnCode),
        CONSTRAINT FK_Returns_SalesHeader FOREIGN KEY (SalesHeaderId) REFERENCES core.SalesHeader(SalesHeaderId),
        CONSTRAINT FK_Returns_Product FOREIGN KEY (ProductId) REFERENCES core.Product(ProductId),
        CONSTRAINT CK_Returns_Qty CHECK (Qty > 0)
    );
End

IF OBJECT_ID('core.ExchangeRate','U') is null 
Begin 
    CREATE TABLE core.ExchangeRate (
        RateDate DATE NOT NULL,
        CurrencyCode CHAR(3) NOT NULL,
        Rate DECIMAL(12,4) NOT NULL,

        CONSTRAINT PK_ExchangeRate PRIMARY KEY CLUSTERED (RateDate, CurrencyCode),
        CONSTRAINT CK_ExchangeRate_CurrencyCode CHECK (CurrencyCode IN ('USD', 'EUR', 'RUB')),
        CONSTRAINT CK_ExchangeRate_Rate CHECK (Rate > 0)
    );
End 