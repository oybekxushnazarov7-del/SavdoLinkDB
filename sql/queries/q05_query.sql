WITH DailySales AS (
    SELECT 
        CAST(sh.SaleDateTime AS DATE) AS SaleDate,
        SUM(sd.LineAmount) AS DailyTotal
    FROM core.SalesHeader sh
    JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
    GROUP BY CAST(sh.SaleDateTime AS DATE)
)
SELECT 
    SaleDate,
    DailyTotal,
    SUM(DailyTotal) OVER (ORDER BY SaleDate) AS RunningTotal
FROM DailySales;