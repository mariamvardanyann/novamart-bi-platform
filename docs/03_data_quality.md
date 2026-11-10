# Data Quality Requirements
## NovaMart Business Intelligence Platform — Phase 1.2c

**Version:** v1.1 | **Status:** Implementation Ready  
**Related:** `01_brd.md`, `02_kpi_dictionary.md`, `04_data_dictionary.md`

## Purpose

These rules define valid data across NovaMart's seven source systems before KPI calculation. They are implemented in the Python ETL layer and preserve raw-source auditability.

## Data Quality Principles

1. **Raw is immutable.** Source values are preserved unchanged.
2. **Validation is explicit.** Every failed rule receives a rule ID and reason.
3. **Invalid data is traceable.** Rejected or unresolved records are written to quarantine.
4. **Corrections happen downstream.** Any deterministic correction is applied only in cleaned/analytical layers.
5. **KPI eligibility is separate from raw preservation.** A record can remain in raw data but be excluded from one or more KPIs.

## Data Quality Rules

| ID | Rule | Applies To | Failure Handling |
|---|---|---|---|
| DQ-001 | `order_id` must not be NULL and must be unique at order-header grain. `order_line_id` must not be NULL and must be unique at order-line grain. | Sales | Reject invalid row/entity; log to quarantine |
| DQ-002 | `quantity` must be an integer > 0. | Sales / Order Items | Reject row; quarantine |
| DQ-003 | `original_unit_price` and `unit_price` must be ≥ 0. | Sales / Order Items | Reject row; quarantine |
| DQ-004 | If both order and delivery timestamps exist, `order_timestamp ≤ actual_delivery_timestamp`. NULL delivery is valid for pending, cancelled, or undelivered orders. | Sales + Logistics | Flag/quarantine inconsistent record |
| DQ-005 | Cancelled orders must not contribute to Net Revenue or downstream revenue/profit KPIs. | Sales | Preserve raw order; exclude in cleaned KPI-eligible layer |
| DQ-006 | Customer FK must resolve for customer-level analysis. | Sales + Customer | Map unresolved customer to controlled `Guest/Unknown` analytical member; log orphan |
| DQ-007 | Product FK must resolve to Product Catalog. | Sales + Product | Quarantine invalid order line |
| DQ-008 | `line_discount ≥ 0` and may not cause final line merchandise value to be negative. Raw invalid values are not mutated. | Sales | Preserve raw; quarantine/flag; apply documented cap only in cleaned layer if approved |
| DQ-009 | Return timestamp must be on/after corresponding actual delivery timestamp where delivery exists. | Logistics | Flag/quarantine; exclude unresolved record from KPI-027/028 |
| DQ-010 | Attribution lookback must not exceed 30 days and touchpoint timestamp must precede purchase timestamp. | Marketing + Sales | Exclude ineligible touchpoint from attribution |
| DQ-011 | Ad spend, impressions, clicks, and session/event counts must be ≥ 0; clicks must not exceed impressions when measured at compatible grain. | Marketing | Reject/quarantine invalid row |
| DQ-012 | Shipping cost, payment fee, refund amount, return cost, finance cost amount must be ≥ 0. | Logistics + Payment + Finance/Cost | Reject/quarantine invalid transaction |
| DQ-013 | `session_id` must be present for session-based funnel events used in KPI-021/022. | Marketing Events | Exclude event from session-based funnel; quarantine if required |
| DQ-014 | Marketing event timestamp must fall within the session's observed bounds; event type must be from the controlled event vocabulary. | Marketing Events | Reject/quarantine invalid event |
| DQ-015 | A completed purchase used for conversion must map to a valid order and, when attribution is evaluated, a valid customer/session relationship. | Marketing + Sales | Exclude from attributed conversion; log unresolved mapping |
| DQ-016 | Payment/refund references must map to a valid `order_id`; cumulative refund amount may not exceed the successful payment amount. | Payment | Quarantine unresolved references; deterministically normalize resolved excess amounts in clean while preserving raw |
| DQ-017 | Shipment must map to a valid non-null `order_id`; `shipping_timestamp ≤ actual_delivery_timestamp` when both exist. | Logistics | Quarantine invalid shipment |
| DQ-018 | `expected_delivery_date` used by KPI-025 must represent the value recorded at ship time and must not be overwritten by a later actual-delivery event. | Logistics | Preserve original SLA date; flag mutation |
| DQ-019 | Finance/Cost records must use controlled `cost_type`/`cost_category` values and must not duplicate shipping, payment, return, or marketing costs already sourced elsewhere. | Finance/Cost | Quarantine duplicate/invalid categorization |
| DQ-020 | All Phase 1 monetary records must use `currency_code = EUR`. | All monetary sources | Reject/quarantine non-EUR record in Phase 1 |
| DQ-021 | Promotion start date must be ≤ promotion end date; promotion discount configuration must be non-negative. | Sales / Promotions | Reject/quarantine invalid promotion |
| DQ-022 | A promotion baseline requires four complete calendar weeks immediately preceding promotion start; insufficient history must be reported as unavailable, not estimated silently. | Sales / Analytics | Mark KPI-032 unavailable |
| DQ-023 | Customer lifecycle must be chronological (`order_timestamp` may not precede `signup_date`), and first-purchase date used for CAC/cohort logic must equal the minimum eligible completed purchase timestamp. | Sales + Customer | Quarantine lifecycle-invalid order; recalculate first purchase in clean layer |
| DQ-024 | Warehouse and carrier keys on shipment facts must resolve to their dimension records. | Logistics | Quarantine invalid shipment |
| DQ-025 | Duplicate raw records must be detected using source-specific business keys and ingestion metadata; duplicates are preserved in raw but deduplicated only in clean according to documented rules. | All sources | Flag duplicate; retain raw; deduplicate clean |

