"""
NovaMart Synthetic Data Generator — v0.1d: Promotions

Generates:
1. promotions.csv
   - matches the SQL promotions table

2. helpers/promotion_profiles.csv
   - generator-only promotion archetypes
   - used later when generating orders and promotion effects

Run:
    python src/data_generation/generate_promotions.py
"""

import os

import numpy as np
import pandas as pd

import config


def generate_archetypes(
    rng: np.random.Generator,
) -> list[str]:
    """
    Assign exactly 40 promotions across configured archetypes
    according to their locked shares.
    """

    archetypes: list[str] = []

    for archetype in config.PROMOTION_ARCHETYPES:
        count = round(
            archetype["share"] * config.N_PROMOTIONS
        )

        archetypes.extend(
            [archetype["name"]] * count
        )

    # Protect against rounding differences.
    while len(archetypes) < config.N_PROMOTIONS:
        archetypes.append(
            config.PROMOTION_ARCHETYPES[0]["name"]
        )

    archetypes = archetypes[
        :config.N_PROMOTIONS
    ]

    rng.shuffle(archetypes)

    return archetypes


def generate_promotion_dates(
    rng: np.random.Generator,
) -> tuple[list, list]:
    """
    Generate logically valid promotion date ranges
    within the dataset period.
    """

    start_boundary = pd.Timestamp(
        config.START_DATE
    )

    end_boundary = pd.Timestamp(
        config.END_DATE
    )

    start_dates = []
    end_dates = []

    total_days = (
        end_boundary - start_boundary
    ).days

    for _ in range(config.N_PROMOTIONS):

        start_offset = rng.integers(
            0,
            total_days + 1,
        )

        promotion_start = (
            start_boundary
            + pd.Timedelta(days=int(start_offset))
        )

        # Promotions normally last between 3 and 45 days.
        duration_days = int(
            rng.integers(3, 46)
        )

        promotion_end = (
            promotion_start
            + pd.Timedelta(days=duration_days)
        )

        # Never go outside dataset period.
        promotion_end = min(
            promotion_end,
            end_boundary,
        )

        start_dates.append(
            promotion_start.date()
        )

        end_dates.append(
            promotion_end.date()
        )

    return start_dates, end_dates


def generate_discount(
    rng: np.random.Generator,
    promotion_type: str,
    archetype: str,
) -> tuple[str, float]:
    """
    Generate discount type and amount.

    Percentage discounts use values such as 10, 15, 20,
    meaning percentage points, not decimal fractions.

    Fixed discounts are EUR amounts.
    """

    # Loyalty and category promotions can use either mechanism.
    if promotion_type in {
        "loyalty",
        "category_specific",
    }:
        discount_type = rng.choice(
            ["percentage", "fixed_amount"],
            p=[0.75, 0.25],
        )

    else:
        discount_type = rng.choice(
            ["percentage", "fixed_amount"],
            p=[0.85, 0.15],
        )

    # Archetype influences promotion aggressiveness.
    if archetype == "strong_uplift_margin_erosion":
        percentage_range = (20, 41)
        fixed_range = (15, 41)

    elif archetype == "strong_uplift_healthy_margin":
        percentage_range = (10, 26)
        fixed_range = (8, 26)

    elif archetype == "weak_uplift":
        percentage_range = (5, 16)
        fixed_range = (5, 16)

    else:  # country_or_category_specific
        percentage_range = (10, 31)
        fixed_range = (7, 31)

    if discount_type == "percentage":
        amount = float(
            rng.integers(
                percentage_range[0],
                percentage_range[1],
            )
        )

    else:
        amount = float(
            rng.integers(
                fixed_range[0],
                fixed_range[1],
            )
        )

    return discount_type, amount


