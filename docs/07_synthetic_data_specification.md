# NovaMart Synthetic Data Specification
**Document ID:** 07_synthetic_data_specification  
**Version:** 1.0  
**Project:** NovaMart Business Intelligence Platform  
**Purpose:** Define the scope, volumes, distributions, business behavior, and intentional data-quality issues for the synthetic dataset used in the NovaMart BI project.

---

## 1. Objective

The synthetic dataset must simulate realistic e-commerce behavior across multiple European markets. It should support:

- KPI calculation
- SQL analytical views
- customer and product analysis
- marketing attribution and funnel analysis
- logistics and return analysis
- profitability analysis
- Power BI dashboards
- ETL validation and quarantine logic

The data must not be purely random. It should contain intentional business patterns, seasonality, differences between countries/categories/channels, and a small number of invalid raw records for data-quality testing.

---

## 2. Time and Geographic Scope

### Historical period
- 24 months of historical data
- Exact dates will be generated relative to the chosen dataset end date
- Daily transaction activity
- Monthly and seasonal patterns included

### Currency
- EUR only for Phase 1

### Countries
The Phase 1 dataset will include 8 European countries:

| Country | Approx. Order Share | Intended Pattern |
|---|---:|---|
| Germany | 25% | Highest volume, stable growth |
| France | 18% | High revenue, slightly lower margin |
| Italy | 14% | Higher promotion sensitivity |
| Spain | 13% | Stronger growth trend |
| Netherlands | 10% | Higher average order value |
| Poland | 9% | Lower AOV, faster growth |
| Belgium | 6% | Smaller, stable market |
| Austria | 5% | Smaller market, relatively high margin |

These patterns are synthetic assumptions for analytical purposes and are not claims about real markets.

---

## 3. Target Dataset Size

| Table | Target Rows |
|---|---:|
| countries | 8 |
| categories | 12 |
| products | 400 |
| customers | 10,000 |
| promotions | 40 |
| warehouses | 12 |
| carriers | 6 |
| channels | 6 |
| campaigns | 45 |
| orders | 60,000 |
| order_items | ~140,000 |
| payments | ~60,000–63,000 |
| refunds | ~5,000 |
| shipments | ~55,000 |
| returns | ~7,000 |
| marketing_events | ~450,000 |
| marketing_spend | ~15,000 |
| finance_costs | ~1,500 |
| marketing_attribution | ETL-derived |
| customer_cohorts | ETL-derived |
| dim_date | ETL-derived |
| quarantine | Depends on DQ failures |

Row counts may vary slightly because child-table volumes depend on generated business behavior.

---

## 4. Reference Data

### 4.1 Product Categories

The dataset will contain 12 categories:

1. Electronics
2. Home & Kitchen
3. Beauty
4. Fashion
5. Sports
6. Books
7. Toys
8. Office
9. Pet Supplies
10. Automotive Accessories
11. Garden
12. Personal Care

> **Taxonomy note (locked):** `Beauty` and `Personal Care` are kept as
> separate categories with a deliberate boundary: `Beauty` = makeup,
> cosmetics, skincare-oriented products; `Personal Care` = hygiene,
> grooming, and body-care essentials. Product assignment during generation
> must follow this split consistently to avoid ambiguous overlap.

### 4.2 Marketing Channels

The dataset will contain 6 channels:

1. Paid Search
2. Paid Social
3. Email
4. Organic Search
5. Affiliate
6. Direct

### 4.3 Carriers

Six synthetic carriers will be created. Carrier names will be fictional.

Intended carrier behavior:

| Carrier Profile | Pattern |
|---|---|
| Carrier A | Fastest, higher shipping cost |
| Carrier B | Lower cost, slightly weaker on-time performance |
| Carrier C | Strong performance in Germany and Netherlands |
| Carrier D | Higher delay rate in Spain and Italy |
| Carrier E | Balanced mid-range performance |
| Carrier F | Smaller-volume backup carrier |

### 4.4 Warehouses

- 12 warehouses
- Distributed across the 8 countries
- Higher-volume markets may have more than one warehouse
- Warehouse assignment should prefer geographically appropriate markets while still allowing cross-border fulfillment

---

## 5. Customer Generation Rules

### Volume
- 10,000 customers

### Customer purchase-frequency distribution

