"""
NovaMart Synthetic Data Generator — v0.4c: Refunds

Generates:
    data/generated/refunds.csv

Uses:
    data/generated/orders.csv
    data/generated/order_items.csv
    data/generated/payments.csv
    data/generated/returns.csv

Business rule:
    85% of refunds are linked to returns.
    15% are standalone refunds.

Run:
    python src/data_generation/generate_refunds.py
"""

import os

import numpy as np
import pandas as pd

import config


N_REFUNDS_TARGET = 5_000
RETURN_LINK_SHARE = 0.85


def get_project_root():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )


def load_data():

    project_root = get_project_root()

    generated_dir = os.path.join(
        project_root,
        "data",
        "generated",
    )

    orders = pd.read_csv(
        os.path.join(
            generated_dir,
            "orders.csv",
        ),
        parse_dates=["order_timestamp"],
    )

    order_items = pd.read_csv(
        os.path.join(
            generated_dir,
            "order_items.csv",
        )
    )

    payments = pd.read_csv(
        os.path.join(
            generated_dir,
            "payments.csv",
        ),
        parse_dates=["payment_timestamp"],
    )

    returns = pd.read_csv(
        os.path.join(
            generated_dir,
            "returns.csv",
        ),
        parse_dates=["return_timestamp"],
    )

    return (
        orders,
        order_items,
        payments,
        returns,
    )


def calculate_order_totals(
    order_items,
):

    items = order_items.copy()

    items["line_revenue"] = (
        items["unit_price"]
        * items["quantity"]
        - items["line_discount"]
    )

    totals_df = (
        items
        .groupby(
            "order_id",
            as_index=False,
        )["line_revenue"]
        .sum()
    )

    lookup = {}

    for row in totals_df.to_dict(
        "records"
    ):

        order_id = int(
            row["order_id"]
        )

        total = float(
            row["line_revenue"]
        )

        lookup[
            order_id
        ] = total

    return lookup


def build_payment_lookup(
    payments,
):

    successful = payments[
        payments["payment_status"]
        == "succeeded"
    ].copy()

    successful = (
        successful
        .sort_values(
            "payment_timestamp"
        )
        .drop_duplicates(
            subset=["order_id"],
            keep="last",
        )
    )

    lookup = {}

    for row in successful.to_dict(
        "records"
    ):

        order_id = int(
            row["order_id"]
        )

        lookup[
            order_id
        ] = {
            "payment_id": int(
                row["payment_id"]
            ),
            "payment_timestamp":
                pd.Timestamp(
                    row[
                        "payment_timestamp"
                    ]
                ),
            "payment_amount": float(
                row["payment_amount"]
            ),
        }

    return lookup


