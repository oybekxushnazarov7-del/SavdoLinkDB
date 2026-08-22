/* ------------------------------------------------------------------
   Fayl   : q14_employee_hierarchy.sql
   Savol  : Kategoriya/Tuzilma ierarxiyasi
   Texnika: Rekursiv CTE
   ------------------------------------------------------------------ */
WITH CategoryTree AS (
    SELECT 
        CategoryId, 
        CategoryName, 
        ParentCategoryId, 
        1 AS Level
    FROM core.Category 
    WHERE ParentCategoryId IS NULL

    UNION ALL

    SELECT 
        c.CategoryId, 
        c.CategoryName, 
        c.ParentCategoryId, 
        ct.Level + 1
    FROM core.Category c
    JOIN CategoryTree ct ON c.ParentCategoryId = ct.CategoryId
)
SELECT * FROM CategoryTree;