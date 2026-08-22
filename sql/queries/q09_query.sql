/* ------------------------------------------------------------------
   Fayl   : q09_top3_per_store.sql
   Savol  : Har bir do'kondagi top-3 mahsulot
   Texnika: ROW_NUMBER() OVER()
   ------------------------------------------------------------------ */
WITH RankedProducts AS (
    SELECT 
        s.StoreName,
        p.ProductName,
        SUM(sd.Qty) AS TotalQty,
        ROW_NUMBER() OVER (PARTITION BY s.StoreId ORDER BY SUM(sd.Qty) DESC) AS RankNo
    FROM core.SalesHeader sh
    JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
    JOIN core.Store s ON s.StoreId = sh.StoreId
    JOIN core.Product p ON p.ProductId = sd.ProductId
    GROUP BY s.StoreId, s.StoreName, p.ProductId, p.ProductName
)
SELECT StoreName, ProductName, TotalQty, RankNo FROM RankedProducts WHERE RankNo <= 3;