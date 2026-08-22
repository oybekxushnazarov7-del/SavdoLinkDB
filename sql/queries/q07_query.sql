/* ------------------------------------------------------------------
   Fayl   : q07_movements.sql
   Savol  : Savdo va Qaytarishlar yagona oqimi
   Texnika: UNION ALL
   ------------------------------------------------------------------ */
SELECT 
    'SALE' AS MovementType,
    sh.SalesHeaderId AS RefId,
    sh.SaleDateTime AS MovementDate,
    SUM(sd.LineAmount) AS Amount
FROM core.SalesHeader sh
JOIN core.SalesDetail sd ON sh.SalesHeaderId = sd.SalesHeaderId
GROUP BY sh.SalesHeaderId, sh.SaleDateTime

UNION ALL

SELECT 
    'RETURN' AS MovementType,
    r.ReturnId AS RefId,
    r.ReturnDate AS MovementDate,
    SUM(rd.LineAmount) AS Amount
FROM core.Returns r
JOIN core.ReturnDetail rd ON r.ReturnId = rd.ReturnId
GROUP BY r.ReturnId, r.ReturnDate;