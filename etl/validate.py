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

def validate_orders(
    df,
    customers_df=None,
):

    valid_statuses = {
        "placed",
        "paid",
        "fulfilled",
        "shipped",
        "delivered",
        "cancelled",
    }

    currency_valid = df["currency_code"].eq("EUR")
    status_valid = df["status"].isin(valid_statuses)
    duplicate_mask = df.duplicated(keep=False)

    customer_valid = pd.Series(True, index=df.index)
    lifecycle_valid = pd.Series(True, index=df.index)

    if customers_df is not None:
        customer_lookup = customers_df[["customer_id", "signup_date"]].copy()
        customer_lookup["signup_date"] = pd.to_datetime(
            customer_lookup["signup_date"],
            errors="coerce",
        ).dt.normalize()

        signup_lookup = customer_lookup.set_index("customer_id")["signup_date"]
        resolved_signup = df["customer_id"].map(signup_lookup)
        customer_valid = resolved_signup.notna()

        order_dates = pd.to_datetime(
            df["order_timestamp"],
            errors="coerce",
        ).dt.normalize()
        lifecycle_valid = (
            customer_valid
            & order_dates.notna()
            & (order_dates >= resolved_signup)
        )

    valid_mask = (
        currency_valid
        & status_valid
        & ~duplicate_mask
        & customer_valid
        & lifecycle_valid
    )

    clean = df[valid_mask].copy()
    quarantine = df[~valid_mask].copy()

    def get_reason(row):
        reasons = []

        if row["currency_code"] != "EUR":
            reasons.append("currency_must_be_EUR")

        if row["status"] not in valid_statuses:
            reasons.append("invalid_order_status")

        if duplicate_mask.loc[row.name]:
            reasons.append("duplicate_order")

        if not customer_valid.loc[row.name]:
            reasons.append("customer_not_found")
        elif not lifecycle_valid.loc[row.name]:
            reasons.append("order_before_customer_signup")

        return "|".join(reasons)

    quarantine["dq_reason"] = quarantine.apply(get_reason, axis=1)

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


def _normalize_refunds_to_payment_limit(
    refunds_df,
    payment_amount_lookup,
):
    """Scale only over-refunded payment groups in the clean layer.

    Raw source rows remain unchanged. The correction is deterministic and keeps
    every already-resolved refund row while ensuring cumulative refunds never
    exceed the successful payment amount.
    """

    corrected = refunds_df.copy()
    corrected["_refund_ts"] = pd.to_datetime(
        corrected["refund_timestamp"],
        errors="coerce",
    )

    for payment_id, group in corrected.groupby("payment_id", sort=False):
        if payment_id not in payment_amount_lookup:
            continue

        limit = float(payment_amount_lookup[payment_id])
        group_total = float(group["refund_amount"].sum())
        if group_total <= limit + 0.01:
            continue

        ordered = group.sort_values(["_refund_ts", "refund_id"]).copy()
        factor = limit / group_total
        scaled = (ordered["refund_amount"] * factor).round(2)

        # Make rounding exact at cent precision.
        rounding_delta = round(limit - float(scaled.sum()), 2)
        last_idx = scaled.index[-1]
        scaled.loc[last_idx] = round(float(scaled.loc[last_idx]) + rounding_delta, 2)

        corrected.loc[scaled.index, "refund_amount"] = scaled.values

    return corrected.drop(columns=["_refund_ts"])


def validate_refunds(
    refunds_df,
    clean_order_ids,
    clean_return_ids,
    clean_order_item_order_ids,
    clean_payments_df,
):

    successful_payments = clean_payments_df[
        clean_payments_df["payment_status"].eq("succeeded")
    ].copy()

    payment_order_lookup = (
        successful_payments
        .drop_duplicates(subset=["payment_id"])
        .set_index("payment_id")["order_id"]
        .to_dict()
    )
    payment_amount_lookup = (
        successful_payments
        .drop_duplicates(subset=["payment_id"])
        .set_index("payment_id")["payment_amount"]
        .to_dict()
    )

    valid_order = refunds_df["order_id"].isin(clean_order_ids)
    has_clean_merchandise = refunds_df["order_id"].isin(
        clean_order_item_order_ids
    )

    valid_payment = refunds_df["payment_id"].isin(payment_order_lookup.keys())
    expected_order = refunds_df["payment_id"].map(payment_order_lookup)
    payment_matches_order = valid_payment & (
        expected_order == refunds_df["order_id"]
    )

    valid_return = (
        refunds_df["return_id"].isna()
        | refunds_df["return_id"].isin(clean_return_ids)
    )
    positive_amount = refunds_df["refund_amount"].gt(0)

    base_valid_mask = (
        valid_order
        & has_clean_merchandise
        & valid_payment
        & payment_matches_order
        & valid_return
        & positive_amount
    )

    clean = refunds_df[base_valid_mask].copy()
    quarantine = refunds_df[~base_valid_mask].copy()

    # DQ-016 resolved correction: normalize aggregate refund amounts only after
    # reference-quality checks, so invalid/quarantined rows cannot reduce a
    # legitimate clean refund.
    clean = _normalize_refunds_to_payment_limit(
        clean,
        payment_amount_lookup,
    )

    def get_reason(row):
        reasons = []
        if row["order_id"] not in clean_order_ids:
            reasons.append("order_not_in_clean_orders")
        if row["order_id"] not in clean_order_item_order_ids:
            reasons.append("order_has_no_clean_order_items")
        if row["payment_id"] not in payment_order_lookup:
            reasons.append("payment_not_successful_or_missing")
        elif payment_order_lookup[row["payment_id"]] != row["order_id"]:
            reasons.append("payment_order_mismatch")
        if (
            not pd.isna(row["return_id"])
            and row["return_id"] not in clean_return_ids
        ):
            reasons.append("return_not_in_clean_returns")
        if row["refund_amount"] <= 0:
            reasons.append("refund_amount_must_be_positive")
        return "|".join(reasons)

    quarantine["dq_reason"] = quarantine.apply(get_reason, axis=1)
    return clean, quarantine


def validate_finance_costs(df):
    """Validate DQ-019/DQ-020 for Finance/Cost source rows."""

    allowed_cost_types = {
        "payroll",
        "software",
        "rent",
        "infrastructure",
        "professional_services",
        "other",
    }

    type_valid = df["cost_type"].isin(allowed_cost_types)
    amount_valid = df["cost_amount"].gt(0)
    currency_valid = df["currency_code"].eq("EUR")

    valid_mask = type_valid & amount_valid & currency_valid
    clean = df[valid_mask].copy()
    quarantine = df[~valid_mask].copy()

    def get_reason(row):
        reasons = []
        if row["cost_type"] not in allowed_cost_types:
            reasons.append("invalid_finance_cost_type")
        if row["cost_amount"] <= 0:
            reasons.append("finance_cost_must_be_positive")
        if row["currency_code"] != "EUR":
            reasons.append("currency_must_be_EUR")
        return "|".join(reasons)

    quarantine["dq_reason"] = quarantine.apply(get_reason, axis=1)
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