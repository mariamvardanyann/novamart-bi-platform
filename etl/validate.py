import pandas as pd

def validate_order_items(
    df,
    valid_product_ids,
):

    positive_quantity = (
        df["quantity"] > 0
    )

    known_product = (
        df["product_id"]
        .isin(valid_product_ids)
    )

    valid_mask = (
        positive_quantity
        & known_product
    )

    clean = df[
        valid_mask
    ].copy()

    quarantine = df[
        ~valid_mask
    ].copy()

    def get_reason(row):

        reasons = []

        if row["quantity"] <= 0:
            reasons.append(
                "quantity_must_be_positive"
            )

        if (
            row["product_id"]
            not in valid_product_ids
        ):
            reasons.append(
                "unknown_product"
            )

        return "|".join(reasons)

    quarantine["dq_reason"] = (
        quarantine.apply(
            get_reason,
            axis=1,
        )
    )

    return clean, quarantine

def validate_orders(df):

    valid_statuses = {
        "placed",
        "paid",
        "fulfilled",
        "shipped",
        "delivered",
        "cancelled",
    }

    currency_valid = (
        df["currency_code"] == "EUR"
    )

    status_valid = (
        df["status"].isin(
            valid_statuses
        )
    )

    duplicate_mask = (
        df.duplicated(
            keep=False
        )
    )

    valid_mask = (
        currency_valid
        & status_valid
        & ~duplicate_mask
    )

    clean = df[
        valid_mask
    ].copy()

    quarantine = df[
        ~valid_mask
    ].copy()

    def get_reason(row):

        reasons = []

        if row["currency_code"] != "EUR":
            reasons.append(
                "currency_must_be_EUR"
            )

        if row["status"] not in valid_statuses:
            reasons.append(
                "invalid_order_status"
            )

        if duplicate_mask.loc[row.name]:
            reasons.append(
                "duplicate_order"
            )

        return "|".join(reasons)

    quarantine["dq_reason"] = (
        quarantine.apply(
            get_reason,
            axis=1,
        )
    )

    return clean, quarantine

def validate_shipments(df):

    shipped = pd.to_datetime(
        df["shipped_timestamp"],
        errors="coerce",
    )

    actual_delivery = pd.to_datetime(
        df["actual_delivery_timestamp"],
        errors="coerce",
    )

    invalid_delivery_order = (
        actual_delivery.notna()
        & shipped.notna()
        & (actual_delivery < shipped)
    )

    valid_mask = (
        ~invalid_delivery_order
    )

    clean = df[
        valid_mask
    ].copy()

    quarantine = df[
        ~valid_mask
    ].copy()

    quarantine[
        "dq_reason"
    ] = "delivery_before_shipment"

    return clean, quarantine

def validate_returns(
    returns_df,
    shipments_df,
):

    shipments = shipments_df.copy()

    shipments[
        "actual_delivery_timestamp"
    ] = pd.to_datetime(
        shipments[
            "actual_delivery_timestamp"
        ],
        errors="coerce",
    )

    returns = returns_df.copy()

    returns[
        "return_timestamp"
    ] = pd.to_datetime(
        returns[
            "return_timestamp"
        ],
        errors="coerce",
    )

    delivery_lookup = (
        shipments[
            shipments[
                "actual_delivery_timestamp"
            ].notna()
        ]
        .drop_duplicates(
            subset=["order_id"],
            keep="first",
        )
        .set_index(
            "order_id"
        )[
            "actual_delivery_timestamp"
        ]
        .to_dict()
    )

    invalid_mask = returns.apply(
        lambda row:
            (
                row["order_id"]
                in delivery_lookup
                and row[
                    "return_timestamp"
                ]
                < delivery_lookup[
                    row["order_id"]
                ]
            ),
        axis=1,
    )

    clean = returns[
        ~invalid_mask
    ].copy()

    quarantine = returns[
        invalid_mask
    ].copy()

    quarantine[
        "dq_reason"
    ] = "return_before_delivery"

    return clean, quarantine


def validate_marketing_spend(df):

    valid_clicks = (
        df["clicks"]
        <= df["impressions"]
    )

    clean = df[
        valid_clicks
    ].copy()

    quarantine = df[
        ~valid_clicks
    ].copy()

    quarantine[
        "dq_reason"
    ] = "clicks_exceed_impressions"

    return clean, quarantine

