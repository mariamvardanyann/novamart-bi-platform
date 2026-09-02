"""
NovaMart Synthetic Data Generator — v0.4b: Returns

Generates:
    data/generated/returns.csv

Uses:
    data/generated/orders.csv
    data/generated/order_items.csv
    data/generated/products.csv
    data/generated/shipments.csv

Run:
    python src/data_generation/generate_returns.py
"""

import os

import numpy as np
import pandas as pd

import config


def load_inputs(
    project_root: str,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:

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

    products = pd.read_csv(
        os.path.join(
            generated_dir,
            "products.csv",
        )
    )

    shipments = pd.read_csv(
        os.path.join(
            generated_dir,
            "shipments.csv",
        ),
        parse_dates=[
            "actual_delivery_timestamp"
        ],
    )

    return (
        orders,
        order_items,
        products,
        shipments,
    )


def build_category_lookup(
    products: pd.DataFrame,
) -> dict[int, str]:
    """
    Map product_id -> category name.
    """

    category_names = {
        i + 1: name
        for i, name
        in enumerate(config.CATEGORIES)
    }

    return {
        int(row["product_id"]):
            category_names[
                int(row["category_id"])
            ]
        for row
        in products.to_dict("records")
    }


def get_return_probability(
    category_name: str,
) -> float:
    """
    Calculate category-specific return probability.
    """

    multiplier = float(
        config.CATEGORY_PROFILES[
            category_name
        ]["return_rate_multiplier"]
    )

    probability = (
        config.BASE_RETURN_RATE
        * multiplier
    )

    return min(
        probability,
        0.40,
    )


def choose_return_reason(
    rng: np.random.Generator,
    category_name: str,
) -> str:

    defect_share = float(
        config.CATEGORY_PROFILES[
            category_name
        ]["defect_share"]
    )

    if category_name == "Fashion":

        reasons = [
            "size_issue",
            "changed_mind",
            "defective",
            "wrong_item",
            "damaged",
            "late_delivery",
            "other",
        ]

        weights = np.array([
            0.40,
            0.20,
            0.10,
            0.08,
            0.08,
            0.06,
            0.08,
        ])

    else:

        remaining = (
            1.0 - defect_share
        )

        reasons = [
            "defective",
            "wrong_item",
            "changed_mind",
            "damaged",
            "late_delivery",
            "other",
        ]

        weights = np.array([
            defect_share,
            remaining * 0.15,
            remaining * 0.35,
            remaining * 0.15,
            remaining * 0.10,
            remaining * 0.25,
        ])

    weights = (
        weights
        / weights.sum()
    )

    return str(
        rng.choice(
            reasons,
            p=weights,
        )
    )


def generate_returns() -> pd.DataFrame:

    rng = np.random.default_rng(
        config.RANDOM_SEED + 600
    )

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    (
        orders,
        items,
        products,
        shipments,
    ) = load_inputs(
        project_root
    )

    delivered_shipments = (
        shipments[
            shipments[
                "actual_delivery_timestamp"
            ].notna()
        ]
        .copy()
    )

    delivery_lookup = {
        int(row["order_id"]):
            pd.Timestamp(
                row[
                    "actual_delivery_timestamp"
                ]
            )
        for row
        in delivered_shipments.to_dict(
            "records"
        )
    }

    category_lookup = (
        build_category_lookup(
            products
        )
    )

    eligible_items = items[
        items[
            "order_id"
        ].isin(
            delivery_lookup.keys()
        )
    ]

    rows = []

    return_id = 1

    for item in eligible_items.to_dict(
        "records"
    ):

        product_id = int(
            item["product_id"]
        )

        category_name = (
            category_lookup[
                product_id
            ]
        )

        probability = (
            get_return_probability(
                category_name
            )
        )

        if rng.random() >= probability:
            continue

        purchased_quantity = int(
            item["quantity"]
        )

        returned_quantity = int(
            rng.integers(
                1,
                purchased_quantity + 1,
            )
        )

        order_id = int(
            item["order_id"]
        )

        delivery_timestamp = (
            delivery_lookup[
                order_id
            ]
        )

        return_timestamp = (
            delivery_timestamp
            + pd.Timedelta(
                days=int(
                    rng.integers(
                        1,
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

        return_reason = (
            choose_return_reason(
                rng,
                category_name,
            )
        )

        unit_cogs = float(
            item["unit_cogs"]
        )

        return_cost = round(
            returned_quantity
            * unit_cogs
            * float(
                rng.uniform(
                    0.05,
                    0.20,
                )
            ),
            2,
        )

        rows.append({
            "return_id": return_id,
            "order_id": order_id,
            "order_line_id": int(
                item["order_line_id"]
            ),
            "return_timestamp":
                return_timestamp,
            "returned_quantity":
                returned_quantity,
            "return_reason":
                return_reason,
            "return_cost":
                return_cost,
            "currency_code":
                config.CURRENCY_CODE,
        })

        return_id += 1

    return pd.DataFrame(rows)


def validate_returns(
    returns: pd.DataFrame,
    items: pd.DataFrame,
    shipments: pd.DataFrame,
) -> None:

    assert returns[
        "return_id"
    ].is_unique

    assert returns[
        "return_id"
    ].notna().all()

    assert returns[
        "returned_quantity"
    ].gt(0).all()

    assert returns[
        "return_cost"
    ].ge(0).all()

    assert returns[
        "currency_code"
    ].eq(
        config.CURRENCY_CODE
    ).all()

    # order_line_id -> purchased quantity
    quantity_lookup = {
        int(row["order_line_id"]):
            int(row["quantity"])
        for row
        in items.to_dict("records")
    }

    for row in returns.to_dict(
        "records"
    ):

        line_id = int(
            row["order_line_id"]
        )

        purchased_quantity = (
            quantity_lookup[
                line_id
            ]
        )

        returned_quantity = int(
            row["returned_quantity"]
        )

        assert (
            returned_quantity
            <= purchased_quantity
        )

    # order_id -> delivery timestamp
    delivery_lookup = {
        int(row["order_id"]):
            pd.Timestamp(
                row[
                    "actual_delivery_timestamp"
                ]
            )
        for row
        in shipments[
            shipments[
                "actual_delivery_timestamp"
            ].notna()
        ].to_dict("records")
    }

    for row in returns.to_dict(
        "records"
    ):

        order_id = int(
            row["order_id"]
        )

        delivery_timestamp = (
            delivery_lookup[
                order_id
            ]
        )

        return_timestamp = (
            pd.Timestamp(
                row["return_timestamp"]
            )
        )

        assert (
            return_timestamp
            >= delivery_timestamp
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

    items = pd.read_csv(
        os.path.join(
            generated_dir,
            "order_items.csv",
        )
    )

    shipments = pd.read_csv(
        os.path.join(
            generated_dir,
            "shipments.csv",
        )
    )

    returns = generate_returns()

    validate_returns(
        returns,
        items,
        shipments,
    )

    output_path = os.path.join(
        generated_dir,
        "returns.csv",
    )

    returns.to_csv(
        output_path,
        index=False,
    )

    print()

    print(
        "NovaMart v0.4b — Returns "
        "generated successfully"
    )

    print("=" * 60)

    print(
        f"Return rows: "
        f"{len(returns):,}"
    )

    print()
    print("Return reasons:")

    print(
        returns[
            "return_reason"
        ]
        .value_counts()
        .to_string()
    )

    print()
    print(
        "Average returned quantity:"
    )

    print(
        f"{returns['returned_quantity'].mean():.2f}"
    )

    print()
    print(
        "Total return handling cost:"
    )

    print(
        f"EUR "
        f"{returns['return_cost'].sum():,.2f}"
    )

    print()
    print(
        f"File created: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()