| Segment | Approx. Share | Behavior |
|---|---:|---|
| One-time | 20–25% | 1 purchase |
| Occasional | 45–50% | 2–5 purchases |
| Frequent | ~20% | 6–10 purchases |
| Loyal | 5–10% | More than 10 purchases |

### Additional rules
- Signup dates span the full 24-month period
- Customer country must reference `countries`
- Customer acquisition should vary by channel and month
- Some older customers should become inactive
- Newer cohorts should have shorter observable lifetimes
- Repeat purchase timing should be uneven rather than perfectly periodic

### Demographic distributions (locked, synthetic assumptions — not market claims)

**Age group** (`age_group` field), uneven weights:

| Age Group | Approx. Share |
|---|---:|
| 18–24 | 12% |
| 25–34 | 28% |
| 35–44 | 26% |
| 45–54 | 18% |
| 55–64 | 11% |
| 65+ | 5% |

**Gender** (`gender` field): approximately balanced — 48% female, 48% male,
4% unspecified/other.

The resulting population must support:
- Repeat Customer Rate
- Purchase Frequency
- Customer Lifetime Value
- Churn Rate
- RFM segmentation
- Retention/cohort analysis

---

## 6. Product Generation Rules

### Volume
- 400 products across 12 categories

### Distribution
- Product count should be uneven across categories
- A minority of products should generate a disproportionate share of revenue
- Approximate Pareto-like behavior is desired: roughly 20% of products may generate a large share of sales

### Pricing
Each product must have values consistent with:
- `original_unit_price`
- selling `unit_price`
- `unit_cogs`

### Margin behavior
Margins should vary by category.

Examples of intended analytical patterns:
- Electronics: higher revenue, lower percentage margin
- Beauty: lower revenue volume than Electronics but higher percentage margin
- Fashion: strong sales but elevated return rate
- Books: lower return rate and moderate basket value

All monetary values must be non-negative and expressed in EUR.

---

## 7. Order Generation Rules

### Volume
- Approximately 60,000 orders

### Period
- Distributed over 24 months

### Seasonality
Order generation should include:
- stronger November–December demand
- Black Friday / holiday spikes
- lower demand after the holiday period
- moderate seasonal variation during summer
- gradual market-specific growth trends

### Order status behavior
Approximate final distribution:
- 88–92% delivered
- 3–5% cancelled
- remaining share in valid non-final states such as placed, paid, fulfilled, or shipped near the dataset cutoff

### Currency
- All clean orders must use `EUR`

### Cancellation behavior
- Cancelled orders should have an appropriate cancellation reason
- Non-cancelled orders should not contain contradictory cancellation data

---

## 8. Order Item Rules

### Volume
- Approximately 140,000 rows

### Basket size
- Average order should contain roughly 2–3 line items
- Most line quantities: 1–3
- Small minority: 4 or more

### Commercial logic
- Product must exist
- Quantity must be positive
- Selling price must be non-negative
- Discounts must never produce a negative final merchandise value
- Promotions may affect selling price where appropriate

The generated data should support:
- revenue analysis
- basket-size analysis
- product/category ranking
- gross margin analysis
- promotion analysis

---

## 9. Promotion Rules

### Volume
- 40 promotions

### Promotion types
- Seasonal
- Flash sale
- Clearance
- Loyalty
- Category-specific

### Behavior
Promotions must have varied performance:
- some create strong revenue uplift
- some have little effect
- some increase revenue but reduce margin
- some work better in specific countries/categories
- not every customer/order should use a promotion

Promotion dates must be logically valid in the clean layer.

---

## 10. Payment Rules

### Volume
- Approximately one successful payment per completed order
- A small number of retry attempts may create additional rows

### Payment outcomes
Include:
- successful
- failed
- pending where appropriate

### Payment fees
- Fees should vary slightly by payment method
- Fees must be non-negative

Payment generation must preserve order-level consistency.

---

## 11. Shipment Rules

### Volume
- Approximately 55,000 shipments

### Canonical delivery field
- `actual_delivery_timestamp`

### Logic
Valid clean shipments must follow chronological order:
- shipment/dispatch timestamp
- estimated delivery timestamp where applicable
- `actual_delivery_timestamp`

Actual delivery must not precede shipment.

