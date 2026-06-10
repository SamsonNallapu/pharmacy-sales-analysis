"""
analysis.py
-----------
Analyses the cleaned pharmacy dataset and produces summary statistics
plus three charts saved to the outputs/ folder.

Usage:
    python src/analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CLEAN_PATH = "data/cleaned/pharmacy_sales_clean.csv"

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("colorblind")


def headline_stats(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("HEADLINE STATISTICS")
    print("=" * 60)
    print(f"Transactions:        {len(df):,}")
    print(f"Total revenue:       £{df['revenue'].sum():,.2f}")
    print(f"Avg transaction:     £{df['revenue'].mean():.2f}")
    print(f"Date range:          {df['date'].min().date()} to {df['date'].max().date()}")
    top = df.groupby("product_name")["revenue"].sum().idxmax()
    print(f"Top product:         {top}")
    print()


def chart_monthly_revenue(df: pd.DataFrame) -> None:
    monthly = df.groupby("month")["revenue"].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly.index, monthly.values, marker="o", linewidth=2)
    ax.set_title("Monthly Revenue Trend (2025)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Revenue (£)", fontsize=11)
    ax.tick_params(axis="x", rotation=45)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig("outputs/monthly_revenue.png", dpi=150, bbox_inches="tight")
    plt.close()


def chart_category_revenue(df: pd.DataFrame) -> None:
    cat = df.groupby("category")["revenue"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(cat.index, cat.values)
    ax.set_title("Revenue by Product Category", fontsize=14, fontweight="bold")
    ax.set_xlabel("Revenue (£)", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    for i, v in enumerate(cat.values):
        ax.text(v, i, f" £{v:,.0f}", va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig("outputs/category_revenue.png", dpi=150, bbox_inches="tight")
    plt.close()


def chart_payment_mix(df: pd.DataFrame) -> None:
    mix = (
        df.groupby(["month", "payment_type"])["revenue"]
        .sum()
        .unstack(fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    mix.plot(kind="bar", stacked=True, ax=ax, width=0.8)
    ax.set_title("Monthly Revenue by Payment Type", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Revenue (£)", fontsize=11)
    ax.tick_params(axis="x", rotation=45)
    ax.legend(title="Payment type", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig("outputs/payment_mix.png", dpi=150, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_PATH, parse_dates=["date"])
    headline_stats(df)
    chart_monthly_revenue(df)
    chart_category_revenue(df)
    chart_payment_mix(df)
    print("Charts saved to outputs/:")
    print("  - monthly_revenue.png")
    print("  - category_revenue.png")
    print("  - payment_mix.png")
