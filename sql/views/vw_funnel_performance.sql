USE [novamart]
GO

/****** Object:  View [dbo].[vw_fulfillment_performance]    Script Date: 02/09/2026 18:41:01 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


ALTER   VIEW [dbo].[vw_fulfillment_performance]
AS

WITH order_base AS (
    SELECT
        o.order_id,
        o.order_timestamp,
        o.status,

        CASE
            WHEN o.status = 'cancelled' THEN 1
            ELSE 0
        END AS is_cancelled

    FROM dbo.orders o
),

shipment_summary AS (
    SELECT
        s.order_id,

        MAX(
            CASE
                WHEN s.shipping_timestamp IS NOT NULL THEN 1
                ELSE 0
            END
        ) AS has_shipment,

        MIN(s.shipping_timestamp)
            AS first_shipping_timestamp,

        SUM(s.shipping_cost)
            AS shipping_cost

    FROM dbo.shipments s

    GROUP BY
        s.order_id
)

SELECT
    COUNT(*) AS total_orders,

    SUM(
        CASE
            WHEN ob.is_cancelled = 0 THEN 1
            ELSE 0
        END
    ) AS eligible_orders,

    SUM(
        ob.is_cancelled
    ) AS cancelled_orders,

    CAST(
        100.0 * SUM(ob.is_cancelled)
        / NULLIF(COUNT(*), 0)
        AS decimal(10, 2)
    ) AS cancellation_rate_pct,

    SUM(
        CASE
            WHEN ob.is_cancelled = 0
             AND ISNULL(ss.has_shipment, 0) = 1
            THEN 1
            ELSE 0
        END
    ) AS fulfilled_orders,

    CAST(
        100.0
        * SUM(
            CASE
                WHEN ob.is_cancelled = 0
                 AND ISNULL(ss.has_shipment, 0) = 1
                THEN 1
                ELSE 0
            END
        )
        / NULLIF(
            SUM(
                CASE
                    WHEN ob.is_cancelled = 0 THEN 1
                    ELSE 0
                END
            ),
            0
        )
        AS decimal(10, 2)
    ) AS fulfillment_rate_pct,

    CAST(
        AVG(
            CASE
                WHEN ob.is_cancelled = 0
                 AND ss.first_shipping_timestamp IS NOT NULL
                THEN
                    CAST(
                        DATEDIFF(
                            MINUTE,
                            ob.order_timestamp,
                            ss.first_shipping_timestamp
                        ) / 60.0
                        AS decimal(18, 2)
                    )
            END
        )
        AS decimal(10, 2)
    ) AS avg_order_to_ship_hours,

    SUM(
        ISNULL(ss.shipping_cost, 0)
    ) AS total_shipping_cost,

    CAST(
        AVG(
            CASE
                WHEN ss.has_shipment = 1
                THEN ss.shipping_cost
            END
        )
        AS decimal(10, 2)
    ) AS avg_shipping_cost

FROM order_base ob

LEFT JOIN shipment_summary ss
    ON ob.order_id = ss.order_id;
GO

