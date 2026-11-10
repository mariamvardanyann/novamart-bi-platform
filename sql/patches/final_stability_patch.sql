-- IMPORTANT: ONE-TIME MIGRATION FOR THE ORIGINAL NOVAMART V2 SNAPSHOT ONLY.
-- Contains hardcoded refund IDs/amounts from that specific synthetic dataset.
-- DO NOT run on a freshly generated database, or on a database already patched.
-- Reproducible new clean data should instead use the ETL validation pipeline.

USE novamart;
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;

PRINT 'NovaMart final stability patch';
PRINT 'This patch does NOT rebuild orders, products, marketing, logistics, or the Power BI schema.';

BEGIN TRANSACTION;

-- 1) Customer lifecycle: no clean order may predate customer signup.
;WITH first_clean_order AS (
    SELECT
        customer_id,
        CAST(MIN(order_timestamp) AS date) AS first_order_date
    FROM dbo.orders
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
UPDATE c
SET c.signup_date = f.first_order_date
FROM dbo.customers c
INNER JOIN first_clean_order f
    ON c.customer_id = f.customer_id
WHERE c.signup_date > f.first_order_date;

PRINT CONCAT('Customer signup dates corrected: ', @@ROWCOUNT);

-- 2) Finance/Cost taxonomy: relabel legacy overhead names without changing
--    dates, IDs, or amounts. These are operating expenses that explicitly
--    exclude shipping charges, payment fees, return costs and ad spend.
UPDATE dbo.finance_costs
SET cost_type =
    CASE cost_type
        WHEN 'warehouse_operations' THEN 'rent'
        WHEN 'technology' THEN 'software'
        WHEN 'customer_support' THEN 'payroll'
        WHEN 'payment_processing' THEN 'professional_services'
        WHEN 'administration' THEN 'other'
        WHEN 'logistics_overhead' THEN 'infrastructure'
        WHEN 'marketing_overhead' THEN 'professional_services'
        ELSE cost_type
    END;

UPDATE dbo.finance_costs
SET cost_category = 'operating';

