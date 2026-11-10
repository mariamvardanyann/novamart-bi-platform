USE novamart;
GO

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
    SUM(
        CASE
            WHEN cc.is_retained_next_month = 1 THEN 1
            ELSE 0
        END
    ) AS retained_next_month,
    CAST(
        SUM(
            CASE
                WHEN cc.is_retained_next_month = 1 THEN 1
                ELSE 0
            END
        ) * 100.0
        / NULLIF(COUNT(*), 0)
        AS decimal(10,2)
    ) AS retention_rate_pct
FROM dbo.customer_cohorts cc
CROSS JOIN eligible_max_month em
-- N+1 retention is undefined for the final observable month.
WHERE cc.acquisition_month < em.max_observed_month
GROUP BY cc.acquisition_month;
GO

SELECT *
FROM dbo.vw_customer_retention
ORDER BY acquisition_month;
