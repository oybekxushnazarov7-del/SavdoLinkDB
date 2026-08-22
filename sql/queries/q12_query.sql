/* ------------------------------------------------------------------
   Fayl   : q12_sales_in_usd.sql
   Savol  : Savdoni USD ga o'tkazish
   Texnika: JOIN + CONVERT + ROUND
   ------------------------------------------------------------------ */
SELECT 
    sh.SalesHeaderId,
    sh.SaleDateTime,
    SUM(sd.LineAmount) AS AmountUZS,
    ROUND(SUM(sd.LineAmount) / 12800.0, 2) AS AmountUSD
FROM core.SalesHeader sh
JOIN core.SalesDetail sd ON sh.SalesHeaderId = sd.SalesHeaderId
GROUP BY sh.SalesHeaderId, sh.SaleDateTime;