-- 3) DQ-016 resolved correction: synchronize the 190 clean refund amounts
--    normalized by the final ETL so cumulative refunds never exceed the
--    successful payment amount. Order/revenue-generating facts are untouched.
;WITH corrected_refunds(refund_id, refund_amount) AS (
    SELECT *
    FROM (VALUES
        (28, CAST(125.08 AS decimal(12,2))),
        (95, CAST(123.34 AS decimal(12,2))),
        (152, CAST(264.10 AS decimal(12,2))),
        (158, CAST(90.32 AS decimal(12,2))),
        (160, CAST(130.15 AS decimal(12,2))),
        (168, CAST(39.23 AS decimal(12,2))),
        (182, CAST(158.06 AS decimal(12,2))),
        (211, CAST(158.81 AS decimal(12,2))),
        (232, CAST(70.09 AS decimal(12,2))),
        (249, CAST(127.52 AS decimal(12,2))),
        (294, CAST(246.53 AS decimal(12,2))),
        (341, CAST(189.70 AS decimal(12,2))),
        (355, CAST(228.89 AS decimal(12,2))),
        (403, CAST(190.65 AS decimal(12,2))),
        (467, CAST(144.67 AS decimal(12,2))),
        (481, CAST(30.97 AS decimal(12,2))),
        (502, CAST(210.48 AS decimal(12,2))),
        (523, CAST(1332.95 AS decimal(12,2))),
        (528, CAST(64.00 AS decimal(12,2))),
        (536, CAST(959.43 AS decimal(12,2))),
        (567, CAST(319.52 AS decimal(12,2))),
        (599, CAST(82.39 AS decimal(12,2))),
        (602, CAST(491.97 AS decimal(12,2))),
        (649, CAST(28.07 AS decimal(12,2))),
        (689, CAST(88.31 AS decimal(12,2))),
        (709, CAST(756.43 AS decimal(12,2))),
        (721, CAST(103.79 AS decimal(12,2))),
        (723, CAST(244.25 AS decimal(12,2))),
        (738, CAST(34.96 AS decimal(12,2))),
        (746, CAST(217.01 AS decimal(12,2))),
        (754, CAST(59.12 AS decimal(12,2))),
        (759, CAST(149.48 AS decimal(12,2))),
        (874, CAST(59.92 AS decimal(12,2))),
        (891, CAST(80.13 AS decimal(12,2))),
        (936, CAST(228.16 AS decimal(12,2))),
        (965, CAST(135.17 AS decimal(12,2))),
        (985, CAST(160.56 AS decimal(12,2))),
        (1023, CAST(31.93 AS decimal(12,2))),
        (1054, CAST(134.12 AS decimal(12,2))),
        (1063, CAST(62.61 AS decimal(12,2))),
        (1093, CAST(35.93 AS decimal(12,2))),
        (1129, CAST(70.08 AS decimal(12,2))),
        (1133, CAST(36.91 AS decimal(12,2))),
        (1215, CAST(24.62 AS decimal(12,2))),
        (1262, CAST(100.45 AS decimal(12,2))),
        (1263, CAST(75.65 AS decimal(12,2))),
        (1302, CAST(149.48 AS decimal(12,2))),
        (1330, CAST(86.62 AS decimal(12,2))),
        (1331, CAST(161.41 AS decimal(12,2))),
        (1336, CAST(206.94 AS decimal(12,2))),
        (1351, CAST(18.56 AS decimal(12,2))),
        (1355, CAST(40.04 AS decimal(12,2))),
        (1360, CAST(205.10 AS decimal(12,2))),
        (1383, CAST(434.72 AS decimal(12,2))),
        (1395, CAST(103.80 AS decimal(12,2))),
        (1444, CAST(144.13 AS decimal(12,2))),
        (1520, CAST(101.94 AS decimal(12,2))),
        (1561, CAST(75.65 AS decimal(12,2))),
        (1576, CAST(80.26 AS decimal(12,2))),
        (1591, CAST(23.60 AS decimal(12,2))),
        (1597, CAST(722.99 AS decimal(12,2))),
        (1623, CAST(61.06 AS decimal(12,2))),
        (1645, CAST(284.59 AS decimal(12,2))),
        (1667, CAST(2194.03 AS decimal(12,2))),
        (1673, CAST(80.27 AS decimal(12,2))),
        (1683, CAST(55.94 AS decimal(12,2))),
        (1693, CAST(132.02 AS decimal(12,2))),
        (1751, CAST(101.48 AS decimal(12,2))),
        (1755, CAST(133.72 AS decimal(12,2))),
        (1785, CAST(71.51 AS decimal(12,2))),
        (1789, CAST(28.96 AS decimal(12,2))),
        (1829, CAST(429.10 AS decimal(12,2))),
        (1844, CAST(194.39 AS decimal(12,2))),
        (1863, CAST(27.76 AS decimal(12,2))),
        (1878, CAST(195.37 AS decimal(12,2))),
        (1898, CAST(152.30 AS decimal(12,2))),
        (1913, CAST(10.24 AS decimal(12,2))),
        (1920, CAST(149.65 AS decimal(12,2))),
        (1925, CAST(21.32 AS decimal(12,2))),
        (1934, CAST(80.99 AS decimal(12,2))),
        (1946, CAST(660.94 AS decimal(12,2))),
        (1948, CAST(175.02 AS decimal(12,2))),
        (2006, CAST(142.57 AS decimal(12,2))),
        (2032, CAST(113.20 AS decimal(12,2))),
        (2062, CAST(158.05 AS decimal(12,2))),
        (2063, CAST(80.91 AS decimal(12,2))),
        (2065, CAST(41.75 AS decimal(12,2))),
        (2093, CAST(129.31 AS decimal(12,2))),
        (2124, CAST(673.10 AS decimal(12,2))),
        (2149, CAST(129.09 AS decimal(12,2))),
        (2196, CAST(431.45 AS decimal(12,2))),
        (2247, CAST(63.21 AS decimal(12,2))),
        (2249, CAST(284.85 AS decimal(12,2))),
        (2250, CAST(864.88 AS decimal(12,2))),
        (2252, CAST(393.81 AS decimal(12,2))),
        (2283, CAST(21.36 AS decimal(12,2))),
        (2288, CAST(87.32 AS decimal(12,2))),
        (2308, CAST(199.02 AS decimal(12,2))),
        (2334, CAST(81.79 AS decimal(12,2))),
        (2359, CAST(123.99 AS decimal(12,2))),
        (2426, CAST(36.43 AS decimal(12,2))),
        (2433, CAST(356.03 AS decimal(12,2))),
        (2468, CAST(181.62 AS decimal(12,2))),
        (2564, CAST(124.00 AS decimal(12,2))),
        (2604, CAST(266.74 AS decimal(12,2))),
        (2605, CAST(103.81 AS decimal(12,2))),
        (2624, CAST(80.12 AS decimal(12,2))),
        (2644, CAST(134.12 AS decimal(12,2))),
        (2648, CAST(63.85 AS decimal(12,2))),
        (2668, CAST(279.00 AS decimal(12,2))),
        (2690, CAST(59.93 AS decimal(12,2))),
        (2697, CAST(54.56 AS decimal(12,2))),
        (2698, CAST(129.02 AS decimal(12,2))),
        (2703, CAST(792.72 AS decimal(12,2))),
        (2718, CAST(80.99 AS decimal(12,2))),
        (2720, CAST(864.50 AS decimal(12,2))),
        (2741, CAST(58.07 AS decimal(12,2))),
        (2761, CAST(137.26 AS decimal(12,2))),
        (2762, CAST(210.48 AS decimal(12,2))),
        (2772, CAST(284.85 AS decimal(12,2))),
        (2788, CAST(161.40 AS decimal(12,2))),
        (2790, CAST(197.29 AS decimal(12,2))),
        (2798, CAST(9.55 AS decimal(12,2))),
        (2807, CAST(45.61 AS decimal(12,2))),
        (2813, CAST(9.42 AS decimal(12,2))),
        (2829, CAST(388.53 AS decimal(12,2))),
        (2853, CAST(160.56 AS decimal(12,2))),
        (2937, CAST(2133.59 AS decimal(12,2))),
        (2955, CAST(147.68 AS decimal(12,2))),
        (2958, CAST(236.19 AS decimal(12,2))),
        (2962, CAST(82.30 AS decimal(12,2))),
        (2963, CAST(11.21 AS decimal(12,2))),
        (2978, CAST(48.81 AS decimal(12,2))),
        (3011, CAST(68.81 AS decimal(12,2))),
        (3037, CAST(110.91 AS decimal(12,2))),
        (3062, CAST(78.59 AS decimal(12,2))),
        (3064, CAST(396.53 AS decimal(12,2))),
        (3083, CAST(92.47 AS decimal(12,2))),
        (3091, CAST(236.19 AS decimal(12,2))),
        (3094, CAST(33.07 AS decimal(12,2))),
        (3154, CAST(142.57 AS decimal(12,2))),
        (3160, CAST(66.43 AS decimal(12,2))),
        (3164, CAST(183.22 AS decimal(12,2))),
        (3165, CAST(82.15 AS decimal(12,2))),
        (3189, CAST(129.09 AS decimal(12,2))),
        (3202, CAST(230.51 AS decimal(12,2))),
        (3211, CAST(254.99 AS decimal(12,2))),
        (3216, CAST(39.19 AS decimal(12,2))),
        (3271, CAST(155.58 AS decimal(12,2))),
        (3283, CAST(189.22 AS decimal(12,2))),
        (3356, CAST(132.01 AS decimal(12,2))),
        (3358, CAST(800.61 AS decimal(12,2))),
        (3373, CAST(179.64 AS decimal(12,2))),
        (3405, CAST(155.58 AS decimal(12,2))),
        (3432, CAST(618.21 AS decimal(12,2))),
        (3437, CAST(412.68 AS decimal(12,2))),
        (3450, CAST(20.86 AS decimal(12,2))),
        (3464, CAST(756.42 AS decimal(12,2))),
        (3493, CAST(52.91 AS decimal(12,2))),
        (3538, CAST(74.14 AS decimal(12,2))),
        (3594, CAST(17.93 AS decimal(12,2))),
        (3613, CAST(461.31 AS decimal(12,2))),
        (3614, CAST(69.82 AS decimal(12,2))),
        (3617, CAST(54.15 AS decimal(12,2))),
        (3626, CAST(76.26 AS decimal(12,2))),
        (3653, CAST(30.73 AS decimal(12,2))),
        (3667, CAST(126.65 AS decimal(12,2))),
        (3697, CAST(66.44 AS decimal(12,2))),
        (3769, CAST(55.36 AS decimal(12,2))),
        (3874, CAST(284.59 AS decimal(12,2))),
        (3882, CAST(41.74 AS decimal(12,2))),
        (3899, CAST(18.56 AS decimal(12,2))),
        (3906, CAST(144.67 AS decimal(12,2))),
        (3954, CAST(255.95 AS decimal(12,2))),
        (3968, CAST(37.45 AS decimal(12,2))),
        (3972, CAST(41.62 AS decimal(12,2))),
        (3974, CAST(126.64 AS decimal(12,2))),
        (3975, CAST(223.54 AS decimal(12,2))),
        (4002, CAST(37.90 AS decimal(12,2))),
        (4044, CAST(101.54 AS decimal(12,2))),
        (4066, CAST(334.88 AS decimal(12,2))),
        (4091, CAST(144.25 AS decimal(12,2))),
        (4131, CAST(82.30 AS decimal(12,2))),
        (4180, CAST(44.64 AS decimal(12,2))),
        (4185, CAST(253.33 AS decimal(12,2))),
        (4212, CAST(361.72 AS decimal(12,2))),
        (4214, CAST(46.77 AS decimal(12,2))),
        (4221, CAST(77.09 AS decimal(12,2))),
        (4223, CAST(144.98 AS decimal(12,2))),
        (4246, CAST(379.48 AS decimal(12,2)))
    ) v(refund_id, refund_amount)
)
UPDATE r
SET r.refund_amount = c.refund_amount
FROM dbo.refunds r
INNER JOIN corrected_refunds c
    ON r.refund_id = c.refund_id;

