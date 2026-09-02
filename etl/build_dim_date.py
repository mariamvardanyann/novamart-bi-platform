import os

import pandas as pd

from config import PROCESSED_DIR


START_DATE = "2024-08-01"
END_DATE = "2026-07-31"


def build_dim_date():

    dates = pd.date_range(
        start=START_DATE,
        end=END_DATE,
        freq="D",
    )

    dim_date = pd.DataFrame({
        "date": dates
    })

    dim_date["date_key"] = (
        dim_date["date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    dim_date["year"] = (
        dim_date["date"].dt.year
    )

    dim_date["quarter"] = (
        dim_date["date"]
        .dt.quarter
    )

    dim_date["month"] = (
        dim_date["date"]
        .dt.month
    )

    dim_date["month_name"] = (
        dim_date["date"]
        .dt.month_name()
    )

    dim_date["week_of_year"] = (
        dim_date["date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    dim_date["day"] = (
        dim_date["date"]
        .dt.day
    )

    dim_date["day_name"] = (
        dim_date["date"]
        .dt.day_name()
    )

    dim_date["is_weekend"] = (
        dim_date["date"]
        .dt.dayofweek
        .isin([5, 6])
    )

    dim_date["year_month"] = (
        dim_date["date"]
        .dt.strftime("%Y-%m")
    )

    dim_date["date"] = (
        dim_date["date"]
        .dt.date
    )

    return dim_date[
        [
            "date_key",
            "date",
            "year",
            "quarter",
            "month",
            "month_name",
            "week_of_year",
            "day",
            "day_name",
            "is_weekend",
            "year_month",
        ]
    ]


def main():

    dim_date = build_dim_date()

    output_path = os.path.join(
        PROCESSED_DIR,
        "dim_date.csv",
    )

    dim_date.to_csv(
        output_path,
        index=False,
    )

    print()
    print(
        "NovaMart ETL — dim_date created"
    )
    print("=" * 50)

    print(
        f"Rows: {len(dim_date):,}"
    )

    print(
        f"Date range: "
        f"{dim_date['date'].min()} "
        f"→ "
        f"{dim_date['date'].max()}"
    )

    print()
    print(
        f"File created: {output_path}"
    )


if __name__ == "__main__":
    main()