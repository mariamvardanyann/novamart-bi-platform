import os

import pandas as pd

from config import PROCESSED_DIR
from business_rules import get_eligible_completed_orders


def build_customer_cohorts():

    orders = pd.read_csv(
        os.path.join(PROCESSED_DIR, "orders.csv"),
        parse_dates=["order_timestamp"],
    )

    payments = pd.read_csv(
        os.path.join(PROCESSED_DIR, "payments.csv"),
        parse_dates=["payment_timestamp"],
    )

    eligible_orders = get_eligible_completed_orders(orders, payments)

    # Acquisition month = month of the customer's first eligible completed
    # purchase, never signup month.
    first_purchase = (
        eligible_orders
        .groupby("customer_id", as_index=False)["order_timestamp"]
        .min()
        .rename(columns={"order_timestamp": "first_purchase_timestamp"})
    )

    first_purchase["acquisition_month"] = (
        first_purchase["first_purchase_timestamp"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    first_purchase["next_month"] = (
        first_purchase["acquisition_month"] + pd.offsets.MonthBegin(1)
    )

    eligible_orders["order_month"] = (
        eligible_orders["order_timestamp"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # Next-month retention is only defined for cohorts whose N+1 month is
    # observable in the dataset. The final acquisition month is therefore
    # excluded instead of being silently treated as 0% retained.
    max_observed_month = eligible_orders["order_month"].max()
    first_purchase = first_purchase[
        first_purchase["next_month"] <= max_observed_month
    ].copy()

    customer_month_orders = (
        eligible_orders[["customer_id", "order_month"]]
        .drop_duplicates()
    )

    retention_check = first_purchase.merge(
        customer_month_orders,
        left_on=["customer_id", "next_month"],
        right_on=["customer_id", "order_month"],
        how="left",
    )

    retention_check["is_retained_next_month"] = (
        retention_check["order_month"].notna()
    )

    final = retention_check[[
        "customer_id",
        "acquisition_month",
        "is_retained_next_month",
    ]].copy()

    final["acquisition_month"] = final["acquisition_month"].dt.date
    final["is_retained_next_month"] = final["is_retained_next_month"].astype(bool)

    return final


def main():
    cohorts = build_customer_cohorts()
    output_path = os.path.join(PROCESSED_DIR, "customer_cohorts.csv")
    cohorts.to_csv(output_path, index=False)

    retained = int(cohorts["is_retained_next_month"].sum())
    retention_rate = retained / len(cohorts) * 100 if len(cohorts) else 0.0

    print()
    print("NovaMart ETL — customer_cohorts created")
    print("=" * 50)
    print(f"Customers in observable N+1 cohorts: {len(cohorts):,}")
    print(f"Retained next month: {retained:,}")
    print(f"Next-month retention rate: {retention_rate:.2f}%")
    if len(cohorts):
        print()
        print("Acquisition month range:")
        print(f"{cohorts['acquisition_month'].min()} → {cohorts['acquisition_month'].max()}")
    print()
    print(f"File created: {output_path}")


if __name__ == "__main__":
    main()
