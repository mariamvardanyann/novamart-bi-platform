"""
NovaMart Synthetic Data Generator — v0.3a: Payments

Generates:
    data/generated/payments.csv

Uses:
    data/generated/orders.csv
    data/generated/order_items.csv

Run:
    python src/data_generation/generate_payments.py
"""

import os

import numpy as np
import pandas as pd

import config


def load_inputs(
    project_root: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:

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

    return orders, order_items


def calculate_order_totals(
    order_items: pd.DataFrame,
) -> pd.Series:
    """
    Calculate final merchandise value per order.

    line revenue =
        unit_price * quantity - line_discount
    """

    items = order_items.copy()

    items["line_revenue"] = (
        items["unit_price"]
        * items["quantity"]
        - items["line_discount"]
    )

    return (
        items
        .groupby("order_id")["line_revenue"]
        .sum()
    )


def generate_payment_status(
    rng: np.random.Generator,
) -> str:

    statuses = list(
        config.PAYMENT_STATUS_SHARE.keys()
    )

    weights = list(
        config.PAYMENT_STATUS_SHARE.values()
    )

    return str(
        rng.choice(
            statuses,
            p=weights,
        )
    )


def generate_payments() -> pd.DataFrame:

    rng = np.random.default_rng(
        config.RANDOM_SEED + 300
    )

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    orders, order_items = load_inputs(
        project_root
    )

    order_totals = calculate_order_totals(
        order_items
    )

    rows = []
    payment_id = 1

    for order in orders.to_dict("records"):

        order_id = int(
            order["order_id"]
        )

        order_total = float(
            order_totals.get(
                order_id,
                0.0,
            )
        )

        # Cancelled orders normally should not have successful payments.
        if order["status"] == "cancelled":

            # Some cancelled orders may have had failed payment attempts.
            if rng.random() < 0.40:
                payment_status = "failed"
            else:
                continue

        else:
            payment_status = generate_payment_status(
                rng
            )

        payment_method = str(
            rng.choice(
                config.PAYMENT_METHODS
            )
        )

        fee_rate = float(
            config.PAYMENT_FEE_RATE_BY_METHOD[
                payment_method
            ]
        )

        # Successful payment amount corresponds to order merchandise value.
        if payment_status == "succeeded":
            payment_amount = round(
                order_total,
                2,
            )

            payment_fee = round(
                payment_amount
                * fee_rate,
                2,
            )

        elif payment_status == "failed":
            payment_amount = 0.0
            payment_fee = 0.0

        else:  # pending
            payment_amount = round(
                order_total,
                2,
            )
            payment_fee = 0.0

        order_timestamp = pd.Timestamp(
            order["order_timestamp"]
        )

        # Payment happens shortly after order placement.
        payment_timestamp = (
            order_timestamp
            + pd.Timedelta(
                minutes=int(
                    rng.integers(
                        0,
                        31,
                    )
                )
            )
        )

        rows.append({
            "payment_id": payment_id,
            "order_id": order_id,
            "payment_timestamp": payment_timestamp,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "payment_amount": payment_amount,
            "payment_fee": payment_fee,
            "currency_code": config.CURRENCY_CODE,
        })

        payment_id += 1

        # Small number of retry attempts after failed payment.
        if (
            payment_status == "failed"
            and order["status"] != "cancelled"
            and rng.random() < 0.35
        ):

            retry_method = str(
                rng.choice(
                    config.PAYMENT_METHODS
                )
            )

            retry_fee_rate = float(
                config.PAYMENT_FEE_RATE_BY_METHOD[
                    retry_method
                ]
            )

            retry_timestamp = (
                payment_timestamp
                + pd.Timedelta(
                    minutes=int(
                        rng.integers(
                            5,
                            121,
                        )
                    )
                )
            )

            rows.append({
                "payment_id": payment_id,
                "order_id": order_id,
                "payment_timestamp": retry_timestamp,
                "payment_method": retry_method,
                "payment_status": "succeeded",
                "payment_amount": round(
                    order_total,
                    2,
                ),
                "payment_fee": round(
                    order_total
                    * retry_fee_rate,
                    2,
                ),
                "currency_code": config.CURRENCY_CODE,
            })

            payment_id += 1

    return pd.DataFrame(rows)


def validate_payments(
    payments: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:

    assert payments[
        "payment_id"
    ].is_unique

    assert payments[
        "payment_id"
    ].notna().all()

    assert payments[
        "order_id"
    ].notna().all()

    assert payments[
        "payment_amount"
    ].ge(0).all()

    assert payments[
        "payment_fee"
    ].ge(0).all()

    assert payments[
        "currency_code"
    ].eq(
        config.CURRENCY_CODE
    ).all()

    valid_order_ids = set(
        orders[
            "order_id"
        ].astype(int)
    )

    assert set(
        payments[
            "order_id"
        ].astype(int)
    ).issubset(
        valid_order_ids
    )

    assert set(
        payments[
            "payment_status"
        ].unique()
    ).issubset(
        set(
            config.PAYMENT_STATUS_SHARE.keys()
        )
    )

    assert set(
        payments[
            "payment_method"
        ].unique()
    ).issubset(
        set(
            config.PAYMENT_METHODS
        )
    )


def main() -> None:

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    generated_dir = os.path.join(
        project_root,
        "data",
        "generated",
    )

    orders = pd.read_csv(
        os.path.join(
            generated_dir,
            "orders.csv",
        )
    )

    payments = generate_payments()

    validate_payments(
        payments,
        orders,
    )

    output_path = os.path.join(
        generated_dir,
        "payments.csv",
    )

    payments.to_csv(
        output_path,
        index=False,
    )

    print()
    print(
        "NovaMart v0.3a — Payments generated successfully"
    )
    print("=" * 60)

    print(
        f"Payment rows: {len(payments):,}"
    )

    print()
    print("Payment status distribution (%):")

    print(
        payments[
            "payment_status"
        ]
        .value_counts(
            normalize=True
        )
        .mul(100)
        .round(2)
        .to_string()
    )

    print()
    print("Payment methods:")

    print(
        payments[
            "payment_method"
        ]
        .value_counts()
        .to_string()
    )

    print()
    print("Total processed amount:")

    print(
        f"EUR "
        f"{payments['payment_amount'].sum():,.2f}"
    )

    print()
    print("Total payment fees:")

    print(
        f"EUR "
        f"{payments['payment_fee'].sum():,.2f}"
    )

    print()
    print(
        f"File created: {output_path}"
    )


if __name__ == "__main__":
    main()