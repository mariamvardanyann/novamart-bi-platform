USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_category_performance
AS
WITH category_financials AS (
    SELECT
        pp.category_id,
        pp.category_name,
        SUM(pp.units_sold) AS units_sold,
        SUM(pp.sales_revenue) AS sales_revenue,
        SUM(pp.refund_amount) AS refund_amount,
        SUM(pp.net_revenue) AS net_revenue,
        SUM(pp.cogs) AS cogs,
        SUM(pp.gross_profit) AS gross_profit
    FROM dbo.vw_product_profitability pp
    GROUP BY
        pp.category_id,
        pp.category_name
),
category_orders AS (
    SELECT
        p.category_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM dbo.orders o
    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id
    INNER JOIN dbo.products p
        ON oi.product_id = p.product_id
    WHERE o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
        AND EXISTS (
            SELECT 1
            FROM dbo.payments p_eligible
            WHERE p_eligible.order_id = o.order_id
              AND p_eligible.payment_status = 'succeeded'
        )
    GROUP BY p.category_id
),
monthly_category AS (
    SELECT
        p.category_id,
        DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
            AS revenue_month,
        SUM(oi.quantity * oi.unit_price - oi.line_discount) AS sales_revenue
    FROM dbo.orders o
    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id
    INNER JOIN dbo.products p
        ON oi.product_id = p.product_id
    WHERE o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
        AND EXISTS (
            SELECT 1
            FROM dbo.payments p_eligible
            WHERE p_eligible.order_id = o.order_id
              AND p_eligible.payment_status = 'succeeded'
        )
    GROUP BY
        p.category_id,
        DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
),
category_growth_base AS (
    SELECT
        category_id,
        revenue_month,
        sales_revenue,
        LAG(sales_revenue) OVER (
            PARTITION BY category_id
            ORDER BY revenue_month
        ) AS previous_month_revenue
    FROM monthly_category
),
latest_category_growth AS (
    SELECT
        category_id,
        revenue_month,
        sales_revenue,
        previous_month_revenue,
        ROW_NUMBER() OVER (
            PARTITION BY category_id
            ORDER BY revenue_month DESC
        ) AS rn
    FROM category_growth_base
)
SELECT
    cf.category_id,
    cf.category_name,
    ISNULL(co.order_count, 0) AS order_count,
    cf.units_sold,
    cf.sales_revenue,
    cf.refund_amount,
    cf.net_revenue,
    cf.cogs,
    cf.gross_profit,
    CAST(
        100.0 * cf.gross_profit / NULLIF(cf.net_revenue, 0)
        AS decimal(10, 2)
    ) AS gross_margin_pct,
    lcg.revenue_month AS latest_month,
    CAST(
        100.0 * (lcg.sales_revenue - lcg.previous_month_revenue)
        / NULLIF(lcg.previous_month_revenue, 0)
        AS decimal(10, 2)
    ) AS latest_month_growth_pct
FROM category_financials cf
LEFT JOIN category_orders co
    ON cf.category_id = co.category_id
LEFT JOIN latest_category_growth lcg
    ON cf.category_id = lcg.category_id
    AND lcg.rn = 1;
GO

SELECT *
FROM dbo.vw_category_performance
ORDER BY net_revenue DESC;
