import os


from config import (
    PROCESSED_DIR,
    QUARANTINE_DIR,
)

from load_raw import load_csv

from copy_passthrough import (
    copy_passthrough_tables,
)

from build_quarantine import (
    build_consolidated_quarantine,
)

from build_dim_date import (
    build_dim_date,
)

from build_customer_cohorts import (
    build_customer_cohorts,
)

from build_marketing_attribution import (
    build_marketing_attribution,
)

from validate import (
    validate_order_items,
    validate_orders,
    validate_shipments,
    validate_returns,
    validate_marketing_spend,
    validate_marketing_events,
    validate_promotions,
    validate_payments,
    validate_refunds,
    enforce_clean_order_reference,
    enforce_clean_order_line_reference,
)


def save_outputs(
    clean,
    quarantine,
    filename,
):

    clean.to_csv(
        os.path.join(
            PROCESSED_DIR,
            filename,
        ),
        index=False,
    )

    quarantine_filename = (
        filename.replace(
            ".csv",
            "_quarantine.csv",
        )
    )

    quarantine.to_csv(
        os.path.join(
            QUARANTINE_DIR,
            quarantine_filename,
        ),
        index=False,
    )


def print_result(
    title,
    raw,
    clean,
    quarantine,
):

    print()
    print(
        f"NovaMart ETL — {title}"
    )
    print("=" * 50)

    print(
        f"Raw rows: {len(raw):,}"
    )

    print(
        f"Clean rows: {len(clean):,}"
    )

    print(
        f"Quarantined rows: "
        f"{len(quarantine):,}"
    )

    if len(quarantine) > 0:

        print()
        print("DQ reasons:")

        print(
            quarantine[
                "dq_reason"
            ]
            .value_counts()
            .to_string()
        )


