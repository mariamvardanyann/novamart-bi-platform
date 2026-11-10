"""
NovaMart Synthetic Data Generator — Centralized Configuration

Every volume, distribution, and business-pattern assumption lives here.
No other script in src/data_generation/ should hardcode a magic number that
belongs here. See docs/07_synthetic_data_specification.md for the rationale
behind each value.

All distributions marked "synthetic assumption" are illustrative choices
for this portfolio project, not claims about real-world markets.
"""

import numpy as np

# ============================================================================
# REPRODUCIBILITY
# ============================================================================
RANDOM_SEED = 42
RNG = np.random.default_rng(RANDOM_SEED)

# ============================================================================
# TIME SCOPE (spec §2)
# ============================================================================
START_DATE = "2024-08-01"
END_DATE = "2026-07-31"  # 24 full months

# ============================================================================
# CURRENCY (spec §2, locked per DQ-020 / KPI-001 governing definition)
# ============================================================================
CURRENCY_CODE = "EUR"

# ============================================================================
# COUNTRIES (spec §2) — order share is a synthetic assumption
# ============================================================================
COUNTRIES = [
    {"code": "DE", "name": "Germany",     "order_share": 0.25},
    {"code": "FR", "name": "France",      "order_share": 0.18},
    {"code": "IT", "name": "Italy",       "order_share": 0.14},
    {"code": "ES", "name": "Spain",       "order_share": 0.13},
    {"code": "NL", "name": "Netherlands", "order_share": 0.10},
    {"code": "PL", "name": "Poland",      "order_share": 0.09},
    {"code": "BE", "name": "Belgium",     "order_share": 0.06},
    {"code": "AT", "name": "Austria",     "order_share": 0.05},
]
assert abs(sum(c["order_share"] for c in COUNTRIES) - 1.0) < 1e-9

# ============================================================================
# CATEGORIES (spec §4.1) — Beauty vs Personal Care boundary is locked
# ============================================================================
CATEGORIES = [
    "Electronics", "Home & Kitchen", "Beauty", "Fashion", "Sports", "Books",
    "Toys", "Office", "Pet Supplies", "Automotive Accessories", "Garden",
    "Personal Care",
]

# Category-level margin/return-rate personality (spec §6, §12)
# cogs_ratio = unit_cogs as a fraction of original_unit_price (before discount)
# return_rate_multiplier scales the base return rate for that category
CATEGORY_PROFILES = {
    "Electronics":             {"cogs_ratio": 0.72, "return_rate_multiplier": 1.15, "defect_share": 0.55},
    "Home & Kitchen":          {"cogs_ratio": 0.60, "return_rate_multiplier": 0.90, "defect_share": 0.30},
    "Beauty":                  {"cogs_ratio": 0.35, "return_rate_multiplier": 0.70, "defect_share": 0.15},
    "Fashion":                 {"cogs_ratio": 0.45, "return_rate_multiplier": 1.45, "defect_share": 0.10},
    "Sports":                  {"cogs_ratio": 0.55, "return_rate_multiplier": 0.95, "defect_share": 0.25},
    "Books":                   {"cogs_ratio": 0.50, "return_rate_multiplier": 0.35, "defect_share": 0.05},
    "Toys":                    {"cogs_ratio": 0.48, "return_rate_multiplier": 1.00, "defect_share": 0.20},
    "Office":                  {"cogs_ratio": 0.55, "return_rate_multiplier": 0.60, "defect_share": 0.20},
    "Pet Supplies":            {"cogs_ratio": 0.52, "return_rate_multiplier": 0.55, "defect_share": 0.15},
    "Automotive Accessories":  {"cogs_ratio": 0.58, "return_rate_multiplier": 0.85, "defect_share": 0.30},
    "Garden":                  {"cogs_ratio": 0.50, "return_rate_multiplier": 0.65, "defect_share": 0.20},
    "Personal Care":           {"cogs_ratio": 0.38, "return_rate_multiplier": 0.60, "defect_share": 0.10},
}
BASE_RETURN_RATE = 0.064  # overall target ~8-12% of eligible delivered order lines (spec §12)

# ============================================================================
# CHANNELS (spec §4.2)
# ============================================================================
CHANNELS = ["Paid Search", "Paid Social", "Email", "Organic Search", "Affiliate", "Direct"]

