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


def load_inputs(project_root: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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

    promotion_profiles = pd.read_csv(
        os.path.join(helper_dir, "promotion_profiles.csv")
    )

    return customers, profiles, promotions, promotion_profiles


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


def assign_customers_by_signup(
    rng: np.random.Generator,
    order_timestamps: pd.Series,
    customers: pd.DataFrame,
    profiles: pd.DataFrame,
) -> np.ndarray:
    """Assign each existing order timestamp only to customers already signed up.

    Segment weights are preserved, but the eligible customer pool is constrained
    by ``signup_date <= order_date``. Grouping by order date keeps the operation
    efficient while preserving deterministic weighted sampling.
    """

    merged = customers.merge(
        profiles,
        on="customer_id",
        how="inner",
        validate="one_to_one",
    ).copy()

    segment_weight = {
        "one_time": 1.0,
        "occasional": 3.0,
        "frequent": 7.0,
        "loyal": 14.0,
    }
    merged["order_weight"] = (
        merged["customer_segment"].map(segment_weight).astype(float)
    )
    merged["signup_date"] = pd.to_datetime(merged["signup_date"]).dt.normalize()

    selected = np.empty(len(order_timestamps), dtype=int)
    order_days = pd.to_datetime(order_timestamps).dt.normalize()

    for order_day, indexes in order_days.groupby(order_days).groups.items():
        eligible = merged[merged["signup_date"] <= pd.Timestamp(order_day)]
        if eligible.empty:
            raise RuntimeError(
                f"No signed-up customers available for order date {order_day}."
            )

        weights = eligible["order_weight"].to_numpy(dtype=float)
        weights = weights / weights.sum()
        selected[list(indexes)] = rng.choice(
            eligible["customer_id"].to_numpy(dtype=int),
            size=len(indexes),
            replace=True,
            p=weights,
        )

    return selected


def generate_order_timestamps(
    rng: np.random.Generator,
    size: int,
    promotions: pd.DataFrame,
    promotion_profiles: pd.DataFrame,
) -> pd.Series:
    """Generate orders across the 24-month period.

    Base demand follows the configured growth curve and seasonality. Active
    promotions additionally raise date-level demand weight according to their
    synthetic archetype. Overlapping promotions use the strongest active
    multiplier (rather than multiplying effects) to avoid unrealistic spikes.
    """

    start_date = pd.Timestamp(config.START_DATE)
    end_date = pd.Timestamp(config.END_DATE)
    dates = pd.date_range(start_date, end_date, freq="D")

    months = pd.date_range(start=start_date, end=end_date, freq="MS")
    month_curve = config.monthly_growth_curve(len(months)).astype(float)
    month_weight = {month.to_period("M"): w for month, w in zip(months, month_curve)}

    profile_map = (
        promotion_profiles
        .set_index("promotion_id")["demand_multiplier"]
        .astype(float)
        .to_dict()
    )

    daily_weights = []
    for day in dates:
        weight = float(month_weight[day.to_period("M")])

        if day.month == 11:
            weight *= 1.30
        elif day.month == 12:
            weight *= 1.40
        elif day.month in (7, 8):
            weight *= 0.88
        elif day.month == 1:
            weight *= 0.90

        active = promotions[
            (promotions["promotion_start_date"] <= day)
            & (promotions["promotion_end_date"] >= day)
        ]
        if len(active):
            active_multipliers = [
                profile_map.get(int(pid), 1.0)
                for pid in active["promotion_id"]
            ]
            weight *= min(max(active_multipliers), 1.75)

        daily_weights.append(weight)

    daily_weights = np.asarray(daily_weights, dtype=float)
    daily_weights = daily_weights / daily_weights.sum()

    selected_days = rng.choice(dates, size=size, p=daily_weights)
    timestamps = []
    for selected_day in selected_days:
        day = pd.Timestamp(selected_day)
        timestamps.append(
            day
            + pd.Timedelta(hours=int(rng.integers(8, 23)))
            + pd.Timedelta(minutes=int(rng.integers(0, 60)))
            + pd.Timedelta(seconds=int(rng.integers(0, 60)))
        )

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
    promotion_profiles: pd.DataFrame,
) -> list[int | None]:
    """Assign active promotions using archetype-specific adoption rates."""

    profile = promotion_profiles.set_index("promotion_id")
    promotion_ids: list[int | None] = []

    for timestamp in order_timestamps:
        order_date = pd.Timestamp(timestamp).normalize()
        active = promotions[
            (promotions["promotion_start_date"] <= order_date)
            & (promotions["promotion_end_date"] >= order_date)
        ]

        if len(active) == 0:
            promotion_ids.append(None)
            continue

        active_ids = active["promotion_id"].astype(int).tolist()
        adoption_rates = np.array([
            float(profile.loc[pid, "adoption_rate"])
            for pid in active_ids
        ])
        # Use the strongest active adoption probability, capped for realism.
        adoption_probability = min(float(adoption_rates.max()), 0.65)

        if rng.random() < adoption_probability:
            demand_weights = np.array([
                float(profile.loc[pid, "demand_multiplier"])
                for pid in active_ids
            ])
            demand_weights = demand_weights / demand_weights.sum()
            promotion_ids.append(int(rng.choice(active_ids, p=demand_weights)))
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

    customers, profiles, promotions, promotion_profiles = load_inputs(project_root)

    n = config.N_ORDERS_TARGET

    order_timestamps = generate_order_timestamps(
        rng,
        n,
        promotions,
        promotion_profiles,
    )

    selected_customer_ids = assign_customers_by_signup(
        rng,
        order_timestamps,
        customers,
        profiles,
    )

    statuses = generate_statuses(
        rng,
        n,
    )

    promotion_ids = assign_promotions(
        rng,
        order_timestamps,
        promotions,
        promotion_profiles,
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
    customers: pd.DataFrame,
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

    lifecycle = orders.merge(
        customers[["customer_id", "signup_date"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )
    lifecycle["signup_date"] = pd.to_datetime(lifecycle["signup_date"])
    assert lifecycle["signup_date"].notna().all()
    assert (
        pd.to_datetime(lifecycle["order_timestamp"]).dt.normalize()
        >= lifecycle["signup_date"].dt.normalize()
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

    validate_orders(orders, customers)

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