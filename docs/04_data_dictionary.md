# Data Dictionary & Grain Register
## NovaMart Business Intelligence Platform — Phase 1.2d

**Version:** v1.1 | **Status:** Ready for ERD Design  
**Related:** `00_project_charter.md`, `01_brd.md`, `02_kpi_dictionary.md`, `03_data_quality.md`

## 1. Source and Entity Grain Register

| Source | Entity / Dataset | Grain | Primary Key | Main Integration Keys |
|---|---|---|---|---|
| Sales | `orders` | 1 row = 1 order | `order_id` | `customer_id`, `country_id`, `promotion_id` |
| Sales | `order_items` | 1 row = 1 product line in an order | `order_line_id` | `order_id`, `product_id` |
| Sales | `promotions` | 1 row = 1 promotion | `promotion_id` | — |
| Customer | `customers` | 1 row = 1 customer | `customer_id` | `country_id` |
| Product | `products` | 1 row = 1 product | `product_id` | `category_id` |
| Product | `categories` | 1 row = 1 category | `category_id` | — |
| Reference | `countries` | 1 row = 1 country | `country_id` | — |
| Payment | `payments` | 1 row = 1 payment transaction | `payment_id` | `order_id` |
| Payment | `refunds` | 1 row = 1 refund transaction | `refund_id` | `order_id`, optional `payment_id`, optional `return_id` |
| Logistics | `shipments` | 1 row = 1 shipment | `shipment_id` | `order_id`, `warehouse_id`, `carrier_id` |
| Logistics | `warehouses` | 1 row = 1 warehouse | `warehouse_id` | `country_id` |
| Logistics | `carriers` | 1 row = 1 carrier | `carrier_id` | — |
| Logistics | `returns` | 1 row = 1 returned order line / return transaction | `return_id` | `order_id`, `order_line_id`, `shipment_id` |
| Marketing | `channels` | 1 row = 1 channel | `channel_id` | — |
| Marketing | `campaigns` | 1 row = 1 campaign | `campaign_id` | `channel_id` |
| Marketing | `marketing_events` | 1 row = 1 tracked session event | `event_id` | `session_id`, nullable `customer_id`, `campaign_id`, `channel_id` |
| Marketing | `marketing_spend` | 1 row = campaign × channel × date × country | composite / surrogate `spend_id` | `campaign_id`, `channel_id`, `country_id` |
| Finance/Cost | `finance_costs` | 1 row = 1 operating/other cost transaction | `cost_id` | optional `country_id` |

## 2. Core Fields

### `orders`

| Field | Type Intent | Notes |
|---|---|---|
| `order_id` | BIGINT / VARCHAR | PK |
| `customer_id` | FK nullable only for controlled guest orders | Customer link |
| `order_timestamp` | DATETIME | Placement time |
| `status` | ENUM/reference | placed, paid, fulfilled, shipped, delivered, cancelled, etc. |
| `cancellation_reason` | VARCHAR nullable | Required for cancellation breakdown when cancelled |
| `country_id` | FK | Commercial/order country |
| `promotion_id` | FK nullable | Order-level promotion where applicable |
| `currency_code` | CHAR(3) | `EUR` in Phase 1 |

### `order_items`

| Field | Type Intent | Notes |
|---|---|---|
| `order_line_id` | BIGINT | PK |
| `order_id` | FK | Parent order |
| `product_id` | FK | Product |
| `quantity` | INT | > 0 |
| `original_unit_price` | DECIMAL | Pre-discount/list price |
| `unit_price` | DECIMAL | Post-markdown, pre-line-discount |
| `line_discount` | DECIMAL | Additional line-level discount |
| `unit_cogs` | DECIMAL | Cost per unit for gross profit |

### `promotions`

`promotion_id`, `promotion_name`, `promotion_type`, `discount_type`, `discount_amount`, `promotion_start_date`, `promotion_end_date`.

### `customers`

`customer_id`, `signup_date`, `country_id`, optional demographic/segment-safe synthetic attributes. First purchase is preferably derived from orders rather than trusted as a raw authoritative field.

### `products`

`product_id`, `product_name`, `category_id`, `brand`, `active_flag`.

### `payments`

`payment_id`, `order_id`, `payment_timestamp`, `payment_status`, `payment_method`, `payment_amount`, `payment_fee`, `currency_code`.

### `refunds`

`refund_id`, `order_id`, optional `payment_id`, optional `return_id`, `refund_timestamp`, `refund_amount`, `refund_reason`, `currency_code`.

### `shipments`

`shipment_id`, `order_id`, `warehouse_id`, `carrier_id`, `fulfillment_timestamp`, `shipping_timestamp`, `expected_delivery_date`, `actual_delivery_timestamp`, `shipping_cost`, `shipment_status`.

### `returns`

`return_id`, `order_id`, `order_line_id`, optional `shipment_id`, `return_timestamp`, `return_reason`, `returned_quantity`, `defect_flag`, `return_cost`, `return_status`.

### `marketing_events`

`event_id`, `session_id`, nullable `customer_id`, nullable `campaign_id`, `channel_id`, `event_timestamp`, `event_type`, `country_id`, `device`.

Controlled event vocabulary should support at least: `impression`, `click`, `session_start`, `product_view`, `add_to_cart`, `checkout_started`, `purchase`.

