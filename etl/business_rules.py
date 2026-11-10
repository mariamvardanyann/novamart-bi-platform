"""Shared analytical eligibility rules for NovaMart ETL-derived datasets."""

from __future__ import annotations

import pandas as pd

ELIGIBLE_COMPLETED_STATUSES = {
    "paid",
    "fulfilled",
    "shipped",
    "delivered",
}


def get_eligible_completed_orders(
    orders: pd.DataFrame,
    payments: pd.DataFrame,
) -> pd.DataFrame:
    """Return orders that have reached paid-or-later and have a successful payment.

    This is the governing Phase-1 definition used for customer and commercial
    purchase-based KPIs. ``placed`` and ``cancelled`` orders are excluded.
    """

    succeeded_order_ids = set(
        payments.loc[
            payments["payment_status"].eq("succeeded"),
            "order_id",
        ].dropna().astype(int)
    )

    eligible = orders[
        orders["status"].isin(ELIGIBLE_COMPLETED_STATUSES)
        & orders["order_id"].isin(succeeded_order_ids)
    ].copy()

    return eligible
