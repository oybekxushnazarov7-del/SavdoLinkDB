/* ------------------------------------------------------------------
   Fayl   : q10_incomplete_rows.sql
   Savol  : To'liq bo'lmagan yozuvlar ulushi
   Texnika: COALESCE, NULLIF, CASE
   ------------------------------------------------------------------ */
SELECT 
    COUNT(*) AS TotalRows,
    SUM(CASE WHEN BarCode IS NULL OR BarCode = '' THEN 1 ELSE 0 END) AS MissingBarCode,
    ROUND(
        CAST(SUM(CASE WHEN BarCode IS NULL OR BarCode = '' THEN 1 ELSE 0 END) AS FLOAT) 
        / NULLIF(COUNT(*), 0) * 100, 
        2
    ) AS MissingBarCodePct
FROM core.Product;