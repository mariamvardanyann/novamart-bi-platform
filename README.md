# NovaMart Business Intelligence Platform

NovaMart is an end-to-end Business Intelligence portfolio project that simulates an e-commerce analytics environment and covers the full workflow from synthetic data generation to decision-ready dashboards.

> All data in this project is synthetic and was created for educational and portfolio purposes.

## Project Overview

The project demonstrates practical work with:

- Python ETL
- data-quality validation and quarantine
- Microsoft SQL Server
- analytical SQL views
- KPI reconciliation
- Power BI
- DAX measures
- dashboard design and business analysis

The solution follows this pipeline:

```text
Synthetic Data Generation
        ↓
Raw Data
        ↓
Python ETL
        ↓
Data Quality Validation
        ↓
Clean / Quarantine Layers
        ↓
SQL Server
        ↓
Analytical SQL Views
        ↓
Power BI
        ↓
DAX Measures
        ↓
Business Dashboards
```

## Tech Stack

- **ETL / Data Processing:** Python, Pandas, PyODBC
- **Database:** Microsoft SQL Server, SQL Server Management Studio
- **BI & Analytics:** Microsoft Power BI Desktop, DAX
- **Version Control:** Git, GitHub

## Business Questions

NovaMart was designed to answer questions such as:

- How much Net Revenue is the business generating?
- How much revenue is lost through refunds?
- Which countries and categories generate the most value?
- Which customer segments have the highest lifetime value?
- How effective are marketing campaigns and promotions?
- Which carriers perform best on delivery speed and reliability?
- Which categories have the highest return rates?
- Which products and categories generate the most Gross Profit?
- How are operating costs affecting profitability?

## Analytical Layer

The Power BI model contains **19 analytical SQL views**.

### Revenue & Profitability
- `vw_revenue_performance`
- `vw_revenue_growth`
- `vw_profitability`
- `vw_cost_performance`

### Product & Category
- `vw_product_sales`
- `vw_product_profitability`
- `vw_category_performance`

### Geography
- `vw_country_performance`

### Customer
- `vw_customer_value`
- `vw_customer_rfm`
- `vw_customer_retention`

### Marketing
- `vw_marketing_attribution`
- `vw_marketing_performance`
- `vw_funnel_performance`
- `vw_promotion_performance`

### Operations
- `vw_fulfillment_performance`
- `vw_delivery_performance`
- `vw_carrier_performance`
- `vw_return_performance`

## Data Quality

The ETL pipeline follows:

```text
Raw → Clean → Quarantine
```

Invalid records are not silently removed. Records that fail validation are stored in a quarantine layer so data-quality problems remain traceable.

Validation covers issues such as:

- invalid quantities
- foreign-key violations
- invalid promotions
- invalid marketing records
- shipment inconsistencies
- invalid returns
- invalid payments
- invalid refunds
- date consistency problems

The final consolidated quarantine dataset contains more than **16,000 rejected records**.

## Revenue Reconciliation

A core requirement was ensuring that financial metrics reconcile consistently across analytical views.

| Metric | Value |
|---|---:|
| Sales Revenue | €12,323,972.99 |
| Refunds | €933,654.35 |
| Net Revenue | €11,390,318.64 |
| Gross Profit | €3,575,760.10 |
| Net Profit | ~€1.61M |

Revenue totals reconcile across:

- Revenue Performance
- Product Sales
- Product Profitability
- Category Performance
- Country Performance
- Profitability

## Refund Allocation

For product-level analysis:

1. Refunds linked to returns are assigned to the related order line.
2. Refunds without a return identifier are allocated proportionally across order lines based on revenue share.
3. Rounding remainder is assigned so product-level totals reconcile exactly with overall refunds.

```text
Sales Revenue - Refunds = Net Revenue
```

## Key KPIs

### Revenue
- Sales Revenue
- Refund Amount
- Net Revenue
- Month-over-Month Revenue Growth

### Profitability
- Gross Profit
- Gross Margin
- Contribution Profit
- Net Profit
- Net Margin
- Cost-to-Revenue Ratio

### Customer
- Customer Lifetime Revenue
- Customer Lifetime Profit
- Customer Segmentation
- RFM Metrics
- Retention Rate

### Marketing
- ROAS
- CTR
- CPC
- Attributed Net Revenue
- Conversion Rate
- Promotion Revenue Uplift

### Operations
- Fulfillment Rate
- Cancellation Rate
- Average Order-to-Ship Hours
- On-Time Delivery Rate
- Average Delivery Hours
- Return Rate
- Shipping Cost

# Power BI Dashboard

The report contains **5 analytical pages**.

## 1. Executive Overview

**KPIs**
- Net Revenue
- Net Profit
- Net Margin %
- Fulfillment Rate %
- Latest MoM Revenue Growth %

**Visuals**
- Monthly Net Revenue Trend
- Net Revenue by Country
- Net Revenue by Category
- Top 10 Campaigns by ROAS

## 2. Customer Analysis

**Visuals**
- Customer Segments
- Customer Retention Trend
- Customer Lifetime Net Revenue by Segment
- Average Customer Value by Segment

