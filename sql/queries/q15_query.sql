/* ------------------------------------------------------------------
   Fayl   : q15_store_quartiles.sql
   Savol  : Do'konlarni daromadi bo'yicha 4 guruhga bo'lish
   Texnika: NTILE()
   ------------------------------------------------------------------ */
WITH StoreSales AS (
    SELECT sh.StoreId, SUM(sd.LineAmount) AS Revenue
    FROM core.SalesHeader sh
    JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
    GROUP BY sh.StoreId
)
SELECT StoreId, Revenue, NTILE(4) OVER (ORDER BY Revenue DESC) AS Quartile FROM StoreSales;