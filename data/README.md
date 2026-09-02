# Data Folder Convention

- `generated/` — intermediate, clean synthetic output straight from the
  generator (no intentional defects yet). Useful for debugging the generator
  itself in isolation from DQ-defect injection.
- `raw/` — **final deliverable**: `generated/` data plus the intentional
  ~0.5–1.5% DQ-rule-violating rows injected per
  `docs/07_synthetic_data_specification.md` §20. This is what the Sprint 2
  Python ETL actually reads — it is the simulated "real source system export,"
  messy the way real exports are. Once written, files here are treated as
  immutable (never hand-edited).
- `processed/` — reserved for Sprint 2 ETL output staging, if needed before
  loading into the SQL Server CLEAN tables.
