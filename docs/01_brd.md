# Business Requirements Document (BRD)
## NovaMart Business Intelligence Platform — Phase 1.2

**Version:** v1.1 | **Status:** Approved for Sprint 1 Design  
**Related:** `00_project_charter.md`, `02_kpi_dictionary.md`, `03_data_quality.md`, `04_data_dictionary.md`, `05_traceability_matrix.md`, `06_dashboard_requirements.md`

## Document Purpose

This BRD defines **what the NovaMart BI Platform must do** for five stakeholders.

```text
Business Question → Business Requirement → KPI(s) → Acceptance Criteria → Decision
```

KPI formulas live only in `02_kpi_dictionary.md`.

## Traceability Convention

| Stakeholder | BQ Prefix | Requirement Prefix | Dashboard |
|---|---|---|---|
| CEO | `CEO-BQ#` | `BR-CEO-###` | `DB-CEO` |
| Sales | `SALES-BQ#` | `BR-SALES-###` | `DB-SALES` |
| Marketing | `MKT-BQ#` | `BR-MKT-###` | `DB-MKT` |
| Operations | `OPS-BQ#` | `BR-OPS-###` | `DB-OPS` |
| Finance | `FIN-BQ#` | `BR-FIN-###` | `DB-FIN` |

Full implementation traceability is maintained in `05_traceability_matrix.md`.

## Business Question Register

| BQ ID | Business Question | Stakeholder | Priority | BR |
|---|---|---|---|---|
| CEO-BQ1 | Where is our revenue coming from? | CEO | High | BR-CEO-001 |
| CEO-BQ2 | Are we growing, or is growth slowing? | CEO | High | BR-CEO-002 |
| CEO-BQ3 | Is sales growth turning into profit? | CEO | High | BR-CEO-003 |
| CEO-BQ4 | Where is growth profitable, and where is it not? | CEO | High | BR-CEO-004 |
| CEO-BQ5 | Which markets deserve more investment? | CEO | High | BR-CEO-005 |
| CEO-BQ6 | Which categories are the real drivers of growth? | CEO | High | BR-CEO-006 |
| CEO-BQ7 | Who are our most valuable customers? | CEO | High | BR-CEO-007 |
| CEO-BQ8 | Which internal combinations offer the strongest growth opportunities? | CEO | Medium | BR-CEO-008 |
| SALES-BQ1 | Which products should Sales focus on? | Sales | High | BR-SALES-001 |
| SALES-BQ2 | Which categories should be developed further? | Sales | High | BR-SALES-002 |
| SALES-BQ3 | When do sales rise or fall? | Sales | High | BR-SALES-003 |
| SALES-BQ4 | Which products are truly valuable, not merely high-selling? | Sales | High | BR-SALES-004 |
| SALES-BQ5 | Where should Sales focus geographically? | Sales | Medium | BR-SALES-005 |
| SALES-BQ6 | Which customer groups should Sales prioritize? | Sales | Medium | BR-SALES-006 |
| SALES-BQ7 | Are promotions worth running? | Sales | High | BR-SALES-007 |
| MKT-BQ1 | Which channel should receive more budget? | Marketing | High | BR-MKT-001 |
| MKT-BQ2 | Where is acquisition most cost-efficient? | Marketing | High | BR-MKT-002 |
| MKT-BQ3 | Which campaigns should be scaled or stopped? | Marketing | High | BR-MKT-003 |
| MKT-BQ4 | Where is the funnel leaking? | Marketing | High | BR-MKT-004 |
| MKT-BQ5 | Which strategy fits each customer segment? | Marketing | High | BR-MKT-005 |
| MKT-BQ6 | Which channels bring long-term valuable customers? | Marketing | High | BR-MKT-006 |
| MKT-BQ7 | How do retention and repeat purchase behave? | Marketing | High | BR-MKT-007 |
| OPS-BQ1 | Where are fulfillment bottlenecks? | Operations | High | BR-OPS-001 |
| OPS-BQ2 | Where and with which carrier are delivery problems concentrated? | Operations | High | BR-OPS-002 |
| OPS-BQ3 | Which products require return investigation? | Operations | High | BR-OPS-003 |
| OPS-BQ4 | What product/operational problems drive returns? | Operations | High | BR-OPS-004 |
| OPS-BQ5 | Why are orders cancelled? | Operations | High | BR-OPS-005 |
| OPS-BQ6 | Which carrier contracts should be kept, renegotiated, or dropped? | Operations | High | BR-OPS-006 |
| FIN-BQ1 | Where are we actually generating profit? | Finance | High | BR-FIN-001 |
| FIN-BQ2 | Which products/categories should be grown, repriced, or reconsidered? | Finance | High | BR-FIN-002 |
| FIN-BQ3 | Which costs are hurting profitability? | Finance | High | BR-FIN-003 |
| FIN-BQ4 | Which marketing investments are financially justified? | Finance | High | BR-FIN-004 |
| FIN-BQ5 | What improves revenue per transaction? | Finance | Medium | BR-FIN-005 |
| FIN-BQ6 | Should we continue each acquisition strategy? | Finance | High | BR-FIN-006 |
| FIN-BQ7 | Which discounts are profitable versus margin-destructive? | Finance | High | BR-FIN-007 |