PRINT CONCAT('Refund rows normalized: ', @@ROWCOUNT);

-- 4) Derived cohort table: N+1 retention is undefined for the final observable
--    month, so remove that immature cohort rather than storing it as 0%.
;WITH max_eligible_month AS (
    SELECT
        MAX(DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1))
            AS max_observed_month
    FROM dbo.orders o
    WHERE o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
      AND EXISTS (
          SELECT 1
          FROM dbo.payments p
          WHERE p.order_id = o.order_id
            AND p.payment_status = 'succeeded'
      )
)
DELETE cc
FROM dbo.customer_cohorts cc
CROSS JOIN max_eligible_month m
WHERE cc.acquisition_month >= m.max_observed_month;

PRINT CONCAT('Immature cohort rows removed: ', @@ROWCOUNT);

-- Guard checks before commit.
IF EXISTS (
    SELECT 1
    FROM dbo.orders o
    INNER JOIN dbo.customers c
        ON o.customer_id = c.customer_id
    WHERE CAST(o.order_timestamp AS date) < c.signup_date
)
BEGIN
    ROLLBACK TRANSACTION;
    THROW 51001, 'Lifecycle validation failed: order before signup remains.', 1;
END;

IF EXISTS (
    SELECT 1
    FROM dbo.refunds r
    INNER JOIN dbo.payments p
        ON r.payment_id = p.payment_id
    GROUP BY r.payment_id, p.payment_amount
    HAVING SUM(r.refund_amount) > p.payment_amount + 0.01
)
BEGIN
    ROLLBACK TRANSACTION;
    THROW 51002, 'Refund validation failed: cumulative refunds exceed payment amount.', 1;
