"""
NovaMart Synthetic Data Generator — v0.5b: Marketing Events

Generates:
    data/generated/marketing_events.csv

Uses:
    data/generated/customers.csv
    data/generated/campaigns.csv
    data/generated/countries.csv

Target:
    ~450,000 marketing events

Funnel:
    session_start
    -> product_view
    -> add_to_cart
    -> checkout_started
    -> purchase

Run:
    python src/data_generation/generate_marketing_events.py
"""

import os

import numpy as np
import pandas as pd

import config


N_EVENTS_TARGET = 450_000


def get_project_root():

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )


def load_data():

    generated_dir = os.path.join(
        get_project_root(),
        "data",
        "generated",
    )

    customers = pd.read_csv(
        os.path.join(
            generated_dir,
            "customers.csv",
        )
    )

    campaigns = pd.read_csv(
        os.path.join(
            generated_dir,
            "campaigns.csv",
        )
    )

    countries = pd.read_csv(
        os.path.join(
            generated_dir,
            "countries.csv",
        )
    )

    return (
        customers,
        campaigns,
        countries,
    )


def random_timestamp(
    rng,
):

    start = pd.Timestamp(
        config.START_DATE
    )

    end = pd.Timestamp(
        config.END_DATE
    ) + pd.Timedelta(
        hours=23,
        minutes=59,
        seconds=59,
    )

    total_seconds = int(
        (
            end - start
        ).total_seconds()
    )

    offset = int(
        rng.integers(
            0,
            total_seconds + 1,
        )
    )

    return (
        start
        + pd.Timedelta(
            seconds=offset
        )
    )


def generate_marketing_events():

    rng = np.random.default_rng(
        config.RANDOM_SEED + 800
    )

    (
        customers,
        campaigns,
        countries,
    ) = load_data()

    customer_ids = (
        customers[
            "customer_id"
        ]
        .astype(int)
        .to_numpy()
    )

    campaign_ids = (
        campaigns[
            "campaign_id"
        ]
        .astype(int)
        .to_numpy()
    )

    # ========================================================
    # CUSTOMER → COUNTRY LOOKUP
    # ========================================================

    customer_country_lookup = {
        int(row["customer_id"]):
            int(row["country_id"])
        for row
        in customers.to_dict(
            "records"
        )
    }

    # ========================================================
    # CAMPAIGN → CHANNEL LOOKUP
    # ========================================================

    campaign_channel_lookup = {
        int(row["campaign_id"]):
            int(row["channel_id"])
        for row
        in campaigns.to_dict(
            "records"
        )
    }

    # ========================================================
    # COUNTRY DISTRIBUTION FOR ANONYMOUS USERS
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

    rows = []

    event_id = 1
    session_id = 1

    funnel_probabilities = {
        "product_view": 0.75,
        "add_to_cart": 0.35,
        "checkout_started": 0.50,
        "purchase": 0.65,
    }

    while len(rows) < N_EVENTS_TARGET:

        current_session_id = (
            f"S{session_id:08d}"
        )

        session_id += 1

        # ====================================================
        # CUSTOMER
        # ====================================================

        customer_id = None

        if rng.random() < 0.72:

            customer_id = int(
                rng.choice(
                    customer_ids
                )
            )

        # ====================================================
        # COUNTRY
        # ====================================================

        if customer_id is not None:

            country_id = (
                customer_country_lookup[
                    customer_id
                ]
            )

        else:

            country_id = int(
                rng.choice(
                    country_ids,
                    p=country_weights,
                )
            )

        # ====================================================
        # CAMPAIGN + CHANNEL
        # ====================================================

        campaign_id = None

        if rng.random() < 0.58:

            campaign_id = int(
                rng.choice(
                    campaign_ids
                )
            )

            channel_id = (
                campaign_channel_lookup[
                    campaign_id
                ]
            )

        else:

            # Non-campaign traffic.
            # Direct channel is channel_id 6
            # in the canonical NovaMart channel list.
            channel_id = 6

        # ====================================================
        # SESSION START
        # ====================================================

        session_start = (
            random_timestamp(
                rng
            )
        )

        session_events = []

        session_events.append({
            "event_type":
                "session_start",

            "event_timestamp":
                session_start,
        })

        current_timestamp = (
            session_start
        )

        # ====================================================
        # FUNNEL
        # ====================================================

        if (
            rng.random()
            < funnel_probabilities[
                "product_view"
            ]
        ):

            current_timestamp += (
                pd.Timedelta(
                    seconds=int(
                        rng.integers(
                            5,
                            180,
                        )
                    )
                )
            )

            session_events.append({
                "event_type":
                    "product_view",

                "event_timestamp":
                    current_timestamp,
            })

            if (
                rng.random()
                < funnel_probabilities[
                    "add_to_cart"
                ]
            ):

                current_timestamp += (
                    pd.Timedelta(
                        seconds=int(
                            rng.integers(
                                10,
                                300,
                            )
                        )
                    )
                )

                session_events.append({
                    "event_type":
                        "add_to_cart",

                    "event_timestamp":
                        current_timestamp,
                })

                if (
                    rng.random()
                    < funnel_probabilities[
                        "checkout_started"
                    ]
                ):

                    current_timestamp += (
                        pd.Timedelta(
                            seconds=int(
                                rng.integers(
                                    20,
                                    420,
                                )
                            )
                        )
                    )

                    session_events.append({
                        "event_type":
                            "checkout_started",

                        "event_timestamp":
                            current_timestamp,
                    })

                    if (
                        rng.random()
                        < funnel_probabilities[
                            "purchase"
                        ]
                    ):

                        current_timestamp += (
                            pd.Timedelta(
                                seconds=int(
                                    rng.integers(
                                        20,
                                        600,
                                    )
                                )
                            )
                        )

                        session_events.append({
                            "event_type":
                                "purchase",

                            "event_timestamp":
                                current_timestamp,
                        })

        # ====================================================
        # SAVE EVENTS
        # ====================================================

        for event in session_events:

            if len(rows) >= N_EVENTS_TARGET:
                break

            rows.append({

                "event_id":
                    event_id,

                "session_id":
                    current_session_id,

                "customer_id":
                    customer_id,

                "campaign_id":
                    campaign_id,

                "channel_id":
                    channel_id,

                "country_id":
                    country_id,

                "event_type":
                    event[
                        "event_type"
                    ],

                "event_timestamp":
                    event[
                        "event_timestamp"
                    ],
            })

            event_id += 1

    return pd.DataFrame(
        rows
    )