# ============================================================================
# CARRIERS (spec §4.3) — fictional names, distinct performance personalities
# ============================================================================
CARRIERS = [
    {"name": "SwiftPost",     "speed_days_mean": 2.0, "speed_days_sd": 0.6, "on_time_rate": 0.94, "cost_multiplier": 1.25},
    {"name": "ValueLine",     "speed_days_mean": 3.5, "speed_days_sd": 1.2, "on_time_rate": 0.82, "cost_multiplier": 0.80},
    {"name": "NordCarrier",   "speed_days_mean": 2.5, "speed_days_sd": 0.7, "on_time_rate": 0.93, "cost_multiplier": 1.05},
    {"name": "MedExpress",    "speed_days_mean": 3.0, "speed_days_sd": 1.5, "on_time_rate": 0.78, "cost_multiplier": 0.95},
    {"name": "BalancedFreight", "speed_days_mean": 2.8, "speed_days_sd": 0.9, "on_time_rate": 0.88, "cost_multiplier": 1.00},
    {"name": "BackupShip",    "speed_days_mean": 4.0, "speed_days_sd": 1.3, "on_time_rate": 0.80, "cost_multiplier": 0.85},
]
# NordCarrier performs best in DE/NL; MedExpress has higher delay rate in ES/IT (spec §4.3)
CARRIER_COUNTRY_BONUS = {
    "NordCarrier": {"DE": 0.04, "NL": 0.04},
    "MedExpress":  {"ES": -0.08, "IT": -0.08},
}

# ============================================================================
# WAREHOUSES (spec §4.4)
# ============================================================================
N_WAREHOUSES = 12
# Higher-volume countries get more warehouses; exact assignment done in generator

# ============================================================================
# PRODUCTS (spec §6)
# ============================================================================
N_PRODUCTS = 400
PARETO_TOP_SHARE_OF_PRODUCTS = 0.20   # ~20% of products ...
PARETO_TOP_SHARE_OF_REVENUE_WEIGHT = 0.70  # ...drive a disproportionate share of sales weight

# How many of the 400 products fall in each category (synthetic assumption,
# reflecting typical e-commerce SKU-count mix — Fashion/Electronics carry
# many more SKUs than e.g. Personal Care)
CATEGORY_PRODUCT_SHARE = {
    "Electronics":             0.12,
    "Home & Kitchen":          0.10,
    "Beauty":                  0.08,
    "Fashion":                 0.18,
    "Sports":                  0.08,
    "Books":                   0.10,
    "Toys":                    0.08,
    "Office":                  0.06,
    "Pet Supplies":            0.06,
    "Automotive Accessories":  0.05,
    "Garden":                  0.05,
    "Personal Care":           0.04,
}
assert abs(sum(CATEGORY_PRODUCT_SHARE.values()) - 1.0) < 1e-9

# (min, max) EUR list price per category — synthetic assumption
PRICE_RANGE_EUR_BY_CATEGORY = {
    "Electronics":             (15, 800),
    "Home & Kitchen":          (8, 250),
    "Beauty":                  (5, 80),
    "Fashion":                 (10, 150),
    "Sports":                  (8, 300),
    "Books":                   (6, 40),
    "Toys":                    (5, 120),
    "Office":                  (4, 150),
    "Pet Supplies":            (5, 90),
    "Automotive Accessories":  (6, 200),
    "Garden":                  (8, 180),
    "Personal Care":           (3, 40),
}

# Fictional brand pool, resampled across products (not category-exclusive)
BRAND_NAMES = [
    "Norvex", "Lumeo", "Kastel", "Verano", "Brixly", "Solento", "Marnova",
    "Quirin", "Delvato", "Orbex", "Fennora", "Halvex", "Tresoro", "Nordwell",
    "Calvex", "Ambrion", "Ristone", "Velmora", "Trenzo", "Auralite",
    "Boskin", "Zenmara", "Corvale", "Pellara", "Vintro",
]

# ============================================================================
# CUSTOMERS (spec §5)
# ============================================================================
N_CUSTOMERS = 10_000

# Purchase-frequency segments (spec §5) — used to drive number of orders per customer
CUSTOMER_SEGMENTS = [
    {"name": "one_time",   "share": 0.225, "order_count_range": (1, 1)},
    {"name": "occasional", "share": 0.475, "order_count_range": (2, 5)},
    {"name": "frequent",   "share": 0.20,  "order_count_range": (6, 10)},
    {"name": "loyal",      "share": 0.10,  "order_count_range": (11, 25)},
]
assert abs(sum(s["share"] for s in CUSTOMER_SEGMENTS) - 1.0) < 1e-9

