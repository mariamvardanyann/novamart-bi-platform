USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_return_performance
AS

WITH sold_units AS (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS sold_units
    FROM dbo.orders o
    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id
    WHERE o.status <> 'cancelled'
    GROUP BY oi.product_id
),

return_metrics AS (
    SELECT
        oi.product_id,

        COUNT(DISTINCT r.return_id) AS return_count,

        SUM(r.returned_quantity) AS returned_units,

        SUM(r.return_cost) AS total_return_cost,

        SUM(
            CASE
                WHEN r.defect_flag = 1 THEN 1
                ELSE 0
            END
        ) AS defect_returns

    FROM dbo.returns r

    INNER JOIN dbo.order_items oi
        ON r.order_line_id = oi.order_line_id

    GROUP BY
        oi.product_id
)

SELECT
    p.product_id,
    p.product_name,

    c.category_id,
    c.category_name,

    ISNULL(su.sold_units, 0)
        AS sold_units,

    ISNULL(rm.return_count, 0)
        AS return_count,

    ISNULL(rm.returned_units, 0)
        AS returned_units,

    CAST(
        100.0 * ISNULL(rm.returned_units, 0)
        / NULLIF(su.sold_units, 0)
        AS decimal(10, 2)
    ) AS return_rate_pct,

    ISNULL(rm.defect_returns, 0)
        AS defect_returns,

    CAST(
        100.0 * ISNULL(rm.defect_returns, 0)
        / NULLIF(rm.return_count, 0)
        AS decimal(10, 2)
    ) AS defect_rate_pct,

    ISNULL(rm.total_return_cost, 0)
        AS total_return_cost

FROM dbo.products p

INNER JOIN dbo.categories c
    ON p.category_id = c.category_id

LEFT JOIN sold_units su
    ON p.product_id = su.product_id

LEFT JOIN return_metrics rm
    ON p.product_id = rm.product_id;
GO


SELECT TOP 20 *
FROM dbo.vw_return_performance
ORDER BY return_rate_pct DESC;