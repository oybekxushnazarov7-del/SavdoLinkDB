/* ------------------------------------------------------------------
   Fayl   : q08_period_intersect.sql
   Savol  : Yanvar va Fevral oylarining ikkalasida ham sotilgan mahsulotlar
   Texnika: INTERSECT
   ------------------------------------------------------------------ */
SELECT ProductId FROM core.SalesDetail sd JOIN core.SalesHeader sh ON sh.SalesHeaderId = sd.SalesHeaderId WHERE MONTH(sh.SaleDateTime) = 1
INTERSECT
SELECT ProductId FROM core.SalesDetail sd JOIN core.SalesHeader sh ON sh.SalesHeaderId = sd.SalesHeaderId WHERE MONTH(sh.SaleDateTime) = 2;