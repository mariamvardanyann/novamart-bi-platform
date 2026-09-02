USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_product_profitability
AS

WITH product_cogs AS (
    SELECT
        oi.product_id,

        SUM(
            oi.quantity * oi.unit_cogs
        ) AS cogs

    FROM dbo.order_items oi

    INNER JOIN dbo.orders o
        ON oi.order_id = o.order_id

    WHERE o.status <> 'cancelled'

    GROUP BY
        oi.product_id
)

SELECT
    ps.product_id,
    ps.product_name,
    ps.category_id,
    ps.category_name,

    ps.order_count,
    ps.units_sold,

    ps.sales_revenue,
    ps.refund_amount,
    ps.net_revenue,

    CAST(
        ISNULL(pc.cogs, 0)
        AS decimal(18, 2)
    ) AS cogs,

    CAST(
        ps.net_revenue
        - ISNULL(pc.cogs, 0)
        AS decimal(18, 2)
    ) AS gross_profit,

    CAST(
        100.0
        * (
            ps.net_revenue
            - ISNULL(pc.cogs, 0)
        )
        / NULLIF(ps.net_revenue, 0)
        AS decimal(10, 2)
    ) AS gross_margin_pct

FROM dbo.vw_product_sales ps

LEFT JOIN product_cogs pc
    ON ps.product_id = pc.product_id;
GO

SELECT TOP 20 *
FROM dbo.vw_product_profitability
ORDER BY gross_profit DESC;

SELECT
    SUM(sales_revenue) AS total_sales_revenue,
    SUM(refund_amount) AS total_refunds,
    SUM(net_revenue) AS total_net_revenue,
    SUM(cogs) AS total_cogs,
    SUM(gross_profit) AS total_gross_profit
FROM dbo.vw_product_profitability;