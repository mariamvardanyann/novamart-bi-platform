# SQL Analytical Views

Run the schema and load the clean/derived tables before creating these views.

The project has **18 canonical analytical views** documented in `docs/04_data_dictionary.md`, plus one helper attribution-summary view (`vw_marketing_attribution`).

## Suggested execution order

Most views are independent. The following dependency order avoids view-reference errors:

1. `vw_revenue_performance.sql`
2. `vw_revenue_growth.sql`
3. `vw_product_sales.sql`
4. `vw_product_profitability.sql`
5. `vw_category_performance.sql`
6. `vw_country_performance.sql`
7. `vw_customer_value.sql`
8. `vw_customer_rfm.sql`
9. `vw_customer_retention.sql`
10. `vw_marketing_attribution.sql`
11. `vw_marketing_performance.sql`
12. `vw_funnel_performance.sql`
13. `vw_promotion_performance.sql`
14. `vw_fulfillment_performance.sql`
15. `vw_delivery_performance.sql`
16. `vw_return_performance.sql`
17. `vw_carrier_performance.sql`
18. `vw_cost_performance.sql`
19. `vw_profitability.sql`

Then run `../tests/final_sql_validation.sql`.

## Important implementation notes

- `vw_funnel_performance` is reconstructed from the current event schema and counts unique sessions reaching each tracked event stage. The current event data does **not** contain an `order_id`, so a purchase event cannot yet be independently reconciled to a completed order as required by DQ-015. Treat this as a known modeling limitation until the event/order mapping is added.
- `vw_return_performance` exposes both the KPI-dictionary order-based `return_rate_pct` and a supplementary `unit_return_rate_pct` diagnostic.
- `vw_profitability` follows the KPI dictionary's full modeled cost formula and therefore requires the Power BI report to be refreshed before publishing updated Net Profit values/screenshots.