---

## 1. CEO — Executive Business Performance

**Business Goal:** Understand overall business health and achieve sustainable, profitable growth.

| Req ID | BQ | Requirement Statement | Linked KPIs | Decision Enabled |
|---|---|---|---|---|
| BR-CEO-001 | CEO-BQ1 | Report Net Revenue by country, category, product, and customer segment. | KPI-001 | Where is revenue coming from? |
| BR-CEO-002 | CEO-BQ2 | Report Revenue Growth % on MoM, QoQ, and YoY bases. | KPI-002 | Are we growing? |
| BR-CEO-003 | CEO-BQ3 | Report Gross Profit and Gross Margin %, trended over time and by country/category. | KPI-003, KPI-004 | Is growth profitable? |
| BR-CEO-004 | CEO-BQ4 | Compare Revenue Growth % with Gross Profit growth/Gross Margin movement. | KPI-002, KPI-003, KPI-004 | Where is growth profitable? |
| BR-CEO-005 | CEO-BQ5 | Report Net Revenue, Growth %, and Gross Profit by country with contribution to total growth. | KPI-001, KPI-002, KPI-003 | Which markets deserve investment? |
| BR-CEO-006 | CEO-BQ6 | Report Net Revenue, Growth %, and Gross Margin % by product category. | KPI-001, KPI-002, KPI-004 | Which categories drive growth? |
| BR-CEO-007 | CEO-BQ7 | Report Simplified Historical CLV, AOV, and Purchase Frequency by customer segment. | KPI-015, KPI-008, KPI-011 | Who are the most valuable customers? |
| BR-CEO-008 | CEO-BQ8 | Rank country × category × customer-segment combinations by growth, margin, and CLV. | KPI-002, KPI-004, KPI-015 | Which internal opportunities look strongest? |

### BR-CEO-001 — Revenue Reporting
- Uses KPI-001 exactly as defined in the KPI Dictionary.
- Cancelled orders are excluded per DQ-005; validated refunds are deducted.
- Supports month, country, category, product, and customer-segment filters.
- Current and previous comparable periods are visible.
- Totals reconcile to the underlying eligible order/payment data.
### BR-CEO-002 — Growth Reporting
- MoM, QoQ, and YoY use comparable complete periods.
- A zero/absent prior-period denominator returns N/A rather than divide-by-zero.
- Filters match the same dimensions available for KPI-001.
- The current and comparison values used in the rate are visible.
### BR-CEO-003 — Profitability Trend
- Gross Profit uses KPI-003 and Gross Margin uses KPI-004.
- COGS is sourced from validated order-item/product cost data.
- Trend can be filtered by month, country, and category.
- Revenue and COGS reconcile to Finance for the same filter context.
### BR-CEO-004 — Growth vs Profitability
- Revenue growth and profitability are shown on a directly comparable view.
- Positive revenue growth with declining Gross Margin is flagged.
- Comparison uses the same date and dimensional filter context.
- Drill-down identifies the country/category causing the divergence.
### BR-CEO-005 — Market Performance
- Country ranking shows Net Revenue, Growth %, Gross Profit, and contribution to total growth.
- Contribution to growth sums consistently across displayed countries, subject to rounding.
- Only internal NovaMart data is used; no market-share claim is implied.
- At least a 24-month history supports YoY analysis where data is available.
### BR-CEO-006 — Category Performance
- Category metrics use consistent KPI definitions.
- Category hierarchy resolves from Product Catalog.
- Results support time and country filters.
- High-growth/low-margin categories can be identified without changing the KPI formula.
### BR-CEO-007 — Customer Value
- CLV is explicitly labeled Simplified Historical CLV.
- Average Customer Lifespan follows the governing definition.
- AOV and Purchase Frequency use completed eligible orders.
- Customer segments include documented derived RFM segments where used.
### BR-CEO-008 — Growth Opportunity Ranking
- Ranking uses KPI-002, KPI-004, KPI-015 only from internal data.
- Output is a ranked list, not a fabricated market-opportunity score.
- Combinations below a configurable minimum eligible-order threshold are excluded and the threshold is displayed.
- Each ranked row can be traced to country, category, and customer segment.

