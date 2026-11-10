USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_funnel_performance
AS
WITH session_stage AS (
    SELECT
        me.session_id,
        DATEFROMPARTS(
            YEAR(MIN(me.event_timestamp)),
            MONTH(MIN(me.event_timestamp)),
            1
        ) AS funnel_month,
        me.channel_id,
        me.campaign_id,
        me.country_id,
        MAX(CASE WHEN me.event_type = 'session_start' THEN 1 ELSE 0 END)
            AS reached_session_start,
        MAX(CASE WHEN me.event_type = 'product_view' THEN 1 ELSE 0 END)
            AS reached_product_view,
        MAX(CASE WHEN me.event_type = 'add_to_cart' THEN 1 ELSE 0 END)
            AS reached_add_to_cart,
        MAX(CASE WHEN me.event_type = 'checkout_started' THEN 1 ELSE 0 END)
            AS reached_checkout,
        MAX(CASE WHEN me.event_type = 'purchase' THEN 1 ELSE 0 END)
            AS reached_purchase
    FROM dbo.marketing_events me
    WHERE me.session_id IS NOT NULL
    GROUP BY
        me.session_id,
        me.channel_id,
        me.campaign_id,
        me.country_id
),
aggregated AS (
    SELECT
        ss.funnel_month,
        ss.channel_id,
        ss.campaign_id,
        ss.country_id,
        COUNT(*) AS total_sessions,
        SUM(ss.reached_product_view) AS product_view_sessions,
        SUM(ss.reached_add_to_cart) AS add_to_cart_sessions,
        SUM(ss.reached_checkout) AS checkout_sessions,
        SUM(ss.reached_purchase) AS purchase_sessions
    FROM session_stage ss
    GROUP BY
        ss.funnel_month,
        ss.channel_id,
        ss.campaign_id,
        ss.country_id
)
SELECT
    a.funnel_month,
    a.channel_id,
    ch.channel_name,
    a.campaign_id,
    c.campaign_name,
    a.country_id,
    a.total_sessions,
    a.product_view_sessions,
    a.add_to_cart_sessions,
    a.checkout_sessions,
    a.purchase_sessions,
    CAST(100.0 * a.product_view_sessions / NULLIF(a.total_sessions, 0) AS decimal(10,2))
        AS session_to_product_view_pct,
    CAST(100.0 * a.add_to_cart_sessions / NULLIF(a.product_view_sessions, 0) AS decimal(10,2))
        AS product_view_to_cart_pct,
    CAST(100.0 * a.checkout_sessions / NULLIF(a.add_to_cart_sessions, 0) AS decimal(10,2))
        AS cart_to_checkout_pct,
    CAST(100.0 * a.purchase_sessions / NULLIF(a.checkout_sessions, 0) AS decimal(10,2))
        AS checkout_to_purchase_pct,
    CAST(100.0 * a.purchase_sessions / NULLIF(a.total_sessions, 0) AS decimal(10,2))
        AS conversion_rate_pct
FROM aggregated a
INNER JOIN dbo.channels ch
    ON a.channel_id = ch.channel_id
LEFT JOIN dbo.campaigns c
    ON a.campaign_id = c.campaign_id;
GO

SELECT TOP 50 *
FROM dbo.vw_funnel_performance
ORDER BY funnel_month DESC, conversion_rate_pct DESC;
