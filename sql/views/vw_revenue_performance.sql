USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_revenue_performance
AS

WITH order_sales AS (
    SELECT
        o.order_id,
        CAST(o.order_timestamp AS date) AS order_date,
        o.country_id,

        SUM(
            oi.quantity * oi.unit_price
            - oi.line_discount
        ) AS sales_revenue,

        SUM(
            oi.quantity
        ) AS units_sold

    FROM dbo.orders o

    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'cancelled'

    GROUP BY
        o.order_id,
        CAST(o.order_timestamp AS date),
        o.country_id
),

order_refunds AS (
    SELECT
        r.order_id,

        SUM(
            r.refund_amount
        ) AS refund_amount

    FROM dbo.refunds r

    GROUP BY
        r.order_id
)

SELECT
    os.order_date,
    os.country_id,

    COUNT(*) AS total_orders,

    SUM(
        os.units_sold
    ) AS units_sold,

    SUM(
        os.sales_revenue
    ) AS sales_revenue,

    SUM(
        ISNULL(
            r.refund_amount,
            0
        )
    ) AS refund_amount,

    SUM(
        os.sales_revenue
        - ISNULL(
            r.refund_amount,
            0
        )
    ) AS net_revenue

FROM order_sales os

LEFT JOIN order_refunds r
    ON os.order_id = r.order_id

GROUP BY
    os.order_date,
    os.country_id;
GO


SELECT TOP 20 *
FROM dbo.vw_revenue_performance
ORDER BY order_date, country_id;


SELECT
    SUM(sales_revenue) AS total_sales_revenue,
    SUM(refund_amount) AS total_refunds,
    SUM(net_revenue) AS total_net_revenue
FROM dbo.vw_revenue_performance;