def generate_refunds():

    rng = np.random.default_rng(
        config.RANDOM_SEED + 700
    )

    (
        orders,
        order_items,
        payments,
        returns,
    ) = load_data()

    order_totals = (
        calculate_order_totals(
            order_items
        )
    )

    payment_lookup = (
        build_payment_lookup(
            payments
        )
    )

    rows = []

    refund_id = 1

    # =========================================================
    # RETURN-LINKED REFUNDS
    # =========================================================

    target_linked = int(
        N_REFUNDS_TARGET
        * RETURN_LINK_SHARE
    )

    eligible_returns = returns[
        returns[
            "order_id"
        ].isin(
            payment_lookup.keys()
        )
    ].copy()

    # One refund candidate per order prevents multiple return-line refunds from
    # independently refunding the same full order amount.
    eligible_returns = (
        eligible_returns
        .sort_values(["order_id", "return_timestamp", "return_id"])
        .drop_duplicates(subset=["order_id"], keep="first")
    )

    if len(
        eligible_returns
    ) < target_linked:

        raise ValueError(
            "Not enough eligible returns "
            "to create 85% linked refunds."
        )

    linked_sample = (
        eligible_returns.sample(
            n=target_linked,
            random_state=
                config.RANDOM_SEED + 700,
            replace=False,
        )
    )

    refund_types = list(
        config.REFUND_TYPE_SHARE.keys()
    )

    refund_weights = list(
        config.REFUND_TYPE_SHARE.values()
    )

    for row in linked_sample.to_dict(
        "records"
    ):

        order_id = int(
            row["order_id"]
        )

        return_id = int(
            row["return_id"]
        )

        payment_data = (
            payment_lookup[
                order_id
            ]
        )

        payment_id = (
            payment_data[
                "payment_id"
            ]
        )

        payment_amount = float(
            payment_data["payment_amount"]
        )

        order_total = (
            order_totals[
                order_id
            ]
        )

        refund_type = str(
            rng.choice(
                refund_types,
                p=refund_weights,
            )
        )

        if refund_type == "full":

            refund_amount = (
                order_total
            )

        else:

            percentage = float(
                rng.uniform(
                    0.15,
                    0.70,
                )
            )

            refund_amount = (
                order_total
                * percentage
            )

        refund_amount = round(
            min(
                refund_amount,
                order_total,
                payment_amount,
            ),
            2,
        )

        return_timestamp = pd.Timestamp(
            row[
                "return_timestamp"
            ]
        )

        refund_timestamp = (
            return_timestamp
            + pd.Timedelta(
                days=int(
                    rng.integers(
                        0,
                        8,
                    )
                ),
                hours=int(
                    rng.integers(
                        0,
                        24,
                    )
                ),
            )
        )

        rows.append({
            "refund_id":
                refund_id,

            "order_id":
                order_id,

            "payment_id":
                payment_id,

            "return_id":
                return_id,

            "refund_timestamp":
                refund_timestamp,

            "refund_amount":
                refund_amount,

            "currency_code":
                config.CURRENCY_CODE,
        })

        refund_id += 1

    # =========================================================
    # STANDALONE REFUNDS
    # =========================================================

    standalone_target = (
        N_REFUNDS_TARGET
        - target_linked
    )

    linked_order_ids = set(
        linked_sample[
            "order_id"
        ].astype(int)
    )

    eligible_orders = orders[
        (
            orders[
                "status"
            ] == "delivered"
        )
        & (
            orders[
                "order_id"
            ].isin(
                payment_lookup.keys()
            )
        )
        & (
            ~orders[
                "order_id"
            ].isin(
                linked_order_ids
            )
        )
    ].copy()

    if len(
        eligible_orders
    ) < standalone_target:

        raise ValueError(
            "Not enough eligible orders "
            "for standalone refunds."
        )

    standalone_sample = (
        eligible_orders.sample(
            n=standalone_target,
            random_state=
                config.RANDOM_SEED + 701,
            replace=False,
        )
    )

    for row in standalone_sample.to_dict(
        "records"
    ):

        order_id = int(
            row["order_id"]
        )

        payment_data = (
            payment_lookup[
                order_id
            ]
        )

        payment_id = (
            payment_data[
                "payment_id"
            ]
        )

        payment_amount = float(
            payment_data["payment_amount"]
        )

        payment_timestamp = (
            payment_data[
                "payment_timestamp"
            ]
        )

        order_total = (
            order_totals[
                order_id
            ]
        )

        percentage = float(
            rng.uniform(
                0.10,
                0.50,
            )
        )

        refund_amount = round(
            min(
                order_total * percentage,
                payment_amount,
            ),
            2,
        )

        refund_timestamp = (
            payment_timestamp
            + pd.Timedelta(
                days=int(
                    rng.integers(
                        2,
                        31,
                    )
                ),
                hours=int(
                    rng.integers(
                        0,
                        24,
                    )
                ),
            )
        )

        rows.append({
            "refund_id":
                refund_id,

            "order_id":
                order_id,

            "payment_id":
                payment_id,

            "return_id":
                None,

            "refund_timestamp":
                refund_timestamp,

            "refund_amount":
                refund_amount,

            "currency_code":
                config.CURRENCY_CODE,
        })

        refund_id += 1

    return pd.DataFrame(
        rows
    )


