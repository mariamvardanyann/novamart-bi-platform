# KPI Dictionary
## NovaMart Business Intelligence Platform — Phase 1.2b

**Version:** v1.1 | **Status:** Implementation Ready  
**Related:** `00_project_charter.md`, `01_brd.md`, `03_data_quality.md`, `04_data_dictionary.md`

## Purpose

This document is the **single source of truth** for every KPI used in the NovaMart BI Platform. Each KPI is defined exactly once with a stable ID. The BRD references KPI IDs and does not redefine formulas.

## Governing Definitions

### Revenue

Unless stated otherwise, **Revenue means Net Revenue**.

```text
Net Revenue =
Σ(quantity × unit_price − line_discount)
for eligible non-cancelled order lines
− eligible refunds
```

Rules:

- Cancelled orders remain in raw data but do not contribute to Net Revenue.
- Refunds are deducted according to validated refund transactions.
- `original_unit_price` = list/pre-discount price.
- `unit_price` = post-markdown selling price before any additional line discount.
- `line_discount` = additional order-line discount.
- Final merchandise value per line before refund treatment is `quantity × unit_price − line_discount`.
- A line discount must never create a negative final merchandise value.

### Profit

NovaMart uses three profit tiers. A requirement that says only **Profit** means **Gross Profit** unless explicitly qualified.

| Tier | Formula | Use |
|---|---|---|
| Gross Profit | `Net Revenue − COGS` | Default profitability measure |
| Contribution Profit | `Gross Profit − Shipping Cost − Payment Fees − Return Cost` | Operational contribution analysis |
| Net Profit | `Contribution Profit − Marketing Cost − Operating Cost − Other Expenses` | Finance analysis when cost data exists at compatible grain |

`Finance/Cost` must not duplicate shipping, payment, return, or marketing costs already represented in their source systems.

### Simplified Historical CLV

```text
Simplified Historical CLV =
AOV × Purchase Frequency × Average Customer Lifespan
```

**Average Customer Lifespan** is measured in months as the average observed tenure from a customer's first completed purchase to their last observed completed purchase over the eligible historical customer population.

This is a historical descriptive KPI, not a predictive CLV model.

### Retention vs Repeat Purchase

- **Repeat Customer Rate**: all-time share of customers with at least two completed orders.
- **Retention Rate**: cohort-based share of customers acquired in period N who are active again in period N+1.

They are never treated as synonyms.

### Marketing Attribution

Phase 1 uses **last-touch attribution with a 30-day lookback window**.

An order is attributed to the latest eligible tracked marketing touchpoint before purchase within 30 days. Attribution is created in the ETL/analytical layer, not stored as a pre-derived field in raw marketing events.

### New Customer for CAC

A **new customer** is a customer whose first completed purchase occurs in the reporting period. For channel/campaign CAC, that customer is assigned to the last-touch channel/campaign preceding the first purchase within the attribution window.

### Funnel Counting

Funnel stage rates use **unique eligible sessions reaching each stage**, not raw event counts.

### Promotion Baseline

The promotion baseline is the average Net Revenue for the same product/category during the **four complete calendar weeks immediately preceding the promotion start date**, evaluated at the selected reporting grain.

### RFM Definitions

RFM is a derived segmentation method:

- **Recency** = days since last completed purchase.
- **Frequency** = number of completed orders.
- **Monetary** = cumulative Net Revenue.
- R, F, and M are each scored from 1–5 using portfolio-defined quintile rules.
- `RFM Score = R + F + M`.
- Example labels: Champions, Loyal Customers, Potential Loyalists, At Risk, Lost.

RFM is not a raw-source entity.

### Currency

All Phase 1 synthetic monetary values and KPI outputs are reported in **EUR**. FX conversion is out of scope.

## Targets

No KPI carries a business-approved target unless explicitly marked. Status values:

