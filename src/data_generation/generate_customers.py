"""
NovaMart Synthetic Data Generator — v0.1c: Customers

Generates:
1. customers.csv
   - matches the SQL customers table

2. helpers/customer_profiles.csv
   - generator-only behavioral segment file
   - used later when generating orders

Run:
    python src/data_generation/generate_customers.py
"""

import os

import numpy as np
import pandas as pd

import config


def generate_country_ids(
    rng: np.random.Generator,
    size: int,
) -> np.ndarray:
    """Assign customers to countries using configured country weights."""

    country_ids = np.arange(1, len(config.COUNTRIES) + 1)

    weights = np.array(
        [country["order_share"] for country in config.COUNTRIES],
        dtype=float,
    )

    weights = weights / weights.sum()

    return rng.choice(
        country_ids,
        size=size,
        p=weights,
    )


def generate_signup_dates(
    rng: np.random.Generator,
    size: int,
) -> pd.Series:
    """
    Generate signup dates across the 24-month project period.

    Customer acquisition gradually increases over time instead of
    being perfectly flat.
    """

    start_date = pd.Timestamp(config.START_DATE)
    end_date = pd.Timestamp(config.END_DATE)

    months = pd.date_range(
        start=start_date,
        end=end_date,
        freq="MS",
    )

    # Slight gradual growth in customer acquisition.
    month_weights = np.linspace(0.8, 1.2, len(months))
    month_weights = month_weights / month_weights.sum()

    selected_months = rng.choice(
        months,
        size=size,
        p=month_weights,
    )

    signup_dates = []

    for selected_month in selected_months:
        month = pd.Timestamp(selected_month)

        month_end = month + pd.offsets.MonthEnd(0)

        effective_start = max(month, start_date)
        effective_end = min(month_end, end_date)

        available_days = (
            effective_end - effective_start
        ).days + 1

        day_offset = rng.integers(
            0,
            available_days,
        )

        signup_date = effective_start + pd.Timedelta(
            days=int(day_offset)
        )

        signup_dates.append(signup_date.date())

    return pd.Series(signup_dates)


def generate_age_groups(
    rng: np.random.Generator,
    size: int,
) -> np.ndarray:
    """Generate age groups using configured demographic shares."""

    labels = [
        age["label"]
        for age in config.AGE_GROUPS
    ]

    weights = [
        age["share"]
        for age in config.AGE_GROUPS
    ]

    return rng.choice(
        labels,
        size=size,
        p=weights,
    )


def generate_genders(
    rng: np.random.Generator,
    size: int,
) -> np.ndarray:
    """Generate gender values using configured demographic shares."""

    labels = list(
        config.GENDER_DISTRIBUTION.keys()
    )

    weights = list(
        config.GENDER_DISTRIBUTION.values()
    )

    return rng.choice(
        labels,
        size=size,
        p=weights,
    )


def generate_segments(
    rng: np.random.Generator,
    size: int,
) -> np.ndarray:
    """
    Generate customer purchase-frequency segments.

    These segments are NOT part of the SQL customers table.
    They are stored separately for later order generation.
    """

    names = [
        segment["name"]
        for segment in config.CUSTOMER_SEGMENTS
    ]

    weights = [
        segment["share"]
        for segment in config.CUSTOMER_SEGMENTS
    ]

    return rng.choice(
        names,
        size=size,
        p=weights,
    )


def generate_customers() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate SQL-compatible customers and generator-only customer profiles.
    """

    # Local RNG ensures this script is reproducible independently.
    rng = np.random.default_rng(config.RANDOM_SEED)

    n = config.N_CUSTOMERS

    customer_ids = np.arange(
        1,
        n + 1,
    )

    customers = pd.DataFrame({
        "customer_id": customer_ids,
        "signup_date": generate_signup_dates(rng, n),
        "country_id": generate_country_ids(rng, n),
        "age_group": generate_age_groups(rng, n),
        "gender": generate_genders(rng, n),
    })

    customer_profiles = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_segment": generate_segments(rng, n),
    })

    return customers, customer_profiles


def validate_customers(
    customers: pd.DataFrame,
    profiles: pd.DataFrame,
) -> None:
    """Basic v0.1c validation checks."""

    assert len(customers) == config.N_CUSTOMERS
    assert len(profiles) == config.N_CUSTOMERS

    assert customers["customer_id"].is_unique
    assert profiles["customer_id"].is_unique

    assert customers["customer_id"].notna().all()
    assert customers["signup_date"].notna().all()
    assert customers["country_id"].notna().all()
    assert customers["age_group"].notna().all()
    assert customers["gender"].notna().all()

    assert customers["country_id"].between(
        1,
        len(config.COUNTRIES),
    ).all()

    start_date = pd.Timestamp(
        config.START_DATE
    ).date()

    end_date = pd.Timestamp(
        config.END_DATE
    ).date()

    assert customers["signup_date"].between(
        start_date,
        end_date,
    ).all()

    valid_age_groups = {
        age["label"]
        for age in config.AGE_GROUPS
    }

    assert set(
        customers["age_group"].unique()
    ).issubset(valid_age_groups)

    valid_genders = set(
        config.GENDER_DISTRIBUTION.keys()
    )

    assert set(
        customers["gender"].unique()
    ).issubset(valid_genders)

    valid_segments = {
        segment["name"]
        for segment in config.CUSTOMER_SEGMENTS
    }

    assert set(
        profiles["customer_segment"].unique()
    ).issubset(valid_segments)


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

    helper_dir = os.path.join(
        output_dir,
        "helpers",
    )

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    os.makedirs(
        helper_dir,
        exist_ok=True,
    )

    customers, profiles = generate_customers()

    validate_customers(
        customers,
        profiles,
    )

    customers_path = os.path.join(
        output_dir,
        "customers.csv",
    )

    profiles_path = os.path.join(
        helper_dir,
        "customer_profiles.csv",
    )

    customers.to_csv(
        customers_path,
        index=False,
    )

    profiles.to_csv(
        profiles_path,
        index=False,
    )

    print()
    print("NovaMart v0.1c — Customers generated successfully")
    print("=" * 60)
    print(f"Customers: {len(customers):,}")

    # ---------------------------------------------------------
    # Country distribution
    # ---------------------------------------------------------

    countries_lookup = pd.DataFrame([
        {
            "country_id": i + 1,
            "country_name": country["name"],
        }
        for i, country in enumerate(config.COUNTRIES)
    ])

    country_summary = (
        customers
        .merge(
            countries_lookup,
            on="country_id",
        )
        .groupby("country_name")
        .size()
        .sort_values(ascending=False)
    )

    print()
    print("Country distribution:")
    print(country_summary.to_string())

    # ---------------------------------------------------------
    # Age groups
    # ---------------------------------------------------------

    print()
    print("Age-group distribution (%):")

    age_summary = (
        customers["age_group"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    print(age_summary.to_string())

    # ---------------------------------------------------------
    # Gender
    # ---------------------------------------------------------

    print()
    print("Gender distribution (%):")

    gender_summary = (
        customers["gender"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    print(gender_summary.to_string())

    # ---------------------------------------------------------
    # Behavioral segments
    # ---------------------------------------------------------

    print()
    print("Customer segments (%):")

    segment_summary = (
        profiles["customer_segment"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    print(segment_summary.to_string())

    print()
    print("Signup period:")
    print(
        f"{customers['signup_date'].min()} "
        f"→ {customers['signup_date'].max()}"
    )

    print()
    print("Files created:")
    print(f"  {customers_path}")
    print(f"  {profiles_path}")


if __name__ == "__main__":
    main()