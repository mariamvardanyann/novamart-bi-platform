# NovaMart Final Stability Audit

**Goal:** finish the existing portfolio project without regenerating the order/marketing/logistics dataset or rebuilding the Power BI model.

## What was confirmed and fixed

### 1. Customer lifecycle
The original customer dimension allowed existing orders to predate `signup_date`. The final source patch moves only inconsistent signup dates back to the date of the customer's already-existing first generated order. **No order ID, order timestamp, product, quantity, price, customer assignment, payment, shipment, return, or marketing fact was regenerated.**

The order generator and ETL now also enforce `order_date >= signup_date` so the issue cannot silently return.

### 2. Refund ceiling (DQ-016)
The original clean layer contained 95 payments whose cumulative clean refunds exceeded the successful payment amount. The cause was multiple return-linked refund rows independently using order-level refund amounts.

The final ETL keeps raw refund rows auditable, then deterministically normalizes only resolved clean refund groups when their cumulative amount exceeds the successful payment amount. The future refund generator additionally restricts return-linked selection to one refund candidate per order and caps refund amounts by the successful payment amount.

Final clean result: **0 over-refunded payments**.

### 3. Finance/Cost taxonomy
The legacy finance generator used labels such as `payment_processing`, `logistics_overhead`, and `marketing_overhead` while payment fees, shipping cost, and ad spend already exist as separate sources. This was ambiguous against the project's no-double-counting rule.

The controlled Finance/Cost vocabulary is now:

`payroll`, `software`, `rent`, `infrastructure`, `professional_services`, `other`

These represent operating expenses only and explicitly exclude shipping charges, per-transaction payment fees, return costs, and ad spend. **Finance amounts and dates were not changed.**

### 4. Retention observability
Next-month retention is undefined for a cohort whose N+1 month is outside the dataset. The ETL and SQL view now exclude the final acquisition month instead of treating it as 0% retention.

The final observable cohort ends at **2026-06-01**; July 2026 is not used for N+1 retention.

The lower retention rates in some later *observable* cohorts were not artificially smoothed. They are a property of the existing synthetic purchase-frequency/order-assignment pattern, not a calculation error. This is intentionally left unchanged to avoid rewriting order history.

### 5. Cost-to-Revenue naming
The Power BI measure uses `operating_costs / net_revenue`, while documentation previously described KPI-033 as all eligible costs. The project now consistently names this KPI **Operating Cost-to-Revenue Ratio %**. The visual title was updated in Power BI Desktop to match the metric; the measure and data model were not rebuilt.

## Regression / stability checks

- Python compilation: **PASS**
- Full ETL execution: **PASS**
- ETL reconciliation / FK checks: **PASS**
- Order generator validation: **PASS** (60,000 test orders)
- Refund generator validation: **PASS** (5,000 test refunds)
- Finance generator validation: **PASS** (1,500 test costs)
- Orders before customer signup: **0**
- Clean payments over-refunded: **0**
- Invalid Finance/Cost types: **0**
- Consolidated quarantine rows: **16,571** (unchanged)
- Eligible completed orders: **53,473** (unchanged)
- Eligible purchasing customers: **9,203** (unchanged)
- Observable N+1 cohort customers: **9,158**

### Stability comparison against the uploaded v2
The following generated/raw/processed business facts were data-equal before vs after the stability patch: orders, order items, payments, shipments, returns, marketing spend, marketing events, products, promotions, and campaigns.

The intentional changes are limited to customer signup dates, Finance/Cost labels, clean refund amounts, observable cohort rows, validation/generator logic, documentation, the retention view, and one Power BI visual title.

## Final financial totals after DQ-016 correction

| Metric | Final value |
|---|---:|
| Sales Revenue | €11,261,554.82 |
| Refunds | €890,386.00 |
| Net Revenue | €10,371,168.82 |
| Gross Profit | €2,943,383.00 |
| Gross Margin | 28.38% |
| Shipping Cost | €421,206.54 |
| Payment Fees | €206,705.74 |
| Return Costs | €49,195.05 |
| Contribution Profit | €2,266,275.67 |
| Marketing Cost | €1,661,545.15 |
| Operating Costs | €1,528,057.71 |
| Net Profit | **-€923,327.19** |
| Net Margin | **-8.90%** |

The negative Net Profit is now a valid synthetic scenario outcome rather than a known reconciliation/taxonomy defect: contribution profit is insufficient to cover both marketing and operating expenses.

## What still requires the local Windows environment

The offline project was validated, and SQL Server reconciliation and the Power BI refresh were also confirmed locally. Because this environment does not have access to the user's local SQL Server/Power BI Desktop session, the final local deployment check is intentionally small:

1. Run `sql/patches/final_stability_patch.sql` against the existing `novamart` database.
2. Run `sql/tests/final_sql_validation.sql`.
3. Open `dashboard/NovaMart_BI_Final_Portfolio.pbix`, which is the refreshed and saved report.
4. Confirm the headline values above and save the PBIX.

No database recreation, full data reload, relationship rebuild, or visual rebuild is required by this patch.
