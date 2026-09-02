"""
NovaMart Synthetic Data Generator — v0.4a: Shipments

Generates:
    data/generated/shipments.csv

Uses:
    data/generated/orders.csv
    data/generated/warehouses.csv
    data/generated/carriers.csv

Run:
    python src/data_generation/generate_shipments.py
"""

import os

import numpy as np
import pandas as pd

import config


def load_inputs(
    project_root: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    generated_dir = os.path.join(
        project_root,
        "data",
        "generated",
    )

    orders = pd.read_csv(
        os.path.join(generated_dir, "orders.csv"),
        parse_dates=["order_timestamp"],
    )

    warehouses = pd.read_csv(
        os.path.join(generated_dir, "warehouses.csv")
    )

    carriers = pd.read_csv(
        os.path.join(generated_dir, "carriers.csv")
    )

    return orders, warehouses, carriers


def choose_warehouse(
    rng: np.random.Generator,
    order_country_id: int,
    warehouses: pd.DataFrame,
) -> int:
    """
    Prefer a warehouse in the same country.
    Occasionally allow cross-border fulfillment.
    """

    local = warehouses[
        warehouses["country_id"] == order_country_id
    ]

    if len(local) > 0 and rng.random() < 0.88:
        return int(
            rng.choice(
                local["warehouse_id"].to_numpy()
            )
        )

    return int(
        rng.choice(
            warehouses["warehouse_id"].to_numpy()
        )
    )


def choose_carrier(
    rng: np.random.Generator,
) -> int:
    """
    Carrier 6 is a lower-volume backup carrier.
    """

    carrier_ids = np.arange(
        1,
        len(config.CARRIERS) + 1,
    )

    weights = np.array([
        0.20,
        0.19,
        0.20,
        0.18,
        0.18,
        0.05,
    ])

    return int(
        rng.choice(
            carrier_ids,
            p=weights,
        )
    )


def generate_shipments() -> pd.DataFrame:

    rng = np.random.default_rng(
        config.RANDOM_SEED + 500
    )

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    orders, warehouses, carriers = load_inputs(
        project_root
    )

    # Orders that logically may have a shipment.
    eligible_statuses = {
        "fulfilled",
        "shipped",
        "delivered",
    }

    eligible_orders = orders[
        orders["status"].isin(
            eligible_statuses
        )
    ].copy()

    rows = []

    shipment_id = 1

    for order in eligible_orders.to_dict("records"):

        order_timestamp = pd.Timestamp(
            order["order_timestamp"]
        )

        country_id = int(
            order["country_id"]
        )

        warehouse_id = choose_warehouse(
            rng,
            country_id,
            warehouses,
        )

        carrier_id = choose_carrier(
            rng
        )

        carrier_profile = config.CARRIERS[
            carrier_id - 1
        ]

        # Fulfillment usually takes 0–2 days.
        fulfillment_days = int(
            rng.choice(
                [0, 1, 2],
                p=[0.15, 0.65, 0.20],
            )
        )

        shipped_timestamp = (
            order_timestamp
            + pd.Timedelta(
                days=fulfillment_days,
                hours=int(
                    rng.integers(
                        2,
                        18,
                    )
                ),
            )
        )

        speed_mean = float(
            carrier_profile[
                "speed_days_mean"
            ]
        )

        speed_sd = float(
            carrier_profile[
                "speed_days_sd"
            ]
        )

        estimated_days = max(
            1,
            int(
                round(
                    rng.normal(
                        speed_mean,
                        speed_sd,
                    )
                )
            ),
        )

        estimated_delivery_timestamp = (
            shipped_timestamp
            + pd.Timedelta(
                days=estimated_days
            )
        )

        actual_delivery_timestamp = pd.NaT

        if order["status"] == "delivered":

            on_time_rate = float(
                carrier_profile[
                    "on_time_rate"
                ]
            )

            country_code = config.COUNTRIES[
                country_id - 1
            ]["code"]

            carrier_name = str(
                carrier_profile["name"]
            )

            bonus = (
                config.CARRIER_COUNTRY_BONUS
                .get(
                    carrier_name,
                    {},
                )
                .get(
                    country_code,
                    0.0,
                )
            )

            effective_on_time_rate = min(
                0.99,
                max(
                    0.50,
                    on_time_rate + bonus,
                ),
            )

            if rng.random() < effective_on_time_rate:
                delivery_shift_days = int(
                    rng.choice(
                        [-1, 0],
                        p=[0.20, 0.80],
                    )
                )
            else:
                delivery_shift_days = int(
                    rng.integers(
                        1,
                        5,
                    )
                )

            actual_delivery_timestamp = (
                estimated_delivery_timestamp
                + pd.Timedelta(
                    days=delivery_shift_days,
                    hours=int(
                        rng.integers(
                            -4,
                            5,
                        )
                    ),
                )
            )

            # Safety guard:
            # actual delivery must never precede shipment.
            if (
                actual_delivery_timestamp
                < shipped_timestamp
            ):
                actual_delivery_timestamp = (
                    shipped_timestamp
                    + pd.Timedelta(hours=1)
                )

        base_shipping_cost = float(
            rng.uniform(
                4.0,
                12.0,
            )
        )

        shipping_cost = round(
            base_shipping_cost
            * float(
                carrier_profile[
                    "cost_multiplier"
                ]
            ),
            2,
        )

        rows.append({
            "shipment_id": shipment_id,
            "order_id": int(
                order["order_id"]
            ),
            "warehouse_id": warehouse_id,
            "carrier_id": carrier_id,
            "shipped_timestamp": shipped_timestamp,
            "estimated_delivery_timestamp": (
                estimated_delivery_timestamp
            ),
            "actual_delivery_timestamp": (
                actual_delivery_timestamp
            ),
            "shipping_cost": shipping_cost,
            "currency_code": config.CURRENCY_CODE,
        })

        shipment_id += 1

    return pd.DataFrame(rows)


def validate_shipments(
    shipments: pd.DataFrame,
    orders: pd.DataFrame,
    warehouses: pd.DataFrame,
    carriers: pd.DataFrame,
) -> None:

    assert shipments[
        "shipment_id"
    ].is_unique

    assert shipments[
        "shipment_id"
    ].notna().all()

    assert shipments[
        "order_id"
    ].notna().all()

    assert shipments[
        "warehouse_id"
    ].notna().all()

    assert shipments[
        "carrier_id"
    ].notna().all()

    assert shipments[
        "shipping_cost"
    ].ge(0).all()

    assert shipments[
        "currency_code"
    ].eq(
        config.CURRENCY_CODE
    ).all()

    valid_order_ids = set(
        orders["order_id"]
        .astype(int)
    )

    assert set(
        shipments["order_id"]
        .astype(int)
    ).issubset(
        valid_order_ids
    )

    valid_warehouse_ids = set(
        warehouses["warehouse_id"]
        .astype(int)
    )

    assert set(
        shipments["warehouse_id"]
        .astype(int)
    ).issubset(
        valid_warehouse_ids
    )

    valid_carrier_ids = set(
        carriers["carrier_id"]
        .astype(int)
    )

    assert set(
        shipments["carrier_id"]
        .astype(int)
    ).issubset(
        valid_carrier_ids
    )

    delivered = shipments[
        "actual_delivery_timestamp"
    ].notna()

    delivered_rows = shipments[
        delivered
    ]

    assert (
        pd.to_datetime(
            delivered_rows[
                "actual_delivery_timestamp"
            ]
        )
        >= pd.to_datetime(
            delivered_rows[
                "shipped_timestamp"
            ]
        )
    ).all()


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

    warehouses = pd.read_csv(
        os.path.join(
            generated_dir,
            "warehouses.csv",
        )
    )

    carriers = pd.read_csv(
        os.path.join(
            generated_dir,
            "carriers.csv",
        )
    )

    shipments = generate_shipments()

    validate_shipments(
        shipments,
        orders,
        warehouses,
        carriers,
    )

    output_path = os.path.join(
        generated_dir,
        "shipments.csv",
    )

    shipments.to_csv(
        output_path,
        index=False,
    )

    print()
    print(
        "NovaMart v0.4a — Shipments generated successfully"
    )
    print("=" * 60)

    print(
        f"Shipment rows: {len(shipments):,}"
    )

    print()
    print("Delivered shipments:")

    delivered_count = (
        shipments[
            "actual_delivery_timestamp"
        ]
        .notna()
        .sum()
    )

    print(
        f"{delivered_count:,}"
    )

    print()
    print("Average shipping cost:")

    print(
        f"EUR "
        f"{shipments['shipping_cost'].mean():,.2f}"
    )

    print()
    print("Carrier distribution:")

    print(
        shipments[
            "carrier_id"
        ]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print(
        f"File created: {output_path}"
    )


if __name__ == "__main__":
    main()