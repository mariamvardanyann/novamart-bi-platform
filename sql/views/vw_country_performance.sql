USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_country_performance
AS

WITH order_sales AS (
    SELECT
        o.order_id,
        o.country_id,

        DATEFROMPARTS(
            YEAR(o.order_timestamp),
            MONTH(o.order_timestamp),
            1
        ) AS revenue_month,

        SUM(oi.quantity) AS units_sold,

        SUM(
            oi.quantity * oi.unit_price
            - oi.line_discount
        ) AS sales_revenue,

        SUM(
            oi.quantity * oi.unit_cogs
        ) AS cogs

    FROM dbo.orders o

    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'cancelled'

    GROUP BY
        o.order_id,
        o.country_id,
        DATEFROMPARTS(
            YEAR(o.order_timestamp),
            MONTH(o.order_timestamp),
            1
        )
),

order_refunds AS (
    SELECT
        order_id,
        SUM(refund_amount) AS refund_amount

    FROM dbo.refunds

    GROUP BY
        order_id
),

country_financials AS (
    SELECT
        os.country_id,

        COUNT(DISTINCT os.order_id)
            AS order_count,

        SUM(os.units_sold)
            AS units_sold,

        SUM(os.sales_revenue)
            AS sales_revenue,

        SUM(
            ISNULL(rf.refund_amount, 0)
        ) AS refund_amount,

        SUM(
            os.sales_revenue
            - ISNULL(rf.refund_amount, 0)
        ) AS net_revenue,

        SUM(os.cogs)
            AS cogs

    FROM order_sales os

    LEFT JOIN order_refunds rf
        ON os.order_id = rf.order_id

    GROUP BY
        os.country_id
),

monthly_country AS (
    SELECT
        os.country_id,
        os.revenue_month,

        SUM(
            os.sales_revenue
            - ISNULL(rf.refund_amount, 0)
        ) AS net_revenue

    FROM order_sales os

    LEFT JOIN order_refunds rf
        ON os.order_id = rf.order_id

    GROUP BY
        os.country_id,
        os.revenue_month
),

country_growth AS (
    SELECT
        country_id,
        revenue_month,
        net_revenue,

        LAG(net_revenue) OVER (
            PARTITION BY country_id
            ORDER BY revenue_month
        ) AS previous_month_net_revenue

    FROM monthly_country
),

latest_country_growth AS (
    SELECT
        country_id,
        revenue_month,
        net_revenue,
        previous_month_net_revenue,

        ROW_NUMBER() OVER (
            PARTITION BY country_id
            ORDER BY revenue_month DESC
        ) AS rn

    FROM country_growth
)

SELECT
    c.country_id,
    c.country_code,
    c.country_name,

    cf.order_count,
    cf.units_sold,

    CAST(
        cf.sales_revenue
        AS decimal(18, 2)
    ) AS sales_revenue,

    CAST(
        cf.refund_amount
        AS decimal(18, 2)
    ) AS refund_amount,

    CAST(
        cf.net_revenue
        AS decimal(18, 2)
    ) AS net_revenue,

    CAST(
        cf.cogs
        AS decimal(18, 2)
    ) AS cogs,

    CAST(
        cf.net_revenue - cf.cogs
        AS decimal(18, 2)
    ) AS gross_profit,

    CAST(
        100.0
        * (
            cf.net_revenue - cf.cogs
        )
        / NULLIF(cf.net_revenue, 0)
        AS decimal(10, 2)
    ) AS gross_margin_pct,

    lcg.revenue_month
        AS latest_month,

    CAST(
        100.0
        * (
            lcg.net_revenue
            - lcg.previous_month_net_revenue
        )
        / NULLIF(
            lcg.previous_month_net_revenue,
            0
        )
        AS decimal(10, 2)
    ) AS latest_month_growth_pct

FROM country_financials cf

INNER JOIN dbo.countries c
    ON cf.country_id = c.country_id

LEFT JOIN latest_country_growth lcg
    ON cf.country_id = lcg.country_id
    AND lcg.rn = 1;
GO

SELECT *
FROM dbo.vw_country_performance
ORDER BY net_revenue DESC;


SELECT
    SUM(sales_revenue) AS total_sales_revenue,
    SUM(refund_amount) AS total_refunds,
    SUM(net_revenue) AS total_net_revenue,
    SUM(cogs) AS total_cogs,
    SUM(gross_profit) AS total_gross_profit
FROM dbo.vw_country_performance;