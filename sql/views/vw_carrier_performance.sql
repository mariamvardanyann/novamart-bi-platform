USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_carrier_performance
AS

WITH shipment_base AS (
    SELECT
        s.shipment_id,
        s.order_id,
        s.carrier_id,
        s.shipping_timestamp,
        s.actual_delivery_timestamp,
        s.expected_delivery_date,
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
),

carrier_orders AS (
    SELECT DISTINCT
        carrier_id,
        order_id
    FROM dbo.shipments
),

carrier_returns AS (
    SELECT
        co.carrier_id,

        COUNT(DISTINCT r.return_id)
            AS return_count,

        COUNT(DISTINCT r.order_id)
            AS returned_orders,

        SUM(r.returned_quantity)
            AS returned_units,

        SUM(r.return_cost)
            AS total_return_cost

    FROM dbo.returns r

    INNER JOIN carrier_orders co
        ON r.order_id = co.order_id

    GROUP BY
        co.carrier_id
),

carrier_shipments AS (
    SELECT
        carrier_id,

        COUNT(*) AS total_shipments,

        COUNT(DISTINCT order_id)
            AS carrier_orders,

        SUM(is_delivered)
            AS delivered_shipments,

        SUM(is_on_time)
            AS on_time_shipments,

        AVG(delivery_hours)
            AS avg_delivery_hours,

        SUM(shipping_cost)
            AS total_shipping_cost,

        AVG(shipping_cost)
            AS avg_shipping_cost

    FROM shipment_base

    GROUP BY
        carrier_id
)

SELECT
    c.carrier_id,
    c.carrier_name,

    ISNULL(cs.total_shipments, 0)
        AS total_shipments,

    ISNULL(cs.carrier_orders, 0)
        AS carrier_orders,

    ISNULL(cs.delivered_shipments, 0)
        AS delivered_shipments,

    ISNULL(cs.on_time_shipments, 0)
        AS on_time_shipments,

    CAST(
        100.0 * ISNULL(cs.on_time_shipments, 0)
        / NULLIF(cs.delivered_shipments, 0)
        AS decimal(10, 2)
    ) AS on_time_delivery_rate_pct,

    CAST(
        cs.avg_delivery_hours
        AS decimal(10, 2)
    ) AS avg_delivery_hours,

    ISNULL(cr.return_count, 0)
        AS return_count,

    ISNULL(cr.returned_orders, 0)
        AS returned_orders,

    ISNULL(cr.returned_units, 0)
        AS returned_units,

    CAST(
        100.0 * ISNULL(cr.returned_orders, 0)
        / NULLIF(cs.carrier_orders, 0)
        AS decimal(10, 2)
    ) AS return_rate_pct,

    ISNULL(cr.total_return_cost, 0)
        AS total_return_cost,

    CAST(
        cs.total_shipping_cost
        AS decimal(18, 2)
    ) AS total_shipping_cost,

    CAST(
        cs.avg_shipping_cost
        AS decimal(10, 2)
    ) AS avg_shipping_cost

FROM dbo.carriers c

LEFT JOIN carrier_shipments cs
    ON c.carrier_id = cs.carrier_id

LEFT JOIN carrier_returns cr
    ON c.carrier_id = cr.carrier_id;
GO

SELECT *
FROM dbo.vw_carrier_performance
ORDER BY return_rate_pct DESC;