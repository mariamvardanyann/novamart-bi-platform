# Constraint Validation — Test Run Evidence

**Executed:** 2026-08-25, via SSMS against a live SQL Server instance
(SQLEXPRESS), using `constraint_validation_test.sql`.

## Result: 5/5 PASSED

```text
--- Reference data created (country_id=1, product_id=1, order_id=1) ---

TEST 1 (valid insert): PASSED - insert succeeded as expected.
TEST 2 (negative quantity): PASSED - correctly rejected: The INSERT statement
    conflicted with the CHECK constraint "chk_qty_positive". The conflict
    occurred in database "novamart", table "dbo.order_items", column 'quantity'.
TEST 3 (invalid product_id): PASSED - correctly rejected: The INSERT statement
    conflicted with the FOREIGN KEY constraint "FK_order_items_products". The
    conflict occurred in database "novamart", table "dbo.products", column
    'product_id'.
TEST 4 (invalid currency): PASSED - correctly rejected: The INSERT statement
    conflicted with the CHECK constraint "chk_order_currency". The conflict
    occurred in database "novamart", table "dbo.orders", column 'currency_code'.
TEST 5 (invalid promotion dates): PASSED - correctly rejected: The INSERT
    statement conflicted with the CHECK constraint "chk_promo_dates". The
    conflict occurred in database "novamart", table "dbo.promotions".

--- Rolling back: no test data is kept in the database ---
Completion time: 2026-08-25T01:41:25.9171661+04:00
```

## What this proves

Each rejection names the **exact constraint** the test targeted — not just
"an error occurred," but the correct DQ rule enforcing it:

| Test | DQ Rule | Constraint | Result |
|---|---|---|---|
| Valid insert | — | — | Succeeded (control case) |
| Negative quantity | DQ-002 | `chk_qty_positive` | Rejected |
| Nonexistent product_id | Referential integrity | `FK_order_items_products` | Rejected |
| Non-EUR currency | DQ-020 | `chk_order_currency` | Rejected |
| Promotion end before start | DQ-021 | `chk_promo_dates` | Rejected |

Test data was inserted inside a transaction and rolled back — the database
was left clean after the run, so this test is safe to re-run at any time
(e.g., after future schema changes) without polluting real data.
