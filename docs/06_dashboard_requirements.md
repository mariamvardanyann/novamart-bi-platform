# Dashboard Requirements
## NovaMart Business Intelligence Platform — Phase 1.2f

**Version:** v1.1 | **Status:** Design Baseline

## Global Dashboard Rules

- Every metric label uses the KPI Dictionary name.
- Shared KPIs use one formula across all dashboards.
- Global filters: date; country where applicable.
- Views must surface N/A rather than silently substitute zero for undefined KPIs.
- Tooltips or info panels document eligibility rules for complex KPIs.
- Current vs comparison period is shown where meaningful.
- Monetary values display in EUR.
- Dashboard calculations must be reproducible from planned SQL analytical views.

## Dashboard Register

| Dashboard ID | Stakeholder | Core Purpose |
|---|---|---|
| DB-CEO | CEO | Executive health, growth, profitability, customer value |
| DB-SALES | Sales | Product/category/geographic sales and promotion performance |
| DB-MKT | Marketing | Acquisition, campaign efficiency, funnel, retention |
| DB-OPS | Operations | Fulfillment, delivery, returns, carriers |
| DB-FIN | Finance | Profitability, costs, marketing economics, discount economics |
| DB-DQ | Analytics/Data Team | Data quality and quarantine monitoring |

## DB-CEO

Required visuals:
- KPI cards: Net Revenue, Revenue Growth, Gross Profit, Gross Margin, Simplified Historical CLV.
- Revenue/Gross Profit trend.
- Country performance matrix.
- Category growth vs margin scatter.
- Customer value by segment.
- Ranked internal growth-opportunity table.

## DB-SALES

Required visuals:
- Net Revenue / Orders / AOV trend.
- Top products toggleable by revenue/units.
- Product profitability matrix.
- Category performance.
- Country sales performance.
- Segment performance.
- Promotion vs baseline comparison.

## DB-MKT

Required visuals:
- Channel scorecard with CAC, ROAS, CTR, CPC, Conversion Rate together.
- Campaign ROAS ranking.
- Session funnel.
- CAC trend by channel/campaign/country.
- RFM segment view.
- CLV/CAC by channel/cohort.
- Retention cohort view plus separate Repeat Customer Rate.

## DB-OPS

Required visuals:
- Fulfillment Rate/Time by warehouse.
- On-Time Delivery and mean/median time by carrier.
- Return Rate by product/category.
- Return reason/defect breakdown.
- Cancellation reason breakdown.
- Carrier scorecard with delivery, returns, shipping cost, cancellations side by side.

## DB-FIN

Required visuals:
- Monthly Net Revenue, Gross Profit, Contribution Profit, Net Profit.
- Gross and Net Margin trend.
- Product/category profitability.
- Cost category trend and Cost-to-Revenue Ratio.
- Marketing economics panel: ROAS, CAC, CLV/CAC, Marketing ROI.
- Gross Profit Payback Period by channel/cohort.
- AOV drivers and discount profitability comparison.

## DB-DQ

Required visuals:
- Source records ingested.
- Valid vs quarantined counts.
- Failures by DQ rule.
- Unresolved quarantine aging.
- Duplicate count by source.
- Orphan FK counts.
- Reconciliation status by batch.