## Quarantine Record Minimum Fields

```text
quarantine_id
source_system
source_file_or_batch
source_record_key
dq_rule_id
failure_reason
raw_payload_or_reference
detected_at
resolution_status
resolved_at nullable
```

## ETL Enforcement Pattern

```text
RAW
 ↓
VALIDATE
 ├── valid ─────→ CLEAN
 └── invalid ───→ QUARANTINE
                    ↓
              review / rule-based resolution
                    ↓
                 CLEAN (when allowed)
```

## Notes

- Cancelled orders, invalid returns, and unresolved attribution records remain available for audit/operational analysis even when excluded from a KPI.
- Quarantine counts must be reconcilable to source-row counts.
- DQ rules should be unit-tested in Sprint 2 with both valid and intentionally invalid synthetic examples.


## Implementation / Enforcement Matrix

This matrix distinguishes documented rules from where they are actually enforced. `Partial` means the rule is implemented for the portfolio's current scenario but not as a production-grade exhaustive control.

| Rule | Primary enforcement layer | Current status |
|---|---|---|
| DQ-001 | Python ETL + SQL PK/unique constraints | Partial |
| DQ-002 | Python ETL + SQL CHECK | Implemented |
| DQ-003 | SQL CHECK / generator validation | Partial |
| DQ-004 | Python ETL (shipment chronology) | Partial |
| DQ-005 | Analytical SQL eligibility rule | Implemented |
| DQ-006 | SQL FK / analytical handling | Partial — controlled Guest/Unknown mapping not implemented |
| DQ-007 | Python ETL + SQL FK | Implemented |
| DQ-008 | Generator/SQL validation | Partial |
| DQ-009 | Python ETL | Implemented |
| DQ-010 | Python ETL attribution builder | Implemented |
| DQ-011 | Python ETL | Implemented |
| DQ-012 | Generator + SQL CHECK constraints | Partial |
| DQ-013 | Python ETL | Implemented |
| DQ-014 | Generator vocabulary; ETL session validation | Partial |
| DQ-015 | ETL + eligible-purchase business rule | Implemented for order/customer mapping; session linkage partial |
| DQ-016 | Python ETL refund validation + SQL FK | Implemented, including cumulative refund ≤ successful payment amount |
| DQ-017 | Python ETL + SQL FK | Implemented |
| DQ-018 | Generator source field preservation | Partial |
| DQ-019 | Generator controlled vocabulary + Python ETL finance validation | Implemented |
| DQ-020 | Python ETL / generator | Implemented for orders; other monetary tables rely on generator/constraints |
| DQ-021 | Python ETL | Implemented |
| DQ-022 | Analytical SQL promotion baseline | Implemented — incomplete 28-day baselines return NULL |
| DQ-023 | Python ETL order lifecycle validation + cohort builder | Implemented |
| DQ-024 | SQL FK / generator validation | Partial |
| DQ-025 | Python ETL for orders; source-specific handling elsewhere | Partial |

The table is intentionally explicit about partial controls so the repository does not imply that all 25 rules are enforced in one Python validator.
