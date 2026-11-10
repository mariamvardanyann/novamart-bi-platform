USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_profitability
AS
WITH order_sales AS (
    SELECT
        o.order_id,
        DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
            AS profit_month,
        SUM(oi.quantity * oi.unit_price - oi.line_discount) AS sales_revenue,
        SUM(oi.quantity * oi.unit_cogs) AS cogs
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
        o.order_id,
        DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
),
order_refunds AS (
    SELECT
        r.order_id,
        SUM(r.refund_amount) AS refund_amount
    FROM dbo.refunds r
    GROUP BY r.order_id
),
monthly_sales AS (
    SELECT
        os.profit_month,
        SUM(os.sales_revenue) AS sales_revenue,
        SUM(ISNULL(rf.refund_amount, 0)) AS refund_amount,
        SUM(os.sales_revenue - ISNULL(rf.refund_amount, 0)) AS net_revenue,
        SUM(os.cogs) AS cogs
    FROM order_sales os
    LEFT JOIN order_refunds rf
        ON os.order_id = rf.order_id
    GROUP BY os.profit_month
),
monthly_shipping AS (
    SELECT
        DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
            AS profit_month,
        SUM(s.shipping_cost) AS shipping_cost
    FROM dbo.shipments s
    INNER JOIN dbo.orders o
        ON s.order_id = o.order_id
    WHERE o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
        AND EXISTS (
            SELECT 1
            FROM dbo.payments p_eligible
            WHERE p_eligible.order_id = o.order_id
              AND p_eligible.payment_status = 'succeeded'
        )
    GROUP BY DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
),
monthly_payment_fees AS (
    SELECT
        DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
            AS profit_month,
        SUM(CASE WHEN p.payment_status = 'succeeded' THEN p.payment_fee ELSE 0 END)
            AS payment_fees
    FROM dbo.payments p
    INNER JOIN dbo.orders o
        ON p.order_id = o.order_id
    WHERE o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
        AND EXISTS (
            SELECT 1
            FROM dbo.payments p_eligible
            WHERE p_eligible.order_id = o.order_id
              AND p_eligible.payment_status = 'succeeded'
        )
    GROUP BY DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
),
monthly_return_costs AS (
    SELECT
        DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
            AS profit_month,
        SUM(r.return_cost) AS return_costs
    FROM dbo.returns r
    INNER JOIN dbo.orders o
        ON r.order_id = o.order_id
    WHERE o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
        AND EXISTS (
            SELECT 1
            FROM dbo.payments p_eligible
            WHERE p_eligible.order_id = o.order_id
              AND p_eligible.payment_status = 'succeeded'
        )
    GROUP BY DATEFROMPARTS(YEAR(o.order_timestamp), MONTH(o.order_timestamp), 1)
),
monthly_marketing AS (
    SELECT
        DATEFROMPARTS(YEAR(ms.spend_date), MONTH(ms.spend_date), 1)
            AS profit_month,
        SUM(ms.ad_spend) AS marketing_cost
    FROM dbo.marketing_spend ms
    GROUP BY DATEFROMPARTS(YEAR(ms.spend_date), MONTH(ms.spend_date), 1)
),
monthly_operating_costs AS (
    SELECT
        DATEFROMPARTS(YEAR(fc.cost_date), MONTH(fc.cost_date), 1)
            AS profit_month,
        SUM(fc.amount) AS operating_costs
    FROM dbo.finance_costs fc
    GROUP BY DATEFROMPARTS(YEAR(fc.cost_date), MONTH(fc.cost_date), 1)
),
month_spine AS (
    SELECT profit_month FROM monthly_sales
    UNION SELECT profit_month FROM monthly_shipping
    UNION SELECT profit_month FROM monthly_payment_fees
    UNION SELECT profit_month FROM monthly_return_costs
    UNION SELECT profit_month FROM monthly_marketing
    UNION SELECT profit_month FROM monthly_operating_costs
),
profit_base AS (
    SELECT
        m.profit_month,
        ISNULL(ms.sales_revenue, 0) AS sales_revenue,
        ISNULL(ms.refund_amount, 0) AS refund_amount,
        ISNULL(ms.net_revenue, 0) AS net_revenue,
        ISNULL(ms.cogs, 0) AS cogs,
        ISNULL(sh.shipping_cost, 0) AS shipping_cost,
        ISNULL(pf.payment_fees, 0) AS payment_fees,
        ISNULL(rc.return_costs, 0) AS return_costs,
        ISNULL(mk.marketing_cost, 0) AS marketing_cost,
        ISNULL(oc.operating_costs, 0) AS operating_costs
    FROM month_spine m
    LEFT JOIN monthly_sales ms ON m.profit_month = ms.profit_month
    LEFT JOIN monthly_shipping sh ON m.profit_month = sh.profit_month
    LEFT JOIN monthly_payment_fees pf ON m.profit_month = pf.profit_month
    LEFT JOIN monthly_return_costs rc ON m.profit_month = rc.profit_month
    LEFT JOIN monthly_marketing mk ON m.profit_month = mk.profit_month
    LEFT JOIN monthly_operating_costs oc ON m.profit_month = oc.profit_month
)
SELECT
    profit_month,
    sales_revenue,
    refund_amount,
    net_revenue,
    cogs,
    net_revenue - cogs AS gross_profit,
    CAST(100.0 * (net_revenue - cogs) / NULLIF(net_revenue, 0) AS decimal(10,2))
        AS gross_margin_pct,
    shipping_cost,
    payment_fees,
    return_costs,
    net_revenue - cogs - shipping_cost - payment_fees - return_costs
        AS contribution_profit,
    CAST(
        100.0 * (net_revenue - cogs - shipping_cost - payment_fees - return_costs)
        / NULLIF(net_revenue, 0)
        AS decimal(10,2)
    ) AS contribution_margin_pct,
    marketing_cost,
    operating_costs,
    net_revenue - cogs - shipping_cost - payment_fees - return_costs
        - marketing_cost - operating_costs AS net_profit,
    CAST(
        100.0 * (
            net_revenue - cogs - shipping_cost - payment_fees - return_costs
            - marketing_cost - operating_costs
        ) / NULLIF(net_revenue, 0)
        AS decimal(10,2)
    ) AS net_margin_pct
FROM profit_base;
GO

SELECT *
FROM dbo.vw_profitability
ORDER BY profit_month DESC;
