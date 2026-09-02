"""
NovaMart Synthetic Data Generator — v0.1b: Products

Generates 400 products across 12 categories, with:
- uneven category sizes (config.CATEGORY_PRODUCT_SHARE)
- category-appropriate price ranges and margins (config.PRICE_RANGE_EUR_BY_CATEGORY,
  config.CATEGORY_PROFILES)
- a Pareto-style popularity weight so ~20% of products can later drive ~70%
  of weighted sales volume in order_items generation

IMPORTANT — internal generator metadata:
`base_price`, `unit_cogs_base`, and `popularity_weight` are NOT part of the
canonical `products` table schema (see docs/04_data_dictionary.md). They are
generator-internal columns consumed by generate_order_items.py later, and
will be dropped when the final raw CSV is assembled (Sprint 1 finalization
step). This is called out explicitly so nobody mistakes them for real schema
fields.

Depends on: data/generated/categories.csv (must run generate_reference_data.py first)

Run: python src/data_generation/generate_products.py
Output: data/generated/products.csv
"""

import os
import pandas as pd
import numpy as np
import config

GENERATED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "generated"))


def load_categories() -> pd.DataFrame:
    path = os.path.join(GENERATED_DIR, "categories.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Run generate_reference_data.py first."
        )
    return pd.read_csv(path)


def allocate_product_counts_per_category() -> dict:
    """Largest-remainder allocation so counts sum exactly to N_PRODUCTS."""
    n = config.N_PRODUCTS
    exact = {cat: share * n for cat, share in config.CATEGORY_PRODUCT_SHARE.items()}
    floors = {cat: int(v) for cat, v in exact.items()}
    remainder = n - sum(floors.values())
    fractional = sorted(exact.items(), key=lambda kv: kv[1] - floors[kv[0]], reverse=True)
    for cat, _ in fractional[:remainder]:
        floors[cat] += 1
    assert sum(floors.values()) == n
    return floors


def make_popularity_weights(n: int) -> np.ndarray:
    """
    Two-tier Pareto-style weighting: top PARETO_TOP_SHARE_OF_PRODUCTS of
    products get a much higher base weight, calibrated so they command
    PARETO_TOP_SHARE_OF_REVENUE_WEIGHT of total weight. Light jitter keeps it
    from looking artificially flat within each tier.
    """
    n_top = round(config.PARETO_TOP_SHARE_OF_PRODUCTS * n)
    n_rest = n - n_top
    top_share = config.PARETO_TOP_SHARE_OF_REVENUE_WEIGHT

    # solve n_top*w_top / (n_top*w_top + n_rest*w_rest) = top_share, with w_rest = 1
    w_rest = 1.0
    w_top = (top_share * n_rest * w_rest) / ((1 - top_share) * n_top)

    weights = np.concatenate([
        np.full(n_top, w_top) * config.RNG.uniform(0.7, 1.3, size=n_top),
        np.full(n_rest, w_rest) * config.RNG.uniform(0.7, 1.3, size=n_rest),
    ])
    config.RNG.shuffle(weights)  # so "top" products aren't just the first N rows
    return weights