### Performance variation
Carrier and country combinations should produce differences in:
- delivery time
- on-time delivery rate
- shipping cost

This data must support:
- fulfillment analysis
- delivery-performance analysis
- carrier-performance analysis
- shipping-cost analysis

---

## 12. Return Rules

### Volume
- Approximately 7,000 return records

### Overall behavior
Target return behavior should be approximately 8–12% of eligible delivered orders, with category variation.

### Category patterns
- Fashion: relatively high return rate
- Electronics: moderate returns, more defect-related
- Books: low return rate
- Other categories: varied intermediate behavior

### Return reasons
Examples:
- defective
- wrong_item
- changed_mind
- damaged
- size_issue
- late_delivery
- other

Return quantities must be positive and must not exceed the eligible purchased quantity in the clean dataset.

---

## 13. Refund Rules

### Volume
- Approximately 5,000 refunds

### Types
- full refund
- partial refund

Refunds may be linked to:
- an order
- a payment
- a return where relevant

Refund amounts must be logically consistent and non-negative in the clean layer.

---

## 14. Marketing Campaign Rules

### Volume
- 45 campaigns

### Campaign characteristics
Campaigns should vary by:
- channel
- target country
- date range
- spend level
- click-through behavior
- conversion efficiency
- customer quality

Not all campaigns should be successful.

### Campaign archetypes (locked distribution across 45 campaigns)

| Archetype | Share | Count | Behavior |
|---|---:|---:|---|
| High Traffic / Weak Conversion | 20% | 9 | Strong impressions/clicks, low purchase conversion |
| High CAC / Strong Revenue | 20% | 9 | Expensive per acquisition, but high per-order revenue |
| Efficient / High ROAS | 25% | 11 | Best-performing archetype — low CAC, strong ROAS |
| Low-cost / Strong Customer Value | 20% | 9 | Cheap acquisition, high downstream CLV |
| Average / Mixed Performance | 15% | 7 | No strong signal either way — realistic "noise" campaigns |

Every campaign is assigned exactly one archetype at generation time, which
then drives its spend level, CTR, conversion efficiency, and the CLV of the
customers it acquires. This is what makes campaign-level analysis (MKT-BQ3)
meaningful rather than uniformly random.

---

## 15. Marketing Event Rules

### Volume
- Approximately 450,000 events

### Controlled event vocabulary
Events should use the project-defined controlled vocabulary, including stages such as:

- session_start
- product_view
- add_to_cart
- checkout_started
- purchase

### Funnel behavior (locked: previous-stage-based, matching KPI-022's formula exactly)

Each stage's probability is defined **relative to the immediately preceding
stage** — never relative to total sessions — so it matches
`02_kpi_dictionary.md` KPI-022 (`Stage N Events / Stage N-1 Events × 100`)
exactly with no reinterpretation needed downstream:

```text
session_start
   ↓
product_view       ~75% of session_start
   ↓
add_to_cart        ~35% of product_view
   ↓
checkout_started   ~50% of add_to_cart
   ↓
purchase           ~65% of checkout_started
```

Compounding these gives an approximate overall session→purchase rate of
~75% × 35% × 50% × 65% ≈ **8.5%**, consistent with the general "8–10% of
relevant sessions" scale mentioned in earlier drafts of this spec, but now
fully unambiguous about which base each percentage is measured against.

These percentages are synthetic configuration targets, not real-world benchmarks.

### Important rule
Funnel KPIs must later be calculated using the documented unique-session logic rather than blindly counting raw events.

---

## 16. Marketing Spend Rules

### Volume
- Approximately 15,000 rows

### Grain
Spend should be generated by an appropriate combination of:
- date
- campaign
- channel
- country

### Rules
- spend must be non-negative
- impressions must be non-negative
- clicks must be non-negative
- valid clean rows must satisfy `clicks <= impressions`

Different channels should have different cost and performance profiles.

---

## 17. Marketing Attribution

`marketing_attribution` is not treated as raw source data.

It will be created during ETL using the documented attribution rule:

> Last eligible marketing touchpoint within 30 days before purchase.

The derived table should connect:
- order
- customer
- campaign
- channel

This enables:
- CAC
- ROAS
- channel performance
- campaign performance
- acquisition analysis

---

