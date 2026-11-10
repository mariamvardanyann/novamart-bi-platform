# Synthetic Data Layers

- `generated/` — initial synthetic generator output.
- `raw/` — synthetic source exports with intentional data-quality defects.
- `processed/` — cleaned validated tables and derived customer/attribution outputs.
- `quarantine/` — invalid rows retained with reasons for inspection.

These large CSV outputs are excluded from GitHub through `.gitignore`. The Power BI report contains a validated synthetic snapshot, while the Python generator, ETL code, SQL and documentation are versioned in this repository.
