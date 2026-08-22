CREATE OR ALTER FUNCTION core.fn_MaskPhone
(
    @Phone NVARCHAR(30)
)
RETURNS NVARCHAR(30)
AS
BEGIN
    IF @Phone IS NULL OR LEN(@Phone) < 9
        RETURN @Phone;

    -- Tel nomerni niqoblash formatiga keltirish (+998 90 *** ** 45)
    RETURN SUBSTRING(@Phone, 1, 7) + ' *** ** ' + RIGHT(@Phone, 2);
END;
GO