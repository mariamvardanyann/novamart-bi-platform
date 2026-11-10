"""
NovaMart Synthetic Data Generator — v0.6a: Finance Costs

Generates:
    data/generated/finance_costs.csv

Target:
    ~1,500 finance cost rows

Run:
    python src/data_generation/generate_finance_costs.py
"""

import os

import numpy as np
import pandas as pd

import config


N_FINANCE_COSTS_TARGET = config.N_FINANCE_COST_ROWS_TARGET


def get_project_root():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )


def generate_finance_costs():

    rng = np.random.default_rng(
        config.RANDOM_SEED + 1000
    )

    start_date = pd.Timestamp(
        config.START_DATE
    )

    end_date = pd.Timestamp(
        config.END_DATE
    )

    all_dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    cost_types = list(config.COST_TYPES)
    cost_type_weights = [
        config.COST_TYPE_WEIGHTS[cost_type]
        for cost_type in cost_types
    ]
    amount_ranges = config.COST_AMOUNT_RANGES

    rows = []

    for finance_cost_id in range(
        1,
        N_FINANCE_COSTS_TARGET + 1,
    ):

        cost_type = str(
            rng.choice(
                cost_types,
                p=cost_type_weights,
            )
        )

        min_amount, max_amount = (
            amount_ranges[
                cost_type
            ]
        )

        cost_amount = round(
            float(
                rng.uniform(
                    min_amount,
                    max_amount,
                )
            ),
            2,
        )

        cost_date = pd.Timestamp(
            rng.choice(
                all_dates
            )
        )

        rows.append({
            "finance_cost_id":
                finance_cost_id,

            "cost_date":
                cost_date.date(),

            "cost_type":
                cost_type,

            "cost_amount":
                cost_amount,

            "currency_code":
                config.CURRENCY_CODE,
        })

    finance_costs = pd.DataFrame(
        rows
    )

    finance_costs = (
        finance_costs
        .sort_values(
            [
                "cost_date",
                "finance_cost_id",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    return finance_costs


def validate_finance_costs(
    finance_costs,
):

    assert (
        len(finance_costs)
        == N_FINANCE_COSTS_TARGET
    )

    assert finance_costs[
        "finance_cost_id"
    ].is_unique

    assert finance_costs[
        "cost_date"
    ].notna().all()

    assert finance_costs[
        "cost_type"
    ].notna().all()

    assert set(finance_costs["cost_type"].unique()).issubset(
        set(config.COST_TYPES)
    )

    assert finance_costs[
        "cost_amount"
    ].gt(0).all()

    assert finance_costs[
        "currency_code"
    ].eq(
        config.CURRENCY_CODE
    ).all()


def main():

    finance_costs = (
        generate_finance_costs()
    )

    validate_finance_costs(
        finance_costs
    )

    output_path = os.path.join(
        get_project_root(),
        "data",
        "generated",
        "finance_costs.csv",
    )

    finance_costs.to_csv(
        output_path,
        index=False,
    )

    total_cost = float(
        finance_costs[
            "cost_amount"
        ].sum()
    )

    average_cost = float(
        finance_costs[
            "cost_amount"
        ].mean()
    )

    print()

    print(
        "NovaMart v0.6a — "
        "Finance Costs generated successfully"
    )

    print("=" * 60)

    print(
        f"Finance cost rows: "
        f"{len(finance_costs):,}"
    )

    print()

    print(
        "Cost type distribution:"
    )

    print(
        finance_costs[
            "cost_type"
        ]
        .value_counts()
        .to_string()
    )

    print()

    print(
        f"Total finance costs: "
        f"EUR {total_cost:,.2f}"
    )

    print(
        f"Average cost record: "
        f"EUR {average_cost:,.2f}"
    )

    print()

    print(
        f"Date range: "
        f"{finance_costs['cost_date'].min()} "
        f"→ "
        f"{finance_costs['cost_date'].max()}"
    )

    print()

    print(
        f"File created: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()