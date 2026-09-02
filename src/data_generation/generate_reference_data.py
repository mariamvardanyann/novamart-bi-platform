"""
NovaMart Synthetic Data Generator — v0.1a: Reference Data

Generates the smallest, static reference tables: countries, categories,
channels, warehouses, carriers. No dependencies on any other generated table.

Run: python src/data_generation/generate_reference_data.py
Output: data/generated/{countries,categories,channels,warehouses,carriers}.csv
"""

import os
import pandas as pd
import config


def generate_countries() -> pd.DataFrame:
    rows = [
        {"country_id": i + 1, "country_code": c["code"], "country_name": c["name"]}
        for i, c in enumerate(config.COUNTRIES)
    ]
    return pd.DataFrame(rows)


def generate_categories() -> pd.DataFrame:
    rows = [
        {"category_id": i + 1, "category_name": name}
        for i, name in enumerate(config.CATEGORIES)
    ]
    return pd.DataFrame(rows)


def generate_channels() -> pd.DataFrame:
    rows = [
        {"channel_id": i + 1, "channel_name": name}
        for i, name in enumerate(config.CHANNELS)
    ]
    return pd.DataFrame(rows)


def generate_carriers() -> pd.DataFrame:
    rows = [
        {"carrier_id": i + 1, "carrier_name": c["name"]}
        for i, c in enumerate(config.CARRIERS)
    ]
    return pd.DataFrame(rows)


def generate_warehouses() -> pd.DataFrame:
    """
    Distribute N_WAREHOUSES across countries proportionally to order_share,
    using the largest-remainder method so every country gets at least 1
    warehouse and the total exactly matches config.N_WAREHOUSES.
    """
    shares = {c["code"]: c["order_share"] for c in config.COUNTRIES}
    n = config.N_WAREHOUSES
    n_countries = len(config.COUNTRIES)

    scale = (n - n_countries) / sum(share * n for share in shares.values()) if n > n_countries else 0
    exact = {code: 1 + shares[code] * n * scale for code in shares}

    floors = {code: int(v) for code, v in exact.items()}
    remainder = n - sum(floors.values())
    # give leftover warehouses to countries with the largest fractional remainder
    fractional = sorted(exact.items(), key=lambda kv: kv[1] - floors[kv[0]], reverse=True)
    for code, _ in fractional[:remainder]:
        floors[code] += 1

    rows = []
    warehouse_id = 1
    code_to_country_id = {c["code"]: i + 1 for i, c in enumerate(config.COUNTRIES)}
    for code, count in floors.items():
        country_name = next(c["name"] for c in config.COUNTRIES if c["code"] == code)
        for k in range(count):
            suffix = f" #{k+1}" if count > 1 else ""
            rows.append({
                "warehouse_id": warehouse_id,
                "warehouse_name": f"{country_name} Fulfillment Center{suffix}",
                "country_id": code_to_country_id[code],
            })
            warehouse_id += 1

    df = pd.DataFrame(rows)
    assert len(df) == config.N_WAREHOUSES, f"Expected {config.N_WAREHOUSES} warehouses, got {len(df)}"
    return df


def main() -> None:
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "generated")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    countries = generate_countries()
    categories = generate_categories()
    channels = generate_channels()
    carriers = generate_carriers()
    warehouses = generate_warehouses()

    countries.to_csv(os.path.join(out_dir, "countries.csv"), index=False)
    categories.to_csv(os.path.join(out_dir, "categories.csv"), index=False)
    channels.to_csv(os.path.join(out_dir, "channels.csv"), index=False)
    carriers.to_csv(os.path.join(out_dir, "carriers.csv"), index=False)
    warehouses.to_csv(os.path.join(out_dir, "warehouses.csv"), index=False)

    print("Reference data generated:")
    print(f"  countries.csv   : {len(countries):>4} rows")
    print(f"  categories.csv  : {len(categories):>4} rows")
    print(f"  channels.csv    : {len(channels):>4} rows")
    print(f"  carriers.csv    : {len(carriers):>4} rows")
    print(f"  warehouses.csv  : {len(warehouses):>4} rows")
    print()
    print("Warehouse distribution by country:")
    merged = warehouses.merge(countries, on="country_id")
    print(merged.groupby("country_name").size().sort_values(ascending=False).to_string())
    print()
    print(f"Output folder: {out_dir}")


if __name__ == "__main__":
    main()
