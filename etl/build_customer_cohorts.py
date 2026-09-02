import os

import pandas as pd

from config import PROCESSED_DIR


def build_customer_cohorts():

    customers_path = os.path.join(
        PROCESSED_DIR,
        "customers.csv",
    )

    orders_path = os.path.join(
        PROCESSED_DIR,
        "orders.csv",
    )

    customers = pd.read_csv(
        customers_path,
        parse_dates=[
            "signup_date",
        ],
    )

    orders = pd.read_csv(
        orders_path,
        parse_dates=[
            "order_timestamp",
        ],
    )

    # ========================================================
    # ACQUISITION MONTH
    # ========================================================
    #
    # Acquisition is based on customer signup month.
    # SQL expects a DATE, so we store the first day
    # of the acquisition month.
    #
    # Example:
    # 2024-08-17 -> 2024-08-01
    # ========================================================

    cohorts = customers[
        [
            "customer_id",
            "signup_date",
        ]
    ].copy()

    cohorts[
        "acquisition_month"
    ] = (
        cohorts[
            "signup_date"
        ]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # ========================================================
    # ORDER MONTH
    # ========================================================

    orders[
        "order_month"
    ] = (
        orders[
            "order_timestamp"
        ]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # ========================================================
    # NEXT MONTH
    # ========================================================

    cohorts[
        "next_month"
    ] = (
        cohorts[
            "acquisition_month"
        ]
        + pd.offsets.MonthBegin(1)
    )

    # ========================================================
    # RETENTION
    # ========================================================
    #
    # A customer is retained next month if they placed
    # at least one clean order in the month immediately
    # after their acquisition month.
    # ========================================================

    customer_month_orders = (
        orders[
            [
                "customer_id",
                "order_month",
            ]
        ]
        .drop_duplicates()
    )

    retention_check = cohorts.merge(
        customer_month_orders,
        left_on=[
            "customer_id",
            "next_month",
        ],
        right_on=[
            "customer_id",
            "order_month",
        ],
        how="left",
    )

    retention_check[
        "is_retained_next_month"
    ] = (
        retention_check[
            "order_month"
        ]
        .notna()
    )

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    final = retention_check[
        [
            "customer_id",
            "acquisition_month",
            "is_retained_next_month",
        ]
    ].copy()

    final[
        "acquisition_month"
    ] = (
        final[
            "acquisition_month"
        ].dt.date
    )

    final[
        "is_retained_next_month"
    ] = (
        final[
            "is_retained_next_month"
        ].astype(bool)
    )

    return final


def main():

    cohorts = build_customer_cohorts()

    output_path = os.path.join(
        PROCESSED_DIR,
        "customer_cohorts.csv",
    )

    cohorts.to_csv(
        output_path,
        index=False,
    )

    retained = int(
        cohorts[
            "is_retained_next_month"
        ].sum()
    )

    retention_rate = (
        retained
        / len(cohorts)
        * 100
    )

    print()
    print(
        "NovaMart ETL — customer_cohorts created"
    )

    print("=" * 50)

    print(
        f"Rows: "
        f"{len(cohorts):,}"
    )

    print(
        f"Retained next month: "
        f"{retained:,}"
    )

    print(
        f"Next-month retention rate: "
        f"{retention_rate:.2f}%"
    )

    print()

    print(
        "Acquisition month range:"
    )

    print(
        f"{cohorts['acquisition_month'].min()} "
        f"→ "
        f"{cohorts['acquisition_month'].max()}"
    )

    print()

    print(
        f"File created: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()