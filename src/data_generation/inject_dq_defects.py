"""
NovaMart Synthetic Data Generator — v0.6b: DQ Defect Injection

Purpose:
    Copy clean generated data into data/raw
    and intentionally inject realistic data-quality defects.

Clean source:
    data/generated/

Dirty raw output:
    data/raw/

Run:
    python src/data_generation/inject_dq_defects.py
"""

import os
import shutil
from typing import Any, cast

import numpy as np
import pandas as pd

import config


DQ_RATE = 0.01


def get_project_root():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )


def get_generated_dir():
    return os.path.join(
        get_project_root(),
        "data",
        "generated",
    )


def get_raw_dir():
    return os.path.join(
        get_project_root(),
        "data",
        "raw",
    )


def copy_generated_to_raw():
    generated_dir = get_generated_dir()
    raw_dir = get_raw_dir()

    os.makedirs(
        raw_dir,
        exist_ok=True,
    )

    csv_files = [
        filename
        for filename in os.listdir(generated_dir)
        if filename.endswith(".csv")
    ]

    for filename in csv_files:
        source = os.path.join(
            generated_dir,
            filename,
        )

        destination = os.path.join(
            raw_dir,
            filename,
        )

        shutil.copy2(
            source,
            destination,
        )

    return len(csv_files)


def sample_indices(
    df,
    rng,
    rate=DQ_RATE,
    minimum=1,
):
    if len(df) == 0:
        return []

    count = max(
        minimum,
        int(
            round(
                len(df) * rate
            )
        ),
    )

    count = min(
        count,
        len(df),
    )

    raw_indices = rng.choice(
        df.index.to_numpy(),
        size=count,
        replace=False,
    )

    return [
        int(index)
        for index in raw_indices
    ]


# ============================================================
# DQ-001 — Negative quantity
# ============================================================

def inject_negative_quantity(rng):
    path = os.path.join(
        get_raw_dir(),
        "order_items.csv",
    )

    df = pd.read_csv(path)

    indices = sample_indices(
        df,
        rng,
    )

    for index in indices:
        df.at[
            index,
            "quantity",
        ] = -1

    df.to_csv(
        path,
        index=False,
    )

    return len(indices)


# ============================================================
# DQ-002 — Unknown product
# ============================================================

def inject_unknown_product(rng):
    path = os.path.join(
        get_raw_dir(),
        "order_items.csv",
    )

    df = pd.read_csv(path)

    indices = sample_indices(
        df,
        rng,
    )

    for index in indices:
        df.at[
            index,
            "product_id",
        ] = 999999

    df.to_csv(
        path,
        index=False,
    )

    return len(indices)


# ============================================================
# DQ-003 — Non-EUR currency
# ============================================================

def inject_non_eur_currency(rng):
    path = os.path.join(
        get_raw_dir(),
        "orders.csv",
    )

    df = pd.read_csv(path)

    indices = sample_indices(
        df,
        rng,
    )

    invalid_currencies = [
        "USD",
        "GBP",
        "CHF",
    ]

    for index in indices:
        df.at[
            index,
            "currency_code",
        ] = str(
            rng.choice(
                invalid_currencies
            )
        )

    df.to_csv(
        path,
        index=False,
    )

    return len(indices)


# ============================================================
# DQ-004 — Delivery before shipment
# ============================================================

def inject_delivery_before_shipment(rng):
    path = os.path.join(
        get_raw_dir(),
        "shipments.csv",
    )

    df = pd.read_csv(
        path,
        parse_dates=[
            "shipped_timestamp",
            "actual_delivery_timestamp",
        ],
    )

    eligible = df[
        df[
            "actual_delivery_timestamp"
        ].notna()
    ].copy()

    indices = sample_indices(
        eligible,
        rng,
    )

    for index in indices:
        shipped = pd.Timestamp(
            cast(
                Any,
                df.at[
                    index,
                    "shipped_timestamp",
                ],
            )
        )

        df.at[
            index,
            "actual_delivery_timestamp",
        ] = (
            shipped
            - pd.Timedelta(days=1)
        )

    df.to_csv(
        path,
        index=False,
    )

    return len(indices)


# ============================================================
# DQ-005 — Clicks greater than impressions
# ============================================================

def inject_clicks_gt_impressions(rng):
    path = os.path.join(
        get_raw_dir(),
        "marketing_spend.csv",
    )

    df = pd.read_csv(path)

    indices = sample_indices(
        df,
        rng,
    )

    for index in indices:
        impressions = int(
            cast(
                Any,
                df.at[
                    index,
                    "impressions",
                ],
            )
        )

        extra_clicks = int(
            rng.integers(
                1,
                500,
            )
        )

        df.at[
            index,
            "clicks",
        ] = (
            impressions
            + extra_clicks
        )

    df.to_csv(
        path,
        index=False,
    )

    return len(indices)


# ============================================================
# DQ-006 — Invalid return date
# ============================================================

