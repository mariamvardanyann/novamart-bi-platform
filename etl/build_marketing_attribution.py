import os

import pandas as pd

from config import PROCESSED_DIR
from business_rules import get_eligible_completed_orders


LOOKBACK_DAYS = 30


def build_marketing_attribution():

    events_path = os.path.join(
        PROCESSED_DIR,
        "marketing_events.csv",
    )

    orders_path = os.path.join(
        PROCESSED_DIR,
        "orders.csv",
    )

    events = pd.read_csv(
        events_path,
        parse_dates=[
            "event_timestamp",
        ],
    )

    orders = pd.read_csv(
        orders_path,
        parse_dates=[
            "order_timestamp",
        ],
    )

    payments = pd.read_csv(
        os.path.join(PROCESSED_DIR, "payments.csv"),
        parse_dates=["payment_timestamp"],
    )

    orders = get_eligible_completed_orders(orders, payments)

    # ========================================================
    # PREPARE ORDERS
    # ========================================================

    orders = orders[
        [
            "order_id",
            "customer_id",
            "order_timestamp",
        ]
    ].copy()

    orders = orders[
        orders["customer_id"].notna()
    ].copy()

    orders[
        "customer_id"
    ] = orders[
        "customer_id"
    ].astype(int)

    # ========================================================
    # PREPARE CAMPAIGN TOUCHPOINTS
    # ========================================================

    touchpoints = events[
        events["customer_id"].notna()
        & events["campaign_id"].notna()
    ].copy()

    touchpoints[
        "customer_id"
    ] = touchpoints[
        "customer_id"
    ].astype(int)

    touchpoints[
        "campaign_id"
    ] = touchpoints[
        "campaign_id"
    ].astype(int)

    touchpoints = touchpoints[
        [
            "customer_id",
            "campaign_id",
            "channel_id",
            "event_timestamp",
        ]
    ].copy()

    touchpoints = touchpoints.rename(
        columns={
            "event_timestamp":
                "touchpoint_timestamp",
        }
    )

    # ========================================================
    # SORT FOR ASOF MATCHING
    # ========================================================

    orders = orders.sort_values(
        [
            "order_timestamp",
            "customer_id",
        ]
    ).reset_index(
        drop=True
    )

    touchpoints = touchpoints.sort_values(
        [
            "touchpoint_timestamp",
            "customer_id",
        ]
    ).reset_index(
        drop=True
    )

    # ========================================================
    # LAST-TOUCH ATTRIBUTION
    # ========================================================
    #
    # For every eligible completed purchase, find the most recent
    # campaign touchpoint from the same customer
    # occurring before the order.
    #
    # Maximum lookback window = 30 days.
    # ========================================================

    attribution = pd.merge_asof(
        orders,
        touchpoints,
        left_on="order_timestamp",
        right_on="touchpoint_timestamp",
        by="customer_id",
        direction="backward",
        tolerance=pd.Timedelta(
            days=LOOKBACK_DAYS
        ),
    )

    # Keep only orders that actually have
    # a campaign touchpoint.
    attribution = attribution[
        attribution[
            "campaign_id"
        ].notna()
    ].copy()

    attribution[
        "campaign_id"
    ] = attribution[
        "campaign_id"
    ].astype(int)

    if (
        "channel_id"
        in attribution.columns
    ):

        attribution[
            "channel_id"
        ] = attribution[
            "channel_id"
        ].astype(
            "Int64"
        )

    # ========================================================
    # FINAL SQL-SHAPED OUTPUT
    # ========================================================

    attribution = attribution[
        [
            "order_id",
            "customer_id",
            "campaign_id",
            "channel_id",
            "touchpoint_timestamp",
        ]
    ].copy()

    attribution = (
        attribution
        .sort_values(
            "order_id"
        )
        .reset_index(
            drop=True
        )
    )

    attribution.insert(
        0,
        "attribution_id",
        range(
            1,
            len(attribution) + 1,
        ),
    )

    attribution[
        "attribution_model"
    ] = "session_last_touch"

    return attribution


def main():

    attribution = (
        build_marketing_attribution()
    )

    output_path = os.path.join(
        PROCESSED_DIR,
        "marketing_attribution.csv",
    )

    attribution.to_csv(
        output_path,
        index=False,
    )

    print()

    print(
        "NovaMart ETL — "
        "marketing_attribution created"
    )

    print("=" * 50)

    print(
        f"Rows: "
        f"{len(attribution):,}"
    )

    print(
        f"Orders attributed: "
        f"{attribution['order_id'].nunique():,}"
    )

    print(
        f"Customers represented: "
        f"{attribution['customer_id'].nunique():,}"
    )

    print(
        f"Campaigns represented: "
        f"{attribution['campaign_id'].nunique():,}"
    )

    print(
        f"Channels represented: "
        f"{attribution['channel_id'].nunique():,}"
    )

    print()

    print(
        f"Lookback window: "
        f"{LOOKBACK_DAYS} days"
    )

    print()

    print(
        "Attribution model:"
    )

    print(
        attribution[
            "attribution_model"
        ]
        .value_counts()
        .to_string()
    )

    print()

    print(
        f"File created: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()