END;

IF EXISTS (
    SELECT 1
    FROM dbo.finance_costs
    WHERE cost_type NOT IN (
        'payroll',
        'software',
        'rent',
        'infrastructure',
        'professional_services',
        'other'
    )
       OR cost_category <> 'operating'
)
BEGIN
    ROLLBACK TRANSACTION;
    THROW 51003, 'Finance taxonomy validation failed.', 1;
END;

COMMIT TRANSACTION;
GO

-- Keep the same Power BI-facing schema; only correct final-cohort eligibility.
CREATE OR ALTER VIEW dbo.vw_customer_retention
AS
WITH eligible_max_month AS (
    SELECT
        MAX(
            DATEFROMPARTS(
                YEAR(o.order_timestamp),
                MONTH(o.order_timestamp),
                1
            )
        ) AS max_observed_month
    FROM dbo.orders o
    WHERE o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
      AND EXISTS (
          SELECT 1
          FROM dbo.payments p
          WHERE p.order_id = o.order_id
            AND p.payment_status = 'succeeded'
      )
)
SELECT
    cc.acquisition_month,
    COUNT(*) AS acquired_customers,
    SUM(CASE WHEN cc.is_retained_next_month = 1 THEN 1 ELSE 0 END)
        AS retained_next_month,
    CAST(
        SUM(CASE WHEN cc.is_retained_next_month = 1 THEN 1 ELSE 0 END)
        * 100.0 / NULLIF(COUNT(*), 0)
        AS decimal(10,2)
    ) AS retention_rate_pct