def validate_refunds(
    refunds,
    payments,
    returns,
):

    # Exactly 5,000 refunds
    assert (
        len(refunds)
        == N_REFUNDS_TARGET
    )

    # refund_id must be unique
    assert refunds[
        "refund_id"
    ].is_unique

    # Refund amount must be positive
    assert refunds[
        "refund_amount"
    ].gt(0).all()

    # EUR only
    assert refunds[
        "currency_code"
    ].eq(
        config.CURRENCY_CODE
    ).all()

    # ---------------------------------------------------------
    # Validate payment IDs
    # ---------------------------------------------------------

    successful_payment_ids = set(
        payments.loc[
            payments[
                "payment_status"
            ] == "succeeded",
            "payment_id",
        ].astype(int)
    )

    refund_payment_ids = set(
        refunds[
            "payment_id"
        ].astype(int)
    )

    assert (
        refund_payment_ids
        .issubset(
            successful_payment_ids
        )
    )

    # ---------------------------------------------------------
    # Validate return IDs
    # ---------------------------------------------------------

    valid_return_ids = set(
        returns[
            "return_id"
        ].astype(int)
    )

    linked_refunds = refunds[
        refunds[
            "return_id"
        ].notna()
    ].copy()

    linked_return_ids = set(
        linked_refunds[
            "return_id"
        ].astype(int)
    )

    assert (
        linked_return_ids
        .issubset(
            valid_return_ids
        )
    )

    # ---------------------------------------------------------
    # Validate that return belongs to same order
    # ---------------------------------------------------------

    return_order_lookup = {}

    for row in returns.to_dict(
        "records"
    ):

        return_id = int(
            row["return_id"]
        )

        order_id = int(
            row["order_id"]
        )

        return_order_lookup[
            return_id
        ] = order_id

    for row in linked_refunds.to_dict(
        "records"
    ):

        return_id = int(
            row["return_id"]
        )

        refund_order_id = int(
            row["order_id"]
        )

        expected_order_id = (
            return_order_lookup[
                return_id
            ]
        )

        assert (
            refund_order_id
            == expected_order_id
        )

    # ---------------------------------------------------------
    # Validate cumulative refundable amount
    # ---------------------------------------------------------

    successful_payments = (
        payments.loc[
            payments["payment_status"] == "succeeded",
            ["payment_id", "order_id", "payment_amount"],
        ]
        .drop_duplicates(subset=["payment_id"])
    )

    payment_amount_lookup = successful_payments.set_index(
        "payment_id"
    )["payment_amount"]
    payment_order_lookup = successful_payments.set_index(
        "payment_id"
    )["order_id"]

    refund_totals = refunds.groupby("payment_id")["refund_amount"].sum()
    limits = payment_amount_lookup.reindex(refund_totals.index)
    assert limits.notna().all()
    assert (refund_totals <= limits + 0.01).all()

    expected_order = refunds["payment_id"].map(payment_order_lookup)
    assert expected_order.notna().all()
    assert (expected_order.astype(int) == refunds["order_id"].astype(int)).all()

    # ---------------------------------------------------------
    # Validate linked share
    # ---------------------------------------------------------

    linked_count = int(
        refunds[
            "return_id"
        ].notna().sum()
    )

    linked_share = (
        linked_count
        / len(refunds)
    )

    assert (
        0.84
        <= linked_share
        <= 0.86
    )


def main():

    project_root = (
        get_project_root()
    )

    generated_dir = os.path.join(
        project_root,
        "data",
        "generated",
    )

    (
        orders,
        order_items,
        payments,
        returns,
    ) = load_data()

    refunds = (
        generate_refunds()
    )

    validate_refunds(
        refunds,
        payments,
        returns,
    )

    output_path = os.path.join(
        generated_dir,
        "refunds.csv",
    )

    refunds.to_csv(
        output_path,
        index=False,
    )

    linked_count = int(
        refunds[
            "return_id"
        ].notna().sum()
    )

    standalone_count = int(
        refunds[
            "return_id"
        ].isna().sum()
    )

    linked_share = (
        linked_count
        / len(refunds)
        * 100
    )

    total_refunded = float(
        refunds[
            "refund_amount"
        ].sum()
    )

    print()

    print(
        "NovaMart v0.4c — "
        "Refunds regenerated successfully"
    )

    print("=" * 60)

    print(
        f"Total refunds: "
        f"{len(refunds):,}"
    )

    print(
        f"Linked to returns: "
        f"{linked_count:,}"
    )

    print(
        f"Standalone refunds: "
        f"{standalone_count:,}"
    )

    print(
        f"Return-linked share: "
        f"{linked_share:.2f}%"
    )

    print()

    print(
        f"Total refunded: "
        f"EUR {total_refunded:,.2f}"
    )

    print()

    print(
        f"File created: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()