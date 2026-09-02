USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_marketing_attribution
AS

SELECT
    ma.campaign_id,
    ma.channel_id,

    COUNT(DISTINCT ma.order_id) AS attributed_orders,

    COUNT(DISTINCT ma.customer_id) AS attributed_customers,

    MIN(ma.touchpoint_timestamp) AS first_touchpoint_timestamp,

    MAX(ma.touchpoint_timestamp) AS last_touchpoint_timestamp

FROM dbo.marketing_attribution ma

GROUP BY
    ma.campaign_id,
    ma.channel_id;
GO

SELECT TOP 20 *
FROM dbo.vw_marketing_attribution
ORDER BY attributed_orders DESC;ok