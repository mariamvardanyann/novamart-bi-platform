import os

from config import (
    PROCESSED_DIR,
)

from load_raw import load_csv


PASSTHROUGH_TABLES = [
    "countries.csv",
    "categories.csv",
    "channels.csv",
    "carriers.csv",
    "warehouses.csv",
    "products.csv",
    "customers.csv",
    "campaigns.csv",
]


def copy_passthrough_tables():

    results = {}

    for filename in PASSTHROUGH_TABLES:

        df = load_csv(
            filename
        )

        output_path = os.path.join(
            PROCESSED_DIR,
            filename,
        )

        df.to_csv(
            output_path,
            index=False,
        )

        results[
            filename
        ] = len(df)

    return results