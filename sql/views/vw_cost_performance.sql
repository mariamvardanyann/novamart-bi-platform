USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_cost_performance
AS

WITH monthly_costs AS (
    SELECT
        DATEFROMPARTS(
            YEAR(fc.cost_date),
            MONTH(fc.cost_date),
            1
        ) AS cost_month,

        fc.cost_type,
        fc.cost_category,

        SUM(fc.amount) AS total_cost

    FROM dbo.finance_costs fc

    GROUP BY
        DATEFROMPARTS(
            YEAR(fc.cost_date),
            MONTH(fc.cost_date),
            1
        ),
        fc.cost_type,
        fc.cost_category
),

monthly_revenue AS (
    SELECT
        DATEFROMPARTS(
            YEAR(vr.order_date),
            MONTH(vr.order_date),
            1
        ) AS revenue_month,

        SUM(vr.net_revenue) AS net_revenue

    FROM dbo.vw_revenue_performance vr

    GROUP BY
        DATEFROMPARTS(
            YEAR(vr.order_date),
            MONTH(vr.order_date),
            1
        )
),

cost_with_previous AS (
    SELECT
        mc.*,

        LAG(mc.total_cost) OVER (
            PARTITION BY
                mc.cost_type,
                mc.cost_category
            ORDER BY
                mc.cost_month
        ) AS previous_month_cost

    FROM monthly_costs mc
)

SELECT
    cwp.cost_month,
    cwp.cost_type,
    cwp.cost_category,

    cwp.total_cost,

    ISNULL(mr.net_revenue, 0)
        AS net_revenue,

    CAST(
        100.0 * cwp.total_cost
        / NULLIF(mr.net_revenue, 0)
        AS decimal(10, 2)
    ) AS cost_to_revenue_ratio_pct,

    cwp.previous_month_cost,

    CAST(
        100.0
        * (
            cwp.total_cost
            - cwp.previous_month_cost
        )
        / NULLIF(cwp.previous_month_cost, 0)
        AS decimal(10, 2)
    ) AS cost_growth_pct

FROM cost_with_previous cwp

LEFT JOIN monthly_revenue mr
    ON cwp.cost_month = mr.revenue_month;
GO

SELECT TOP 30 *
FROM dbo.vw_cost_performance
ORDER BY
    cost_month DESC,
    total_cost DESC;