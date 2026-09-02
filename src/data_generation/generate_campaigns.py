"""
NovaMart Synthetic Data Generator — v0.1e: Campaigns

Generates:
1. campaigns.csv
   - matches the SQL campaigns table

2. helpers/campaign_profiles.csv
   - generator-only archetype/profile data
   - used later for marketing spend/events and attribution behavior

Run:
    python src/data_generation/generate_campaigns.py
"""

import os

import numpy as np
import pandas as pd

import config


def generate_archetypes(
    rng: np.random.Generator,
) -> list[str]:
    """
    Assign exactly 45 campaigns across the locked archetypes.
    """

    archetypes: list[str] = []

    for archetype in config.CAMPAIGN_ARCHETYPES:
        count = round(
            archetype["share"] * config.N_CAMPAIGNS
        )

        archetypes.extend(
            [archetype["name"]] * count
        )

    # Correct any rounding difference.
    while len(archetypes) < config.N_CAMPAIGNS:
        archetypes.append(
            config.CAMPAIGN_ARCHETYPES[0]["name"]
        )

    archetypes = archetypes[:config.N_CAMPAIGNS]

    rng.shuffle(archetypes)

    return archetypes


def generate_channel_ids(
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Assign channels to campaigns.

    Direct is intentionally much less likely to have a campaign,
    because it usually represents non-campaign traffic.
    """

    channel_ids = np.arange(
        1,
        len(config.CHANNELS) + 1,
    )

    channel_weights = np.array([
        0.28,  # Paid Search
        0.26,  # Paid Social
        0.14,  # Email
        0.10,  # Organic Search
        0.18,  # Affiliate
        0.04,  # Direct
    ])

    return rng.choice(
        channel_ids,
        size=config.N_CAMPAIGNS,
        p=channel_weights,
    )


def generate_campaigns() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Generate SQL-compatible campaigns and helper profiles.
    """

    rng = np.random.default_rng(
        config.RANDOM_SEED
    )

    campaign_ids = np.arange(
        1,
        config.N_CAMPAIGNS + 1,
    )

    channel_ids = generate_channel_ids(
        rng
    )

    archetypes = generate_archetypes(
        rng
    )

    campaign_names = []

    for campaign_id, channel_id in zip(
        campaign_ids,
        channel_ids,
    ):
        channel_name = config.CHANNELS[
            int(channel_id) - 1
        ]

        clean_channel_name = (
            channel_name
            .replace(" ", "_")
            .lower()
        )

        campaign_names.append(
            f"novamart_{clean_channel_name}_campaign_{campaign_id:02d}"
        )

    campaigns = pd.DataFrame({
        "campaign_id": campaign_ids,
        "channel_id": channel_ids,
        "campaign_name": campaign_names,
    })

    profiles = pd.DataFrame({
        "campaign_id": campaign_ids,
        "campaign_archetype": archetypes,
    })

    return campaigns, profiles


def validate_campaigns(
    campaigns: pd.DataFrame,
    profiles: pd.DataFrame,
) -> None:
    """Validate v0.1e campaign output."""

    assert len(campaigns) == config.N_CAMPAIGNS
    assert len(profiles) == config.N_CAMPAIGNS

    assert campaigns[
        "campaign_id"
    ].is_unique

    assert profiles[
        "campaign_id"
    ].is_unique

    assert campaigns[
        "campaign_name"
    ].notna().all()

    assert campaigns[
        "channel_id"
    ].between(
        1,
        len(config.CHANNELS),
    ).all()

    valid_archetypes = {
        archetype["name"]
        for archetype
        in config.CAMPAIGN_ARCHETYPES
    }

    assert set(
        profiles[
            "campaign_archetype"
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

    campaigns, profiles = generate_campaigns()

    validate_campaigns(
        campaigns,
        profiles,
    )

    campaigns_path = os.path.join(
        output_dir,
        "campaigns.csv",
    )

    profiles_path = os.path.join(
        helper_dir,
        "campaign_profiles.csv",
    )

    campaigns.to_csv(
        campaigns_path,
        index=False,
    )

    profiles.to_csv(
        profiles_path,
        index=False,
    )

    print()
    print(
        "NovaMart v0.1e — Campaigns generated successfully"
    )
    print("=" * 60)

    print(
        f"Campaigns: {len(campaigns)}"
    )

    print()
    print("Campaigns by channel:")

    channel_lookup = pd.DataFrame({
        "channel_id": np.arange(
            1,
            len(config.CHANNELS) + 1,
        ),
        "channel_name": config.CHANNELS,
    })

    channel_summary = (
        campaigns
        .merge(
            channel_lookup,
            on="channel_id",
        )
        .groupby("channel_name")
        .size()
        .sort_values(ascending=False)
    )

    print(
        channel_summary.to_string()
    )

    print()
    print("Campaign archetypes:")

    print(
        profiles[
            "campaign_archetype"
        ]
        .value_counts()
        .to_string()
    )

    print()
    print("Files created:")
    print(f"  {campaigns_path}")
    print(f"  {profiles_path}")


if __name__ == "__main__":
    main()