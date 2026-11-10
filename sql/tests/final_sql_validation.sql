USE novamart;
GO

SET NOCOUNT ON;

/*
NovaMart final analytical validation.
Run after schema, data load, and all scripts in sql/views/.
The checks compare analytical layers against each other instead of hard-coding
portfolio totals, so they remain useful after controlled data/model changes.
*/

PRINT '--- NovaMart analytical reconciliation ---';

WITH totals AS (
    SELECT
        'vw_revenue_performance' AS source_name,
        CAST(SUM(sales_revenue) AS decimal(18,2)) AS sales_revenue,
        CAST(SUM(refund_amount) AS decimal(18,2)) AS refunds,
        CAST(SUM(net_revenue) AS decimal(18,2)) AS net_revenue
    FROM dbo.vw_revenue_performance

    UNION ALL

    SELECT
        'vw_product_sales',
        CAST(SUM(sales_revenue) AS decimal(18,2)),
        CAST(SUM(refund_amount) AS decimal(18,2)),
        CAST(SUM(net_revenue) AS decimal(18,2))
    FROM dbo.vw_product_sales

    UNION ALL

    SELECT
        'vw_category_performance',
        CAST(SUM(sales_revenue) AS decimal(18,2)),
        CAST(SUM(refund_amount) AS decimal(18,2)),
        CAST(SUM(net_revenue) AS decimal(18,2))
    FROM dbo.vw_category_performance

    UNION ALL

    SELECT
        'vw_country_performance',
        CAST(SUM(sales_revenue) AS decimal(18,2)),
        CAST(SUM(refund_amount) AS decimal(18,2)),
        CAST(SUM(net_revenue) AS decimal(18,2))
    FROM dbo.vw_country_performance

    UNION ALL

    SELECT
        'vw_profitability',
        CAST(SUM(sales_revenue) AS decimal(18,2)),
        CAST(SUM(refund_amount) AS decimal(18,2)),
        CAST(SUM(net_revenue) AS decimal(18,2))
    FROM dbo.vw_profitability
),
baseline AS (
    SELECT
        sales_revenue,
        refunds,
        net_revenue
    FROM totals
    WHERE source_name = 'vw_revenue_performance'
)
SELECT
    t.source_name,
    t.sales_revenue,
    t.refunds,
    t.net_revenue,
    CAST(t.sales_revenue - b.sales_revenue AS decimal(18,2)) AS sales_delta,
    CAST(t.refunds - b.refunds AS decimal(18,2)) AS refund_delta,
    CAST(t.net_revenue - b.net_revenue AS decimal(18,2)) AS net_revenue_delta,
    CASE
        WHEN ABS(t.sales_revenue - b.sales_revenue) < 0.01
         AND ABS(t.refunds - b.refunds) < 0.01
         AND ABS(t.net_revenue - b.net_revenue) < 0.01
        THEN 'PASS'
        ELSE 'CHECK'
    END AS reconciliation_status
FROM totals t
CROSS JOIN baseline b
ORDER BY t.source_name;

PRINT '';
PRINT '--- Gross profit reconciliation ---';

WITH gross_totals AS (
    SELECT
        'vw_product_profitability' AS source_name,
        CAST(SUM(gross_profit) AS decimal(18,2)) AS gross_profit
    FROM dbo.vw_product_profitability

    UNION ALL

    SELECT
        'vw_category_performance',
        CAST(SUM(gross_profit) AS decimal(18,2))
    FROM dbo.vw_category_performance

    UNION ALL

    SELECT
        'vw_country_performance',
        CAST(SUM(gross_profit) AS decimal(18,2))
    FROM dbo.vw_country_performance

    UNION ALL

    SELECT
        'vw_profitability',
        CAST(SUM(gross_profit) AS decimal(18,2))
    FROM dbo.vw_profitability
),
gross_baseline AS (
    SELECT gross_profit
    FROM gross_totals
    WHERE source_name = 'vw_product_profitability'
)
SELECT
    g.source_name,
    g.gross_profit,
    CAST(g.gross_profit - b.gross_profit AS decimal(18,2)) AS gross_profit_delta,
    CASE
        WHEN ABS(g.gross_profit - b.gross_profit) < 0.01 THEN 'PASS'
        ELSE 'CHECK'
    END AS reconciliation_status
FROM gross_totals g
CROSS JOIN gross_baseline b
ORDER BY g.source_name;

PRINT '';
PRINT '--- Profitability cost coverage ---';
SELECT
    CAST(SUM(shipping_cost) AS decimal(18,2)) AS shipping_cost,
    CAST(SUM(payment_fees) AS decimal(18,2)) AS payment_fees,
    CAST(SUM(return_costs) AS decimal(18,2)) AS return_costs,
    CAST(SUM(marketing_cost) AS decimal(18,2)) AS marketing_cost,
    CAST(SUM(operating_costs) AS decimal(18,2)) AS operating_costs,
    CAST(SUM(contribution_profit) AS decimal(18,2)) AS contribution_profit,
    CAST(SUM(net_profit) AS decimal(18,2)) AS net_profit
FROM dbo.vw_profitability;

PRINT '';
PRINT '--- Analytical object count ---';
SELECT
    COUNT(*) AS novamart_vw_object_count
FROM sys.views
WHERE schema_id = SCHEMA_ID('dbo')
  AND name LIKE 'vw[_]%';
GO
