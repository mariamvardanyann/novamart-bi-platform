import os

import pandas as pd

from config import (
    QUARANTINE_DIR,
)


QUARANTINE_FILES = {
    "order_items":
        "order_items_quarantine.csv",

    "orders":
        "orders_quarantine.csv",

    "shipments":
        "shipments_quarantine.csv",

    "returns":
        "returns_quarantine.csv",

    "payments":
        "payments_quarantine.csv",

    "refunds":
        "refunds_quarantine.csv",

    "marketing_spend":
        "marketing_spend_quarantine.csv",

    "marketing_events":
        "marketing_events_quarantine.csv",

    "promotions":
        "promotions_quarantine.csv",
}


def build_consolidated_quarantine():

    frames = []

    for (
        source_table,
        filename,
    ) in QUARANTINE_FILES.items():

        path = os.path.join(
            QUARANTINE_DIR,
            filename,
        )

        if not os.path.exists(path):
            continue

        df = pd.read_csv(path)

        if len(df) == 0:
            continue

        df.insert(
            0,
            "source_table",
            source_table,
        )

        frames.append(df)

    if not frames:

        return pd.DataFrame()

    consolidated = pd.concat(
        frames,
        ignore_index=True,
        sort=False,
    )

    return consolidated


def main():

    quarantine = (
        build_consolidated_quarantine()
    )

    output_path = os.path.join(
        QUARANTINE_DIR,
        "quarantine.csv",
    )

    quarantine.to_csv(
        output_path,
        index=False,
    )

    print()
    print(
        "NovaMart ETL — Consolidated Quarantine"
    )
    print("=" * 50)

    print(
        f"Total quarantine rows: "
        f"{len(quarantine):,}"
    )

    print()

    print(
        "Rows by source table:"
    )

    print(
        quarantine[
            "source_table"
        ]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "Top DQ reasons:"
    )

    print(
        quarantine[
            "dq_reason"
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