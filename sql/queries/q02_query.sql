SELECT 
    p.ProductId,
    p.ProductName,
    p.SKU
FROM core.Product p
LEFT JOIN core.SalesDetail sd ON sd.ProductId = p.ProductId
WHERE sd.SalesHeaderId IS NULL;