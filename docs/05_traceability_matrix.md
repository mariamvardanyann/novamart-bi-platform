# Traceability Matrix
## NovaMart Business Intelligence Platform — Phase 1.2e

**Version:** v1.2 | **Status:** Sprint 1 Baseline — reconciled to canonical 18-view catalog (`04_data_dictionary.md` §3.2)

## Traceability Chain

```text
BQ → BR → KPI → Source → Entity/Field → DQ → ETL/Logic → SQL View → Dashboard → Decision
```

> **Canonical registry rule:** the "Analytical View" column below may only
> contain view names defined in `04_data_dictionary.md` §3.2. No new view
> names are introduced here. Where a BR needs more than one view, the
> dashboard layer joins them — see the note at the end of §3.2.

| BQ / BR | KPI(s) | Core Source / Entities | Key Logic / DQ | Analytical View | Dashboard |
|---|---|---|---|---|---|
| CEO-BQ1 / BR-CEO-001 | KPI-001 | orders, order_items, refunds, products, customers | DQ-005; exclude cancelled, deduct valid refunds | `vw_revenue_performance` | DB-CEO |
| CEO-BQ2 / BR-CEO-002 | KPI-002 | vw_revenue_performance, dim_date | comparable periods | `vw_revenue_growth` | DB-CEO |
| CEO-BQ3 / BR-CEO-003 | KPI-003, KPI-004 | order_items, products | COGS + revenue eligibility | `vw_profitability` | DB-CEO |
| CEO-BQ4 / BR-CEO-004 | KPI-002, KPI-003, KPI-004 | vw_revenue_growth, vw_profitability | same filter context; dashboard-layer join | `vw_revenue_growth` + `vw_profitability` | DB-CEO |
| CEO-BQ5 / BR-CEO-005 | KPI-001, KPI-002, KPI-003 | orders, countries, order_items | country mapping | `vw_country_performance` | DB-CEO |
| CEO-BQ6 / BR-CEO-006 | KPI-001, KPI-002, KPI-004 | products, categories, order_items | category FK resolution | `vw_category_performance` | DB-CEO |
| CEO-BQ7 / BR-CEO-007 | KPI-015, KPI-008, KPI-011 | customers, orders | completed orders; CLV definition | `vw_customer_value` | DB-CEO |
| CEO-BQ8 / BR-CEO-008 | KPI-002, KPI-004, KPI-015 | vw_revenue_growth, vw_profitability, vw_customer_value | minimum sample threshold; dashboard-layer join | `vw_revenue_growth` + `vw_profitability` + `vw_customer_value` | DB-CEO |
| SALES-BQ1 / BR-SALES-001 | KPI-001, KPI-009 | order_items, products | sales eligibility | `vw_product_sales` | DB-SALES |
| SALES-BQ2 / BR-SALES-002 | KPI-001, KPI-002, KPI-004 | categories, products, order_items | category aggregation | `vw_category_performance` | DB-SALES |
| SALES-BQ3 / BR-SALES-003 | KPI-001, KPI-010, KPI-008 | orders, order_items, dim_date | completed eligible orders | `vw_revenue_performance` | DB-SALES |
| SALES-BQ4 / BR-SALES-004 | KPI-003, KPI-004 | order_items, products | unit_cogs | `vw_product_profitability` | DB-SALES |
| SALES-BQ5 / BR-SALES-005 | KPI-001, KPI-002, KPI-008 | orders, countries | geography mapping | `vw_country_performance` | DB-SALES |
| SALES-BQ6 / BR-SALES-006 | KPI-001, KPI-008, KPI-011 | customers, orders | customer segment snapshot | `vw_customer_value` | DB-SALES |
| SALES-BQ7 / BR-SALES-007 | KPI-032, KPI-008, KPI-004 | promotions, orders, order_items | four-week baseline; DQ-021, DQ-022 | `vw_promotion_performance` | DB-SALES |
| MKT-BQ1 / BR-MKT-001 | KPI-016, KPI-018, KPI-019, KPI-020, KPI-021 | marketing_spend, marketing_events, marketing_attribution | last-touch 30d; session conversion | `vw_marketing_performance` | DB-MKT |
| MKT-BQ2 / BR-MKT-002 | KPI-016 | marketing_spend, marketing_attribution, orders | first purchase + attribution | `vw_marketing_performance` | DB-MKT |
| MKT-BQ3 / BR-MKT-003 | KPI-018 | marketing_spend, marketing_attribution, orders | attributed Net Revenue | `vw_marketing_performance` | DB-MKT |
| MKT-BQ4 / BR-MKT-004 | KPI-019, KPI-021, KPI-022 | marketing_events | unique sessions; DQ-013, DQ-014 | `vw_funnel_performance` | DB-MKT |
| MKT-BQ5 / BR-MKT-005 | KPI-015, KPI-016, KPI-021, KPI-013 | customers, orders, marketing_attribution, customer_cohorts | derived RFM quintile logic | `vw_customer_rfm` | DB-MKT |
| MKT-BQ6 / BR-MKT-006 | KPI-017 | vw_customer_value, vw_marketing_performance | cohort/channel grain; dashboard-layer join | `vw_customer_value` + `vw_marketing_performance` | DB-MKT |
| MKT-BQ7 / BR-MKT-007 | KPI-013, KPI-014, KPI-012 | customers, orders, customer_cohorts | first purchase cohort; Churn = 100 − Retention | `vw_customer_retention` | DB-MKT |
| OPS-BQ1 / BR-OPS-001 | KPI-023, KPI-024 | shipments, orders, warehouses | fulfillment definition | `vw_fulfillment_performance` | DB-OPS |
| OPS-BQ2 / BR-OPS-002 | KPI-025, KPI-026 | shipments, carriers | expected date at ship time; DQ-018 | `vw_delivery_performance` | DB-OPS |
| OPS-BQ3 / BR-OPS-003 | KPI-027 | returns, order_items, shipments | delivered denominator | `vw_return_performance` | DB-OPS |
| OPS-BQ4 / BR-OPS-004 | KPI-028 | returns, products | eligible return reasons | `vw_return_performance` | DB-OPS |
| OPS-BQ5 / BR-OPS-005 | KPI-029 | orders, order_items | all placed orders denominator | `vw_fulfillment_performance` | DB-OPS |
| OPS-BQ6 / BR-OPS-006 | KPI-025, KPI-027, KPI-030, KPI-029 | shipments, carriers, returns, orders | compatible populations | `vw_carrier_performance` | DB-OPS |
| FIN-BQ1 / BR-FIN-001 | KPI-001, KPI-003, KPI-005, KPI-006, KPI-004, KPI-007 | sales, product, logistics, payment, marketing, finance_costs | no duplicate costs | `vw_profitability` | DB-FIN |
| FIN-BQ2 / BR-FIN-002 | KPI-003, KPI-004 | order_items, products | COGS | `vw_product_profitability` | DB-FIN |
| FIN-BQ3 / BR-FIN-003 | KPI-002, KPI-033 | all eligible cost sources | stable cost scope | `vw_cost_performance` | DB-FIN |
| FIN-BQ4 / BR-FIN-004 | KPI-018, KPI-016, KPI-017, KPI-034 | marketing_spend, marketing_attribution, sales | consistent attribution | `vw_marketing_performance` | DB-FIN |
| FIN-BQ5 / BR-FIN-005 | KPI-008, KPI-031 | orders, order_items, customer segments | aggregate discount | `vw_revenue_performance` | DB-FIN |
| FIN-BQ6 / BR-FIN-006 | KPI-017, KPI-035 | vw_customer_value, CAC, gross margin | gross-profit payback; dashboard-layer join | `vw_customer_value` | DB-FIN |
| FIN-BQ7 / BR-FIN-007 | KPI-031, KPI-001, KPI-004, KPI-009 | order_items, promotions | controlled product/category comparison | `vw_promotion_performance` | DB-FIN |
