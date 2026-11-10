USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_promotion_performance
AS
WITH eligible_order_sales AS (
    SELECT
        o.order_id,
        o.promotion_id,
        o.order_timestamp,
        SUM(oi.quantity * oi.unit_price - oi.line_discount) AS sales_revenue,
        SUM(oi.quantity * oi.unit_cogs) AS cogs,
        SUM(oi.quantity) AS units_sold
    FROM dbo.orders o
    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id
    WHERE
        o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
        AND EXISTS (
            SELECT 1
            FROM dbo.payments p_eligible
            WHERE p_eligible.order_id = o.order_id
              AND p_eligible.payment_status = 'succeeded'
        )
    GROUP BY o.order_id, o.promotion_id, o.order_timestamp
),
order_refunds AS (
    SELECT order_id, SUM(refund_amount) AS refund_amount
    FROM dbo.refunds
    GROUP BY order_id
),
eligible_net_sales AS (
    SELECT
        eos.*,
        eos.sales_revenue - ISNULL(rf.refund_amount, 0) AS net_revenue
    FROM eligible_order_sales eos
    LEFT JOIN order_refunds rf ON eos.order_id = rf.order_id
),
promotion_actual AS (
    SELECT
        promotion_id,
        COUNT(order_id) AS promoted_orders,
        SUM(units_sold) AS promoted_units,
        SUM(sales_revenue) AS sales_revenue,
        SUM(sales_revenue - net_revenue) AS refund_amount,
        SUM(net_revenue) AS net_revenue,
        SUM(cogs) AS cogs
    FROM eligible_net_sales
    WHERE promotion_id IS NOT NULL
    GROUP BY promotion_id
),
promotion_period AS (
    SELECT
        p.promotion_id,
        DATEDIFF(DAY, p.promotion_start_date, p.promotion_end_date) + 1 AS promotion_days,
        SUM(CASE
            WHEN CAST(ens.order_timestamp AS date) BETWEEN p.promotion_start_date AND p.promotion_end_date
            THEN ens.net_revenue ELSE 0 END) AS period_net_revenue,
        SUM(CASE
            WHEN CAST(ens.order_timestamp AS date) >= DATEADD(DAY, -28, p.promotion_start_date)
             AND CAST(ens.order_timestamp AS date) < p.promotion_start_date
            THEN ens.net_revenue ELSE 0 END) AS pre_28d_net_revenue,
        CASE
            WHEN DATEADD(DAY, -28, p.promotion_start_date) >= (SELECT MIN(CAST(order_timestamp AS date)) FROM eligible_order_sales)
            THEN 1 ELSE 0 END AS has_complete_baseline
    FROM dbo.promotions p
    CROSS JOIN eligible_net_sales ens
    GROUP BY p.promotion_id, p.promotion_start_date, p.promotion_end_date
),
baseline AS (
    SELECT
        promotion_id,
        period_net_revenue,
        has_complete_baseline,
        CASE WHEN has_complete_baseline = 1
            THEN (pre_28d_net_revenue / 28.0) * promotion_days
            ELSE NULL END AS baseline_revenue
    FROM promotion_period
)
SELECT
    p.promotion_id,
    p.promotion_name,
    p.promotion_type,
    p.discount_type,
    p.discount_amount,
    p.promotion_start_date,
    p.promotion_end_date,
    ISNULL(pa.promoted_orders, 0) AS promoted_orders,
    ISNULL(pa.promoted_units, 0) AS promoted_units,
    ISNULL(pa.sales_revenue, 0) AS sales_revenue,
    ISNULL(pa.refund_amount, 0) AS refund_amount,
    ISNULL(pa.net_revenue, 0) AS net_revenue,
    ISNULL(pa.cogs, 0) AS cogs,
    ISNULL(pa.net_revenue, 0) - ISNULL(pa.cogs, 0) AS gross_profit,
    CAST(100.0 * (ISNULL(pa.net_revenue, 0) - ISNULL(pa.cogs, 0))
        / NULLIF(pa.net_revenue, 0) AS decimal(10, 2)) AS gross_margin_pct,
    b.baseline_revenue,
    b.period_net_revenue,
    CASE WHEN b.baseline_revenue IS NULL THEN NULL
         ELSE b.period_net_revenue - b.baseline_revenue END AS revenue_uplift,
    CAST(CASE WHEN b.baseline_revenue IS NULL THEN NULL
         ELSE 100.0 * (b.period_net_revenue - b.baseline_revenue)
              / NULLIF(b.baseline_revenue, 0) END AS decimal(10, 2)) AS revenue_uplift_pct
FROM dbo.promotions p
LEFT JOIN promotion_actual pa ON p.promotion_id = pa.promotion_id
LEFT JOIN baseline b ON p.promotion_id = b.promotion_id;
GO

SELECT TOP 20 *
FROM dbo.vw_promotion_performance
WHERE revenue_uplift_pct IS NOT NULL
ORDER BY revenue_uplift_pct DESC;
