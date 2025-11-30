"""
DataMind Sales Analysis - Data Visualization Module
Generates sales trend charts and regional distribution charts
"""
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np


def setup_matplotlib():
    """Configure matplotlib for English display (avoid font issues)"""
    plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "Verdana", "Tahoma"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["savefig.dpi"] = 300


def generate_sales_charts(df: pd.DataFrame, save_dir: str) -> str:
    """
    Generate daily sales trend and regional distribution charts

    Args:
        df: Cleaned DataFrame (must contain 日期(date), 销售额(sales), 区域(region))
        save_dir: Directory to save charts (absolute path)

    Returns:
        Path to saved chart
    """
    setup_matplotlib()
    print("\n=== Starting data visualization ===")

    os.makedirs(save_dir, exist_ok=True)
    chart_path = os.path.join(save_dir, "sales_analysis_charts.png")

    # Calculate core metrics
    daily_sales = df.groupby("日期")["销售额"].sum().reset_index()
    regional_sales = df.groupby("区域")["销售额"].sum()

    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Subplot 1: Daily sales trend
    ax1.plot(
        daily_sales["日期"], daily_sales["销售额"],
        color="#2E86AB", linewidth=2.5, marker="o", markersize=4
    )
    # Mark October 1st if present
    national_day = pd.to_datetime("2025-10-01")
    if national_day in daily_sales["日期"].values:
        nd_sales = daily_sales[daily_sales["日期"] == national_day]["销售额"].values[0]
        ax1.annotate(
            "Oct 1", xy=(national_day, nd_sales),
            xytext=(national_day, nd_sales + 5000),
            arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
            fontsize=11, color="red", fontweight="bold"
        )
    ax1.set_title("Daily Sales Trend - October 2025", fontsize=14, fontweight="bold", pad=20)
    ax1.set_xlabel("Date", fontsize=12)
    ax1.set_ylabel("Sales (RMB)", fontsize=12)
    ax1.tick_params(axis="x", rotation=45)
    ax1.grid(alpha=0.3)

    # Subplot 2: Regional sales distribution
    colors = ["#A23B72", "#F18F01", "#C73E1D", "#2E86AB", "#3F88C5"]
    wedges, texts, autotexts = ax2.pie(
        regional_sales.values, labels=regional_sales.index,  # Uses English region names
        autopct="%1.1f%%",
        colors=colors[:len(regional_sales)],
        startangle=90,
        textprops={"fontsize": 11}
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    ax2.set_title("Regional Sales Distribution - October 2025", fontsize=14, fontweight="bold", pad=20)

    plt.tight_layout()
    plt.savefig(chart_path, bbox_inches="tight", facecolor="white")
    plt.close()

    print(f"✅ Charts saved to: {chart_path}")
    return chart_path


if __name__ == "__main__":
    dates = pd.date_range(start="2025-10-01", end="2025-10-31", freq="D")
    test_df = pd.DataFrame({
        "日期": dates,
        "产品ID": ["001"] * 15 + ["002"] * 16,
        "销售额": np.random.randint(5000, 20000, size=31),
        "区域": ["North"] * 10 + ["East"] * 12 + ["South"] * 9  # English regions
    })

    test_save_dir = r"D:/DataMind_Reports/202510/Charts"
    generate_sales_charts(test_df, test_save_dir)