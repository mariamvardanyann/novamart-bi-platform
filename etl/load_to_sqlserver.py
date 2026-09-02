import os
import math
from datetime import date, datetime

import numpy as np
import pandas as pd
import pyodbc


# ============================================================
# CONFIGURATION
# ============================================================

SERVER = r"DESKTOP-6R0D4NK\SQLEXPRESS"
DATABASE = "novamart"

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

PROCESSED_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
)

LOAD_ORDER = [
    "countries",
    "categories",
    "channels",
    "carriers",
    "warehouses",
    "products",
    "customers",
    "promotions",
    "campaigns",
    "finance_costs",

    "orders",
    "order_items",
    "payments",
    "shipments",
    "returns",
    "refunds",

    "marketing_spend",
    "marketing_events",

    "dim_date",
    "customer_cohorts",
    "marketing_attribution",
]

BATCH_SIZE = 2_000


# ============================================================
# CONNECTION
# ============================================================

def choose_driver():

    installed = pyodbc.drivers()

    preferred = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "SQL Server",
    ]

    for driver in preferred:
        if driver in installed:
            return driver

    raise RuntimeError(
        "No SQL Server ODBC driver found.\n"
        f"Installed drivers: {installed}"
    )


def connect_to_sql_server():

    driver = choose_driver()

    print(f"Using ODBC driver: {driver}")

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(
        connection_string
    )


# ============================================================
# SQL METADATA
# ============================================================

def get_table_columns(
    cursor,
    table_name,
):

    query = """
    SELECT
        c.name AS column_name,
        c.column_id,
        c.is_identity,
        c.is_nullable
    FROM sys.columns c
    INNER JOIN sys.tables t
        ON c.object_id = t.object_id
    INNER JOIN sys.schemas s
        ON t.schema_id = s.schema_id
    WHERE
        s.name = 'dbo'
        AND t.name = ?
    ORDER BY c.column_id;
    """

    rows = cursor.execute(
        query,
        table_name,
    ).fetchall()

    return [
        {
            "name": row.column_name,
            "is_identity": bool(row.is_identity),
            "is_nullable": bool(row.is_nullable),
        }
        for row in rows
    ]