def main():

    # =========================================================
    # CREATE OUTPUT DIRECTORIES
    # =========================================================

    os.makedirs(
        PROCESSED_DIR,
        exist_ok=True,
    )

    os.makedirs(
        QUARANTINE_DIR,
        exist_ok=True,
    )

    # =========================================================
    # ORDER ITEMS — INITIAL DQ
    # =========================================================

    order_items = load_csv(
        "order_items.csv"
    )

    products = load_csv(
        "products.csv"
    )

    valid_product_ids = set(
        products[
            "product_id"
        ].astype(int)
    )

    (
        clean_order_items,
        quarantine_order_items,
    ) = validate_order_items(
        order_items,
        valid_product_ids,
    )

    # =========================================================
    # ORDERS
    # =========================================================

    orders = load_csv(
        "orders.csv"
    )

    (
        clean_orders,
        quarantine_orders,
    ) = validate_orders(
        orders
    )

    clean_order_ids = set(
        clean_orders[
            "order_id"
        ].astype(int)
    )

    # =========================================================
    # ORDER ITEMS → ORDERS FK CHECK
    # =========================================================

    (
        clean_order_items,
        quarantine_order_items,
    ) = enforce_clean_order_reference(
        clean_order_items,
        quarantine_order_items,
        clean_order_ids,
    )

    clean_order_line_ids = set(
    clean_order_items[
        "order_line_id"
    ].astype(int)
)

    save_outputs(
        clean_order_items,
        quarantine_order_items,
        "order_items.csv",
    )

    # =========================================================
    # SHIPMENTS
    # =========================================================

    shipments = load_csv(
        "shipments.csv"
    )

    (
        clean_shipments,
        quarantine_shipments,
    ) = validate_shipments(
        shipments
    )

    (
        clean_shipments,
        quarantine_shipments,
    ) = enforce_clean_order_reference(
        clean_shipments,
        quarantine_shipments,
        clean_order_ids,
    )

    save_outputs(
        clean_shipments,
        quarantine_shipments,
        "shipments.csv",
    )

    # =========================================================
    # RETURNS
    # =========================================================

    returns = load_csv(
        "returns.csv"
    )

    (
        clean_returns,
        quarantine_returns,
    ) = validate_returns(
        returns,
        shipments,
    )

    (
        clean_returns,
        quarantine_returns,
    ) = enforce_clean_order_reference(
        clean_returns,
        quarantine_returns,
        clean_order_ids,
    )

    (
    clean_returns,
    quarantine_returns,
) = enforce_clean_order_line_reference(
    clean_returns,
    quarantine_returns,
    clean_order_line_ids,
)

    save_outputs(
        clean_returns,
        quarantine_returns,
        "returns.csv",
    )

    clean_return_ids = set(
        clean_returns[
            "return_id"
        ].astype(int)
    )

    # =========================================================
    # PAYMENTS
    # =========================================================

    payments = load_csv(
        "payments.csv"
    )

    (
        clean_payments,
        quarantine_payments,
    ) = validate_payments(
        payments,
        clean_order_ids,
    )

    save_outputs(
        clean_payments,
        quarantine_payments,
        "payments.csv",
    )

    # =========================================================
    # REFUNDS
    # =========================================================

    refunds = load_csv(
        "refunds.csv"
    )

    (
        clean_refunds,
        quarantine_refunds,
    ) = validate_refunds(
        refunds,
        clean_order_ids,
        clean_return_ids,
    )

    save_outputs(
        clean_refunds,
        quarantine_refunds,
        "refunds.csv",
    )

    # =========================================================
    # MARKETING SPEND
    # =========================================================

    marketing_spend = load_csv(
        "marketing_spend.csv"
    )

    (
        clean_marketing_spend,
        quarantine_marketing_spend,
    ) = validate_marketing_spend(
        marketing_spend
    )

    save_outputs(
        clean_marketing_spend,
        quarantine_marketing_spend,
        "marketing_spend.csv",
    )

    # =========================================================
    # MARKETING EVENTS
    # =========================================================

    marketing_events = load_csv(
        "marketing_events.csv"
    )

    (
        clean_marketing_events,
        quarantine_marketing_events,
    ) = validate_marketing_events(
        marketing_events
    )

    save_outputs(
        clean_marketing_events,
        quarantine_marketing_events,
        "marketing_events.csv",
    )

    # =========================================================
    # PROMOTIONS
    # =========================================================

    promotions = load_csv(
        "promotions.csv"
    )

    (
        clean_promotions,
        quarantine_promotions,
    ) = validate_promotions(
        promotions
    )

    save_outputs(
        clean_promotions,
        quarantine_promotions,
        "promotions.csv",
    )

    # =========================================================
    # FIX ORDERS → PROMOTIONS FK
    # =========================================================

    valid_promotion_ids = set(
        clean_promotions[
            "promotion_id"
        ].astype(int)
    )

    invalid_promotion_reference = (
        clean_orders[
            "promotion_id"
        ].notna()
        & ~clean_orders[
            "promotion_id"
        ].isin(
            valid_promotion_ids
        )
    )

    invalid_promotion_count = int(
        invalid_promotion_reference.sum()
    )

    clean_orders.loc[
        invalid_promotion_reference,
        "promotion_id",
    ] = None

    save_outputs(
        clean_orders,
        quarantine_orders,
        "orders.csv",
    )

    print()
    print(
        "Orders with invalid promotion "
        "reference reset to NULL: "
        f"{invalid_promotion_count:,}"
    )

    # =========================================================
    # PASSTHROUGH TABLES
    # =========================================================

    passthrough_results = (
        copy_passthrough_tables()
    )

    # =========================================================
    # CONSOLIDATED QUARANTINE
    # =========================================================

    consolidated_quarantine = (
        build_consolidated_quarantine()
    )

    consolidated_quarantine.to_csv(
        os.path.join(
            QUARANTINE_DIR,
            "quarantine.csv",
        ),
        index=False,
    )

    # =========================================================
    # DIM DATE
    # =========================================================

    dim_date = build_dim_date()

    dim_date.to_csv(
        os.path.join(
            PROCESSED_DIR,
            "dim_date.csv",
        ),
        index=False,
    )

    # =========================================================
    # CUSTOMER COHORTS
    # =========================================================

    customer_cohorts = (
        build_customer_cohorts()
    )

    customer_cohorts.to_csv(
        os.path.join(
            PROCESSED_DIR,
            "customer_cohorts.csv",
        ),
        index=False,
    )

    # =========================================================
    # MARKETING ATTRIBUTION
    # =========================================================

    marketing_attribution = (
        build_marketing_attribution()
    )

    marketing_attribution.to_csv(
        os.path.join(
            PROCESSED_DIR,
            "marketing_attribution.csv",
        ),
        index=False,
    )

    # =========================================================
    # REPORTS
    # =========================================================

    print_result(
        "Order Items",
        order_items,
        clean_order_items,
        quarantine_order_items,
    )

    print_result(
        "Orders",
        orders,
        clean_orders,
        quarantine_orders,
    )

    print_result(
        "Shipments",
        shipments,
        clean_shipments,
        quarantine_shipments,
    )

    print_result(
        "Returns",
        returns,
        clean_returns,
        quarantine_returns,
    )

    print_result(
        "Payments",
        payments,
        clean_payments,
        quarantine_payments,
    )

    print_result(
        "Refunds",
        refunds,
        clean_refunds,
        quarantine_refunds,
    )

    print_result(
        "Marketing Spend",
        marketing_spend,
        clean_marketing_spend,
        quarantine_marketing_spend,
    )

    print_result(
        "Marketing Events",
        marketing_events,
        clean_marketing_events,
        quarantine_marketing_events,
    )

    print_result(
        "Promotions",
        promotions,
        clean_promotions,
        quarantine_promotions,
    )

    # =========================================================
    # PASSTHROUGH REPORT
    # =========================================================

    print()
    print(
        "NovaMart ETL — Passthrough Tables"
    )
    print("=" * 50)

    for (
        filename,
        row_count,
    ) in passthrough_results.items():

        print(
            f"{filename:<25}"
            f"{row_count:>10,} rows"
        )

    # =========================================================
    # QUARANTINE REPORT
    # =========================================================

    print()
    print(
        "NovaMart ETL — "
        "Consolidated Quarantine"
    )
    print("=" * 50)

    print(
        f"Total quarantine rows: "
        f"{len(consolidated_quarantine):,}"
    )

    # =========================================================
    # DERIVED TABLE REPORT
    # =========================================================

    print()
    print(
        "NovaMart ETL — Derived Tables"
    )
    print("=" * 50)

    print(
        f"dim_date: "
        f"{len(dim_date):,} rows"
    )

    print(
        f"customer_cohorts: "
        f"{len(customer_cohorts):,} rows"
    )

    print(
        f"marketing_attribution: "
        f"{len(marketing_attribution):,} rows"
    )

    # =========================================================
    # FINAL RECONCILIATION
    # =========================================================

    print()
    print(
        "NovaMart ETL — Final Reconciliation"
    )
    print("=" * 50)

    assert (
        len(order_items)
        == len(clean_order_items)
        + len(quarantine_order_items)
    )

    assert (
        len(orders)
        == len(clean_orders)
        + len(quarantine_orders)
    )

    assert (
        len(shipments)
        == len(clean_shipments)
        + len(quarantine_shipments)
    )

    assert (
        len(returns)
        == len(clean_returns)
        + len(quarantine_returns)
    )

    assert (
        len(payments)
        == len(clean_payments)
        + len(quarantine_payments)
    )

    assert (
        len(refunds)
        == len(clean_refunds)
        + len(quarantine_refunds)
    )

    assert (
        len(marketing_spend)
        == len(clean_marketing_spend)
        + len(quarantine_marketing_spend)
    )

    assert (
        len(marketing_events)
        == len(clean_marketing_events)
        + len(quarantine_marketing_events)
    )

    assert (
        len(promotions)
        == len(clean_promotions)
        + len(quarantine_promotions)
    )

    # =========================================================
    # FK RECONCILIATION
    # =========================================================

    assert (
        clean_order_items[
            "order_id"
        ].isin(
            clean_order_ids
        ).all()
    )

    assert (
        clean_shipments[
            "order_id"
        ].isin(
            clean_order_ids
        ).all()
    )

    assert (
        clean_returns[
            "order_id"
        ].isin(
            clean_order_ids
        ).all()
    )

    assert (
        clean_payments[
            "order_id"
        ].isin(
            clean_order_ids
        ).all()
    )

    assert (
        clean_refunds[
            "order_id"
        ].isin(
            clean_order_ids
        ).all()
    )

    valid_refund_returns = (
        clean_refunds[
            "return_id"
        ].isna()
        | clean_refunds[
            "return_id"
        ].isin(
            clean_return_ids
        )
    )

    assert (
        valid_refund_returns.all()
    )

    assert (
        clean_orders[
            "promotion_id"
        ].isna()
        | clean_orders[
            "promotion_id"
        ].isin(
            valid_promotion_ids
        )
    ).all()

    assert len(dim_date) == 730

    assert (
        len(customer_cohorts)
        == 10_000
    )

    assert (
        marketing_attribution[
            "campaign_id"
        ].notna().all()
    )

    assert (
    clean_returns[
        "order_line_id"
    ].isin(
        clean_order_line_ids
    ).all()
)

    print(
        "All reconciliation and FK "
        "checks passed."
    )

    print()
    print("=" * 50)

    print(
        "NovaMart Sprint 2 ETL "
        "completed successfully."
    )


if __name__ == "__main__":
    main()