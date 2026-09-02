-- ============================================================================
-- NovaMart BI Platform — CLEAN Layer Schema (SQL Server / T-SQL)
-- Sprint 1 — Database
-- Related: docs/04_data_dictionary.md (grain register), docs/03_data_quality.md
-- Target: SQL Server 2019+ / Azure SQL, managed via SSMS
-- ============================================================================

IF DB_ID('novamart') IS NULL
BEGIN
    CREATE DATABASE novamart;
END
GO

USE novamart;
GO

-- ----------------------------------------------------------------------------
-- REFERENCE / DIMENSION TABLES
-- ----------------------------------------------------------------------------

CREATE TABLE countries (
    country_id      INT IDENTITY(1,1) PRIMARY KEY,
    country_code    NCHAR(2) NOT NULL UNIQUE,      -- ISO 3166-1 alpha-2
    country_name    NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE categories (
    category_id     INT IDENTITY(1,1) PRIMARY KEY,
    category_name   NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE products (
    product_id      INT IDENTITY(1,1) PRIMARY KEY,
    product_name    NVARCHAR(200) NOT NULL,
    category_id     INT NOT NULL,
    brand           NVARCHAR(100),
    active_flag     BIT NOT NULL DEFAULT 1,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
GO
CREATE INDEX idx_products_category ON products(category_id);
GO

CREATE TABLE customers (
    customer_id     INT IDENTITY(1,1) PRIMARY KEY,
    signup_date     DATE NOT NULL,
    country_id      INT NOT NULL,
    age_group       NVARCHAR(20),                  -- synthetic, safe demographic bucket
    gender          NVARCHAR(20),                  -- synthetic
    CONSTRAINT fk_customers_country FOREIGN KEY (country_id) REFERENCES countries(country_id)
);
GO
CREATE INDEX idx_customers_country ON customers(country_id);
GO

CREATE TABLE promotions (
    promotion_id            INT IDENTITY(1,1) PRIMARY KEY,
    promotion_name          NVARCHAR(150) NOT NULL,
    promotion_type          NVARCHAR(50) NOT NULL,      -- e.g. seasonal, flash, clearance
    discount_type           NVARCHAR(20) NOT NULL,      -- percentage | fixed_amount
    discount_amount         DECIMAL(10,2) NOT NULL,
    promotion_start_date    DATE NOT NULL,
    promotion_end_date      DATE NOT NULL,
    CONSTRAINT chk_promo_dates CHECK (promotion_start_date <= promotion_end_date),  -- DQ-021
    CONSTRAINT chk_promo_discount CHECK (discount_amount >= 0)                      -- DQ-021
);
GO

CREATE TABLE warehouses (
    warehouse_id    INT IDENTITY(1,1) PRIMARY KEY,
    warehouse_name  NVARCHAR(100) NOT NULL,
    country_id      INT NOT NULL,
    CONSTRAINT fk_warehouses_country FOREIGN KEY (country_id) REFERENCES countries(country_id)
);
GO

CREATE TABLE carriers (
    carrier_id      INT IDENTITY(1,1) PRIMARY KEY,
    carrier_name    NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE channels (
    channel_id      INT IDENTITY(1,1) PRIMARY KEY,
    channel_name    NVARCHAR(100) NOT NULL          -- e.g. Paid Search, Social, Email, Direct
);
GO

CREATE TABLE campaigns (
    campaign_id     INT IDENTITY(1,1) PRIMARY KEY,
    channel_id      INT NOT NULL,
    campaign_name   NVARCHAR(150) NOT NULL,
    CONSTRAINT fk_campaigns_channel FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);
GO
CREATE INDEX idx_campaigns_channel ON campaigns(channel_id);
GO

-- ----------------------------------------------------------------------------
-- SALES DOMAIN
-- ----------------------------------------------------------------------------

CREATE TABLE orders (
    order_id            INT IDENTITY(1,1) PRIMARY KEY,
    customer_id         INT NULL,                       -- nullable only for controlled guest orders (DQ-006)
    order_timestamp     DATETIME2 NOT NULL,
    status              VARCHAR(20) NOT NULL,           -- placed|paid|fulfilled|shipped|delivered|cancelled
    cancellation_reason NVARCHAR(200) NULL,             -- required when status = 'cancelled' (enforced in ETL)
    country_id          INT NOT NULL,
    promotion_id        INT NULL,
    currency_code       NCHAR(3) NOT NULL DEFAULT 'EUR', -- DQ-020: EUR-only in Phase 1
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_orders_country FOREIGN KEY (country_id) REFERENCES countries(country_id),
    CONSTRAINT fk_orders_promotion FOREIGN KEY (promotion_id) REFERENCES promotions(promotion_id),
    CONSTRAINT chk_order_status CHECK (status IN ('placed','paid','fulfilled','shipped','delivered','cancelled')),
    CONSTRAINT chk_order_currency CHECK (currency_code = 'EUR')
);
GO
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_timestamp ON orders(order_timestamp);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_country ON orders(country_id);
GO

CREATE TABLE order_items (
    order_line_id       INT IDENTITY(1,1) PRIMARY KEY,
    order_id            INT NOT NULL,
    product_id          INT NOT NULL,
    quantity            INT NOT NULL,
    original_unit_price DECIMAL(10,2) NOT NULL,
    unit_price          DECIMAL(10,2) NOT NULL,
    line_discount       DECIMAL(10,2) NOT NULL DEFAULT 0,
    unit_cogs           DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT chk_qty_positive CHECK (quantity > 0),                          -- DQ-002
    CONSTRAINT chk_prices_nonneg CHECK (original_unit_price >= 0 AND unit_price >= 0 AND unit_cogs >= 0), -- DQ-003
    CONSTRAINT chk_discount_nonneg CHECK (line_discount >= 0)                  -- DQ-008
);
GO
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_items_product ON order_items(product_id);
GO

-- ----------------------------------------------------------------------------
-- PAYMENT DOMAIN
-- ----------------------------------------------------------------------------

CREATE TABLE payments (
    payment_id          INT IDENTITY(1,1) PRIMARY KEY,
    order_id            INT NOT NULL,
    payment_timestamp   DATETIME2 NOT NULL,
    payment_status      NVARCHAR(30) NOT NULL,       -- succeeded | failed | pending
    payment_method      NVARCHAR(50) NOT NULL,
    payment_amount      DECIMAL(10,2) NOT NULL,
    payment_fee         DECIMAL(10,2) NOT NULL DEFAULT 0,
    currency_code       NCHAR(3) NOT NULL DEFAULT 'EUR',
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT chk_payment_amounts CHECK (payment_amount >= 0 AND payment_fee >= 0),  -- DQ-012
    CONSTRAINT chk_payment_currency CHECK (currency_code = 'EUR')
);
GO
CREATE INDEX idx_payments_order ON payments(order_id);
GO

-- (returns table is defined further below; refunds.return_id FK is added after it exists)

CREATE TABLE refunds (
    refund_id           INT IDENTITY(1,1) PRIMARY KEY,
    order_id            INT NOT NULL,
    payment_id          INT NULL,
    return_id           INT NULL,                    -- FK added after `returns` table is created
    refund_timestamp    DATETIME2 NOT NULL,
    refund_amount       DECIMAL(10,2) NOT NULL,
    refund_reason       NVARCHAR(200),
    currency_code       NCHAR(3) NOT NULL DEFAULT 'EUR',
    CONSTRAINT fk_refunds_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_refunds_payment FOREIGN KEY (payment_id) REFERENCES payments(payment_id),
    CONSTRAINT chk_refund_amount CHECK (refund_amount >= 0)  -- DQ-012, DQ-016
);
GO
CREATE INDEX idx_refunds_order ON refunds(order_id);
GO

-- ----------------------------------------------------------------------------
-- LOGISTICS DOMAIN
-- ----------------------------------------------------------------------------

CREATE TABLE shipments (
    shipment_id                INT IDENTITY(1,1) PRIMARY KEY,
    order_id                   INT NOT NULL,
    warehouse_id               INT NOT NULL,
    carrier_id                 INT NOT NULL,
    fulfillment_timestamp      DATETIME2 NULL,
    shipping_timestamp         DATETIME2 NULL,
    expected_delivery_date     DATE NULL,               -- immutable once set (DQ-018)
    actual_delivery_timestamp  DATETIME2 NULL,
    shipping_cost              DECIMAL(10,2) NOT NULL DEFAULT 0,
    shipment_status            NVARCHAR(30) NOT NULL,   -- pending | shipped | delivered | returned
    CONSTRAINT fk_shipments_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_shipments_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    CONSTRAINT fk_shipments_carrier FOREIGN KEY (carrier_id) REFERENCES carriers(carrier_id),
    CONSTRAINT chk_shipping_cost CHECK (shipping_cost >= 0)  -- DQ-012
);
GO
CREATE INDEX idx_shipments_order ON shipments(order_id);
CREATE INDEX idx_shipments_carrier ON shipments(carrier_id);
CREATE INDEX idx_shipments_warehouse ON shipments(warehouse_id);
GO

CREATE TABLE returns (
    return_id           INT IDENTITY(1,1) PRIMARY KEY,
    order_id             INT NOT NULL,
    order_line_id        INT NOT NULL,
    shipment_id          INT NULL,
    return_timestamp     DATETIME2 NOT NULL,
    return_reason        NVARCHAR(200),
    returned_quantity    INT NOT NULL,
    defect_flag          BIT NOT NULL DEFAULT 0,
    return_cost          DECIMAL(10,2) NOT NULL DEFAULT 0,
    return_status        NVARCHAR(30) NOT NULL,       -- requested | received | refunded
    CONSTRAINT fk_returns_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_returns_line FOREIGN KEY (order_line_id) REFERENCES order_items(order_line_id),
    CONSTRAINT fk_returns_shipment FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id),
    CONSTRAINT chk_return_qty CHECK (returned_quantity > 0),
    CONSTRAINT chk_return_cost CHECK (return_cost >= 0)  -- DQ-012
);
GO
CREATE INDEX idx_returns_order ON returns(order_id);
CREATE INDEX idx_returns_line ON returns(order_line_id);
GO

-- Now that `returns` exists, add the deferred FK from refunds.return_id
ALTER TABLE refunds
    ADD CONSTRAINT fk_refunds_return FOREIGN KEY (return_id) REFERENCES returns(return_id);
GO

-- ----------------------------------------------------------------------------
-- MARKETING & WEB ANALYTICS DOMAIN (Phase 1.2 scope extension — see 01_brd.md §3)
-- ----------------------------------------------------------------------------

CREATE TABLE marketing_events (
    event_id            BIGINT IDENTITY(1,1) PRIMARY KEY,
    session_id          VARCHAR(64) NOT NULL,            -- required for funnel eligibility (DQ-013)
    customer_id         INT NULL,
    campaign_id         INT NULL,
    channel_id          INT NOT NULL,
    event_timestamp     DATETIME2 NOT NULL,
    event_type          VARCHAR(20) NOT NULL,            -- DQ-014 controlled vocabulary
    country_id          INT NOT NULL,
    device              NVARCHAR(30),
    CONSTRAINT fk_events_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_events_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    CONSTRAINT fk_events_channel FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
    CONSTRAINT fk_events_country FOREIGN KEY (country_id) REFERENCES countries(country_id),
    CONSTRAINT chk_event_type CHECK (event_type IN
        ('impression','click','session_start','product_view','add_to_cart','checkout_started','purchase'))
);
GO
CREATE INDEX idx_events_session ON marketing_events(session_id);
CREATE INDEX idx_events_timestamp ON marketing_events(event_timestamp);
CREATE INDEX idx_events_type ON marketing_events(event_type);
CREATE INDEX idx_events_customer ON marketing_events(customer_id);
GO

CREATE TABLE marketing_spend (
    spend_id            INT IDENTITY(1,1) PRIMARY KEY,
    spend_date          DATE NOT NULL,
    campaign_id         INT NOT NULL,
    channel_id          INT NOT NULL,
    country_id          INT NOT NULL,
    ad_spend            DECIMAL(10,2) NOT NULL,
    impressions         BIGINT NOT NULL DEFAULT 0,
    clicks              BIGINT NOT NULL DEFAULT 0,
    currency_code       NCHAR(3) NOT NULL DEFAULT 'EUR',
    CONSTRAINT fk_spend_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    CONSTRAINT fk_spend_channel FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
    CONSTRAINT fk_spend_country FOREIGN KEY (country_id) REFERENCES countries(country_id),
    CONSTRAINT chk_spend_nonneg CHECK (ad_spend >= 0 AND impressions >= 0 AND clicks >= 0),  -- DQ-011
    CONSTRAINT chk_clicks_le_impr CHECK (clicks <= impressions)                              -- DQ-011
);
GO
CREATE INDEX idx_spend_date ON marketing_spend(spend_date);
CREATE INDEX idx_spend_campaign ON marketing_spend(campaign_id);
GO

-- ----------------------------------------------------------------------------
-- FINANCE / COST DOMAIN
-- ----------------------------------------------------------------------------

CREATE TABLE finance_costs (
    cost_id             INT IDENTITY(1,1) PRIMARY KEY,
    cost_date           DATE NOT NULL,
    cost_type           NVARCHAR(50) NOT NULL,        -- controlled vocabulary (DQ-019)
    cost_category       NVARCHAR(50) NOT NULL,        -- e.g. operating, other
    amount              DECIMAL(12,2) NOT NULL,
    currency_code       NCHAR(3) NOT NULL DEFAULT 'EUR',
    country_id          INT NULL,
    description         NVARCHAR(255),
    CONSTRAINT fk_costs_country FOREIGN KEY (country_id) REFERENCES countries(country_id),
    CONSTRAINT chk_cost_amount CHECK (amount >= 0)   -- DQ-012
);
GO
CREATE INDEX idx_costs_date ON finance_costs(cost_date);
CREATE INDEX idx_costs_type ON finance_costs(cost_type);
GO

-- ----------------------------------------------------------------------------
-- DERIVED STRUCTURES (populated by ETL in Sprint 2 — see 04_data_dictionary.md §3.1)
-- These are NOT raw source tables. Created here so the ETL layer has a
-- physical target to write into.
-- ----------------------------------------------------------------------------

CREATE TABLE marketing_attribution (
    attribution_id       BIGINT IDENTITY(1,1) PRIMARY KEY,
    order_id             INT NOT NULL,
    customer_id          INT NOT NULL,
    campaign_id          INT NULL,
    channel_id           INT NULL,
    touchpoint_timestamp DATETIME2 NULL,
    attribution_model    VARCHAR(30) NOT NULL DEFAULT 'last_touch_30d',  -- see 02_kpi_dictionary.md
    CONSTRAINT fk_attr_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_attr_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_attr_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    CONSTRAINT fk_attr_channel FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
    CONSTRAINT uq_attribution_order UNIQUE (order_id)   -- one attribution result per order
);
GO

CREATE TABLE customer_cohorts (
    customer_id             INT PRIMARY KEY,
    acquisition_month       DATE NOT NULL,           -- first day of first eligible completed-purchase month
    is_retained_next_month  BIT NULL,                -- recomputed each ETL run
    CONSTRAINT fk_cohorts_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
GO

CREATE TABLE dim_date (
    date_key        DATE PRIMARY KEY,
    year            SMALLINT NOT NULL,
    quarter         TINYINT NOT NULL,
    month           TINYINT NOT NULL,
    month_name      NVARCHAR(15) NOT NULL,
    week_of_year    TINYINT NOT NULL,
    day_of_week     TINYINT NOT NULL,
    is_weekend      BIT NOT NULL
);
GO

-- ----------------------------------------------------------------------------
-- QUARANTINE (single generic table for all 25 DQ rules across all sources)
-- See docs/03_data_quality.md "Quarantine Record Minimum Fields"
-- ----------------------------------------------------------------------------

CREATE TABLE quarantine (
    quarantine_id           BIGINT IDENTITY(1,1) PRIMARY KEY,
    source_system           NVARCHAR(50) NOT NULL,     -- e.g. 'Sales', 'Marketing'
    source_file_or_batch    NVARCHAR(150) NOT NULL,    -- e.g. 'orders_2026-08.csv'
    source_record_key       NVARCHAR(100) NULL,        -- original row's natural key if available
    dq_rule_id              VARCHAR(10) NOT NULL,      -- e.g. 'DQ-002'
    failure_reason          NVARCHAR(255) NOT NULL,
    raw_payload             NVARCHAR(MAX) NOT NULL,    -- the full offending row, preserved as JSON text
    detected_at             DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    resolution_status       VARCHAR(10) NOT NULL DEFAULT 'open',  -- open | resolved | wont_fix
    resolved_at             DATETIME2 NULL,
    CONSTRAINT chk_quarantine_status CHECK (resolution_status IN ('open','resolved','wont_fix')),
    CONSTRAINT chk_quarantine_json CHECK (ISJSON(raw_payload) = 1)
);
GO
CREATE INDEX idx_quarantine_rule ON quarantine(dq_rule_id);
CREATE INDEX idx_quarantine_source ON quarantine(source_system);
CREATE INDEX idx_quarantine_status ON quarantine(resolution_status);
GO