# Demographics (locked — synthetic assumption, not a market claim)
AGE_GROUPS = [
    {"label": "18-24", "share": 0.12},
    {"label": "25-34", "share": 0.28},
    {"label": "35-44", "share": 0.26},
    {"label": "45-54", "share": 0.18},
    {"label": "55-64", "share": 0.11},
    {"label": "65+",   "share": 0.05},
]
assert abs(sum(a["share"] for a in AGE_GROUPS) - 1.0) < 1e-9

GENDER_DISTRIBUTION = {"female": 0.48, "male": 0.48, "unspecified": 0.04}

# ============================================================================
# PROMOTIONS (spec §9)
# ============================================================================
N_PROMOTIONS = 40
PROMOTION_TYPES = ["seasonal", "flash", "clearance", "loyalty", "category_specific"]
# Each promotion gets one performance personality at generation time
PROMOTION_ARCHETYPES = [
    {"name": "strong_uplift_healthy_margin", "share": 0.25},
    {"name": "strong_uplift_margin_erosion", "share": 0.25},
    {"name": "weak_uplift",                  "share": 0.30},
    {"name": "country_or_category_specific", "share": 0.20},
]
assert abs(sum(p["share"] for p in PROMOTION_ARCHETYPES) - 1.0) < 1e-9

# Synthetic demand response used to make promotion archetypes affect order
# volume, not only discount depth. These are scenario assumptions, not market
# estimates. A multiplier of 1.45 means the affected dates receive 45% more
# order-generation weight than their non-promotion baseline.
PROMOTION_DEMAND_MULTIPLIER = {
    "strong_uplift_healthy_margin": 1.45,
    "strong_uplift_margin_erosion": 1.60,
    "weak_uplift": 1.08,
    "country_or_category_specific": 1.25,
}

PROMOTION_ADOPTION_RATE = {
    "strong_uplift_healthy_margin": 0.48,
    "strong_uplift_margin_erosion": 0.55,
    "weak_uplift": 0.22,
    "country_or_category_specific": 0.35,
}

# ============================================================================
# ORDERS (spec §7)
# ============================================================================
N_ORDERS_TARGET = 60_000
ORDER_STATUS_SHARE = {
    "delivered": 0.90,
    "cancelled": 0.04,
    "shipped": 0.02,
    "fulfilled": 0.02,
    "paid": 0.01,
    "placed": 0.01,
}
assert abs(sum(ORDER_STATUS_SHARE.values()) - 1.0) < 1e-9

CANCELLATION_REASONS = [
    "customer_changed_mind", "payment_failed", "out_of_stock",
    "fraud_suspected", "duplicate_order",
]

# Growth curve: relative monthly order-volume weights across 24 months.
# Encodes the Charter's "revenue growth has slowed" narrative: strong growth
# months 1-12, flattening/slight decline months 13-24, with a Nov/Dec spike
# and a summer (Jul/Aug) dip layered on top by the generator.
def monthly_growth_curve(n_months: int = 24) -> np.ndarray:
    months = np.arange(n_months)
    growth_phase = np.minimum(months, 11) / 11  # ramps 0->1 over first 12 months
    plateau_phase = np.where(months > 11, 1.0 - 0.10 * (months - 11) / 12, 1.0)  # gentle decline after
    base = 0.5 + 0.5 * growth_phase
    base = base * plateau_phase
    return base / base.mean()  # normalize to mean 1.0; generator scales to N_ORDERS_TARGET

# ============================================================================
# ORDER ITEMS (spec §8)
# ============================================================================
BASKET_SIZE_WEIGHTS = {1: 0.35, 2: 0.30, 3: 0.20, 4: 0.10, 5: 0.05}  # items per order
QUANTITY_WEIGHTS = {1: 0.70, 2: 0.20, 3: 0.07, 4: 0.02, 5: 0.01}     # units per line

# ============================================================================
# PAYMENTS (spec §10)
# ============================================================================
PAYMENT_METHODS = ["Credit Card", "PayPal", "Bank Transfer", "Klarna", "Debit Card"]
PAYMENT_STATUS_SHARE = {"succeeded": 0.95, "failed": 0.03, "pending": 0.02}
PAYMENT_FEE_RATE_BY_METHOD = {
    "Credit Card": 0.018, "PayPal": 0.025, "Bank Transfer": 0.005,
    "Klarna": 0.030, "Debit Card": 0.012,
}

