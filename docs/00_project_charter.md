# Project Charter
## NovaMart — Business Intelligence Platform

| Field | Value |
|---|---|
| Project Name | NovaMart Business Intelligence Platform |
| Project Type | Enterprise Data Analytics Platform |
| Industry | Retail / E-commerce |
| Prepared by | [Your Name], Junior Data Analyst |
| Date | August 2026 |
| Status | Sprint 0 — Documentation Complete / Ready for Sprint 1 |
| Version | v1.1 |

---

## 1. Company Background

NovaMart is a mid-sized online retail company selling thousands of products across multiple European countries. Over the past year, leadership has observed several warning signs:

- Revenue growth has slowed.
- Return rates have increased.
- Marketing budget has grown without a clear read on return on investment.
- It is unclear which customers generate the most long-term value.
- Reporting is manual — almost no dashboards exist.
- Data is fragmented across seven logical source systems with no single analytical source of truth.

NovaMart Phase 1 uses the following synthetic source systems:

1. Sales
2. Customer
3. Product Catalog
4. Payment
5. Logistics
6. Marketing & Web Analytics
7. Finance / Cost

Leadership has approved the creation of an internal Business Intelligence Platform to address these gaps.

## 2. Problem Statement

NovaMart's data is fragmented across seven operational and analytical source systems. Without a centralized analytics layer, management cannot reliably measure business performance, understand customer behavior, evaluate marketing efficiency, identify the most profitable products and segments, or reconcile operational and financial performance. Decisions are currently made on incomplete or outdated information.

## 3. Your Role

**Junior Data Analyst**, recently onboarded to the Analytics team. This is your first end-to-end ownership project:

> *"Build an end-to-end analytics platform that helps management make data-driven decisions."*

## 4. Business Goal

Build an analytics platform that enables NovaMart to:

- Understand sales performance.
- Understand customer behavior and value.
- Understand profitability.
- Understand returns and fulfillment issues.
- Measure marketing acquisition and conversion efficiency.
- Track KPIs consistently across departments.
- Support management in making data-driven decisions.

## 5. Stakeholders & High-Level Needs

| Stakeholder | Business Goal | Key Interests |
|---|---|---|
| CEO | Profitable, sustainable growth | Revenue, Profit, Growth, CLV |
| Sales Manager | Increase sales, improve product/category performance | Top Products, Sales Trend, Category Performance, Promotions |
| Marketing Manager | Acquire, convert, retain valuable customers efficiently | CAC, ROAS, Funnel, Segmentation, Retention, CLV |
| Operations Manager | Deliver orders efficiently, minimize operational problems | Returns, Shipping, Fulfillment, Carriers |
| Finance Manager | Maximize profitability, control costs | Profit, Margin, Cost Efficiency, Marketing Economics |

*(Full stakeholder breakdown with all 35 Business Questions is documented in `01_brd.md`.)*

## 6. Expected Deliverables

- [x] Project Charter — `docs/00_project_charter.md`
- [x] Business Requirements Document — `docs/01_brd.md`
- [x] KPI Dictionary — `docs/02_kpi_dictionary.md`
- [x] Data Quality Requirements — `docs/03_data_quality.md`
- [x] Data Dictionary & Grain Register — `docs/04_data_dictionary.md`
- [x] Traceability Matrix — `docs/05_traceability_matrix.md`
- [x] Dashboard Requirements — `docs/06_dashboard_requirements.md`
- [x] MySQL/SQL Server relational database schema (22 tables) — `sql/schema_sqlserver.sql`, live-validated against SQL Server (SSMS): 5/5 constraint tests passed — `sql/tests/TEST_RESULTS.md`
- [x] ER Diagram (core entities, visual + full technical Mermaid) — `sql/README.md`, `sql/erd.mmd`, `images/erd_core_entities.png`
- [ ] Synthetic source data (24 months)
- [ ] Python ETL pipeline (extraction, validation, cleaning, transformation, load)
- [ ] KPI calculation layer (SQL + Python)
- [ ] Business analysis & insights
- [ ] Power BI dashboard specification + interactive web dashboard demo
- [ ] Business report (executive summary + recommendations)
- [ ] GitHub repository with full documentation

## 7. Technology Stack

| Layer | Tools |
|---|---|
| Backend / ETL | Python, Pandas, NumPy, SQLAlchemy |
| Database | MySQL |
| Visualization | Power BI (spec) + HTML/React interactive dashboard (live demo) |
| Version Control | Git, GitHub |
| Documentation | Markdown, Draw.io (ER diagrams) |

## 8. Development Methodology

Agile, organized in sprints:

| Sprint | Focus | Output |
|---|---|---|
| Sprint 0 | Planning | Charter, BRD, KPI Dictionary, DQ Rules, Data Dictionary, Traceability, Dashboard Requirements |
| Sprint 1 | Database | MySQL schema, ER diagram, synthetic source data |
| Sprint 2 | Python ETL | Raw → validation → quarantine/clean → analytical transformations |
| Sprint 3 | Analytics | KPI calculations, SQL views, insights |
| Sprint 4 | Dashboard | Power BI spec + interactive dashboard |
| Sprint 5 | Documentation | README, business report |
| Sprint 6 | Polish | Final review, reproducibility check, GitHub push |

## 9. Assumptions & Constraints

- All data is **synthetically generated** to realistically resemble NovaMart's operations; no real customer data is used.
- Historical data spans 24 months to support trend, cohort, and growth analysis.
- The seven source systems are linked only through explicitly documented integration keys where applicable; not every source shares every identifier.
- The core commerce model uses `order_id`, `customer_id`, and `product_id` where applicable.
- Marketing attribution is **derived during ETL** from raw session/touchpoint data. Attribution fields are not treated as raw source fields.
- All monetary values are generated and reported in **EUR** in Phase 1. No FX conversion is required.
- Raw source data is immutable. Corrections are applied only in cleaned/analytical layers; invalid records are logged to quarantine for auditability.
- Power BI `.pbix` is not generated by this process because it requires Power BI Desktop. A complete dashboard specification and an equivalent working web dashboard are provided instead.

### 9.1 Data Architecture Assumptions

NovaMart uses a layered architecture:

```text
Synthetic Source Files
        ↓
RAW layer (immutable)
        ↓
Validation
   ↙          ↘
QUARANTINE    CLEAN
                 ↓
Derived / Analytical Layer
                 ↓
SQL KPI Views
                 ↓
Power BI / Web Dashboard
```

Each source dataset has a documented grain and primary key in `04_data_dictionary.md`.

Finance/Cost data contains operating and other expenses that are not already represented in Logistics, Payment, or Marketing sources. Shipping cost, payment fees, return cost, and marketing spend must not be duplicated in Finance/Cost, preventing double counting in Net Profit.

## 10. Success Criteria

The project is considered successful when:

1. All 35 business questions across 5 stakeholders can be answered from the data model.
2. Every KPI has one authoritative formula and documented grain/eligibility rules.
3. Every BR has explicit, testable acceptance criteria.
4. A working, documented database and ETL pipeline exist and are reproducible.
5. Invalid data is traceable through a quarantine mechanism.
6. Core traceability exists from BQ → BR → KPI → source → entity/field → transformation → analytical view → dashboard → decision.
7. A dashboard (spec + live demo) visualizes the core KPIs per stakeholder.
8. The repository is structured and documented to professional standards and is suitable for a job-application portfolio.