def validate_marketing_events(df):

    valid_session = (
        df["session_id"].notna()
        & (
            df["session_id"]
            .astype(str)
            .str.strip()
            != ""
        )
    )

    clean = df[
        valid_session
    ].copy()

    quarantine = df[
        ~valid_session
    ].copy()

    quarantine[
        "dq_reason"
    ] = "missing_session_id"

    return clean, quarantine

def validate_promotions(df):

    promotions = df.copy()

    promotions[
        "promotion_start_date"
    ] = pd.to_datetime(
        promotions[
            "promotion_start_date"
        ],
        errors="coerce",
    )

    promotions[
        "promotion_end_date"
    ] = pd.to_datetime(
        promotions[
            "promotion_end_date"
        ],
        errors="coerce",
    )

    valid_dates = (
        promotions[
            "promotion_end_date"
        ]
        >= promotions[
            "promotion_start_date"
        ]
    )

    clean = promotions[
        valid_dates
    ].copy()

    quarantine = promotions[
        ~valid_dates
    ].copy()

    quarantine[
        "dq_reason"
    ] = "promotion_end_before_start"

    return clean, quarantine


def validate_payments(
    payments_df,
    clean_order_ids,
):

    valid_order = (
        payments_df["order_id"]
        .isin(clean_order_ids)
    )

    clean = payments_df[
        valid_order
    ].copy()

    quarantine = payments_df[
        ~valid_order
    ].copy()

    quarantine[
        "dq_reason"
    ] = "order_not_in_clean_orders"

    return clean, quarantine


def validate_refunds(
    refunds_df,
    clean_order_ids,
    clean_return_ids,
):

    valid_order = (
        refunds_df["order_id"]
        .isin(clean_order_ids)
    )

    # NULL return_id is allowed for standalone refunds.
    valid_return = (
        refunds_df["return_id"].isna()
        | refunds_df["return_id"].isin(
            clean_return_ids
        )
    )

    valid_mask = (
        valid_order
        & valid_return
    )

    clean = refunds_df[
        valid_mask
    ].copy()

    quarantine = refunds_df[
        ~valid_mask
    ].copy()

    def get_reason(row):

        reasons = []

        if (
            row["order_id"]
            not in clean_order_ids
        ):
            reasons.append(
                "order_not_in_clean_orders"
            )

        if (
            not pd.isna(
                row["return_id"]
            )
            and row["return_id"]
            not in clean_return_ids
        ):
            reasons.append(
                "return_not_in_clean_returns"
            )

        return "|".join(reasons)

    quarantine[
        "dq_reason"
    ] = quarantine.apply(
        get_reason,
        axis=1,
    )

    return clean, quarantine



def enforce_clean_order_reference(
    clean_df: pd.DataFrame,
    quarantine_df: pd.DataFrame,
    clean_order_ids: set[int],
) -> tuple[pd.DataFrame, pd.DataFrame]:

    invalid_order_mask = (
        ~clean_df["order_id"].isin(
            clean_order_ids
        )
    )

    relational_quarantine = (
        clean_df.loc[
            invalid_order_mask
        ].copy()
    )

    relational_quarantine[
        "dq_reason"
    ] = "order_not_in_clean_orders"

    final_clean = (
        clean_df.loc[
            ~invalid_order_mask
        ].copy()
    )

    final_quarantine = pd.concat(
        [
            quarantine_df,
            relational_quarantine,
        ],
        ignore_index=True,
    )

    return (
        final_clean,
        final_quarantine,
    )


def enforce_clean_order_line_reference(
    clean_df: pd.DataFrame,
    quarantine_df: pd.DataFrame,
    clean_order_line_ids: set[int],
) -> tuple[pd.DataFrame, pd.DataFrame]:

    invalid_line_mask = (
        ~clean_df["order_line_id"].isin(
            clean_order_line_ids
        )
    )

    relational_quarantine = (
        clean_df.loc[
            invalid_line_mask
        ].copy()
    )

    relational_quarantine[
        "dq_reason"
    ] = "order_line_not_in_clean_order_items"

    final_clean = (
        clean_df.loc[
            ~invalid_line_mask
        ].copy()
    )

    final_quarantine = pd.concat(
        [
            quarantine_df,
            relational_quarantine,
        ],
        ignore_index=True,
    )

    return (
        final_clean,
        final_quarantine,
    )