def validate_events(
    events,
):

    assert (
        len(events)
        == N_EVENTS_TARGET
    )

    assert events[
        "event_id"
    ].is_unique

    assert events[
        "session_id"
    ].notna().all()

    assert events[
        "channel_id"
    ].notna().all()

    assert events[
        "country_id"
    ].notna().all()

    assert events[
        "event_type"
    ].notna().all()

    assert events[
        "event_timestamp"
    ].notna().all()

    valid_event_types = {
        "session_start",
        "product_view",
        "add_to_cart",
        "checkout_started",
        "purchase",
    }

    assert set(
        events[
            "event_type"
        ].unique()
    ).issubset(
        valid_event_types
    )

    valid_channel_ids = set(
        load_data()[1][
            "channel_id"
        ].astype(int)
    )

    valid_country_ids = set(
        load_data()[2][
            "country_id"
        ].astype(int)
    )

    assert events[
        "channel_id"
    ].isin(
        valid_channel_ids
    ).all()

    assert events[
        "country_id"
    ].isin(
        valid_country_ids
    ).all()


def main():

    events = (
        generate_marketing_events()
    )

    validate_events(
        events
    )

    output_path = os.path.join(
        get_project_root(),
        "data",
        "generated",
        "marketing_events.csv",
    )

    events.to_csv(
        output_path,
        index=False,
    )

    total_sessions = (
        events[
            "session_id"
        ].nunique()
    )

    event_counts = (
        events[
            "event_type"
        ]
        .value_counts()
    )

    session_starts = int(
        event_counts.get(
            "session_start",
            0,
        )
    )

    purchases = int(
        event_counts.get(
            "purchase",
            0,
        )
    )

    conversion_rate = (
        purchases
        / session_starts
        * 100
    )

    print()
    print(
        "NovaMart v0.5b — "
        "Marketing Events generated successfully"
    )

    print("=" * 60)

    print(
        f"Marketing events: "
        f"{len(events):,}"
    )

    print(
        f"Sessions: "
        f"{total_sessions:,}"
    )

    print(
        f"Channels: "
        f"{events['channel_id'].nunique():,}"
    )

    print(
        f"Countries: "
        f"{events['country_id'].nunique():,}"
    )

    print()

    print(
        "Event distribution:"
    )

    print(
        event_counts
        .to_string()
    )

    print()

    print(
        f"Session purchase conversion: "
        f"{conversion_rate:.2f}%"
    )

    print()

    print(
        f"File created: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()