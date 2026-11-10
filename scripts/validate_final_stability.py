"""Offline regression checks for the final NovaMart portfolio dataset."""

from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
ALLOWED_FINANCE_TYPES = {
    "payroll",
    "software",
    "rent",
    "infrastructure",
    "professional_services",
    "other",
}
ELIGIBLE_STATUSES = {"paid", "fulfilled", "shipped", "delivered"}


def load(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / f"{name}.csv", **kwargs)


def main() -> None:
    customers = load("customers", parse_dates=["signup_date"])
    orders = load("orders", parse_dates=["order_timestamp"])
    items = load("order_items")
    payments = load("payments")
    refunds = load("refunds")
    shipments = load("shipments")
    returns = load("returns")
    marketing_spend = load("marketing_spend")
    finance = load("finance_costs")
    cohorts = load("customer_cohorts", parse_dates=["acquisition_month"])

    lifecycle = orders.merge(
        customers[["customer_id", "signup_date"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )
    assert lifecycle["signup_date"].notna().all()
    assert (
        lifecycle["order_timestamp"].dt.normalize()
        >= lifecycle["signup_date"].dt.normalize()
    ).all()

    refund_totals = refunds.groupby("payment_id")["refund_amount"].sum()
    payment_limits = payments.set_index("payment_id")["payment_amount"].reindex(
        refund_totals.index
    )
    assert payment_limits.notna().all()
    assert (refund_totals <= payment_limits + 0.01).all()

    assert set(finance["cost_type"].unique()).issubset(ALLOWED_FINANCE_TYPES)
    assert finance["cost_amount"].gt(0).all()
    assert finance["currency_code"].eq("EUR").all()

    succeeded_order_ids = set(
        payments.loc[payments["payment_status"].eq("succeeded"), "order_id"].astype(int)
    )
    eligible = orders[
        orders["status"].isin(ELIGIBLE_STATUSES)
        & orders["order_id"].isin(succeeded_order_ids)
    ].copy()
    eligible_ids = set(eligible["order_id"].astype(int))

    max_eligible_month = (
        eligible["order_timestamp"].max().to_period("M").to_timestamp()
    )
    assert cohorts["acquisition_month"].max() < max_eligible_month

    eligible_items = items[items["order_id"].isin(eligible_ids)].copy()
    eligible_items["sales_revenue"] = (
        eligible_items["quantity"] * eligible_items["unit_price"]
        - eligible_items["line_discount"]
    )
    eligible_items["cogs"] = (
        eligible_items["quantity"] * eligible_items["unit_cogs"]
    )

    sales_revenue = float(eligible_items["sales_revenue"].sum())
    cogs = float(eligible_items["cogs"].sum())
    refund_amount = float(
        refunds.loc[refunds["order_id"].isin(eligible_ids), "refund_amount"].sum()
    )
    net_revenue = sales_revenue - refund_amount
    gross_profit = net_revenue - cogs
    shipping_cost = float(
        shipments.loc[shipments["order_id"].isin(eligible_ids), "shipping_cost"].sum()
    )
    payment_fees = float(
        payments.loc[
            payments["order_id"].isin(eligible_ids)
            & payments["payment_status"].eq("succeeded"),
            "payment_fee",
        ].sum()
    )
    return_costs = float(
        returns.loc[returns["order_id"].isin(eligible_ids), "return_cost"].sum()
    )
    contribution_profit = (
        gross_profit - shipping_cost - payment_fees - return_costs
    )
    marketing_cost = float(marketing_spend["spend_amount"].sum())
    operating_costs = float(finance["cost_amount"].sum())
    net_profit = contribution_profit - marketing_cost - operating_costs

    print("NovaMart final stability validation: PASS")
    print(f"Eligible orders: {len(eligible):,}")
    print(f"Eligible customers: {eligible['customer_id'].nunique():,}")
    print(f"Observable cohort customers: {len(cohorts):,}")
    print(f"Sales Revenue: EUR {sales_revenue:,.2f}")
    print(f"Refunds: EUR {refund_amount:,.2f}")
    print(f"Net Revenue: EUR {net_revenue:,.2f}")
    print(f"Gross Profit: EUR {gross_profit:,.2f}")
    print(f"Contribution Profit: EUR {contribution_profit:,.2f}")
    print(f"Net Profit: EUR {net_profit:,.2f}")
    print(f"Net Margin: {100.0 * net_profit / net_revenue:.2f}%")


if __name__ == "__main__":
    main()
