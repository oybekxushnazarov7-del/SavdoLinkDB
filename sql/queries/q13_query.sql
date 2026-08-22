/* ------------------------------------------------------------------
   Fayl   : q13_price_impact.sql
   Savol  : Narx o'zgarishining sotuvga ta'siri
   Texnika: LAG() / Self-join
   ------------------------------------------------------------------ */
SELECT 
    ProductId,
    ChangeDate,
    OldUnitPrice,
    NewUnitPrice,
    LAG(NewUnitPrice) OVER (PARTITION BY ProductId ORDER BY ChangeDate) AS PreviousPrice
FROM audit.ProductHistory;