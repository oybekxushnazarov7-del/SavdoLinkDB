-- S-08 + S-13: yagona mart refresh (refresh_mart.sql o'chirildi).
-- core.Sales yo'q — SalesHeader + SalesDetail; Qty (Quantity emas).
CREATE OR ALTER PROCEDURE mart.usp_RefreshDailyFacts
    @DateFrom DATE,
    @DateTo   DATE,
    @RowsRefreshed INT = 0 OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @DateFrom IS NULL OR @DateTo IS NULL
        THROW 50002, 'Sana oralig''i ko''rsatilmagan', 1;
    IF @DateFrom > @DateTo
        THROW 50003, 'DateFrom DateTo dan katta bo''lishi mumkin emas', 1;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Idempotentlik: faqat berilgan davr (TRUNCATE emas)
        DELETE FROM mart.FactDailySales
        WHERE SaleDate BETWEEN @DateFrom AND @DateTo;

        ;WITH SalesAgg AS (
            SELECT CAST(sh.SaleDateTime AS DATE) AS SaleDate,
                   sh.StoreId,
                   p.CategoryId,
                   COUNT(DISTINCT sh.SalesHeaderId) AS ReceiptCount,
                   SUM(sd.Qty)                     AS QtySold,
                   SUM(sd.Qty * sd.UnitPrice)      AS GrossAmount,
                   SUM(sd.LineAmount)              AS NetAmount
            FROM core.SalesHeader sh
            JOIN core.SalesDetail sd ON sd.SalesHeaderId = sh.SalesHeaderId
            JOIN core.Product     p  ON p.ProductId      = sd.ProductId
            WHERE CAST(sh.SaleDateTime AS DATE) BETWEEN @DateFrom AND @DateTo
            GROUP BY CAST(sh.SaleDateTime AS DATE), sh.StoreId, p.CategoryId
        ),
        ReturnAgg AS (
            SELECT CAST(sh.SaleDateTime AS DATE) AS SaleDate,
                   sh.StoreId,
                   p.CategoryId,
                   SUM(r.Qty * sd.UnitPrice) AS ReturnAmount
            FROM core.Returns r
            JOIN core.SalesHeader sh ON sh.SalesHeaderId = r.SalesHeaderId
            JOIN core.SalesDetail sd ON sd.SalesHeaderId = r.SalesHeaderId
                                    AND sd.ProductId     = r.ProductId
            JOIN core.Product     p  ON p.ProductId      = r.ProductId
            WHERE CAST(sh.SaleDateTime AS DATE) BETWEEN @DateFrom AND @DateTo
            GROUP BY CAST(sh.SaleDateTime AS DATE), sh.StoreId, p.CategoryId
        )
        INSERT INTO mart.FactDailySales
            (SaleDate, StoreId, CategoryId, StoreName, CategoryName,
             ReceiptCount, QtySold, GrossAmount, NetAmount, ReturnAmount)
        SELECT a.SaleDate, a.StoreId, a.CategoryId, st.StoreName, c.CategoryName,
               a.ReceiptCount, a.QtySold, a.GrossAmount, a.NetAmount,
               ISNULL(ra.ReturnAmount, 0)
        FROM SalesAgg a
        JOIN core.Store    st ON st.StoreId    = a.StoreId
        JOIN core.Category c  ON c.CategoryId  = a.CategoryId
        LEFT JOIN ReturnAgg ra ON ra.SaleDate  = a.SaleDate
                              AND ra.StoreId   = a.StoreId
                              AND ra.CategoryId = a.CategoryId;

        SET @RowsRefreshed = @@ROWCOUNT;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        INSERT INTO audit.ErrorLog (ErrorNumber, ErrorMessage, ErrorLine, ErrorProcedure)
        VALUES (ERROR_NUMBER(), ERROR_MESSAGE(), ERROR_LINE(), ERROR_PROCEDURE());
        THROW;
    END CATCH
END
GO
