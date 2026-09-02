"""
NovaMart Synthetic Data Generator — v0.5c: Marketing Spend

Generates:
    data/generated/marketing_spend.csv

Uses:
    data/generated/campaigns.csv
    data/generated/countries.csv

Target:
    ~15,000 daily campaign spend rows

Run:
    python src/data_generation/generate_marketing_spend.py
"""

import os

import numpy as np
import pandas as pd

import config


N_SPEND_TARGET = 15_000


# ============================================================
# PATH HELPERS
# ============================================================

def get_project_root():

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )


def load_campaigns():

    path = os.path.join(
        get_project_root(),
        "data",
        "generated",
        "campaigns.csv",
    )

    return pd.read_csv(path)


def load_countries():

    path = os.path.join(
        get_project_root(),
        "data",
        "generated",
        "countries.csv",
    )

    return pd.read_csv(path)


# ============================================================
# GENERATOR
# ============================================================

def generate_marketing_spend():

    rng = np.random.default_rng(
        config.RANDOM_SEED + 900
    )

    campaigns = load_campaigns()
    countries = load_countries()

    start_date = pd.Timestamp(
        config.START_DATE
    )

    end_date = pd.Timestamp(
        config.END_DATE
    )

    all_dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    rows = []

    # ========================================================
    # CAMPAIGN LOOKUPS
    # ========================================================

    campaign_ids = (
        campaigns["campaign_id"]
        .astype(int)
        .to_numpy()
    )

    channel_lookup = {
        int(row["campaign_id"]):
            int(row["channel_id"])
        for row
        in campaigns.to_dict(
            "records"
        )
    }

    # ========================================================
    # COUNTRY LOOKUPS
    # ========================================================

    country_code_to_id = {
        str(row["country_code"]):
            int(row["country_id"])
        for row
        in countries.to_dict(
            "records"
        )
    }

    country_ids = []

    country_weights = []

    for country in config.COUNTRIES:

        country_code = country[
            "code"
        ]

        if (
            country_code
            not in country_code_to_id
        ):

            raise RuntimeError(
                "Country from config "
                "not found in countries.csv: "
                f"{country_code}"
            )

        country_ids.append(
            country_code_to_id[
                country_code
            ]
        )

        country_weights.append(
            float(
                country[
                    "order_share"
                ]
            )
        )

    country_ids = np.array(
        country_ids,
        dtype=int,
    )

    country_weights = np.array(
        country_weights,
        dtype=float,
    )

    country_weights = (
        country_weights
        / country_weights.sum()
    )

    # ========================================================
    # CREATE CAMPAIGN-DAY COMBINATIONS
    # ========================================================

    for campaign_id in campaign_ids:

        campaign_id = int(
            campaign_id
        )

        # Campaign starts somewhere during
        # the first ~18 months.

        latest_start_index = max(
            1,
            len(all_dates) - 180,
        )

        start_index = int(
            rng.integers(
                0,
                latest_start_index,
            )
        )

        duration_days = int(
            rng.integers(
                180,
                500,
            )
        )

        end_index = min(
            start_index
            + duration_days,
            len(all_dates),
        )

        campaign_dates = all_dates[
            start_index:end_index
        ]

        channel_id = (
            channel_lookup[
                campaign_id
            ]
        )

        # ====================================================
        # CHANNEL PERSONALITY
        # ====================================================

        # Higher multiplier =
        # more expensive traffic.

        channel_cost_multiplier = {
            1: 1.30,
            2: 1.15,
            3: 0.45,
            4: 0.60,
            5: 0.85,
            6: 0.30,
        }.get(
            channel_id,
            1.0,
        )

        for spend_date in campaign_dates:

            # ------------------------------------------------
            # COUNTRY
            # ------------------------------------------------

            country_id = int(
                rng.choice(
                    country_ids,
                    p=country_weights,
                )
            )

            # ------------------------------------------------
            # IMPRESSIONS
            # ------------------------------------------------

            impressions = int(
                max(
                    100,
                    rng.lognormal(
                        mean=8.0,
                        sigma=0.55,
                    ),
                )
            )

            # ------------------------------------------------
            # CTR
            # ------------------------------------------------

            ctr = float(
                rng.uniform(
                    0.01,
                    0.06,
                )
            )

            clicks = int(
                round(
                    impressions
                    * ctr
                )
            )

            clicks = min(
                clicks,
                impressions,
            )

            # ------------------------------------------------
            # COST PER CLICK
            # ------------------------------------------------

            base_cpc = float(
                rng.uniform(
                    0.25,
                    1.80,
                )
            )

            cpc = (
                base_cpc
                * channel_cost_multiplier
            )

            spend_amount = round(
                clicks * cpc,
                2,
            )

            # ------------------------------------------------
            # OUTPUT ROW
            # ------------------------------------------------

            rows.append({

                "campaign_id":
                    campaign_id,

                "channel_id":
                    channel_id,

                "country_id":
                    country_id,

                "spend_date":
                    spend_date.date(),

                "impressions":
                    impressions,

                "clicks":
                    clicks,

                "spend_amount":
                    spend_amount,

                "currency_code":
                    config.CURRENCY_CODE,
            })

    spend = pd.DataFrame(
        rows
    )

    # ========================================================
    # BRING DATASET CLOSE TO 15,000 ROWS
    # ========================================================

    if len(spend) > N_SPEND_TARGET:

        spend = spend.sample(
            n=N_SPEND_TARGET,
            random_state=
                config.RANDOM_SEED + 900,
            replace=False,
        )

    elif len(spend) < N_SPEND_TARGET:

        needed = (
            N_SPEND_TARGET
            - len(spend)
        )

        extra = spend.sample(
            n=needed,
            random_state=
                config.RANDOM_SEED + 901,
            replace=True,
        ).copy()

        spend = pd.concat(
            [
                spend,
                extra,
            ],
            ignore_index=True,
        )

    # ========================================================
    # SORT
    # ========================================================

    spend = (
        spend
        .sort_values(
            [
                "spend_date",
                "campaign_id",
                "country_id",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    spend.insert(
        0,
        "marketing_spend_id",
        np.arange(
            1,
            len(spend) + 1,
        ),
    )

    return spend


# ============================================================
# VALIDATION
# ============================================================

def validate_marketing_spend(
    spend,
):

    assert (
        len(spend)
        == N_SPEND_TARGET
    )

    assert spend[
        "marketing_spend_id"
    ].is_unique

    assert spend[
        "campaign_id"
    ].notna().all()

    assert spend[
        "channel_id"
    ].notna().all()

    assert spend[
        "country_id"
    ].notna().all()

    assert spend[
        "spend_date"
    ].notna().all()

    assert spend[
        "impressions"
    ].ge(0).all()

    assert spend[
        "clicks"
    ].ge(0).all()

    assert (
        spend["clicks"]
        <= spend["impressions"]
    ).all()

    assert spend[
        "spend_amount"
    ].ge(0).all()

    assert spend[
        "currency_code"
    ].eq(
        config.CURRENCY_CODE
    ).all()

    valid_campaign_ids = set(
        load_campaigns()[
            "campaign_id"
        ].astype(int)
    )

    valid_country_ids = set(
        load_countries()[
            "country_id"
        ].astype(int)
    )

    assert spend[
        "campaign_id"
    ].isin(
        valid_campaign_ids
    ).all()

    assert spend[
        "country_id"
    ].isin(
        valid_country_ids
    ).all()


# ============================================================
# MAIN
# ============================================================

def main():

    spend = (
        generate_marketing_spend()
    )

    validate_marketing_spend(
        spend
    )

    output_path = os.path.join(
        get_project_root(),
        "data",
        "generated",
        "marketing_spend.csv",
    )

    spend.to_csv(
        output_path,
        index=False,
    )

    total_spend = float(
        spend[
            "spend_amount"
        ].sum()
    )

    total_impressions = int(
        spend[
            "impressions"
        ].sum()
    )

    total_clicks = int(
        spend[
            "clicks"
        ].sum()
    )

    ctr = (
        total_clicks
        / total_impressions
        * 100
    )

    print()
    print(
        "NovaMart Synthetic Data "
        "— Marketing Spend"
    )
    print("=" * 60)

    print(
        f"Rows:        "
        f"{len(spend):,}"
    )

    print(
        f"Campaigns:   "
        f"{spend['campaign_id'].nunique():,}"
    )

    print(
        f"Channels:    "
        f"{spend['channel_id'].nunique():,}"
    )

    print(
        f"Countries:   "
        f"{spend['country_id'].nunique():,}"
    )

    print(
        f"Impressions: "
        f"{total_impressions:,}"
    )

    print(
        f"Clicks:      "
        f"{total_clicks:,}"
    )

    print(
        f"CTR:         "
        f"{ctr:.2f}%"
    )

    print(
        f"Spend:       "
        f"€{total_spend:,.2f}"
    )

    print()
    print(
        f"Saved to:\n{output_path}"
    )


if __name__ == "__main__":
    main()