Customer segments are derived from clean order counts:

```text
1 order       → one_time
2–5 orders    → occasional
6–10 orders   → frequent
11+ orders    → loyal
```

The latest incomplete retention cohort is excluded to avoid a false right-censoring drop.

## 3. Marketing Analysis

**Visuals**
- Conversion Rate by Channel
- Top 10 Campaigns by ROAS
- Top 10 Promotions by Revenue Uplift %
- Top 10 Campaigns by Attributed Net Revenue

Weighted conversion:

```DAX
Conversion Rate % =
DIVIDE(
    SUM(vw_funnel_performance[purchase_sessions]),
    SUM(vw_funnel_performance[total_sessions]),
    0
) * 100
```

## 4. Operations & Logistics

**KPIs**
- Fulfillment Rate %
- Cancellation Rate %
- Average Order-to-Ship Hours
- Average Shipping Cost

**Visuals**
- On-Time Delivery Rate by Carrier
- Average Delivery Hours by Carrier
- Return Rate by Carrier
- Return Rate % by Category

Weighted return rate:

```DAX
Return Rate % =
DIVIDE(
    SUM(vw_return_performance[returned_units]),
    SUM(vw_return_performance[sold_units]),
    0
) * 100
```

## 5. Product & Profitability

**KPIs**
- Gross Profit
- Gross Margin %
- Contribution Profit
- Net Profit

**Visuals**
- Top 10 Products by Gross Profit
- Gross Profit by Category
- Monthly Net Profit Trend
- Cost-to-Revenue Ratio Trend

## DAX Measures

### Net Margin

```DAX
Net Margin Overall % =
DIVIDE(
    SUM(vw_profitability[net_profit]),
    SUM(vw_profitability[net_revenue]),
    0
) * 100
```

### Gross Margin

```DAX
Gross Margin Overall % =
DIVIDE(
    SUM(vw_profitability[gross_profit]),
    SUM(vw_profitability[net_revenue]),
    0
) * 100
```

### Cost-to-Revenue Ratio

```DAX
Cost to Revenue Ratio % =
DIVIDE(
    SUM(vw_profitability[operating_costs]),
    SUM(vw_profitability[net_revenue]),
    0
) * 100
```

## Selected Insights

- Germany generates the highest Net Revenue among the modeled markets.
- Electronics is the strongest revenue-generating category.
- Loyal customers generate the highest lifetime value per customer.
- Customer retention is relatively stable across observable cohorts.
- Marketing channels have similar conversion rates while campaign ROAS varies considerably.
- Even the strongest modeled promotions show negative revenue uplift versus the defined pre-promotion baseline.
- SwiftPost combines strong on-time performance with relatively low average delivery time.
- Fashion has the highest weighted category return rate.
- Operating cost pressure changes significantly month to month.
- Profitability remains positive across most of the modeled period.

## Suggested Repository Structure

```text
novamart-bi/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── quarantine/
├── etl/
│   ├── generators/
│   ├── validators/
│   ├── builders/
│   └── loader/
├── sql/
│   ├── schema/
│   ├── views/
│   ├── indexes/
│   └── validation/
├── docs/
│   ├── 00_project_charter.md
│   ├── 01_brd.md
│   ├── 02_kpi_dictionary.md
│   ├── 03_data_quality.md
│   ├── 04_data_dictionary.md
│   ├── 05_traceability_matrix.md
│   ├── 06_dashboard_requirements.md
│   └── 07_synthetic_data_specification.md
├── powerbi/
│   └── NovaMart_BI_Final.pbix
├── screenshots/
│   ├── executive_overview.png
│   ├── customer_analysis.png
│   ├── marketing_analysis.png
│   ├── operations_logistics.png
│   └── product_profitability.png
├── requirements.txt
├── .gitignore
└── README.md
```

## How to Run

### 1. Create the SQL Server database

```sql
CREATE DATABASE novamart;
```

Run the schema scripts from the SQL folder.

### 2. Create and activate a Python virtual environment

```bash
python -m venv .venv
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the synthetic data generation and ETL pipeline

Generate the data, validate it, create clean/quarantine outputs, and build derived datasets.

### 4. Load clean data into SQL Server

Use the PyODBC loader to populate the `novamart` database.

### 5. Create analytical views

Execute the scripts in:

```text
sql/views/
```

### 6. Validate analytical totals

Run:

```text
final_sql_validation.sql
```

### 7. Open Power BI

Open:

```text
NovaMart_BI_Final.pbix
```

Refresh the SQL Server connection if required.

## Future Improvements

- Star-schema Power BI model
- Shared Date and Country dimensions
- Report-wide and cross-page slicers
- Incremental refresh
- Automated ETL orchestration
- Cloud deployment
- Power BI Service publishing
- Row-Level Security
- Forecasting
- Churn modeling
- Automated data-quality monitoring

## Project Purpose

This project demonstrates an end-to-end Business Intelligence workflow and practical skills in:

- SQL
- Python ETL
- data quality
- relational database design
- analytical modeling
- KPI design
- Power BI
- DAX
- dashboard design
- data reconciliation
- business analysis
