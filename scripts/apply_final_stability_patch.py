"""Apply NovaMart's final non-regenerative data corrections.

This script deliberately preserves order assignments, order timestamps, order lines,
marketing facts, logistics facts and finance amounts. It only corrects:
1) customer signup dates that occur after an already-existing first order,
2) legacy finance cost labels so they use the controlled non-overlapping vocabulary,
Refund overages are deliberately corrected in the clean ETL layer so raw refund
rows remain auditable and unchanged.

It is safe to re-run: all operations are deterministic and idempotent.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

FINANCE_TYPE_MAP = {
    "warehouse_operations": "rent",
    "technology": "software",
    "customer_support": "payroll",
    "payment_processing": "professional_services",
    "administration": "other",
    "logistics_overhead": "infrastructure",
    "marketing_overhead": "professional_services",
}


def patch_customer_signup_dates() -> int:
    generated_orders = pd.read_csv(
        DATA_DIR / "generated" / "orders.csv",
        parse_dates=["order_timestamp"],
    )
    first_order_date = (
        generated_orders.groupby("customer_id")["order_timestamp"]
        .min()
        .dt.normalize()
    )

    changed_ids: set[int] = set()
    for layer in ("generated", "raw", "processed"):
        path = DATA_DIR / layer / "customers.csv"
        customers = pd.read_csv(path, parse_dates=["signup_date"])
        first = customers["customer_id"].map(first_order_date)
        invalid = first.notna() & (customers["signup_date"] > first)
        changed_ids.update(customers.loc[invalid, "customer_id"].astype(int))
        customers.loc[invalid, "signup_date"] = first.loc[invalid]
        customers["signup_date"] = customers["signup_date"].dt.date
        customers.to_csv(path, index=False)

    return len(changed_ids)


def patch_finance_cost_types() -> int:
    changed_rows = 0
    for layer in ("generated", "raw", "processed"):
        path = DATA_DIR / layer / "finance_costs.csv"
        df = pd.read_csv(path)
        mapped = df["cost_type"].replace(FINANCE_TYPE_MAP)
        changed_rows = max(changed_rows, int((mapped != df["cost_type"]).sum()))
        df["cost_type"] = mapped
        df.to_csv(path, index=False)
    return changed_rows


def main() -> None:
    signup_changes = patch_customer_signup_dates()
    finance_changes = patch_finance_cost_types()
    print("NovaMart final stability source patch completed")
    print(f"Customer signup dates corrected: {signup_changes:,}")
    print(f"Finance rows relabeled per layer: {finance_changes:,}")
    print("Refund overages: corrected downstream by ETL; raw rows are preserved.")


if __name__ == "__main__":
    main()
