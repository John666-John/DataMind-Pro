"""
DataMind Sales Analysis - Data Preprocessing Module
Functions: Missing value imputation, date standardization, outlier cleaning
"""
import pandas as pd
import numpy as np


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full-process data preprocessing: missing values → date standardization → outliers

    Args:
        df: Raw DataFrame (must contain columns: 日期(date), 产品ID(product_id), 销售额(sales), 区域(region))

    Returns:
        Cleaned DataFrame with English region names
    """
    print("\n=== Starting data preprocessing ===")
    df_clean = df.copy()

    # 1. Convert Chinese region names to English (critical for font issues)
    region_mapping = {
        "华北": "North",
        "华东": "East",
        "华南": "South",
        "西北": "Northwest",
        "西南": "Southwest",
        "东北": "Northeast",
        "中部": "Central"
    }
    if "区域" in df_clean.columns:
        # Replace Chinese regions with English; keep original if not in mapping
        df_clean["区域"] = df_clean["区域"].map(lambda x: region_mapping.get(x, x))
        print("1. Region name conversion: Chinese → English")

    # 2. Handle missing sales values (group by product ID, fill with mean)
    if "销售额" in df_clean.columns and df_clean["销售额"].isnull().sum() > 0:
        missing_count = df_clean["销售额"].isnull().sum()
        df_clean["销售额"] = df_clean.groupby("产品ID")["销售额"].transform(
            lambda x: x.fillna(x.mean())
        )
        print(f"2. Missing value handling: Filled {missing_count} sales values (by product mean)")

    # 3. Standardize date format (MM/DD/YYYY → YYYY-MM-DD)
    if "日期" in df_clean.columns:
        df_clean["日期"] = pd.to_datetime(df_clean["日期"], format="%m/%d/%Y", errors="coerce")
        invalid_date_count = df_clean["日期"].isnull().sum()
        df_clean = df_clean.dropna(subset=["日期"])
        print(f"3. Date standardization: Removed {invalid_date_count} invalid dates (format: YYYY-MM-DD)")

    # 4. Clean outliers (IQR method + remove negative sales)
    if "销售额" in df_clean.columns:
        negative_count = (df_clean["销售额"] < 0).sum()
        df_clean = df_clean[df_clean["销售额"] >= 0]

        Q1 = df_clean["销售额"].quantile(0.25)
        Q3 = df_clean["销售额"].quantile(0.75)
        IQR = Q3 - Q1
        before_clean = len(df_clean)
        df_clean = df_clean[
            (df_clean["销售额"] >= Q1 - 1.5 * IQR) &
            (df_clean["销售额"] <= Q3 + 1.5 * IQR)
        ]
        extreme_count = before_clean - len(df_clean)
        print(f"4. Outlier cleaning: Removed {negative_count} negative sales + {extreme_count} extreme values")

    print(f"✅ Preprocessing completed: {len(df)} → {len(df_clean)} rows retained")
    return df_clean


if __name__ == "__main__":
    test_df = pd.DataFrame({
        "日期": ["10/25/2025", "10/26/2025", "invalid_date", "10/28/2025", "10/29/2025"],
        "产品ID": ["001", "001", "002", "002", "001"],
        "销售额": [1000, None, 2000, -500, 100000],
        "区域": ["华北", "华北", "华东", "华东", "华南"]  # Test Chinese regions
    })

    print("Original test data:")
    print(test_df)

    cleaned_df = preprocess_data(test_df)
    print("\nCleaned data (with English regions):")
    print(cleaned_df)