### `marketing_spend`

`spend_id`, `date`, `campaign_id`, `channel_id`, `country_id`, `ad_spend`, `impressions`, `clicks`, `currency_code`.

### `finance_costs`

`cost_id`, `cost_date`, `cost_type`, `cost_category`, `amount`, `currency_code`, optional `country_id`, `description`.

Phase 1 Finance/Cost is for operating and other expenses not already represented in Logistics, Payment, Returns, or Marketing.

## 3. Derived Analytical Structures & Canonical View Catalog

> **Canonical registry rule:** this section is the **single authoritative
> list** of analytical view names. `05_traceability_matrix.md` and
> `06_dashboard_requirements.md` may only reference views defined here — they
> do not introduce new view names. This prevents the same analytical need
> from silently spawning duplicate views under different names.

### 3.1 Foundational Derived Structures

These are **not raw source tables** and are **not queried directly by
dashboards**. They exist to feed the canonical views below with pre-computed,
reusable logic (attribution, cohorting, calendar).

| Structure | Purpose |
|---|---|
| `marketing_attribution` | Last-touch, 30-day order/channel/campaign attribution (feeds marketing & funnel views) |
| `customer_cohorts` | Acquisition month and retained-activity flags (feeds retention & value views) |
| `dim_date` | Calendar/date dimension (feeds all trended views) |

### 3.2 Canonical Analytical View Catalog (18 views)

These are the **only** views dashboards query against. Each view is reusable
across multiple Business Requirements — a view is not "owned" by one
stakeholder.

| View | Purpose | Used By (BR) |
|---|---|---|
| `vw_revenue_performance` | Net Revenue, trended, sliceable by all core dimensions | BR-CEO-001, BR-SALES-003, BR-FIN-005 |
| `vw_revenue_growth` | MoM/QoQ/YoY Revenue Growth % | BR-CEO-002, BR-CEO-004, BR-CEO-008 |
| `vw_product_sales` | Revenue/units ranking by product | BR-SALES-001 |
| `vw_product_profitability` | Gross Profit/Margin by product | BR-SALES-004, BR-FIN-002 |
| `vw_category_performance` | Revenue/growth/margin by category | BR-CEO-006, BR-SALES-002 |
| `vw_country_performance` | Revenue/growth/profit by country | BR-CEO-005, BR-SALES-005 |
| `vw_customer_value` | AOV, purchase frequency, Simplified Historical CLV, by segment | BR-CEO-007, BR-CEO-008, BR-SALES-006, BR-MKT-006, BR-FIN-006 |
| `vw_customer_rfm` | RFM scores and named segments | BR-MKT-005 |
| `vw_customer_retention` | Cohort-based Retention Rate, Churn Rate, Repeat Customer Rate | BR-MKT-007 |
| `vw_marketing_performance` | CAC, ROAS, CTR, CPC, Conversion Rate by channel/campaign | BR-MKT-001, BR-MKT-002, BR-MKT-003, BR-FIN-004 |
| `vw_funnel_performance` | Session-based funnel stage conversion/drop-off | BR-MKT-004 |
| `vw_promotion_performance` | Promotion vs. 4-week baseline uplift | BR-SALES-007, BR-FIN-007 |
| `vw_fulfillment_performance` | Fulfillment Rate/Time, Cancellation Rate | BR-OPS-001, BR-OPS-005 |
| `vw_delivery_performance` | On-Time Delivery Rate, avg/median delivery time | BR-OPS-002 |
| `vw_return_performance` | Return Rate, return reasons, defect rate | BR-OPS-003, BR-OPS-004 |
| `vw_carrier_performance` | Cross-carrier scorecard (delivery, returns, cost, cancellations) | BR-OPS-006 |
| `vw_cost_performance` | Cost Growth %, Cost-to-Revenue Ratio, cost composition | BR-FIN-003 |
| `vw_profitability` | Gross/Contribution/Net Profit and margins | BR-CEO-003, BR-CEO-004, BR-FIN-001 |

> Where a BR appears under more than one view (e.g., BR-CEO-004 needs both
> `vw_revenue_growth` and `vw_profitability`), the dashboard layer joins the
> two — this is a presentation-layer join, not a reason to create a new
> combined view.

## 4. Recommended ERD Relationships

```text
customers 1 ───< orders 1 ───< order_items >─── 1 products >─── 1 categories
                      │
                      ├────< payments
                      ├────< refunds
                      └────< shipments >──── carriers
                               │
                               └──── warehouses

order_items 1 ───< returns

channels 1 ───< campaigns
channels 1 ───< marketing_events
campaigns 1 ───< marketing_events
campaigns 1 ───< marketing_spend

marketing_events ──(ETL attribution)──> marketing_attribution <── orders
```

## 5. Database Design Rules for Sprint 1

- Use surrogate integer PKs where practical, but preserve business/source IDs when useful.
- Add indexes on major FKs and analytical filter columns.
- Avoid storing derived KPI results in raw operational tables.
- Preserve transaction/event grains; do not prematurely aggregate source data.
- Use DECIMAL for money, not FLOAT.
- Use UTC timestamps internally if timezone behavior is modeled; otherwise document one consistent synthetic timezone.
