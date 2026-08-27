
SELECT s.name AS SchemaName, COUNT(*) AS TableCount
FROM sys.tables t
JOIN sys.schemas s ON s.schema_id = t.schema_id
WHERE s.name IN ('stg', 'core', 'mart', 'audit')
GROUP BY s.name
ORDER BY s.name;
-- Kutilgan: core ~11, stg 9, audit 3, mart 1

SELECT s.name + '.' + t.name AS FullName
FROM sys.tables t
JOIN sys.schemas s ON s.schema_id = t.schema_id
WHERE s.name IN ('stg', 'audit')
ORDER BY FullName;
-- stg.RawSales, stg.RawStores, ..., audit.LoadLog bo'lishi SHART

SELECT @@SERVERNAME AS ServerName, DB_NAME() AS CurrentDb;
GO
