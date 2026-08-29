-- stg.RawSales: StoreCode/Sku/CashierId (EmpCode) — surrogat ID emas.
-- core.SalesHeader: EmployeeId, PaymentType; LineAmount — computed (INSERT qilinmaydi).
CREATE OR ALTER PROCEDURE core.usp_LoadSales
    @LoadId        NVARCHAR(50),
    @HeadersLoaded INT = 0 OUTPUT,
    @DetailsLoaded INT = 0 OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @LoadId IS NULL OR LTRIM(RTRIM(@LoadId)) = ''
        THROW 50001, 'LoadId ko''rsatilmagan', 1;

    DECLARE @StgRows INT = (SELECT COUNT(*) FROM stg.RawSales WHERE LoadId = @LoadId);

    IF @StgRows = 0
        THROW 50010, 'Bu LoadId uchun stg.RawSales da qator yo''q. LoadId to''g''rimi?', 1;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- B-07: yetim havolalarni sanash va jurnalga yozish
        DECLARE @Orphans INT;

        SELECT @Orphans = COUNT(*)
        FROM stg.RawSales rs
        LEFT JOIN core.Store    st ON st.StoreCode = LTRIM(RTRIM(rs.StoreCode))
        LEFT JOIN core.Employee e  ON e.EmpCode    = LTRIM(RTRIM(rs.CashierId))
        LEFT JOIN core.Product  p  ON p.Sku        = LTRIM(RTRIM(rs.Sku))
        WHERE rs.LoadId = @LoadId
          AND NULLIF(LTRIM(RTRIM(rs.ReceiptNo)), '') IS NOT NULL
          AND (st.StoreId IS NULL OR e.EmployeeId IS NULL OR p.ProductId IS NULL);

        IF @Orphans > 0
            INSERT INTO audit.ErrorLog (LoadId, ErrorNumber, ErrorMessage, ErrorProcedure)
            VALUES (
                @LoadId, 0,
                CONCAT(N'Yetim havolali qatorlar core ga yuklanmadi: ', @Orphans),
                N'core.usp_LoadSales'
            );

        SELECT
            LTRIM(RTRIM(rs.ReceiptNo)) AS ReceiptNo,
            st.StoreId,
            e.EmployeeId,
            COALESCE(
                TRY_CONVERT(DATETIME2(0), rs.SaleDateTime, 120),
                TRY_CONVERT(DATETIME2(0), rs.SaleDateTime, 104)
            ) AS SaleDateTime,
            p.ProductId,
            TRY_CONVERT(INT, rs.Qty) AS Qty,
            TRY_CONVERT(DECIMAL(12,2),
                REPLACE(COALESCE(NULLIF(rs.UnitPrice, ''), rs.UnitPriceResolved), ',', '.')
            ) AS UnitPrice,
            ISNULL(TRY_CONVERT(DECIMAL(5,2), REPLACE(rs.DiscountPct, ',', '.')), 0) AS DiscountPct,
            UPPER(LTRIM(RTRIM(rs.PaymentType))) AS PaymentType
        INTO #TempSales
        FROM stg.RawSales rs
        JOIN core.Store st ON st.StoreCode = LTRIM(RTRIM(rs.StoreCode))
        JOIN core.Employee e ON e.EmpCode = LTRIM(RTRIM(rs.CashierId))
        JOIN core.Product p ON p.Sku = LTRIM(RTRIM(rs.Sku))
        WHERE rs.LoadId = @LoadId
          AND NULLIF(LTRIM(RTRIM(rs.ReceiptNo)), '') IS NOT NULL;

        MERGE core.SalesHeader AS tgt
        USING (
            SELECT DISTINCT ReceiptNo, StoreId, EmployeeId, SaleDateTime, PaymentType
            FROM #TempSales
            WHERE SaleDateTime IS NOT NULL
              AND PaymentType IN ('CASH', 'CARD', 'TRANSFER')
        ) AS src
            ON tgt.ReceiptNo = src.ReceiptNo AND tgt.StoreId = src.StoreId
        WHEN NOT MATCHED THEN
            INSERT (ReceiptNo, StoreId, EmployeeId, SaleDateTime, PaymentType, LoadId)
            VALUES (src.ReceiptNo, src.StoreId, src.EmployeeId, src.SaleDateTime, src.PaymentType, @LoadId);

        SET @HeadersLoaded = @@ROWCOUNT;

        -- B-08: faqat o'zgarganda yangilash + manbada takrorlanishni bartaraf etish
        MERGE core.SalesDetail AS tgt
        USING (
            SELECT SalesHeaderId, ProductId, Qty, UnitPrice, DiscountPct
            FROM (
                SELECT
                    sh.SalesHeaderId,
                    ts.ProductId,
                    ts.Qty,
                    ts.UnitPrice,
                    ts.DiscountPct,
                    ROW_NUMBER() OVER (
                        PARTITION BY sh.SalesHeaderId, ts.ProductId
                        ORDER BY ts.UnitPrice DESC
                    ) AS rn
                FROM #TempSales ts
                JOIN core.SalesHeader sh
                    ON sh.ReceiptNo = ts.ReceiptNo AND sh.StoreId = ts.StoreId
                WHERE ts.Qty IS NOT NULL AND ts.UnitPrice IS NOT NULL
            ) x
            WHERE rn = 1
        ) AS src
            ON tgt.SalesHeaderId = src.SalesHeaderId AND tgt.ProductId = src.ProductId
        WHEN MATCHED AND (
                tgt.Qty         <> src.Qty
             OR tgt.UnitPrice   <> src.UnitPrice
             OR tgt.DiscountPct <> src.DiscountPct
        ) THEN
            UPDATE SET
                tgt.Qty = src.Qty,
                tgt.UnitPrice = src.UnitPrice,
                tgt.DiscountPct = src.DiscountPct
        WHEN NOT MATCHED THEN
            INSERT (SalesHeaderId, ProductId, Qty, UnitPrice, DiscountPct)
            VALUES (src.SalesHeaderId, src.ProductId, src.Qty, src.UnitPrice, src.DiscountPct);

        SET @DetailsLoaded = @@ROWCOUNT;

        DROP TABLE #TempSales;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        INSERT INTO audit.ErrorLog (LoadId, ErrorNumber, ErrorMessage, ErrorLine, ErrorProcedure)
        VALUES (@LoadId, ERROR_NUMBER(), ERROR_MESSAGE(), ERROR_LINE(), ERROR_PROCEDURE());
        THROW;
    END CATCH
END
GO
