"""
DataMind Enterprise Monthly Sales Analysis - Main Program
Workflow: Data Import → Preprocessing → Analysis → Modeling → Report Export
"""
import os
import numpy as np
import pandas as pd
from data_loader import load_data
from data_preprocessor import preprocess_data
from data_analyzer import generate_sales_charts
from model_trainer import prepare_model_data, train_rf_model, evaluate_model, predict_nov_sales
from report_exporter import export_area_excel, export_sales_pdf


def main():
    # -------------------------- 1. Configuration (User must modify) --------------------------
    DATA_PATH = r"D:/DataMind_Data/202510销售数据.csv"  # Your data path (CSV/Excel)
    REPORT_DIR = r"D:/DataMind_Reports/202510"          # Report save directory
    CHART_DIR = os.path.join(REPORT_DIR, "Charts")       # Chart subdirectory

    print("="*60)
    print("        DataMind Enterprise Sales Analysis (Python 3.7)")
    print("="*60)

    try:
        # -------------------------- 2. Data Import --------------------------
        df_raw = load_data(DATA_PATH)

        # -------------------------- 3. Data Preprocessing --------------------------
        df_clean = preprocess_data(df_raw)

        # Validate required columns
        required_columns = ["区域", "产品ID"]
        if not set(required_columns).issubset(df_clean.columns):
            missing = [col for col in required_columns if col not in df_clean.columns]
            raise ValueError(f"Missing required columns: {missing}. Check data format.")

        # -------------------------- 4. Data Analysis & Chart Generation --------------------------
        chart_path = generate_sales_charts(df_clean, CHART_DIR)

        # -------------------------- 5. Modeling & Prediction --------------------------
        X_train, y_train, X_test, y_test = prepare_model_data(df_clean)
        rf_model = train_rf_model(X_train, y_train)
        evaluate_model(rf_model, X_test, y_test)

        # Get region and product codes
        area_factor = pd.factorize(df_clean["区域"])
        area_codes = list(np.unique(area_factor[0].astype(np.int64)))
        product_factor = pd.factorize(df_clean["产品ID"])
        product_codes = list(np.unique(product_factor[0].astype(np.int64)))

        predict_df = predict_nov_sales(rf_model, area_codes, product_codes)

        # -------------------------- 6. Report Export --------------------------
        print("\n=== Starting report export ===")
        export_area_excel(df_clean, REPORT_DIR)
        export_sales_pdf(df_clean, chart_path, predict_df, REPORT_DIR)

        # -------------------------- 7. Completion --------------------------
        print("\n" + "="*60)
        print("✅ Workflow completed successfully!")
        print(f"📁 All results saved to: {REPORT_DIR}")
        print("Files included:")
        print(f"  1. Charts: {CHART_DIR}/sales_analysis_charts.png")
        print(f"  2. Excel summary: {REPORT_DIR}/202510_regional_sales_summary.xlsx")
        print(f"  3. PDF report: {REPORT_DIR}/202510_sales_analysis_report.pdf")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")
        print("Please check:")
        print("  1. Data file path is correct (absolute path required)")
        print("  2. Dependencies installed (run: pip install -r requirements.txt)")
        print("  3. Python version is 3.7.x")
        print("  4. Data contains '区域' (region) and '产品ID' (product ID) columns")


if __name__ == "__main__":
    main()