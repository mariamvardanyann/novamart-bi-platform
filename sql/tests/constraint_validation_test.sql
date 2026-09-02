-- ============================================================================
-- NovaMart — Constraint Validation Test
-- Purpose: prove the CHECK constraints and Foreign Keys in schema_sqlserver.sql
--          actually reject bad data, not just that the schema compiles.
-- Safe to re-run any time: wrapped in a transaction that is rolled back at
-- the end, so no test data is ever left behind in the database.
-- ============================================================================

USE novamart;
GO

SET NOCOUNT ON;
BEGIN TRANSACTION;

DECLARE @country_id  INT;
DECLARE @category_id INT;
DECLARE @product_id  INT;
DECLARE @customer_id INT;
DECLARE @order_id    INT;

-- ----------------------------------------------------------------------------
-- Reference data (IDs captured via SCOPE_IDENTITY, never hardcoded)
-- ----------------------------------------------------------------------------
INSERT INTO countries (country_code, country_name) VALUES ('ZZ', 'TestCountry');
SET @country_id = SCOPE_IDENTITY();

INSERT INTO categories (category_name) VALUES ('TestCategory');
SET @category_id = SCOPE_IDENTITY();

INSERT INTO products (product_name, category_id, brand) VALUES ('Test Product', @category_id, 'TestBrand');
SET @product_id = SCOPE_IDENTITY();

INSERT INTO customers (signup_date, country_id) VALUES ('2025-01-01', @country_id);
SET @customer_id = SCOPE_IDENTITY();

INSERT INTO orders (customer_id, order_timestamp, status, country_id)
VALUES (@customer_id, SYSDATETIME(), 'placed', @country_id);
SET @order_id = SCOPE_IDENTITY();

PRINT '--- Reference data created (country_id=' + CAST(@country_id AS VARCHAR)
    + ', product_id=' + CAST(@product_id AS VARCHAR)
    + ', order_id=' + CAST(@order_id AS VARCHAR) + ') ---';
PRINT '';

-- ----------------------------------------------------------------------------
-- TEST 1 — Valid insert. Expected: SUCCESS.
-- ----------------------------------------------------------------------------
BEGIN TRY
    INSERT INTO order_items (order_id, product_id, quantity, original_unit_price, unit_price, unit_cogs)
    VALUES (@order_id, @product_id, 2, 50.00, 45.00, 20.00);
    PRINT 'TEST 1 (valid insert): PASSED - insert succeeded as expected.';
END TRY
BEGIN CATCH
    PRINT 'TEST 1 (valid insert): FAILED - expected success but got error: ' + ERROR_MESSAGE();
END CATCH;

-- ----------------------------------------------------------------------------
-- TEST 2 — Negative quantity. Expected: REJECTED by chk_qty_positive (DQ-002).
-- ----------------------------------------------------------------------------
BEGIN TRY
    INSERT INTO order_items (order_id, product_id, quantity, original_unit_price, unit_price, unit_cogs)
    VALUES (@order_id, @product_id, -5, 10, 10, 5);
    PRINT 'TEST 2 (negative quantity): FAILED - insert succeeded but should have been rejected!';
END TRY
BEGIN CATCH
    PRINT 'TEST 2 (negative quantity): PASSED - correctly rejected: ' + ERROR_MESSAGE();
END CATCH;

-- ----------------------------------------------------------------------------
-- TEST 3 — Nonexistent product_id. Expected: REJECTED by Foreign Key.
-- ----------------------------------------------------------------------------
BEGIN TRY
    INSERT INTO order_items (order_id, product_id, quantity, original_unit_price, unit_price, unit_cogs)
    VALUES (@order_id, 999999, 1, 10, 10, 5);
    PRINT 'TEST 3 (invalid product_id): FAILED - insert succeeded but should have been rejected!';
END TRY
BEGIN CATCH
    PRINT 'TEST 3 (invalid product_id): PASSED - correctly rejected: ' + ERROR_MESSAGE();
END CATCH;

-- ----------------------------------------------------------------------------
-- TEST 4 — Non-EUR currency. Expected: REJECTED by chk_order_currency (DQ-020).
-- ----------------------------------------------------------------------------
BEGIN TRY
    INSERT INTO orders (customer_id, order_timestamp, status, country_id, currency_code)
    VALUES (@customer_id, SYSDATETIME(), 'placed', @country_id, 'USD');
    PRINT 'TEST 4 (invalid currency): FAILED - insert succeeded but should have been rejected!';
END TRY
BEGIN CATCH
    PRINT 'TEST 4 (invalid currency): PASSED - correctly rejected: ' + ERROR_MESSAGE();
END CATCH;

-- ----------------------------------------------------------------------------
-- TEST 5 — Promotion end date before start date. Expected: REJECTED by chk_promo_dates (DQ-021).
-- ----------------------------------------------------------------------------
BEGIN TRY
    INSERT INTO promotions (promotion_name, promotion_type, discount_type, discount_amount, promotion_start_date, promotion_end_date)
    VALUES ('Bad Promo', 'flash', 'percentage', 10, '2026-06-10', '2026-06-01');
    PRINT 'TEST 5 (invalid promotion dates): FAILED - insert succeeded but should have been rejected!';
END TRY
BEGIN CATCH
    PRINT 'TEST 5 (invalid promotion dates): PASSED - correctly rejected: ' + ERROR_MESSAGE();
END CATCH;

PRINT '';
PRINT '--- Rolling back: no test data is kept in the database ---';
ROLLBACK TRANSACTION;
GO