## 18. Finance Cost Rules

### Volume
- Approximately 1,500 rows

### Cost categories
Examples:
- payroll
- software
- rent
- infrastructure
- professional services
- other

### Double-counting prevention
The finance-cost source must not duplicate cost components already represented elsewhere, including:
- shipping cost
- payment fees
- return-related cost
- marketing spend

This separation is required for consistent Net Profit calculation.

---

## 19. Derived Tables

The following tables will be created through ETL/analytical processing rather than generated as independent raw business sources:

### `marketing_attribution`
Derived from marketing touchpoints and purchases.

### `customer_cohorts`
Derived from customer acquisition / first-purchase timing.

### `dim_date`
Generated from the 24-month calendar range and may include additional dates required by the dataset boundaries.

### `quarantine`
Populated only when raw records fail documented data-quality rules.

---

## 20. Intentional Data-Quality Problems

The raw synthetic source files should contain a controlled number of invalid records so the ETL and quarantine process can be demonstrated.

### Target
Approximately 0.5–1.5% of applicable raw records may contain intentional DQ defects.

### Example defects
- negative order-item quantity
- unknown product reference
- invalid/non-EUR currency
- delivery timestamp before shipment
- clicks greater than impressions
- invalid return date
- duplicate source record
- missing required session identifier
- invalid promotion date range
- missing required identifiers
- invalid controlled-vocabulary event values where useful for testing

### Important architecture rule
Invalid source rows must not be repaired by mutating the raw source.

ETL should:
1. ingest raw data
2. validate against DQ rules
3. load valid records to the clean layer
4. send failed records to `quarantine`
5. preserve enough raw payload/context to understand the failure

---

## 21. Reproducibility

The Python generator must use a fixed random seed.

Requirements:
- same seed → reproducible dataset
- configuration values should be centralized where practical
- row volumes and probabilities should be easy to change
- generated foreign keys must remain internally consistent except for intentionally corrupted raw records

---

## 22. Generation Order

To preserve referential integrity, synthetic data should be generated in dependency order.

Recommended sequence:

1. countries
2. categories
3. channels
4. warehouses
5. carriers
6. products
7. customers
8. promotions
9. campaigns
10. orders
11. order_items
12. payments
13. shipments
14. returns
15. refunds
16. marketing_events
17. marketing_spend
18. finance_costs

Derived later through ETL:
19. marketing_attribution
20. customer_cohorts
21. dim_date
22. quarantine

---

## 23. Acceptance Criteria

The synthetic dataset is acceptable when:

- all 8 countries are represented
- all clean monetary values use EUR
- 24 months of data are covered
- major tables are close to their target volumes
- foreign-key relationships are valid in the clean layer
- business patterns differ meaningfully across countries, categories, channels, and carriers
- seasonality is visible
- both one-time and repeat customers exist
- promotion effects are varied
- return rates vary by category
- carrier performance varies
- marketing funnel drop-off is visible
- profitability analysis is possible
- intentional invalid raw rows are detectable by ETL
- invalid rows can be routed to quarantine
- generator output is reproducible using a fixed seed

---

## 24. Implementation Principle

The generator should be implemented incrementally rather than as one large script.

**Corrected versions (dependency-order fix — locked):** the original v0.1/v0.2
ordering below was backwards: `orders`/`order_items` depend on `customers`
and `products` already existing, so reference data must be generated first.

- **v0.1** – Reference Data + Customers + Products (`countries`, `categories`,
  `channels`, `warehouses`, `carriers`, `products`, `customers`,
  `promotions`, `campaigns`)
- **v0.2** – Orders + Order Items
- **v0.3** – Payments + Refunds
- **v0.4** – Shipments + Returns
- **v0.5** – Marketing Events + Spend
- **v0.6** – Finance Costs + intentional DQ defects
- **v1.0** – Fully integrated reproducible dataset + derived tables

Each version should be validated before moving to the next one.

---

## 25. Final Data Flow

```text
Synthetic Source Data
        ↓
Raw Layer
        ↓
Python ETL Validation
      ↙   ↘
 Clean   Quarantine
   ↓
Derived / Analytical Structures
   ↓
SQL Analytical Views
   ↓
Power BI Dashboards
```

This specification becomes the source of truth for NovaMart synthetic-data generation.
