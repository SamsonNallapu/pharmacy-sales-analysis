"""
clean_data.py
-------------
Cleans the raw pharmacy dispensing dataset and saves an analysis-ready
version. Each cleaning step is logged so the process is transparent.

Cleaning steps:
1. Remove exact duplicate rows
2. Strip whitespace and standardise text casing
3. Parse mixed date formats into a single datetime column
4. Convert unit_price text (e.g. "£1.45") to numeric
5. Handle missing values (impute category from product, drop unusable rows)
6. Remove impossible values (negative quantities)
7. Add derived columns (revenue, month, day_of_week)

Usage:
    python src/clean_data.py
"""

import pandas as pd
import numpy as np

RAW_PATH = "data/raw/pharmacy_sales_raw.csv"
CLEAN_PATH = "data/cleaned/pharmacy_sales_clean.csv"


def log(step: str, before: int, after: int) -> None:
    print(f"{step:<45} rows: {before} -> {after}")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Exact duplicates -------------------------------------------------
    n = len(df)
    df = df.drop_duplicates()
    log("1. Removed duplicate rows", n, len(df))

    # 2. Text standardisation ---------------------------------------------
    for col in ["product_name", "category", "payment_type"]:
        df[col] = df[col].astype("string").str.strip().str.title()
    # Fix titlecase artefacts like "Nhs Prescription" and "Otc Sale"
    df["payment_type"] = df["payment_type"].replace(
        {"Nhs Prescription": "NHS Prescription", "Otc Sale": "OTC Sale"}
    )
    # Product names contain dose units, keep e.g. "500Mg" tidy -> "500mg"
    df["product_name"] = (
        df["product_name"]
        .str.replace(r"(\d+)Mg\b", r"\1mg", regex=True)
        .str.replace(r"(\d+)Iu\b", r"\1IU", regex=True)
    )
    print("2. Standardised text columns (strip + title case)")

    # 3. Dates -------------------------------------------------------------
    df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True)
    print("3. Parsed mixed-format dates into datetime")

    # 4. Prices ------------------------------------------------------------
    df["unit_price"] = (
        df["unit_price"]
        .astype("string")
        .str.replace("£", "", regex=False)
        .str.strip()
    )
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    print("4. Converted unit_price to numeric (removed currency symbols)")

    # 5. Missing values ----------------------------------------------------
    # Impute missing category from the product -> category mapping
    product_to_cat = (
        df.dropna(subset=["category"])
        .loc[df["category"] != ""]
        .groupby("product_name")["category"]
        .agg(lambda s: s.mode().iloc[0])
    )
    mask = df["category"].isna() | (df["category"] == "")
    df.loc[mask, "category"] = df.loc[mask, "product_name"].map(product_to_cat)
    print(f"5a. Imputed {mask.sum()} missing categories from product names")

    # Quantity / price still missing -> impute price from product median,
    # drop rows where quantity is missing (cannot be safely inferred)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    median_price = df.groupby("product_name")["unit_price"].transform("median")
    n_price = df["unit_price"].isna().sum()
    df["unit_price"] = df["unit_price"].fillna(median_price)
    print(f"5b. Imputed {n_price} missing prices with product median")

    n = len(df)
    df = df.dropna(subset=["quantity"])
    log("5c. Dropped rows with missing quantity", n, len(df))

    # 6. Impossible values ---------------------------------------------------
    n = len(df)
    df = df[df["quantity"] > 0]
    log("6. Removed negative/zero quantities", n, len(df))

    # 7. Derived columns -----------------------------------------------------
    df["quantity"] = df["quantity"].astype(int)
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["day_of_week"] = df["date"].dt.day_name()
    print("7. Added revenue, month, day_of_week columns")

    return df.sort_values("date").reset_index(drop=True)


if __name__ == "__main__":
    raw = pd.read_csv(RAW_PATH)
    print(f"Loaded {len(raw)} raw rows\n" + "-" * 60)
    cleaned = clean(raw)
    print("-" * 60)
    cleaned.to_csv(CLEAN_PATH, index=False)
    print(f"Saved {len(cleaned)} clean rows to {CLEAN_PATH}")
