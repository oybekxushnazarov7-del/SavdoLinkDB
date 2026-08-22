SELECT * 
FROM (
    SELECT 
        c.CategoryName,
        DATEPART(MONTH, sh.SaleDateTime) AS SaleMonth,
        sd.LineAmount
    FROM core.SalesDetail sd
    JOIN core.SalesHeader sh ON sh.SalesHeaderId = sd.SalesHeaderId
    JOIN core.Product p ON p.ProductId = sd.ProductId
    JOIN core.Category c ON c.CategoryId = p.CategoryId
) AS Src
PIVOT (
    SUM(LineAmount) 
    FOR SaleMonth IN ([1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [12])
) AS Pvt;