def generate_product_name(category: str, idx: int) -> str:
    adjectives = ["Classic", "Pro", "Essential", "Premium", "Everyday", "Compact",
                  "Advanced", "Urban", "Signature", "Active", "Smart", "Original"]
    nouns_by_category = {
        "Electronics": ["Headphones", "Speaker", "Charger", "Smartwatch", "Tablet Stand", "Cable", "Router"],
        "Home & Kitchen": ["Blender", "Cookware Set", "Kettle", "Storage Jar", "Cutting Board", "Toaster"],
        "Beauty": ["Serum", "Lipstick", "Foundation", "Eyeshadow Palette", "Face Mask", "Mascara"],
        "Fashion": ["T-Shirt", "Jacket", "Sneakers", "Jeans", "Dress", "Scarf", "Belt"],
        "Sports": ["Yoga Mat", "Dumbbell Set", "Running Shoes", "Water Bottle", "Resistance Band"],
        "Books": ["Notebook", "Journal", "Planner", "Novel Collection", "Cookbook"],
        "Toys": ["Building Blocks", "Puzzle", "Action Figure", "Board Game", "Plush Toy"],
        "Office": ["Desk Organizer", "Notebook Set", "Pen Set", "Chair Cushion", "Monitor Stand"],
        "Pet Supplies": ["Pet Bed", "Chew Toy", "Leash", "Food Bowl", "Grooming Brush"],
        "Automotive Accessories": ["Phone Mount", "Seat Cover", "Dash Cam", "Floor Mat", "Car Vacuum"],
        "Garden": ["Plant Pot", "Garden Tool Set", "Watering Can", "Hose Reel", "Solar Light"],
        "Personal Care": ["Toothbrush", "Body Wash", "Razor Set", "Deodorant", "Hair Dryer"],
    }
    noun = config.RNG.choice(nouns_by_category.get(category, ["Item"]))
    adj = config.RNG.choice(adjectives)
    return f"{adj} {noun} {idx}"


def generate_products() -> pd.DataFrame:
    categories_df = load_categories()
    cat_name_to_id = dict(zip(categories_df["category_name"], categories_df["category_id"]))

    counts = allocate_product_counts_per_category()

    rows = []
    product_id = 1
    for category, count in counts.items():
        cat_id = cat_name_to_id[category]
        price_min, price_max = config.PRICE_RANGE_EUR_BY_CATEGORY[category]
        cogs_ratio = config.CATEGORY_PROFILES[category]["cogs_ratio"]

        # log-uniform price draw so cheap items aren't crowded out by expensive ones
        log_prices = config.RNG.uniform(np.log(price_min), np.log(price_max), size=count)
        prices = np.round(np.exp(log_prices), 2)

        for i in range(count):
            base_price = float(prices[i])
            unit_cogs_base = round(base_price * cogs_ratio * config.RNG.uniform(0.92, 1.08), 2)
            active_flag = 0 if config.RNG.random() < 0.04 else 1  # ~4% discontinued
            rows.append({
                "product_id": product_id,
                "product_name": generate_product_name(category, product_id),
                "category_id": cat_id,
                "brand": config.RNG.choice(config.BRAND_NAMES),
                "active_flag": active_flag,
                "base_price": base_price,           # generator-internal, not in schema
                "unit_cogs_base": unit_cogs_base,    # generator-internal, not in schema
            })
            product_id += 1

    df = pd.DataFrame(rows)
    df["popularity_weight"] = make_popularity_weights(len(df))  # generator-internal, not in schema
    return df


def main():
    os.makedirs(GENERATED_DIR, exist_ok=True)
    products = generate_products()
    out_path = os.path.join(GENERATED_DIR, "products.csv")
    products.to_csv(out_path, index=False)

    print(f"products.csv generated: {len(products)} rows")
    print()
    print("Products per category:")
    categories_df = load_categories()
    merged = products.merge(categories_df, on="category_id")
    print(merged.groupby("category_name").size().sort_values(ascending=False).to_string())
    print()
    print("Price range check (base_price, EUR) per category:")
    print(merged.groupby("category_name")["base_price"].agg(["min", "max", "mean"]).round(2).to_string())
    print()
    top_n = round(config.PARETO_TOP_SHARE_OF_PRODUCTS * len(products))
    top_weight_share = products.nlargest(top_n, "popularity_weight")["popularity_weight"].sum() / products["popularity_weight"].sum()
    print(f"Top {top_n} products ({config.PARETO_TOP_SHARE_OF_PRODUCTS:.0%}) command "
          f"{top_weight_share:.1%} of total popularity weight "
          f"(target: {config.PARETO_TOP_SHARE_OF_REVENUE_WEIGHT:.0%})")
    print()
    print(f"Inactive (discontinued) products: {(products['active_flag']==0).sum()} "
          f"({(products['active_flag']==0).mean():.1%})")
    print()
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
