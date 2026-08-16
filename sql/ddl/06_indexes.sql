CREATE NONCLUSTERED INDEX IX_FactDailySales_SaleDate 
ON mart.FactDailySales (SaleDate);

CREATE NONCLUSTERED INDEX IX_FactDailySales_Store_Category 
ON mart.FactDailySales (StoreId, CategoryId);