def generate_promotions() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Generate SQL-compatible promotions and helper profiles.
    """

    rng = np.random.default_rng(
        config.RANDOM_SEED
    )

    promotion_ids = np.arange(
        1,
        config.N_PROMOTIONS + 1,
    )

    promotion_types = rng.choice(
        config.PROMOTION_TYPES,
        size=config.N_PROMOTIONS,
        replace=True,
    )

    archetypes = generate_archetypes(
        rng
    )

    start_dates, end_dates = (
        generate_promotion_dates(rng)
    )

    discount_types = []
    discount_amounts = []

    for promotion_type, archetype in zip(
        promotion_types,
        archetypes,
    ):
        discount_type, discount_amount = (
            generate_discount(
                rng,
                str(promotion_type),
                archetype,
            )
        )

        discount_types.append(
            discount_type
        )

        discount_amounts.append(
            discount_amount
        )

    promotion_names = [
        f"NovaMart {str(promotion_type).replace('_', ' ').title()} {promotion_id:02d}"
        for promotion_id, promotion_type
        in zip(
            promotion_ids,
            promotion_types,
        )
    ]

    promotions = pd.DataFrame({
        "promotion_id": promotion_ids,
        "promotion_name": promotion_names,
        "promotion_type": promotion_types,
        "discount_type": discount_types,
        "discount_amount": discount_amounts,
        "promotion_start_date": start_dates,
        "promotion_end_date": end_dates,
    })

    profiles = pd.DataFrame({
        "promotion_id": promotion_ids,
        "promotion_archetype": archetypes,
        "demand_multiplier": [
            config.PROMOTION_DEMAND_MULTIPLIER[a] for a in archetypes
        ],
        "adoption_rate": [
            config.PROMOTION_ADOPTION_RATE[a] for a in archetypes
        ],
    })

    return promotions, profiles


def validate_promotions(
    promotions: pd.DataFrame,
    profiles: pd.DataFrame,
) -> None:
    """Validate clean v0.1d promotion output."""

    assert len(promotions) == config.N_PROMOTIONS
    assert len(profiles) == config.N_PROMOTIONS

    assert promotions[
        "promotion_id"
    ].is_unique

    assert profiles[
        "promotion_id"
    ].is_unique

    assert promotions[
        "promotion_id"
    ].notna().all()

    assert promotions[
        "promotion_name"
    ].notna().all()

    assert promotions[
        "discount_amount"
    ].ge(0).all()

    assert (
        promotions["promotion_start_date"]
        <= promotions["promotion_end_date"]
    ).all()

    assert set(
        promotions["promotion_type"].unique()
    ).issubset(
        set(config.PROMOTION_TYPES)
    )

    assert set(
        promotions["discount_type"].unique()
    ).issubset({
        "percentage",
        "fixed_amount",
    })

    valid_archetypes = {
        archetype["name"]
        for archetype
        in config.PROMOTION_ARCHETYPES
    }

    assert set(
        profiles[
            "promotion_archetype"
        ].unique()
    ).issubset(
        valid_archetypes
    )


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

    promotions, profiles = (
        generate_promotions()
    )

    validate_promotions(
        promotions,
        profiles,
    )

    promotions_path = os.path.join(
        output_dir,
        "promotions.csv",
    )

    profiles_path = os.path.join(
        helper_dir,
        "promotion_profiles.csv",
    )

    promotions.to_csv(
        promotions_path,
        index=False,
    )

    profiles.to_csv(
        profiles_path,
        index=False,
    )

    print()
    print(
        "NovaMart v0.1d — Promotions "
        "generated successfully"
    )
    print("=" * 60)

    print(
        f"Promotions: {len(promotions)}"
    )

    print()
    print("Promotion types:")

    print(
        promotions["promotion_type"]
        .value_counts()
        .to_string()
    )

    print()
    print("Promotion archetypes:")

    print(
        profiles["promotion_archetype"]
        .value_counts()
        .to_string()
    )

    print()
    print("Discount types:")

    print(
        promotions["discount_type"]
        .value_counts()
        .to_string()
    )

    print()
    print("Promotion date range:")

    print(
        f"{promotions['promotion_start_date'].min()} "
        f"→ "
        f"{promotions['promotion_end_date'].max()}"
    )

    print()
    print("Files created:")
    print(f"  {promotions_path}")
    print(f"  {profiles_path}")


if __name__ == "__main__":
    main()