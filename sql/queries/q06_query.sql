WITH CategoryTree AS (
    SELECT CategoryId, CategoryName, ParentCategoryId, CAST(CategoryName AS VARCHAR(MAX)) AS CategoryPath
    FROM core.Category WHERE ParentCategoryId IS NULL
    UNION ALL
    SELECT c.CategoryId, c.CategoryName, c.ParentCategoryId, CAST(ct.CategoryPath + ' -> ' + c.CategoryName AS VARCHAR(MAX))
    FROM core.Category c
    JOIN CategoryTree ct ON c.ParentCategoryId = ct.CategoryId
)
SELECT * FROM CategoryTree;