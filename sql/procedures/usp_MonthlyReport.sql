CREATE OR ALTER PROCEDURE mart.usp_MonthlyReport
    @Year       INT,
    @CategoryId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF @Year IS NULL OR @Year < 2000
        THROW 50003, 'Yaroqsiz yil kiritildi', 1;

    -- PIVOT: Kategoriya va Oylar kesimida sotuv summasi hisoboti
    SELECT 
        Category,
        ISNULL([1], 0) AS Jan, ISNULL([2], 0) AS Feb, ISNULL([3], 0) AS Mar,
        ISNULL([4], 0) AS Apr, ISNULL([5], 0) AS May, ISNULL([6], 0) AS Jun,
        ISNULL([7], 0) AS Jul, ISNULL([8], 0) AS Aug, ISNULL([9], 0) AS Sep,
        ISNULL([10], 0) AS Oct, ISNULL([11], 0) AS Nov, ISNULL([12], 0) AS Dec,
        (ISNULL([1], 0) + ISNULL([2], 0) + ISNULL([3], 0) + ISNULL([4], 0) + 
         ISNULL([5], 0) + ISNULL([6], 0) + ISNULL([7], 0) + ISNULL([8], 0) + 
         ISNULL([9], 0) + ISNULL([10], 0) + ISNULL([11], 0) + ISNULL([12], 0)) AS TotalYear
    FROM (
        SELECT 
            p.Category,
            MONTH(sh.SaleDateTime) AS SaleMonth,
            sd.LineAmount
        FROM core.SalesHeader sh
        JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
        JOIN core.Product p ON p.ProductId = sd.ProductId
        WHERE YEAR(sh.SaleDateTime) = @Year
          AND (@CategoryId IS NULL OR p.CategoryId = @CategoryId)
    ) AS SourceTable
    PIVOT (
        SUM(LineAmount)
        FOR SaleMonth IN ([1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [12])
    ) AS PivotTable
    ORDER BY Category;
END
GO