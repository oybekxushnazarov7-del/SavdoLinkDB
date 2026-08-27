
-- Views
IF OBJECT_ID('mart.vw_CashierPerformance', 'V') IS NOT NULL DROP VIEW mart.vw_CashierPerformance;
IF OBJECT_ID('mart.vw_DailySalesSummary', 'V') IS NOT NULL DROP VIEW mart.vw_DailySalesSummary;
IF OBJECT_ID('mart.vw_ProductPerformance', 'V') IS NOT NULL DROP VIEW mart.vw_ProductPerformance;
IF OBJECT_ID('mart.vw_StoreOverview', 'V') IS NOT NULL DROP VIEW mart.vw_StoreOverview;
IF OBJECT_ID('mart.vw_AuditLogs', 'V') IS NOT NULL DROP VIEW mart.vw_AuditLogs;
GO

-- Mart
IF OBJECT_ID('mart.FactDailySales', 'U') IS NOT NULL DROP TABLE mart.FactDailySales;

-- Core — bola jadvallar
IF OBJECT_ID('core.Returns', 'U') IS NOT NULL DROP TABLE core.Returns;
IF OBJECT_ID('core.SalesDetail', 'U') IS NOT NULL DROP TABLE core.SalesDetail;
IF OBJECT_ID('core.SalesHeader', 'U') IS NOT NULL DROP TABLE core.SalesHeader;
IF OBJECT_ID('core.ProductPrice', 'U') IS NOT NULL DROP TABLE core.ProductPrice;
IF OBJECT_ID('core.Product', 'U') IS NOT NULL DROP TABLE core.Product;
IF OBJECT_ID('core.Employee', 'U') IS NOT NULL DROP TABLE core.Employee;
IF OBJECT_ID('core.Store', 'U') IS NOT NULL DROP TABLE core.Store;

-- Core — ota jadvallar
IF OBJECT_ID('core.Category', 'U') IS NOT NULL DROP TABLE core.Category;
IF OBJECT_ID('core.Supplier', 'U') IS NOT NULL DROP TABLE core.Supplier;
IF OBJECT_ID('core.Region', 'U') IS NOT NULL DROP TABLE core.Region;
IF OBJECT_ID('core.ExchangeRate', 'U') IS NOT NULL DROP TABLE core.ExchangeRate;

-- Staging (FK yo'q)
IF OBJECT_ID('stg.RawSales', 'U') IS NOT NULL DROP TABLE stg.RawSales;
IF OBJECT_ID('stg.RawProducts', 'U') IS NOT NULL DROP TABLE stg.RawProducts;
IF OBJECT_ID('stg.RawPrices', 'U') IS NOT NULL DROP TABLE stg.RawPrices;
IF OBJECT_ID('stg.RawStores', 'U') IS NOT NULL DROP TABLE stg.RawStores;
IF OBJECT_ID('stg.RawEmployees', 'U') IS NOT NULL DROP TABLE stg.RawEmployees;
IF OBJECT_ID('stg.RawCategories', 'U') IS NOT NULL DROP TABLE stg.RawCategories;
IF OBJECT_ID('stg.RawSuppliers', 'U') IS NOT NULL DROP TABLE stg.RawSuppliers;
IF OBJECT_ID('stg.RawReturns', 'U') IS NOT NULL DROP TABLE stg.RawReturns;
IF OBJECT_ID('stg.RawRates', 'U') IS NOT NULL DROP TABLE stg.RawRates;

-- Audit
IF OBJECT_ID('audit.LoadLog', 'U') IS NOT NULL DROP TABLE audit.LoadLog;
IF OBJECT_ID('audit.ErrorLog', 'U') IS NOT NULL DROP TABLE audit.ErrorLog;
IF OBJECT_ID('audit.ProductHistory', 'U') IS NOT NULL DROP TABLE audit.ProductHistory;
GO