## 2. Sales Manager — Sales Performance

**Business Goal:** Increase sales and maximize product/category performance.

| Req ID | BQ | Requirement Statement | Linked KPIs | Decision Enabled |
|---|---|---|---|---|
| BR-SALES-001 | SALES-BQ1 | Rank products by Net Revenue and Units Sold. | KPI-001, KPI-009 | Which products should Sales focus on? |
| BR-SALES-002 | SALES-BQ2 | Report Net Revenue, Growth %, and Gross Margin % by category. | KPI-001, KPI-002, KPI-004 | Which categories should be developed? |
| BR-SALES-003 | SALES-BQ3 | Trend Net Revenue, Orders, and AOV daily/weekly/monthly with period comparisons. | KPI-001, KPI-010, KPI-008 | When do sales rise or fall? |
| BR-SALES-004 | SALES-BQ4 | Report Gross Profit and Gross Margin % per product, flagging high-revenue/low-margin products. | KPI-003, KPI-004 | Which products are truly valuable? |
| BR-SALES-005 | SALES-BQ5 | Report Net Revenue, Growth %, and AOV by country/region. | KPI-001, KPI-002, KPI-008 | Where should Sales focus? |
| BR-SALES-006 | SALES-BQ6 | Report Net Revenue, AOV, and Purchase Frequency by customer segment. | KPI-001, KPI-008, KPI-011 | Which customer groups should be prioritized? |
| BR-SALES-007 | SALES-BQ7 | Compare promotion-window revenue, AOV, margin, and uplift with the documented baseline. | KPI-032, KPI-008, KPI-004 | Is the promotion worth it? |

### BR-SALES-001 — Product Ranking
- Supports ranking by both Net Revenue and Units Sold.
- Uses eligible non-cancelled sales; product FK must resolve.
- Ties are broken deterministically, e.g. by product_id.
- Filters include date, country, category, and promotion where applicable.
### BR-SALES-002 — Category Performance
- Uses the same Net Revenue/Growth/Gross Margin definitions as executive reporting.
- Supports category and time drill-down.
- Category totals reconcile to product-level totals under the same filters.
- Growth is unavailable rather than estimated when a valid comparison period is absent.
### BR-SALES-003 — Sales Trend
- Supports daily, weekly, and monthly grains.
- AOV denominator uses completed eligible orders.
- Period-over-period comparison uses comparable complete periods.
- Trend supports drill-down to country/category/product.
### BR-SALES-004 — Product Profitability
- Gross Profit uses order-item COGS.
- High-revenue/low-margin flag logic is documented as a display rule, not a KPI redefinition.
- Product ranking can switch between revenue, gross profit, and margin.
- Results reconcile to category-level profitability.
### BR-SALES-005 — Geographic Sales
- Country/region mapping is documented and stable.
- Net Revenue, Growth, and AOV use consistent eligible-order filters.
- Current and prior-period values are visible.
- Unknown/guest customer status does not remove valid order geography.
### BR-SALES-006 — Segment Sales
- Customer segmentation logic is documented in the analytical layer.
- Net Revenue, AOV, and Purchase Frequency use the same segment membership snapshot for a displayed period.
- Guest/unknown customers are separated rather than silently mixed into named segments.
- Segment totals reconcile to eligible customer-linked sales.
### BR-SALES-007 — Promotion Effectiveness
- Promotion fields include ID, type, discount configuration, start date, and end date.
- Baseline is the four complete calendar weeks immediately before promotion start.
- KPI-032 is N/A when four full baseline weeks are unavailable.
- Profit impact includes discount effects through realized revenue and Gross Margin.
- Comparison is controlled by product/category to avoid mix bias.