# ============================================================================
# RETURNS (spec §12)
# ============================================================================
RETURN_REASONS = [
    "defective", "wrong_item", "changed_mind", "damaged",
    "size_issue", "late_delivery", "other",
]
# Return rate grows over the 24 months (Charter: "return rate has increased")
RETURN_RATE_START = 0.05
RETURN_RATE_END = 0.13

# ============================================================================
# REFUNDS (spec §13)
# ============================================================================
REFUND_TYPE_SHARE = {"full": 0.55, "partial": 0.45}

# ============================================================================
# MARKETING CAMPAIGNS (spec §14) — 5 locked archetypes
# ============================================================================
N_CAMPAIGNS = 45
CAMPAIGN_ARCHETYPES = [
    {"name": "high_traffic_weak_conversion",     "share": 0.20},
    {"name": "high_cac_strong_revenue",          "share": 0.20},
    {"name": "efficient_high_roas",              "share": 0.25},
    {"name": "low_cost_strong_customer_value",   "share": 0.20},
    {"name": "average_mixed",                    "share": 0.15},
]
assert abs(sum(a["share"] for a in CAMPAIGN_ARCHETYPES) - 1.0) < 1e-9

# ============================================================================
# MARKETING EVENTS / FUNNEL (spec §15) — previous-stage-based, locked
# ============================================================================
N_EVENTS_TARGET = 450_000
FUNNEL_STAGE_ORDER = ["session_start", "product_view", "add_to_cart", "checkout_started", "purchase"]
FUNNEL_STAGE_CONVERSION = {
    # probability of reaching this stage GIVEN the previous stage was reached
    "product_view": 0.75,
    "add_to_cart": 0.35,
    "checkout_started": 0.50,
    "purchase": 0.65,
}
DEVICES = ["mobile", "desktop", "tablet"]

# ============================================================================
# MARKETING SPEND (spec §16)
# ============================================================================
N_SPEND_ROWS_TARGET = 15_000
CHANNEL_COST_PROFILE = {
    # relative CPC and CTR personality per channel (synthetic assumption)
    "Paid Search":    {"cpc_eur": 0.55, "ctr": 0.028},
    "Paid Social":    {"cpc_eur": 0.35, "ctr": 0.015},
    "Email":          {"cpc_eur": 0.05, "ctr": 0.045},
    "Organic Search": {"cpc_eur": 0.00, "ctr": 0.020},  # no spend, organic
    "Affiliate":      {"cpc_eur": 0.40, "ctr": 0.022},
    "Direct":         {"cpc_eur": 0.00, "ctr": 0.000},  # no click model, direct traffic
}

# ============================================================================
# FINANCE COSTS (spec §18) — must never duplicate shipping/payment/marketing/return costs
# ============================================================================
N_FINANCE_COST_ROWS_TARGET = 1_500
COST_TYPES = ["payroll", "software", "rent", "infrastructure", "professional_services", "other"]
COST_TYPE_WEIGHTS = {
    "rent": 0.22,
    "software": 0.14,
    "payroll": 0.13,
    "professional_services": 0.22,
    "other": 0.12,
    "infrastructure": 0.17,
}
COST_AMOUNT_RANGES = {
    "rent": (300, 2500),
    "software": (150, 1800),
    "payroll": (100, 1200),
    "professional_services": (100, 1600),
    "other": (150, 1500),
    "infrastructure": (250, 2200),
}
assert abs(sum(COST_TYPE_WEIGHTS.values()) - 1.0) < 1e-9

# ============================================================================
# INTENTIONAL DATA QUALITY DEFECTS (spec §20)
# ============================================================================
DQ_DEFECT_RATE = 0.01  # ~1% of applicable rows per table get an intentional defect

DQ_DEFECT_TYPES = {
    # table -> list of (defect_name, dq_rule_id)
    "order_items":      [("negative_quantity", "DQ-002"), ("unknown_product_id", "DQ-007")],
    "orders":           [("non_eur_currency", "DQ-020")],
    "shipments":        [("delivery_before_shipment", "DQ-017")],
    "marketing_spend":  [("clicks_exceed_impressions", "DQ-011")],
    "returns":          [("invalid_return_date", "DQ-009")],
    "marketing_events": [("missing_session_id", "DQ-013"), ("invalid_event_type", "DQ-014")],
    "promotions":       [("invalid_date_range", "DQ-021")],
}
