# Data Dictionary
# P-12 / R-06: butun loyihada bitta nomlash lug'ati

| Manba CSV | Python (transform'dan keyin) | stg ustuni | core ustuni |
|---|---|---|---|
| `receipt_no` | `receipt_no` | `ReceiptNo` | `ReceiptNo` |
| `store_code` | `store_code` | `StoreCode` | (→ `StoreId`) |
| `cashier_id` | `cashier_id` | `CashierId` | (→ `EmployeeId` via EmpCode) |
| `sale_datetime` | `sale_datetime` | `SaleDateTime` | `SaleDateTime` |
| `sku` | `sku` | `Sku` | (→ `ProductId`) |
| `qty` | `qty` | `Qty` | `Qty` |
| `unit_price` | `unit_price` | `UnitPrice` | `UnitPrice` |
| `discount_pct` | `discount_pct` | `DiscountPct` | `DiscountPct` |
| `payment_type` | `payment_type` | `PaymentType` | `PaymentType` |
