USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_marketing_performance
AS

WITH campaign_spend AS (
    SELECT
        ms.campaign_id,

        SUM(ms.ad_spend) AS total_spend,
        SUM(ms.impressions) AS impressions,
        SUM(ms.clicks) AS clicks

    FROM dbo.marketing_spend ms

    GROUP BY
        ms.campaign_id
),

order_sales AS (
    SELECT
        o.order_id,

        SUM(
            oi.quantity * oi.unit_price
            - oi.line_discount
        ) AS sales_revenue

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
        o.order_id
),

order_refunds AS (
    SELECT
        r.order_id,
        SUM(r.refund_amount) AS refund_amount

    FROM dbo.refunds r

    GROUP BY
        r.order_id
),

attributed_orders AS (
    SELECT
        ma.campaign_id,
        ma.order_id,

        os.sales_revenue
        - ISNULL(rf.refund_amount, 0)
        AS attributed_net_revenue

    FROM dbo.marketing_attribution ma

    INNER JOIN order_sales os
        ON ma.order_id = os.order_id

    LEFT JOIN order_refunds rf
        ON ma.order_id = rf.order_id
),

campaign_revenue AS (
    SELECT
        campaign_id,

        COUNT(DISTINCT order_id)
            AS attributed_orders,

        SUM(attributed_net_revenue)
            AS attributed_net_revenue

    FROM attributed_orders

    GROUP BY
        campaign_id
)

SELECT
    c.campaign_id,
    c.campaign_name,
    c.channel_id,

    ISNULL(cs.total_spend, 0)
        AS total_spend,

    ISNULL(cs.impressions, 0)
        AS impressions,

    ISNULL(cs.clicks, 0)
        AS clicks,

    CAST(
        100.0 * ISNULL(cs.clicks, 0)
        / NULLIF(cs.impressions, 0)
        AS decimal(10, 2)
    ) AS ctr_pct,

    CAST(
        ISNULL(cs.total_spend, 0)
        / NULLIF(cs.clicks, 0)
        AS decimal(10, 2)
    ) AS cpc,

    ISNULL(cr.attributed_orders, 0)
        AS attributed_orders,

    ISNULL(cr.attributed_net_revenue, 0)
        AS attributed_net_revenue,

    CAST(
        ISNULL(cr.attributed_net_revenue, 0)
        / NULLIF(cs.total_spend, 0)
        AS decimal(10, 2)
    ) AS roas

FROM dbo.campaigns c

LEFT JOIN campaign_spend cs
    ON c.campaign_id = cs.campaign_id

LEFT JOIN campaign_revenue cr
    ON c.campaign_id = cr.campaign_id;
GO


SELECT TOP 20 *
FROM dbo.vw_marketing_performance
ORDER BY roas DESC;