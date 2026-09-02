"""
NovaMart Synthetic Data Generator — v0.2a: Orders

Generates:
    data/generated/orders.csv

Uses:
    data/generated/customers.csv
    data/generated/helpers/customer_profiles.csv
    data/generated/promotions.csv

Run:
    python src/data_generation/generate_orders.py
"""

import os

import numpy as np
import pandas as pd

import config


def load_inputs(project_root: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    generated_dir = os.path.join(project_root, "data", "generated")
    helper_dir = os.path.join(generated_dir, "helpers")

    customers = pd.read_csv(
        os.path.join(generated_dir, "customers.csv"),
        parse_dates=["signup_date"],
    )

    profiles = pd.read_csv(
        os.path.join(helper_dir, "customer_profiles.csv")
    )

    promotions = pd.read_csv(
        os.path.join(generated_dir, "promotions.csv"),
        parse_dates=[
            "promotion_start_date",
            "promotion_end_date",
        ],
    )

    return customers, profiles, promotions


def build_customer_order_weights(
    customers: pd.DataFrame,
    profiles: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Loyal/frequent customers should contribute more orders than one-time customers.
    """

    merged = customers.merge(
        profiles,
        on="customer_id",
        how="inner",
        validate="one_to_one",
    )

    segment_weight = {
        "one_time": 1.0,
        "occasional": 3.0,
        "frequent": 7.0,
        "loyal": 14.0,
    }

    weights = (
        merged["customer_segment"]
        .map(segment_weight)
        .astype(float)
        .to_numpy()
    )

    weights = weights / weights.sum()

    return merged["customer_id"].to_numpy(), weights


def generate_order_timestamps(
    rng: np.random.Generator,
    size: int,
) -> pd.Series:
    """
    Generate orders across the 24-month period using the configured
    growth curve plus seasonality.
    """

    start_date = pd.Timestamp(config.START_DATE)
    end_date = pd.Timestamp(config.END_DATE)

    months = pd.date_range(
        start=start_date,
        end=end_date,
        freq="MS",
    )

    monthly_weights = config.monthly_growth_curve(len(months)).astype(float)

    # Layer in seasonality:
    # Nov/Dec stronger, Jul/Aug weaker.
    for i, month in enumerate(months):
        if month.month == 11:
            monthly_weights[i] *= 1.30
        elif month.month == 12:
            monthly_weights[i] *= 1.40
        elif month.month in (7, 8):
            monthly_weights[i] *= 0.88
        elif month.month == 1:
            monthly_weights[i] *= 0.90

    monthly_weights = monthly_weights / monthly_weights.sum()

    selected_months = rng.choice(
        months,
        size=size,
        p=monthly_weights,
    )

    timestamps: list[pd.Timestamp] = []

    for selected_month in selected_months:
        month = pd.Timestamp(selected_month)
        month_end = month + pd.offsets.MonthEnd(0)

        effective_start = max(month, start_date)
        effective_end = min(month_end, end_date)

        available_days = (effective_end - effective_start).days + 1

        day_offset = int(
            rng.integers(
                0,
                available_days,
            )
        )

        hour = int(rng.integers(8, 23))
        minute = int(rng.integers(0, 60))
        second = int(rng.integers(0, 60))

        timestamp = (
            effective_start
            + pd.Timedelta(days=day_offset)
            + pd.Timedelta(
                hours=hour,
                minutes=minute,
                seconds=second,
            )
        )

        timestamps.append(timestamp)

    return pd.Series(timestamps)


def generate_statuses(
    rng: np.random.Generator,
    size: int,
) -> np.ndarray:
    statuses = list(config.ORDER_STATUS_SHARE.keys())
    weights = list(config.ORDER_STATUS_SHARE.values())

    return rng.choice(
        statuses,
        size=size,
        p=weights,
    )


def assign_promotions(
    rng: np.random.Generator,
    order_timestamps: pd.Series,
    promotions: pd.DataFrame,
) -> list[int | None]:
    """
    Not every order has a promotion.
    Promotion must be active on the order date.
    """

    promotion_ids: list[int | None] = []

    for timestamp in order_timestamps:
        order_date = pd.Timestamp(timestamp).normalize()

        active = promotions[
            (promotions["promotion_start_date"] <= order_date)
            & (promotions["promotion_end_date"] >= order_date)
        ]

        # Around 28% of eligible orders use a promotion.
        if len(active) > 0 and rng.random() < 0.30:
            promotion_id = int(
                rng.choice(
                    active["promotion_id"].to_numpy()
                )
            )
            promotion_ids.append(promotion_id)
        else:
            promotion_ids.append(None)

    return promotion_ids


def generate_orders() -> pd.DataFrame:
    rng = np.random.default_rng(config.RANDOM_SEED + 100)

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    customers, profiles, promotions = load_inputs(project_root)

    customer_ids, customer_weights = build_customer_order_weights(
        customers,
        profiles,
    )

    n = config.N_ORDERS_TARGET

    selected_customer_ids = rng.choice(
        customer_ids,
        size=n,
        p=customer_weights,
        replace=True,
    )

    order_timestamps = generate_order_timestamps(
        rng,
        n,
    )

    statuses = generate_statuses(
        rng,
        n,
    )

    promotion_ids = assign_promotions(
        rng,
        order_timestamps,
        promotions,
    )

    customer_country_lookup = (
        customers
        .set_index("customer_id")["country_id"]
        .to_dict()
    )

    country_ids = [
        int(customer_country_lookup[int(customer_id)])
        for customer_id in selected_customer_ids
    ]

    cancellation_reasons: list[str | None] = []

    for status in statuses:
        if status == "cancelled":
            cancellation_reasons.append(
                str(
                    rng.choice(
                        config.CANCELLATION_REASONS
                    )
                )
            )
        else:
            cancellation_reasons.append(None)

    orders = pd.DataFrame({
        "order_id": np.arange(1, n + 1),
        "customer_id": selected_customer_ids,
        "order_timestamp": order_timestamps,
        "status": statuses,
        "cancellation_reason": cancellation_reasons,
        "country_id": country_ids,
        "promotion_id": promotion_ids,
        "currency_code": config.CURRENCY_CODE,
    })

    return orders


def validate_orders(
    orders: pd.DataFrame,
) -> None:
    assert len(orders) == config.N_ORDERS_TARGET
    assert orders["order_id"].is_unique
    assert orders["order_id"].notna().all()

    assert orders["customer_id"].notna().all()
    assert orders["country_id"].notna().all()

    assert orders["currency_code"].eq(
        config.CURRENCY_CODE
    ).all()

    assert set(
        orders["status"].unique()
    ).issubset(
        set(config.ORDER_STATUS_SHARE.keys())
    )

    cancelled = orders["status"].eq("cancelled")
    non_cancelled = ~cancelled

    assert orders.loc[
        cancelled,
        "cancellation_reason",
    ].notna().all()

    assert orders.loc[
        non_cancelled,
        "cancellation_reason",
    ].isna().all()

    start_date = pd.Timestamp(config.START_DATE)
    end_date = pd.Timestamp(config.END_DATE) + pd.Timedelta(days=1)

    assert orders["order_timestamp"].between(
        start_date,
        end_date,
        inclusive="left",
    ).all()


def main() -> None:
    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    output_dir = os.path.join(
        project_root,
        "data",
        "generated",
    )

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    orders = generate_orders()

    validate_orders(orders)

    output_path = os.path.join(
        output_dir,
        "orders.csv",
    )

    orders.to_csv(
        output_path,
        index=False,
    )

    print()
    print("NovaMart v0.2a — Orders generated successfully")
    print("=" * 60)

    print(f"Orders: {len(orders):,}")

    print()
    print("Status distribution (%):")
    print(
        orders["status"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .to_string()
    )

    print()
    print("Orders by country:")
    print(
        orders["country_id"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print("Promotion usage:")
    promo_share = (
        orders["promotion_id"]
        .notna()
        .mean()
        * 100
    )

    print(f"{promo_share:.2f}% of orders")

    print()
    print("Order date range:")
    print(
        f"{orders['order_timestamp'].min()} "
        f"→ {orders['order_timestamp'].max()}"
    )

    print()
    print(f"File created: {output_path}")


if __name__ == "__main__":
    main()