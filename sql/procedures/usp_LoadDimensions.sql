-- S-10: StoreId emas StoreCode; core.Cashier/RawCashiers yo'q — Employee.
-- Spravochniklar tartibi: Region → Store → Employee → Category → Supplier.
CREATE OR ALTER PROCEDURE core.usp_LoadDimensions
    @LoadId        NVARCHAR(50),
    @RowsInserted INT = 0 OUTPUT,
    @RowsUpdated  INT = 0 OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @LoadId IS NULL OR LTRIM(RTRIM(@LoadId)) = ''
        THROW 50001, 'LoadId ko''rsatilmagan', 1;

    DECLARE @StgRows INT = (
        SELECT COUNT(*) FROM stg.RawStores WHERE LoadId = @LoadId
    ) + (
        SELECT COUNT(*) FROM stg.RawEmployees WHERE LoadId = @LoadId
    );

    IF @StgRows = 0
        THROW 50010, 'Bu LoadId uchun stg.RawStores/RawEmployees da qator yo''q. LoadId to''g''rimi?', 1;

    DECLARE @Changes TABLE (ChangeAction NVARCHAR(10));

    BEGIN TRY
        BEGIN TRANSACTION;

        -- 1. Region
        ;WITH src_region AS (
            SELECT DISTINCT LTRIM(RTRIM(Region)) AS RegionName
            FROM stg.RawStores
            WHERE LoadId = @LoadId AND NULLIF(LTRIM(RTRIM(Region)), '') IS NOT NULL
        )
        MERGE core.Region AS tgt
        USING src_region AS src
            ON tgt.RegionName = src.RegionName
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (RegionName) VALUES (src.RegionName)
        OUTPUT $action INTO @Changes;

        -- 2. Store (S-10)
        ;WITH src_store AS (
            SELECT DISTINCT
                LTRIM(RTRIM(StoreCode))              AS StoreCode,
                LTRIM(RTRIM(StoreName))              AS StoreName,
                LTRIM(RTRIM(City))                   AS City,
                LTRIM(RTRIM(Region))                 AS Region,
                TRY_CONVERT(DATE, OpenedDate)        AS OpenedDate,
                TRY_CONVERT(INT, AreaM2)             AS AreaM2
            FROM stg.RawStores
            WHERE LoadId = @LoadId
              AND NULLIF(LTRIM(RTRIM(StoreCode)), '') IS NOT NULL
        )
        MERGE core.Store AS tgt
        USING (
            SELECT s.*, r.RegionId
            FROM src_store s
            JOIN core.Region r ON r.RegionName = s.Region
        ) AS src
            ON tgt.StoreCode = src.StoreCode
        WHEN MATCHED AND (
            tgt.StoreName <> src.StoreName OR
            tgt.City <> src.City OR
            ISNULL(tgt.AreaM2, -1) <> ISNULL(src.AreaM2, -1)
        ) THEN
            UPDATE SET
                tgt.StoreName = src.StoreName,
                tgt.City = src.City,
                tgt.AreaM2 = src.AreaM2,
                tgt.OpenedDate = src.OpenedDate,
                tgt.RegionId = src.RegionId
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (StoreCode, StoreName, RegionId, City, OpenedDate, AreaM2)
            VALUES (src.StoreCode, src.StoreName, src.RegionId, src.City, src.OpenedDate, src.AreaM2)
        OUTPUT $action INTO @Changes;

        -- 3. Employee (RawCashiers / core.Cashier o'rniga)
        ;WITH src_emp AS (
            SELECT DISTINCT
                LTRIM(RTRIM(EmpCode))     AS EmpCode,
                LTRIM(RTRIM(FullName))    AS FullName,
                LTRIM(RTRIM(StoreCode))   AS StoreCode,
                LTRIM(RTRIM(Position))    AS Position,
                TRY_CONVERT(DECIMAL(12,2), REPLACE(Salary, ',', '.')) AS Salary,
                TRY_CONVERT(DATE, HiredDate) AS HiredDate,
                LTRIM(RTRIM(ManagerCode)) AS ManagerCode,
                TRY_CONVERT(BIT, IsActive) AS IsActive
            FROM stg.RawEmployees
            WHERE LoadId = @LoadId
              AND NULLIF(LTRIM(RTRIM(EmpCode)), '') IS NOT NULL
        )
        MERGE core.Employee AS tgt
        USING (
            SELECT e.EmpCode, e.FullName, st.StoreId, e.Position,
                   ISNULL(e.Salary, 0) AS Salary,
                   ISNULL(e.HiredDate, CAST(SYSDATETIME() AS DATE)) AS HiredDate,
                   ISNULL(e.IsActive, 1) AS IsActive
            FROM src_emp e
            JOIN core.Store st ON st.StoreCode = e.StoreCode
        ) AS src
            ON tgt.EmpCode = src.EmpCode
        WHEN MATCHED AND (
            tgt.FullName <> src.FullName OR
            tgt.StoreId <> src.StoreId OR
            tgt.Position <> src.Position
        ) THEN
            UPDATE SET
                tgt.FullName = src.FullName,
                tgt.StoreId = src.StoreId,
                tgt.Position = src.Position,
                tgt.Salary = src.Salary,
                tgt.IsActive = src.IsActive
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (EmpCode, FullName, StoreId, Position, Salary, HiredDate, IsActive)
            VALUES (src.EmpCode, src.FullName, src.StoreId, src.Position,
                    src.Salary, src.HiredDate, src.IsActive)
        OUTPUT $action INTO @Changes;

        -- 4. Category
        ;WITH src_cat AS (
            SELECT DISTINCT
                LTRIM(RTRIM(CategoryCode)) AS CategoryCode,
                LTRIM(RTRIM(CategoryName)) AS CategoryName,
                LTRIM(RTRIM(ParentCategoryCode)) AS ParentCategoryCode,
                TRY_CONVERT(TINYINT, Level) AS Level
            FROM stg.RawCategories
            WHERE LoadId = @LoadId
              AND NULLIF(LTRIM(RTRIM(CategoryCode)), '') IS NOT NULL
        )
        MERGE core.Category AS tgt
        USING src_cat AS src
            ON tgt.CategoryCode = src.CategoryCode
        WHEN MATCHED AND tgt.CategoryName <> src.CategoryName THEN
            UPDATE SET tgt.CategoryName = src.CategoryName
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (CategoryCode, CategoryName, Level)
            VALUES (src.CategoryCode, src.CategoryName, ISNULL(src.Level, 1))
        OUTPUT $action INTO @Changes;

        -- Parent FK (ikkinchi o'tish)
        UPDATE c
        SET c.ParentCategoryId = p.CategoryId
        FROM core.Category c
        JOIN stg.RawCategories r ON r.CategoryCode = c.CategoryCode AND r.LoadId = @LoadId
        JOIN core.Category p ON p.CategoryCode = LTRIM(RTRIM(r.ParentCategoryCode))
        WHERE NULLIF(LTRIM(RTRIM(r.ParentCategoryCode)), '') IS NOT NULL;

        -- 5. Supplier
        ;WITH src_sup AS (
            SELECT DISTINCT
                LTRIM(RTRIM(Inn)) AS Inn,
                LTRIM(RTRIM(SupplierName)) AS SupplierName,
                LTRIM(RTRIM(Country)) AS Country,
                TRY_CONVERT(DATE, ContractDate) AS ContractDate
            FROM stg.RawSuppliers
            WHERE LoadId = @LoadId
              AND NULLIF(LTRIM(RTRIM(Inn)), '') IS NOT NULL
        )
        MERGE core.Supplier AS tgt
        USING src_sup AS src
            ON tgt.Inn = src.Inn
        WHEN MATCHED AND tgt.SupplierName <> src.SupplierName THEN
            UPDATE SET tgt.SupplierName = src.SupplierName,
                       tgt.Country = src.Country
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (Inn, SupplierName, Country, ContractDate)
            VALUES (src.Inn, src.SupplierName, src.Country,
                    ISNULL(src.ContractDate, CAST(SYSDATETIME() AS DATE)))
        OUTPUT $action INTO @Changes;

        SELECT @RowsInserted = COUNT(*) FROM @Changes WHERE ChangeAction = 'INSERT';
        SELECT @RowsUpdated  = COUNT(*) FROM @Changes WHERE ChangeAction = 'UPDATE';

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