## 3. Marketing Manager — Acquisition & Customer Value

**Business Goal:** Acquire, convert, and retain valuable customers efficiently.

**Source architecture:** raw Marketing & Web Analytics contains touchpoints/events and spend. Order/customer attribution is derived by ETL using the 30-day last-touch rule.

| Req ID | BQ | Requirement Statement | Linked KPIs | Decision Enabled |
|---|---|---|---|---|
| BR-MKT-001 | MKT-BQ1 | Report CAC, ROAS, CTR, CPC, and Conversion Rate by channel. | KPI-016, KPI-018, KPI-019, KPI-020, KPI-021 | Which channel should get more budget? |
| BR-MKT-002 | MKT-BQ2 | Report CAC by channel, campaign, country, and time. | KPI-016 | Where is acquisition most cost-efficient? |
| BR-MKT-003 | MKT-BQ3 | Report ROAS and Attributed Net Revenue per campaign. | KPI-018 | Which campaigns should scale or stop? |
| BR-MKT-004 | MKT-BQ4 | Report session-based funnel conversion/drop-off across tracked stages. | KPI-019, KPI-021, KPI-022 | Where is the funnel leaking? |
| BR-MKT-005 | MKT-BQ5 | Segment customers by RFM and report CLV, CAC, Conversion Rate, and Retention per segment. | KPI-015, KPI-016, KPI-021, KPI-013 | Which strategy fits each segment? |
| BR-MKT-006 | MKT-BQ6 | Report CLV/CAC ratio by acquisition channel and cohort. | KPI-017 | Which channels bring long-term value? |
| BR-MKT-007 | MKT-BQ7 | Report cohort Retention Rate, Churn Rate, and Repeat Customer Rate as three distinct metrics. | KPI-013, KPI-014, KPI-012 | How do we improve retention? |

### BR-MKT-001 — Channel Efficiency
- All five KPIs appear in one comparative channel view.
- CAC uses attributed new customers, not all purchasing customers.
- ROAS uses attributed Net Revenue and the same attribution model as CAC.
- Conversion uses unique eligible sessions.
- Channel totals reconcile to spend/events/attribution sources where mathematically applicable.
### BR-MKT-002 — CAC Breakdown
- Supports channel, campaign, country, and month filters.
- New customer is based on first eligible completed purchase.
- Attribution is last-touch within 30 days before that first purchase.
- Customers without an eligible touchpoint are shown as unattributed rather than forced into a channel.
### BR-MKT-003 — Campaign ROAS
- Attributed revenue is Net Revenue, not gross bookings.
- Campaign spend comes from marketing_spend at compatible grain.
- Orders outside the 30-day attribution window are not credited.
- Campaigns with zero spend return ROAS as N/A, not infinity.
### BR-MKT-004 — Session Funnel
- Funnel stages use unique sessions reaching each stage, not raw event counts.
- Stage denominator is the immediately previous stage's unique sessions.
- The event vocabulary and stage ordering are documented.
- Funnel is filterable by country, device, channel, and campaign where data exists.
- Session IDs are required for KPI eligibility per DQ-013.
### BR-MKT-005 — RFM Segmentation
- Recency, Frequency, Monetary definitions follow the KPI Dictionary.
- R/F/M scores use documented quintile logic and named segment rules.
- CLV is labeled Simplified Historical CLV.
- CAC and conversion are only shown for segment/channel combinations with valid attributable data.
- Retention uses acquisition cohorts, not repeat-rate logic.
### BR-MKT-006 — CLV/CAC by Cohort
- CLV and CAC use compatible acquisition cohort/channel filters.
- Zero/undefined CAC produces N/A ratio rather than divide-by-zero.
- Cohort is based on first eligible completed purchase month.
- Unattributed customers are visible separately.
### BR-MKT-007 — Retention vs Repeat
- Retention Rate, Churn Rate, and Repeat Customer Rate are displayed as three separate metrics, never merged.
- Churn Rate (KPI-014) is always shown alongside Retention Rate (KPI-013) on the same cohort basis, since it is `100 − Retention Rate` for that same cohort — never computed on a different population.
- Acquisition cohorts are defined by first completed purchase month.
- Retention/Churn use N→N+1 cohort activity; Repeat Customer Rate remains all-time within the analysis cutoff.
- Cohort sizes are displayed to prevent misleading small-sample interpretation.

