USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_promotion_performance
AS

WITH order_sales AS (
    SELECT
        o.order_id,
        o.promotion_id,
        o.order_timestamp,

        SUM(
            oi.quantity * oi.unit_price
            - oi.line_discount
        ) AS sales_revenue,

        SUM(
            oi.quantity * oi.unit_cogs
        ) AS cogs,

        SUM(oi.quantity) AS units_sold

    FROM dbo.orders o

    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id

    WHERE
        o.status <> 'cancelled'
        AND o.promotion_id IS NOT NULL

    GROUP BY
        o.order_id,
        o.promotion_id,
        o.order_timestamp
),

order_refunds AS (
    SELECT
        r.order_id,
        SUM(r.refund_amount) AS refund_amount

    FROM dbo.refunds r

    GROUP BY
        r.order_id
),

promotion_actual AS (
    SELECT
        os.promotion_id,

        COUNT(os.order_id) AS promoted_orders,

        SUM(os.units_sold) AS promoted_units,

        SUM(os.sales_revenue) AS sales_revenue,

        SUM(
            ISNULL(rf.refund_amount, 0)
        ) AS refund_amount,

        SUM(
            os.sales_revenue
            - ISNULL(rf.refund_amount, 0)
        ) AS net_revenue,

        SUM(os.cogs) AS cogs

    FROM order_sales os

    LEFT JOIN order_refunds rf
        ON os.order_id = rf.order_id

    GROUP BY
        os.promotion_id
),

promotion_products AS (
    SELECT
        o.promotion_id,
        oi.product_id,

        SUM(oi.quantity)
            AS promotion_quantity

    FROM dbo.orders o

    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id

    WHERE
        o.status <> 'cancelled'
        AND o.promotion_id IS NOT NULL

    GROUP BY
        o.promotion_id,
        oi.product_id
),

baseline_product_prices AS (
    SELECT
        pp.promotion_id,
        pp.product_id,
        pp.promotion_quantity,

        AVG(
            CAST(
                oi.unit_price
                - (
                    oi.line_discount
                    / NULLIF(oi.quantity, 0)
                )
                AS decimal(18, 4)
            )
        ) AS baseline_unit_revenue

    FROM promotion_products pp

    INNER JOIN dbo.promotions p
        ON pp.promotion_id = p.promotion_id

    LEFT JOIN dbo.order_items oi
        ON pp.product_id = oi.product_id

    LEFT JOIN dbo.orders o
        ON oi.order_id = o.order_id
        AND o.status <> 'cancelled'
        AND o.order_timestamp >= DATEADD(
            DAY,
            -28,
            CAST(p.promotion_start_date AS datetime2)
        )
        AND o.order_timestamp <
            CAST(p.promotion_start_date AS datetime2)

    GROUP BY
        pp.promotion_id,
        pp.product_id,
        pp.promotion_quantity
),

promotion_baseline AS (
    SELECT
        promotion_id,

        SUM(
            promotion_quantity
            * ISNULL(baseline_unit_revenue, 0)
        ) AS baseline_revenue

    FROM baseline_product_prices

    GROUP BY
        promotion_id
)

SELECT
    p.promotion_id,
    p.promotion_name,
    p.promotion_type,
    p.discount_type,
    p.discount_amount,
    p.promotion_start_date,
    p.promotion_end_date,

    ISNULL(pa.promoted_orders, 0)
        AS promoted_orders,

    ISNULL(pa.promoted_units, 0)
        AS promoted_units,

    ISNULL(pa.sales_revenue, 0)
        AS sales_revenue,

    ISNULL(pa.refund_amount, 0)
        AS refund_amount,

    ISNULL(pa.net_revenue, 0)
        AS net_revenue,

    ISNULL(pa.cogs, 0)
        AS cogs,

    ISNULL(pa.net_revenue, 0)
        - ISNULL(pa.cogs, 0)
        AS gross_profit,

    CAST(
        100.0
        * (
            ISNULL(pa.net_revenue, 0)
            - ISNULL(pa.cogs, 0)
        )
        / NULLIF(pa.net_revenue, 0)

        AS decimal(10, 2)
    ) AS gross_margin_pct,

    ISNULL(pb.baseline_revenue, 0)
        AS baseline_revenue,

    ISNULL(pa.net_revenue, 0)
        - ISNULL(pb.baseline_revenue, 0)
        AS revenue_uplift,

    CAST(
        100.0
        * (
            ISNULL(pa.net_revenue, 0)
            - ISNULL(pb.baseline_revenue, 0)
        )
        / NULLIF(pb.baseline_revenue, 0)

        AS decimal(10, 2)
    ) AS revenue_uplift_pct

FROM dbo.promotions p

LEFT JOIN promotion_actual pa
    ON p.promotion_id = pa.promotion_id

LEFT JOIN promotion_baseline pb
    ON p.promotion_id = pb.promotion_id;
GO


SELECT TOP 20 *
FROM dbo.vw_promotion_performance
ORDER BY revenue_uplift_pct DESC;