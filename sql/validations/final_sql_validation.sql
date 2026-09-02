USE novamart;
GO

-- 1. Revenue reconciliation
SELECT
    'revenue_performance' AS check_name,
    SUM(sales_revenue) AS sales_revenue,
    SUM(refund_amount) AS refunds,
    SUM(net_revenue) AS net_revenue
FROM dbo.vw_revenue_performance;

-- 2. Product reconciliation
SELECT
    'product_sales' AS check_name,
    SUM(sales_revenue) AS sales_revenue,
    SUM(refund_amount) AS refunds,
    SUM(net_revenue) AS net_revenue
FROM dbo.vw_product_sales;

-- 3. Category reconciliation
SELECT
    'category_performance' AS check_name,
    SUM(sales_revenue) AS sales_revenue,
    SUM(refund_amount) AS refunds,
    SUM(net_revenue) AS net_revenue
FROM dbo.vw_category_performance;

-- 4. Country reconciliation
SELECT
    'country_performance' AS check_name,
    SUM(sales_revenue) AS sales_revenue,
    SUM(refund_amount) AS refunds,
    SUM(net_revenue) AS net_revenue
FROM dbo.vw_country_performance;

-- 5. Profitability totals
SELECT
    SUM(sales_revenue) AS sales_revenue,
    SUM(refund_amount) AS refunds,
    SUM(net_revenue) AS net_revenue,
    SUM(cogs) AS cogs,
    SUM(gross_profit) AS gross_profit,
    SUM(shipping_cost) AS shipping_cost,
    SUM(operating_costs) AS operating_costs,
    SUM(net_profit) AS net_profit
FROM dbo.vw_profitability;

-- 6. Customer segmentation
SELECT
    customer_segment,
    COUNT(*) AS customers
FROM dbo.vw_customer_value
GROUP BY customer_segment
ORDER BY customers DESC;

-- 7. Fulfillment
SELECT *
FROM dbo.vw_fulfillment_performance;

-- 8. Attribution
SELECT
    SUM(attributed_orders) AS attributed_orders
FROM dbo.vw_marketing_attribution;
GO