## 4. Operations Manager — Fulfillment & Delivery

**Business Goal:** Deliver orders efficiently, on time, with minimal operational problems.

| Req ID | BQ | Requirement Statement | Linked KPIs | Decision Enabled |
|---|---|---|---|---|
| BR-OPS-001 | OPS-BQ1 | Report Fulfillment Rate and Fulfillment Time by warehouse and country. | KPI-023, KPI-024 | Where are bottlenecks? |
| BR-OPS-002 | OPS-BQ2 | Report On-Time Delivery Rate and average/median delivery time by carrier and country. | KPI-025, KPI-026 | Where are delivery problems concentrated? |
| BR-OPS-003 | OPS-BQ3 | Report Return Rate by product and category. | KPI-027 | Which products need investigation? |
| BR-OPS-004 | OPS-BQ4 | Report Return Reason % and Defect Rate by product/category. | KPI-028 | What operational/product problem needs fixing? |
| BR-OPS-005 | OPS-BQ5 | Report Cancellation Rate and reason breakdown by product/country. | KPI-029 | Why are orders cancelled? |
| BR-OPS-006 | OPS-BQ6 | Compare On-Time Delivery, Return Rate, Shipping Cost, and Cancellation Rate across carriers. | KPI-025, KPI-027, KPI-030, KPI-029 | Which carrier contracts should change? |

### BR-OPS-001 — Fulfillment Performance
- Fulfilled means non-cancelled order with fulfillment_timestamp populated.
- Fulfillment denominator excludes cancelled orders.
- Warehouse and country keys must resolve.
- Average fulfillment time excludes invalid timestamp sequences.
- Pending orders remain visible operationally but are not falsely counted as fulfilled.
### BR-OPS-002 — Delivery Performance
- On-time status compares actual delivery with expected delivery recorded at ship time.
- Expected delivery date is immutable for KPI purposes per DQ-018.
- Both mean and median delivery times are shown.
- Only eligible delivered orders enter KPI-025/026 denominators.
- Supports carrier and country filters.
### BR-OPS-003 — Return Rate
- KPI-027 denominator is eligible delivered orders, not all placed orders.
- Product/category view identifies delivered orders containing at least one returned selected item.
- Invalid return chronology is excluded until resolved.
- Order-level and item-level supplementary rates are clearly named if both are shown.
### BR-OPS-004 — Return Reasons
- Return reasons use a controlled vocabulary.
- Defect Rate uses eligible return records only.
- Product/category joins resolve through order_line_id/product_id.
- Unknown reasons are shown explicitly rather than dropped.
### BR-OPS-005 — Cancellations
- Cancellation Rate uses all placed orders as denominator.
- Cancellation reason is required or categorized as Unknown for cancelled orders.
- Breakdown supports product and country without double-counting order-level cancellations across multiple items; allocation/display logic is documented.
- Cancelled orders remain excluded from revenue KPIs.
### BR-OPS-006 — Carrier Comparison
- All four KPIs appear side by side.
- Shipping Cost is SUM(shipping_cost), not an ambiguous average/sum KPI.
- Carrier comparison uses compatible delivered/shipped populations and displays denominators.
- Cost-performance tradeoffs can be filtered by country and period.

## 5. Finance Manager — Financial Performance

**Business Goal:** Maximize profitability, control costs, and ensure sustainable financial performance.

