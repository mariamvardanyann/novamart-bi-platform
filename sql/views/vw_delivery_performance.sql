USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_delivery_performance
AS

WITH delivery_base AS (
    SELECT
        s.shipment_id,
        s.carrier_id,
        o.country_id,
        s.shipping_timestamp,
        s.expected_delivery_date,
        s.actual_delivery_timestamp,
        s.shipping_cost,

        CASE
            WHEN s.actual_delivery_timestamp IS NOT NULL
            THEN 1
            ELSE 0
        END AS is_delivered,

        CASE
            WHEN s.actual_delivery_timestamp IS NOT NULL
             AND CAST(s.actual_delivery_timestamp AS date)
                 <= s.expected_delivery_date
            THEN 1
            ELSE 0
        END AS is_on_time,

        CASE
            WHEN s.shipping_timestamp IS NOT NULL
             AND s.actual_delivery_timestamp IS NOT NULL
            THEN
                DATEDIFF(
                    MINUTE,
                    s.shipping_timestamp,
                    s.actual_delivery_timestamp
                ) / 60.0
        END AS delivery_hours

    FROM dbo.shipments s

    INNER JOIN dbo.orders o
        ON s.order_id = o.order_id
),

delivery_with_median AS (
    SELECT
        *,

        PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY delivery_hours
        )
        OVER (
            PARTITION BY carrier_id, country_id
        ) AS median_delivery_hours

    FROM delivery_base
)

SELECT
    d.carrier_id,
    c.carrier_name,

    d.country_id,
    co.country_name,

    COUNT(*) AS total_shipments,

    SUM(d.is_delivered)
        AS delivered_shipments,

    SUM(d.is_on_time)
        AS on_time_shipments,

    CAST(
        100.0 * SUM(d.is_on_time)
        / NULLIF(SUM(d.is_delivered), 0)
        AS decimal(10, 2)
    ) AS on_time_delivery_rate_pct,

    CAST(
        AVG(d.delivery_hours)
        AS decimal(10, 2)
    ) AS avg_delivery_hours,

    CAST(
        MAX(d.median_delivery_hours)
        AS decimal(10, 2)
    ) AS median_delivery_hours,

    CAST(
        SUM(d.shipping_cost)
        AS decimal(18, 2)
    ) AS total_shipping_cost,

    CAST(
        AVG(d.shipping_cost)
        AS decimal(10, 2)
    ) AS avg_shipping_cost

FROM delivery_with_median d

INNER JOIN dbo.carriers c
    ON d.carrier_id = c.carrier_id

INNER JOIN dbo.countries co
    ON d.country_id = co.country_id

GROUP BY
    d.carrier_id,
    c.carrier_name,
    d.country_id,
    co.country_name;
GO


SELECT TOP 20 *
FROM dbo.vw_delivery_performance
ORDER BY on_time_delivery_rate_pct DESC;