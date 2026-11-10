# SQL Layer — Microsoft SQL Server

NovaMart uses SQL Server (T-SQL) for the clean relational model, 19 analytical views and financial reconciliation.

- `schema_sqlserver.sql` — SQL Server schema, constraints and relationships.
- `views/` — 19 analytical views (18 report views and one attribution helper). See [execution order](views/README.md).
- `tests/final_sql_validation.sql` — checks financial totals and view count.
- `tests/constraint_validation_test.sql` — transactional constraint checks.
- `patches/final_stability_patch.sql` — **migration for the previous v2 snapshot only**; it contains dataset-specific refund IDs and should **not** be run on a fresh generated database.
- `erd.mmd` — Mermaid ER diagram.

## Architecture

`data/raw/` contains synthetic source CSVs, which pass through Python validation to `data/processed/` (clean) and `data/quarantine/` (invalid source records). Clean data is loaded into SQL Server, queried via analytical views, and consumed by Power BI.

## Validation

The final project was validated locally in SQL Server Management Studio. The reconciliation script returned **PASS** with zero revenue and gross-profit differences across tested views and confirmed **19 SQL analytical views**. For dataset-specific totals, see [Final Stability Audit](../FINAL_STABILITY_AUDIT.md).

![NovaMart Core Entity Relationship Diagram](../images/erd_core_entities.png)