| Req ID | BQ | Requirement Statement | Linked KPIs | Decision Enabled |
|---|---|---|---|---|
| BR-FIN-001 | FIN-BQ1 | Report Net Revenue, Gross Profit, Contribution Profit, Net Profit, and margin metrics monthly. | KPI-001, KPI-003, KPI-005, KPI-006, KPI-004, KPI-007 | Where are we generating profit? |
| BR-FIN-002 | FIN-BQ2 | Report Gross Profit and Gross Margin % by product/category. | KPI-003, KPI-004 | Which products/categories need pricing or portfolio action? |
| BR-FIN-003 | FIN-BQ3 | Compare Revenue Growth % with Operating Cost Growth and Operating Cost-to-Revenue Ratio. | KPI-002, KPI-033 | Which costs hurt profitability? |
| BR-FIN-004 | FIN-BQ4 | Report ROAS, CAC, CLV/CAC, and Marketing ROI %. | KPI-018, KPI-016, KPI-017, KPI-034 | Which marketing investments are justified? |
| BR-FIN-005 | FIN-BQ5 | Report AOV and its drivers (units/order, Discount %) by segment. | KPI-008, KPI-031 | What improves revenue per transaction? |
| BR-FIN-006 | FIN-BQ6 | Report CLV/CAC and Gross Profit Payback Period by acquisition channel/cohort. | KPI-017, KPI-035 | Should we continue the acquisition strategy? |
| BR-FIN-007 | FIN-BQ7 | Compare Discount %, Net Revenue, Gross Margin %, and Units Sold for discounted vs non-discounted sales. | KPI-031, KPI-001, KPI-004, KPI-009 | Which discounts are profitable? |

### BR-FIN-001 — Profitability Statement
- Gross, Contribution, and Net Profit are shown as separate measures.
- Net Profit includes shipping, payment, return, marketing, operating, and other eligible costs exactly once.
- Finance/Cost does not duplicate costs sourced from Logistics, Payment, or Marketing.
- Net Profit is N/A for periods where required cost data is incomplete at compatible grain.
- Monthly totals reconcile to component sources.
### BR-FIN-002 — Product Profitability
- Gross Profit uses validated unit COGS at order-line grain.
- Supports product/category/time filters.
- Gross Margin uses the same Net Revenue denominator as KPI-004.
- Product totals reconcile to category totals.
### BR-FIN-003 — Cost Efficiency
- Operating Cost includes only Finance/Cost expenses not represented in Logistics, Payment, Returns, or Marketing.
- Operating Cost Growth is computed from the same cost scope in current and comparison periods.
- Operating Cost-to-Revenue uses KPI-033.
- Breakdown identifies the operating-cost types driving deterioration.
### BR-FIN-004 — Marketing Economics
- ROAS/CAC/CLV-CAC/Marketing ROI use one attribution model.
- Attributed revenue is Net Revenue.
- Zero spend or zero attributable customers produces N/A where division is undefined.
- Channel/campaign filters use compatible attribution and spend grains.
### BR-FIN-005 — Revenue per Transaction
- AOV uses completed eligible orders.
- Units per order is shown as a supporting driver.
- Discount % uses Total Discount Amount / Total Original Merchandise Value.
- Segment comparisons use consistent segment definitions and period filters.
### BR-FIN-006 — Acquisition Payback
- KPI-035 is named Gross Profit Payback Period.
- Formula incorporates Gross Margin, not revenue-only payback.
- AOV, purchase frequency, margin, and CAC are evaluated at compatible channel/cohort grain where possible.
- Undefined denominators result in N/A, not silent estimates.
### BR-FIN-007 — Discount Profitability
- Discounted vs non-discounted comparison controls for product/category.
- Discount uses KPI-031 aggregate definition.
- Net Revenue, Gross Margin, and Units Sold use identical date/product scopes.
- Promotion effects are not interpreted as causal beyond the documented baseline comparison.
---

## Appendix A — Deferred / Out-of-Scope Questions

| Question | Reason for Deferral |
|---|---|
| What is our market share? | Requires external market-size/competitor-sales data. |
| Where are we gaining or losing market share? | Same external-data requirement. |

No synthetic external-market data will be fabricated. These are future-phase candidates.

## Appendix B — Shared KPI Usage

KPI formulas remain identical across stakeholders. Only dimensions, filters, and decision context change.

## Appendix C — Phase 1 Derived Analytical Concepts

- Marketing attribution
- RFM segmentation
- Customer acquisition cohort
- Promotion baseline
- KPI analytical views

These are produced after raw-data validation and are not pre-derived source fields.
