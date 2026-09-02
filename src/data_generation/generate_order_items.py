"""
NovaMart Synthetic Data Generator — v0.2b: Order Items

Generates:
    data/generated/order_items.csv

Uses:
    data/generated/orders.csv
    data/generated/products.csv
    data/generated/promotions.csv

Run:
    python src/data_generation/generate_order_items.py
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
        os.path.join(
            generated_dir,
            "orders.csv",
        ),
        parse_dates=["order_timestamp"],
    )

    products = pd.read_csv(
        os.path.join(
            generated_dir,
            "products.csv",
        )
    )

    promotions = pd.read_csv(
        os.path.join(
            generated_dir,
            "promotions.csv",
        )
    )

    return orders, products, promotions


def get_product_weights(
    products: pd.DataFrame,
) -> np.ndarray:
    """
    Use the Pareto-like popularity weights already generated
    in products.csv.
    """

    weights = (
        products["popularity_weight"]
        .astype(float)
        .to_numpy()
    )

    return weights / weights.sum()
    """
    Build Pareto-like product popularity.

    Top ~20% of products receive ~70% of purchase probability.
    """

    n_products = len(products)

    top_count = int(
        round(
            n_products
            * config.PARETO_TOP_SHARE_OF_PRODUCTS
        )
    )

    top_count = max(1, top_count)

    remaining_count = (
        n_products - top_count
    )

    weights = np.zeros(
        n_products,
        dtype=float,
    )

    weights[:top_count] = (
        config.PARETO_TOP_SHARE_OF_REVENUE_WEIGHT
        / top_count
    )

    if remaining_count > 0:
        weights[top_count:] = (
            1
            - config.PARETO_TOP_SHARE_OF_REVENUE_WEIGHT
        ) / remaining_count

    return weights / weights.sum()


def generate_basket_sizes(
    rng: np.random.Generator,
    n_orders: int,
) -> np.ndarray:

    basket_sizes = np.array(
        list(config.BASKET_SIZE_WEIGHTS.keys())
    )

    weights = np.array(
        list(config.BASKET_SIZE_WEIGHTS.values()),
        dtype=float,
    )

    return rng.choice(
        basket_sizes,
        size=n_orders,
        p=weights,
    )


def generate_quantity(
    rng: np.random.Generator,
) -> int:

    quantities = np.array(
        list(config.QUANTITY_WEIGHTS.keys())
    )

    weights = np.array(
        list(config.QUANTITY_WEIGHTS.values()),
        dtype=float,
    )

    return int(
        rng.choice(
            quantities,
            p=weights,
        )
    )


def build_product_lookup(
    products: pd.DataFrame,
) -> dict[int, dict]:

    lookup: dict[int, dict] = {}

    for row in products.to_dict("records"):
        lookup[int(row["product_id"])] = row

    return lookup


def get_price_columns(
    product: dict,
) -> tuple[float, float]:
    """
    products.csv should contain generated pricing helper columns.

    Expected:
    - original_unit_price
    - unit_cogs

    If your product generator used slightly different helper names,
    this function is the one place to change them.
    """

    original_price = float(
        product["base_price"]
    )

    unit_cogs = float(
        product["unit_cogs_base"]
    )

    return original_price, unit_cogs


def calculate_line_prices(
    rng: np.random.Generator,
    original_price: float,
    quantity: int,
    promotion: dict | None,
) -> tuple[float, float]:
    """
    Returns:
        unit_price
        line_discount

    Definitions:
    original_unit_price = list price
    unit_price = post-markdown selling price before line discount
    line_discount = additional total discount on this order line
    """

    # Small normal markdown behavior even without promotion.
    markdown_probability = 0.18

    if rng.random() < markdown_probability:
        markdown_rate = float(
            rng.uniform(
                0.03,
                0.12,
            )
        )
    else:
        markdown_rate = 0.0

    unit_price = (
        original_price
        * (1 - markdown_rate)
    )

    line_discount = 0.0

    if promotion is not None:

        discount_type = promotion[
            "discount_type"
        ]

        discount_amount = float(
            promotion["discount_amount"]
        )

        if discount_type == "percentage":

            promo_rate = min(
                discount_amount / 100.0,
                0.80,
            )

            line_discount = (
                unit_price
                * quantity
                * promo_rate
            )

        elif discount_type == "fixed_amount":

            line_value = (
                unit_price
                * quantity
            )

            line_discount = min(
                discount_amount,
                line_value * 0.80,
            )

    unit_price = round(
        unit_price,
        2,
    )

    line_discount = round(
        line_discount,
        2,
    )

    return unit_price, line_discount


def generate_order_items() -> pd.DataFrame:

    rng = np.random.default_rng(
        config.RANDOM_SEED + 200
    )

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    orders, products, promotions = load_inputs(
        project_root
    )

    product_ids = (
        products["product_id"]
        .astype(int)
        .to_numpy()
    )

    product_weights = get_product_weights(
        products
    )

    product_lookup = build_product_lookup(
        products
    )

    promotion_lookup = {
        int(row["promotion_id"]): row
        for row in promotions.to_dict("records")
    }

    basket_sizes = generate_basket_sizes(
        rng,
        len(orders),
    )

    rows = []

    order_line_id = 1

    for order, basket_size in zip(
        orders.to_dict("records"),
        basket_sizes,
    ):

        # Avoid duplicate products inside one order where possible.
        selected_product_ids = rng.choice(
            product_ids,
            size=int(basket_size),
            replace=False,
            p=product_weights,
        )

        promotion = None

        if pd.notna(
            order["promotion_id"]
        ):
            promotion = promotion_lookup[
                int(order["promotion_id"])
            ]

        for product_id in selected_product_ids:

            product = product_lookup[
                int(product_id)
            ]

            quantity = generate_quantity(
                rng
            )

            original_price, unit_cogs = (
                get_price_columns(
                    product
                )
            )

            unit_price, line_discount = (
                calculate_line_prices(
                    rng=rng,
                    original_price=original_price,
                    quantity=quantity,
                    promotion=promotion,
                )
            )

            rows.append({
                "order_line_id": order_line_id,
                "order_id": int(
                    order["order_id"]
                ),
                "product_id": int(
                    product_id
                ),
                "quantity": quantity,
                "original_unit_price": round(
                    original_price,
                    2,
                ),
                "unit_price": unit_price,
                "line_discount": line_discount,
                "unit_cogs": round(
                    unit_cogs,
                    2,
                ),
            })

            order_line_id += 1

    return pd.DataFrame(rows)


def validate_order_items(
    items: pd.DataFrame,
    orders: pd.DataFrame,
    products: pd.DataFrame,
) -> None:

    assert items[
        "order_line_id"
    ].is_unique

    assert items[
        "order_line_id"
    ].notna().all()

    assert items[
        "quantity"
    ].gt(0).all()

    assert items[
        "original_unit_price"
    ].ge(0).all()

    assert items[
        "unit_price"
    ].ge(0).all()

    assert items[
        "unit_cogs"
    ].ge(0).all()

    assert items[
        "line_discount"
    ].ge(0).all()

    valid_order_ids = set(
        orders["order_id"]
        .astype(int)
    )

    assert set(
        items["order_id"]
    ).issubset(
        valid_order_ids
    )

    valid_product_ids = set(
        products["product_id"]
        .astype(int)
    )

    assert set(
        items["product_id"]
    ).issubset(
        valid_product_ids
    )

    final_line_value = (
        items["unit_price"]
        * items["quantity"]
        - items["line_discount"]
    )

    assert final_line_value.ge(0).all()


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

    products = pd.read_csv(
        os.path.join(
            generated_dir,
            "products.csv",
        )
    )

    items = generate_order_items()

    validate_order_items(
        items,
        orders,
        products,
    )

    output_path = os.path.join(
        generated_dir,
        "order_items.csv",
    )

    items.to_csv(
        output_path,
        index=False,
    )

    print()
    print(
        "NovaMart v0.2b — Order Items generated successfully"
    )
    print("=" * 60)

    print(
        f"Order lines: {len(items):,}"
    )

    print()
    print("Average lines per order:")

    avg_lines = (
        len(items)
        / len(orders)
    )

    print(
        f"{avg_lines:.2f}"
    )

    print()
    print("Quantity distribution (%):")

    print(
        items["quantity"]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(2)
        .to_string()
    )

    print()
    print("Revenue concentration:")

    revenue_by_product = (
        items.assign(
            line_revenue=(
                items["unit_price"]
                * items["quantity"]
                - items["line_discount"]
            )
        )
        .groupby("product_id")[
            "line_revenue"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    top_n = max(
        1,
        int(
            len(products)
            * config.PARETO_TOP_SHARE_OF_PRODUCTS
        )
    )

    concentration = (
        revenue_by_product.head(
            top_n
        ).sum()
        / revenue_by_product.sum()
        * 100
    )

    print(
        f"Top 20% products generate "
        f"{concentration:.2f}% of merchandise revenue"
    )

    print()
    print(
        f"File created: {output_path}"
    )


if __name__ == "__main__":
    main()