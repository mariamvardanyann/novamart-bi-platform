USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_revenue_growth
AS

WITH monthly_revenue AS (
    SELECT
        DATEFROMPARTS(
            YEAR(order_date),
            MONTH(order_date),
            1
        ) AS revenue_month,

        SUM(sales_revenue) AS sales_revenue,
        SUM(refund_amount) AS refund_amount,
        SUM(net_revenue) AS net_revenue

    FROM dbo.vw_revenue_performance

    GROUP BY
        DATEFROMPARTS(
            YEAR(order_date),
            MONTH(order_date),
            1
        )
),

revenue_with_previous AS (
    SELECT
        revenue_month,
        sales_revenue,
        refund_amount,
        net_revenue,

        LAG(net_revenue) OVER (
            ORDER BY revenue_month
        ) AS previous_month_net_revenue

    FROM monthly_revenue
)

SELECT
    revenue_month,
    sales_revenue,
    refund_amount,
    net_revenue,
    previous_month_net_revenue,

    net_revenue
        - previous_month_net_revenue
        AS net_revenue_change,

    CAST(
        100.0
        * (
            net_revenue
            - previous_month_net_revenue
        )
        / NULLIF(previous_month_net_revenue, 0)
        AS decimal(10, 2)
    ) AS revenue_growth_pct

FROM revenue_with_previous;
GO


SELECT *
FROM dbo.vw_revenue_growth
ORDER BY revenue_month DESC;