- `TBD` — stakeholder target not yet defined.
- `Illustrative` — portfolio/demo reference only.
- `SLA-based` — based on an operational service-level assumption still requiring stakeholder confirmation.
- `—` — descriptive KPI with no target.

---

## Master KPI Table

| ID | KPI Name | Formula | Unit | Frequency | Benchmark/Status | Primary Data Source | Used By |
|---|---|---|---|---|---|---|---|
| KPI-001 | Net Revenue | See Revenue definition | EUR | Daily/Monthly | — | Sales + Payment | CEO, Sales, Finance |
| KPI-002 | Revenue Growth % | `(Current Net Revenue − Previous Net Revenue) / Previous Net Revenue × 100` | % | Monthly/Quarterly/Yearly | TBD | Derived from Sales + Payment | CEO, Sales, Finance |
| KPI-003 | Gross Profit | `Net Revenue − COGS` | EUR | Monthly | — | Sales + Product | CEO, Sales, Finance |
| KPI-004 | Gross Margin % | `Gross Profit / Net Revenue × 100` | % | Monthly | Illustrative | Derived | CEO, Sales, Finance |
| KPI-005 | Contribution Profit | `Gross Profit − Shipping Cost − Payment Fees − Return Cost` | EUR | Monthly | — | Sales + Logistics + Payment | Finance, Operations |
| KPI-006 | Net Profit | `Contribution Profit − Marketing Cost − Operating Cost − Other Expenses` | EUR | Monthly | Positive | Sales + Product + Logistics + Payment + Marketing + Finance/Cost | Finance |
| KPI-007 | Net Profit Margin % | `Net Profit / Net Revenue × 100` | % | Monthly | Illustrative | Derived | Finance |
| KPI-008 | Average Order Value (AOV) | `Net Revenue / Completed Eligible Orders` | EUR/order | Monthly | — | Sales + Payment | CEO, Sales, Marketing, Finance |
| KPI-009 | Units Sold | `SUM(quantity)` over eligible completed non-cancelled order lines | units | Daily/Monthly | — | Sales | Sales |
| KPI-010 | Orders | `COUNT(DISTINCT order_id)` for eligible completed orders unless a requirement explicitly requests all order statuses | count | Monthly | — | Sales | Sales, Operations, Finance |
| KPI-011 | Purchase Frequency | `Completed Orders / Distinct Purchasing Customers` | orders/customer | Monthly | — | Sales + Customer | Sales, Marketing, Finance |
| KPI-012 | Repeat Customer Rate % | `Customers with ≥2 completed orders / Customers with ≥1 completed order × 100` | % | Monthly | TBD | Sales + Customer | Marketing, CEO |
| KPI-013 | Retention Rate % | `Cohort customers active in N+1 / Cohort customers acquired in N × 100` | % | Monthly/cohort | TBD | Sales + Customer | Marketing, Finance |
| KPI-014 | Churn Rate % | `100 − Retention Rate %` on same cohort basis | % | Monthly/cohort | TBD | Derived | Marketing |
| KPI-015 | Simplified Historical CLV | See CLV definition | EUR | Quarterly | — | Sales + Customer | CEO, Marketing, Finance |
| KPI-016 | Customer Acquisition Cost (CAC) | `Marketing Spend / Attributed New Customers` | EUR/customer | Monthly | TBD | Marketing + Sales + Attribution | Marketing, Finance |
| KPI-017 | CLV / CAC Ratio | `Simplified Historical CLV / CAC` | ratio (x) | Quarterly | Illustrative | Derived | Marketing, Finance |
| KPI-018 | ROAS | `Attributed Net Revenue / Ad Spend` | ratio (x) | Monthly | Illustrative | Marketing + Attribution + Sales | Marketing, Finance |
| KPI-019 | CTR | `Clicks / Impressions × 100` | % | Monthly | Illustrative | Marketing | Marketing |
| KPI-020 | CPC | `Ad Spend / Clicks` | EUR/click | Monthly | — | Marketing | Marketing |
| KPI-021 | Conversion Rate % | `Unique Sessions with Completed Purchase / Eligible Sessions × 100` | % | Monthly | Illustrative | Marketing Events + Sales | Marketing |
| KPI-022 | Funnel Stage Rate % | `Unique Sessions Reaching Stage N / Unique Sessions Reaching Stage N−1 × 100` | % | Monthly | TBD | Marketing Events | Marketing |
| KPI-023 | Fulfillment Rate % | `Fulfilled Eligible Orders / Eligible Non-Cancelled Orders × 100` | % | Daily/Monthly | SLA-based | Logistics + Sales | Operations |
| KPI-024 | Fulfillment Time | `AVG(fulfillment_timestamp − order_timestamp)` for fulfilled eligible orders | hours | Monthly | SLA-based | Logistics + Sales | Operations |
| KPI-025 | On-Time Delivery Rate % | `Delivered Orders with actual_delivery_timestamp ≤ expected_delivery_date / Eligible Delivered Orders × 100` | % | Monthly | SLA-based | Logistics | Operations |
| KPI-026 | Average / Median Delivery Time | `AVG` and `MEDIAN(actual_delivery_timestamp − shipping_timestamp)` | days | Monthly | SLA-based | Logistics | Operations |
| KPI-027 | Return Rate % | `Returned Delivered Orders / Eligible Delivered Orders × 100` | % | Monthly | TBD | Logistics + Sales | Operations, Finance |
| KPI-028 | Return Reason % / Defect Rate % | `Eligible Returns for reason (or defective) / Total Eligible Returns × 100` | % | Monthly | — | Logistics | Operations |
| KPI-029 | Cancellation Rate % | `Cancelled Orders / All Placed Orders × 100` | % | Monthly | TBD | Sales | Operations, Finance |
| KPI-030 | Shipping Cost | `SUM(shipping_cost)` | EUR | Monthly | — | Logistics | Operations, Finance |
| KPI-031 | Discount % | `Total Discount Amount / Total Original Merchandise Value × 100` | % | Monthly | — | Sales | Sales, Finance |
| KPI-032 | Promotion Uplift % | `(Promo Net Revenue − Baseline Net Revenue) / Baseline Net Revenue × 100` | % | Per campaign | Illustrative | Sales | Sales |
| KPI-033 | Cost-to-Revenue Ratio % | `Total Eligible Costs / Net Revenue × 100` | % | Monthly | — | Derived from Logistics + Payment + Marketing + Finance/Cost | Finance |
| KPI-034 | Marketing ROI % | `(Attributed Net Revenue − Ad Spend) / Ad Spend × 100` | % | Monthly | Illustrative | Marketing + Attribution + Sales | Finance |
| KPI-035 | Gross Profit Payback Period | `CAC / (AOV × Monthly Purchase Frequency × Gross Margin decimal)` | months | Quarterly | TBD | Derived | Finance |

### KPI-027 Product/Category Interpretation

For product/category analysis, Return Rate represents the percentage of eligible delivered orders containing at least one returned item from the selected product/category. Item-level return rates may be exposed as supplementary diagnostics but must be named explicitly to avoid mixing grains.

### KPI-023 Fulfilled Order Definition

A fulfilled order is an eligible non-cancelled order with `fulfillment_timestamp` populated.

### KPI-025 Eligible Delivered Order

An eligible delivered order has a valid `actual_delivery_timestamp` and the `expected_delivery_date` captured at ship time.

### KPI-030 Supplementary Metric

`Average Shipping Cost per Fulfilled Order = Total Shipping Cost / Fulfilled Orders` may be displayed as a supporting metric but is not a separate KPI ID.

### KPI Reuse

A KPI's formula never changes across stakeholders. What changes is its dimensional slice, filters, and decision context.

## Future Enhancement

- Perfect Order Rate.
- Multi-touch attribution.
- Predictive/cohort-survival CLV.
- Multi-currency reporting and FX normalization.
