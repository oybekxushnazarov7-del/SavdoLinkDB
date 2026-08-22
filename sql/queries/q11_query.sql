/* ------------------------------------------------------------------
   Fayl   : q11_by_weekday.sql
   Savol  : Hafta kunlari bo'yicha savdo
   Texnika: DATENAME, DATEPART
   ------------------------------------------------------------------ */
SELECT 
    DATENAME(WEEKDAY, sh.SaleDateTime) AS DayName,
    DATEPART(WEEKDAY, sh.SaleDateTime) AS DayNum,
    SUM(sd.LineAmount) AS TotalSales
FROM core.SalesHeader sh
JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
GROUP BY DATENAME(WEEKDAY, sh.SaleDateTime), DATEPART(WEEKDAY, sh.SaleDateTime)
ORDER BY DayNum;