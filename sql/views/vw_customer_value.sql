USE [novamart]
GO

/****** Object:  View [dbo].[vw_customer_value]    Script Date: 02/09/2026 18:42:10 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE OR ALTER VIEW [dbo].[vw_customer_value]
AS

WITH order_sales AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_timestamp,

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

    WHERE o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
        AND EXISTS (
            SELECT 1
            FROM dbo.payments p_eligible
            WHERE p_eligible.order_id = o.order_id
              AND p_eligible.payment_status = 'succeeded'
        )

    GROUP BY
        o.order_id,
        o.customer_id,
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

customer_summary AS (
    SELECT
        c.customer_id,
        c.country_id,

        COUNT(os.order_id) AS order_count,

        SUM(os.sales_revenue)
            AS lifetime_sales_revenue,

        SUM(
            ISNULL(rf.refund_amount, 0)
        ) AS lifetime_refunds,

        SUM(
            os.sales_revenue
            - ISNULL(rf.refund_amount, 0)
        ) AS lifetime_net_revenue,

        SUM(os.cogs)
            AS lifetime_cogs,

        SUM(
            os.sales_revenue
            - ISNULL(rf.refund_amount, 0)
            - os.cogs
        ) AS lifetime_gross_profit,

        MIN(os.order_timestamp)
            AS first_order_timestamp,

        MAX(os.order_timestamp)
            AS last_order_timestamp

    FROM dbo.customers c

    INNER JOIN order_sales os
        ON c.customer_id = os.customer_id

    LEFT JOIN order_refunds rf
        ON os.order_id = rf.order_id

    GROUP BY
        c.customer_id,
        c.country_id
)

SELECT
    customer_id,
    country_id,
    order_count,

    CASE
        WHEN order_count = 1
            THEN 'one_time'

        WHEN order_count BETWEEN 2 AND 5
            THEN 'occasional'

        WHEN order_count BETWEEN 6 AND 10
            THEN 'frequent'

        ELSE 'loyal'
    END AS customer_segment,

    lifetime_sales_revenue,
    lifetime_refunds,
    lifetime_net_revenue,
    lifetime_cogs,
    lifetime_gross_profit,
    first_order_timestamp,
    last_order_timestamp

FROM customer_summary;
GO