FROM dbo.customer_cohorts cc
CROSS JOIN eligible_max_month em
WHERE cc.acquisition_month < em.max_observed_month
GROUP BY cc.acquisition_month;
GO

PRINT '--- Final patch validation ---';

SELECT
    SUM(CASE WHEN CAST(o.order_timestamp AS date) < c.signup_date THEN 1 ELSE 0 END)
        AS orders_before_signup
FROM dbo.orders o
INNER JOIN dbo.customers c
    ON o.customer_id = c.customer_id;

SELECT
    COUNT(*) AS over_refunded_payments
FROM (
    SELECT r.payment_id
    FROM dbo.refunds r
    INNER JOIN dbo.payments p
        ON r.payment_id = p.payment_id
    GROUP BY r.payment_id, p.payment_amount
    HAVING SUM(r.refund_amount) > p.payment_amount + 0.01
) x;

SELECT
    MIN(acquisition_month) AS first_cohort,
    MAX(acquisition_month) AS last_observable_cohort,
    SUM(acquired_customers) AS cohort_customers
FROM dbo.vw_customer_retention;

SELECT
    CAST(SUM(sales_revenue) AS decimal(18,2)) AS sales_revenue,
    CAST(SUM(refund_amount) AS decimal(18,2)) AS refunds,
    CAST(SUM(net_revenue) AS decimal(18,2)) AS net_revenue,
    CAST(SUM(gross_profit) AS decimal(18,2)) AS gross_profit,
    CAST(SUM(contribution_profit) AS decimal(18,2)) AS contribution_profit,
    CAST(SUM(net_profit) AS decimal(18,2)) AS net_profit
FROM dbo.vw_profitability;
GO