def inject_invalid_return_date(rng):
    returns_path = os.path.join(
        get_raw_dir(),
        "returns.csv",
    )

    shipments_path = os.path.join(
        get_raw_dir(),
        "shipments.csv",
    )

    returns = pd.read_csv(
        returns_path,
        parse_dates=[
            "return_timestamp"
        ],
    )

    shipments = pd.read_csv(
        shipments_path,
        parse_dates=[
            "actual_delivery_timestamp"
        ],
    )

    delivery_lookup = {}

    delivered_shipments = shipments[
        shipments[
            "actual_delivery_timestamp"
        ].notna()
    ]

    for row in delivered_shipments.to_dict(
        "records"
    ):
        order_id = int(
            row["order_id"]
        )

        delivery_lookup[
            order_id
        ] = pd.Timestamp(
            row[
                "actual_delivery_timestamp"
            ]
        )

    eligible = returns[
        returns[
            "order_id"
        ].isin(
            delivery_lookup.keys()
        )
    ].copy()

    indices = sample_indices(
        eligible,
        rng,
    )

    for index in indices:
        order_id = int(
            cast(
                Any,
                returns.at[
                    index,
                    "order_id",
                ],
            )
        )

        delivery_timestamp = (
            delivery_lookup[
                order_id
            ]
        )

        returns.at[
            index,
            "return_timestamp",
        ] = (
            delivery_timestamp
            - pd.Timedelta(days=2)
        )

    returns.to_csv(
        returns_path,
        index=False,
    )

    return len(indices)


# ============================================================
# DQ-007 — Duplicate source rows
# ============================================================

def inject_duplicate_rows():
    path = os.path.join(
        get_raw_dir(),
        "orders.csv",
    )

    df = pd.read_csv(path)

    duplicate_count = max(
        1,
        int(
            round(
                len(df) * DQ_RATE
            )
        ),
    )

    duplicate_sample = df.sample(
        n=duplicate_count,
        random_state=
            config.RANDOM_SEED + 1201,
        replace=False,
    )

    df = pd.concat(
        [
            df,
            duplicate_sample,
        ],
        ignore_index=True,
    )

    df.to_csv(
        path,
        index=False,
    )

    return duplicate_count


# ============================================================
# DQ-008 — Missing session ID
# ============================================================

def inject_missing_session(rng):
    path = os.path.join(
        get_raw_dir(),
        "marketing_events.csv",
    )

    df = pd.read_csv(path)

    indices = sample_indices(
        df,
        rng,
    )

    for index in indices:
        df.at[
            index,
            "session_id",
        ] = None

    df.to_csv(
        path,
        index=False,
    )

    return len(indices)


# ============================================================
# DQ-009 — Invalid promotion date range
# ============================================================
def inject_invalid_promotion_dates(rng):
    path = os.path.join(
        get_raw_dir(),
        "promotions.csv",
    )

    df = pd.read_csv(
        path,
        parse_dates=[
            "promotion_start_date",
            "promotion_end_date",
        ],
    )

    defect_count = max(
        1,
        int(
            round(
                len(df) * 0.05
            )
        ),
    )

    raw_indices = rng.choice(
        df.index.to_numpy(),
        size=defect_count,
        replace=False,
    )

    indices = [
        int(index)
        for index in raw_indices
    ]

    for index in indices:
        start_date = pd.Timestamp(
            cast(
                Any,
                df.at[
                    index,
                    "promotion_start_date",
                ],
            )
        )

        df.at[
            index,
            "promotion_end_date",
        ] = (
            start_date
            - pd.Timedelta(days=5)
        )

    df.to_csv(
        path,
        index=False,
    )

    return len(indices)

# ============================================================
# DQ-010 — Invalid controlled vocabulary
# ============================================================

def inject_bad_order_status(rng):
    path = os.path.join(
        get_raw_dir(),
        "orders.csv",
    )

    df = pd.read_csv(path)

    indices = sample_indices(
        df,
        rng,
        rate=0.005,
    )

    invalid_statuses = [
        "DELIVERED_WRONG",
        "unknown_status",
        "completed",
    ]

    for index in indices:
        df.at[
            index,
            "status",
        ] = str(
            rng.choice(
                invalid_statuses
            )
        )

    df.to_csv(
        path,
        index=False,
    )

    return len(indices)


def main():
    rng = np.random.default_rng(
        config.RANDOM_SEED + 1200
    )

    print()
    print(
        "NovaMart v0.6b — "
        "Intentional DQ Defect Injection"
    )
    print("=" * 60)

    copied_files = (
        copy_generated_to_raw()
    )

    print(
        f"Copied {copied_files} CSV files "
        f"from generated → raw."
    )

    print()
    print("Injecting defects...")
    print()

    results = {}

    results[
        "Negative quantity"
    ] = inject_negative_quantity(
        rng
    )

    results[
        "Unknown product"
    ] = inject_unknown_product(
        rng
    )

    results[
        "Non-EUR currency"
    ] = inject_non_eur_currency(
        rng
    )

    results[
        "Delivery before shipment"
    ] = inject_delivery_before_shipment(
        rng
    )

    results[
        "Clicks > impressions"
    ] = inject_clicks_gt_impressions(
        rng
    )

    results[
        "Invalid return date"
    ] = inject_invalid_return_date(
        rng
    )

    results[
        "Duplicate orders"
    ] = inject_duplicate_rows()

    results[
        "Missing session ID"
    ] = inject_missing_session(
        rng
    )

    results[
        "Invalid promotion dates"
    ] = inject_invalid_promotion_dates(
        rng
    )

    results[
        "Invalid order status"
    ] = inject_bad_order_status(
        rng
    )

    total_defects = sum(
        results.values()
    )

    print(
        "Injected DQ defects:"
    )

    print()

    for name, count in results.items():
        print(
            f"{name:<30}"
            f"{count:>8,}"
        )

    print()
    print(
        f"Total intentional defects: "
        f"{total_defects:,}"
    )

    print()

    print(
        "Clean source preserved:"
    )

    print(
        get_generated_dir()
    )

    print()

    print(
        "Dirty raw dataset created:"
    )

    print(
        get_raw_dir()
    )

    print()

    print(
        "v0.6b completed successfully."
    )


if __name__ == "__main__":
    main()