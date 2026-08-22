CREATE OR ALTER FUNCTION core.fn_NetPrice 
(
    @UnitPrice Decimal(12,2),
    @DiscountPct Decimal(5,2)
)
Returns Decimal(12,2)
AS
Begin 
    Return round(isnull(@UnitPrice, 0)*(1-isnull(@DiscountPct,0)/100.0),2);
END;
GO