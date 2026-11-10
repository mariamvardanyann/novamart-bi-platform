USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_return_performance
AS
WITH eligible_product_orders AS (
    SELECT
        oi.product_id,
        COUNT(DISTINCT o.order_id) AS eligible_delivered_orders,
        SUM(oi.quantity) AS sold_units
    FROM dbo.orders o
    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id
    WHERE o.status = 'delivered'
    GROUP BY oi.product_id
),
return_metrics AS (
    SELECT
        oi.product_id,
        COUNT(DISTINCT r.return_id) AS return_count,
        COUNT(DISTINCT CASE WHEN o.status = 'delivered' THEN r.order_id END)
            AS returned_delivered_orders,
        SUM(CASE WHEN o.status = 'delivered' THEN r.returned_quantity ELSE 0 END)
            AS returned_units,
        SUM(CASE WHEN o.status = 'delivered' THEN r.return_cost ELSE 0 END)
            AS total_return_cost,
        SUM(
            CASE
                WHEN o.status = 'delivered' AND r.defect_flag = 1 THEN 1
                ELSE 0
            END
        ) AS defect_returns
    FROM dbo.returns r
    INNER JOIN dbo.order_items oi
        ON r.order_line_id = oi.order_line_id
    INNER JOIN dbo.orders o
        ON r.order_id = o.order_id
    GROUP BY oi.product_id
)
SELECT
    p.product_id,
    p.product_name,
    c.category_id,
    c.category_name,
    ISNULL(epo.eligible_delivered_orders, 0) AS eligible_delivered_orders,
    ISNULL(rm.returned_delivered_orders, 0) AS returned_delivered_orders,
    CAST(
        100.0 * ISNULL(rm.returned_delivered_orders, 0)
        / NULLIF(epo.eligible_delivered_orders, 0)
        AS decimal(10, 2)
    ) AS return_rate_pct,
    ISNULL(epo.sold_units, 0) AS sold_units,
    ISNULL(rm.return_count, 0) AS return_count,
    ISNULL(rm.returned_units, 0) AS returned_units,
    CAST(
        100.0 * ISNULL(rm.returned_units, 0)
        / NULLIF(epo.sold_units, 0)
        AS decimal(10, 2)
    ) AS unit_return_rate_pct,
    ISNULL(rm.defect_returns, 0) AS defect_returns,
    CAST(
        100.0 * ISNULL(rm.defect_returns, 0)
        / NULLIF(rm.return_count, 0)
        AS decimal(10, 2)
    ) AS defect_rate_pct,
    ISNULL(rm.total_return_cost, 0) AS total_return_cost
FROM dbo.products p
INNER JOIN dbo.categories c
    ON p.category_id = c.category_id
LEFT JOIN eligible_product_orders epo
    ON p.product_id = epo.product_id
LEFT JOIN return_metrics rm
    ON p.product_id = rm.product_id;
GO

SELECT TOP 20 *
FROM dbo.vw_return_performance
ORDER BY return_rate_pct DESC;