def get_table_row_count(
    cursor,
    table_name,
):

    result = cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM dbo.[{table_name}]
        """
    ).fetchone()

    return int(result[0])


# ============================================================
# VALUE CLEANING
# ============================================================

def clean_value(value):

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):

        if math.isnan(float(value)):
            return None

        return float(value)

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if isinstance(value, (datetime, date)):
        return value

    return value


# ============================================================
# TABLE-SPECIFIC TRANSFORMS
# ============================================================

def transform_for_sql(
    table_name,
    df,
):

    df = df.copy()

    # ========================================================
    # FINANCE COSTS
    # ========================================================

    if table_name == "finance_costs":

        df = df.rename(
            columns={
                "finance_cost_id": "cost_id",
                "cost_amount": "amount",
            }
        )

        df["cost_category"] = df["cost_type"]

    # ========================================================
    # SHIPMENTS
    # ========================================================

    elif table_name == "shipments":

        if "shipped_timestamp" in df.columns:

            df = df.rename(
                columns={
                    "shipped_timestamp":
                        "shipping_timestamp",
                }
            )

        if "fulfillment_timestamp" not in df.columns:

            df[
                "fulfillment_timestamp"
            ] = df[
                "shipping_timestamp"
            ]

        if "expected_delivery_date" not in df.columns:

            shipping_dates = pd.to_datetime(
                df["shipping_timestamp"],
                errors="coerce",
            )

            df[
                "expected_delivery_date"
            ] = (
                shipping_dates
                + pd.Timedelta(days=5)
            ).dt.date

        if "shipment_status" not in df.columns:

            df["shipment_status"] = "shipped"

            delivered_mask = (
                df[
                    "actual_delivery_timestamp"
                ].notna()
            )

            df.loc[
                delivered_mask,
                "shipment_status",
            ] = "delivered"

    # ========================================================
    # RETURNS
    # ========================================================

    elif table_name == "returns":

        if "defect_flag" not in df.columns:

            df["defect_flag"] = (
                df["return_reason"]
                .astype(str)
                .str.lower()
                .eq("defective")
                .astype(int)
            )

        if "return_status" not in df.columns:

            df["return_status"] = "received"

    # ========================================================
    # MARKETING SPEND
    # ========================================================

    elif table_name == "marketing_spend":

        df = df.rename(
            columns={
                "marketing_spend_id":
                    "spend_id",
                "spend_amount":
                    "ad_spend",
            }
        )

    # ========================================================
    # DIM DATE
    # ========================================================

    elif table_name == "dim_date":

        df = df.drop(
            columns=[
                "date_key",
            ],
            errors="ignore",
        )

        df = df.rename(
            columns={
                "date": "date_key",
               
            }
        )

        df["date_key"] = pd.to_datetime(
            df["date_key"],
            errors="coerce",
        ).dt.date

        df["day_of_week"] = (
        pd.to_datetime(
            df["date_key"]
        ).dt.dayofweek
        + 1
    )

    return df


# ============================================================
# CSV LOADING
# ============================================================

def read_processed_csv(
    table_name,
):

    path = os.path.join(
        PROCESSED_DIR,
        f"{table_name}.csv",
    )

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"Processed file not found:\n"
            f"{path}"
        )

    df = pd.read_csv(path)

    return transform_for_sql(
        table_name,
        df,
    )


# ============================================================
# REQUIRED COLUMN VALIDATION
# ============================================================

def validate_required_columns(
    sql_metadata,
    df,
    table_name,
):

    missing_required = []

    for column in sql_metadata:

        name = column["name"]

        if (
            not column["is_nullable"]
            and not column["is_identity"]
            and name not in df.columns
        ):

            missing_required.append(name)

    if missing_required:

        raise RuntimeError(
            f"\nCannot load dbo.{table_name}.\n"
            "Required SQL columns are missing "
            "from the transformed dataframe:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing_required
            )
        )


# ============================================================
# BATCH INSERT
# ============================================================

def insert_in_batches(
    cursor,
    insert_sql,
    records,
):

    total_rows = len(records)

    for start in range(
        0,
        total_rows,
        BATCH_SIZE,
    ):

        end = min(
            start + BATCH_SIZE,
            total_rows,
        )

        batch = records[
            start:end
        ]

        cursor.fast_executemany = False

        cursor.executemany(
            insert_sql,
            batch,
        )


# ============================================================
# TABLE LOAD
# ============================================================

def load_table(
    connection,
    table_name,
):

    cursor = connection.cursor()

    existing_rows = (
        get_table_row_count(
            cursor,
            table_name,
        )
    )

    # Resume-safe behavior
    if existing_rows > 0:

        print(
            f"⏭️  {table_name:<25}"
            f"{existing_rows:>10,} rows "
            "(already loaded — skipped)"
        )

        return

    df = read_processed_csv(
        table_name
    )

    sql_metadata = (
        get_table_columns(
            cursor,
            table_name,
        )
    )

    if not sql_metadata:

        raise RuntimeError(
            f"SQL table dbo.{table_name} "
            "was not found."
        )

    validate_required_columns(
        sql_metadata,
        df,
        table_name,
    )

    sql_columns = [
        column["name"]
        for column in sql_metadata
    ]

    identity_columns = {
        column["name"]
        for column in sql_metadata
        if column["is_identity"]
    }

    insert_columns = [
        column
        for column in sql_columns
        if column in df.columns
    ]

    if not insert_columns:

        raise RuntimeError(
            f"No matching columns between "
            f"{table_name}.csv and "
            f"dbo.{table_name}"
        )

    extra_csv_columns = [
        column
        for column in df.columns
        if column not in sql_columns
    ]

    if extra_csv_columns:

        print(
            f"  Extra CSV columns ignored "
            f"for {table_name}:"
        )

        for column in extra_csv_columns:

            print(
                f"    - {column}"
            )

    selected_df = df[
        insert_columns
    ].copy()

    column_sql = ", ".join(
        f"[{column}]"
        for column in insert_columns
    )

    placeholders = ", ".join(
        "?"
        for _ in insert_columns
    )

    insert_sql = (
        f"INSERT INTO "
        f"dbo.[{table_name}] "
        f"({column_sql}) "
        f"VALUES ({placeholders})"
    )

    records = []

    for row in (
        selected_df.itertuples(
            index=False,
            name=None,
        )
    ):

        cleaned_row = tuple(
            clean_value(value)
            for value in row
        )

        records.append(
            cleaned_row
        )

    identity_insert_needed = any(
        column in identity_columns
        for column in insert_columns
    )

    try:

        if identity_insert_needed:

            cursor.execute(
                f"""
                SET IDENTITY_INSERT
                dbo.[{table_name}] ON
                """
            )

        insert_in_batches(
            cursor,
            insert_sql,
            records,
        )

        if identity_insert_needed:

            cursor.execute(
                f"""
                SET IDENTITY_INSERT
                dbo.[{table_name}] OFF
                """
            )

        connection.commit()

    except Exception:

        connection.rollback()

        if identity_insert_needed:

            try:

                cursor.execute(
                    f"""
                    SET IDENTITY_INSERT
                    dbo.[{table_name}] OFF
                    """
                )

                connection.commit()

            except Exception:

                connection.rollback()

        raise

    loaded_rows = (
        get_table_row_count(
            cursor,
            table_name,
        )
    )

    print(
        f"✅ {table_name:<25}"
        f"{loaded_rows:>10,} rows"
    )


# ============================================================
# FINAL DATABASE COUNTS
# ============================================================

def print_database_counts(
    connection,
):

    cursor = connection.cursor()

    print()
    print("SQL Server row counts")
    print("=" * 60)

    for table_name in LOAD_ORDER:

        count = (
            get_table_row_count(
                cursor,
                table_name,
            )
        )

        print(
            f"{table_name:<25}"
            f"{count:>10,}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print(
        "NovaMart Sprint 3.1 — "
        "SQL Server Data Load"
    )

    print("=" * 60)

    print(f"Server:   {SERVER}")
    print(f"Database: {DATABASE}")
    print(f"Source:   {PROCESSED_DIR}")

    print()

    connection = (
        connect_to_sql_server()
    )

    try:

        print()
        print("Loading processed tables...")
        print()

        for table_name in LOAD_ORDER:

            load_table(
                connection,
                table_name,
            )

        print_database_counts(
            connection
        )

        print()
        print("=" * 60)

        print(
            "NovaMart SQL Server load "
            "completed successfully."
        )

    finally:

        connection.close()


if __name__ == "__main__":
    main()