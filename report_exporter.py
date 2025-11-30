"""
DataMind Sales Analysis - Report Export Module
Exports Excel summary tables and PDF analysis reports
"""
import numpy as np
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime


class SalesReportPDF(FPDF):
    """Custom PDF report class with English font configuration"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_font("Arial", "", 12)  # Use built-in English font

    def header(self):
        """PDF header with English title"""
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Monthly Sales Analysis Report (October 2025)", 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
        self.ln(10)


def export_area_excel(df: pd.DataFrame, save_dir: str) -> str:
    """Export regional sales summary in Excel (English headers)"""
    os.makedirs(save_dir, exist_ok=True)
    excel_path = os.path.join(save_dir, "202510_regional_sales_summary.xlsx")

    # Calculate metrics with English column names
    area_summary = df.groupby("区域").agg({
        "销售额": [
            ("Total Sales (RMB)", "sum"),
            ("Avg Daily Sales (RMB)", "mean"),
            ("Median Sales (RMB)", "median")
        ],
        "产品ID": [("Order Count", "count")],
        "日期": [("Coverage Days", "nunique")]
    }).round(2)

    area_summary.columns = [col[1] for col in area_summary.columns]
    area_summary["Regional Rank"] = area_summary["Total Sales (RMB)"].rank(ascending=False, method="min").astype(int)
    area_summary = area_summary.sort_values("Total Sales (RMB)", ascending=False)

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        area_summary.to_excel(writer, sheet_name="Regional Summary", index=True)

    print(f"\n✅ Excel report saved to: {excel_path}")
    return excel_path


def export_sales_pdf(
    df: pd.DataFrame,
    chart_path: str,
    predict_df: pd.DataFrame,
    save_dir: str
) -> str:
    """Generate English PDF report"""
    os.makedirs(save_dir, exist_ok=True)
    pdf_path = os.path.join(save_dir, "202510_sales_analysis_report.pdf")

    pdf = SalesReportPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. Report Summary
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "I. Report Summary", 0, 1, "L")
    pdf.set_font("Arial", "", 12)
    pdf.ln(3)

    total_sales = df["销售额"].sum()
    avg_daily_sales = df["销售额"].mean()
    top_region = df.groupby("区域")["销售额"].sum().idxmax()
    top_region_sales = df.groupby("区域")["销售额"].sum().max()

    summary_text = [
        f"1. Total October sales: {total_sales:,.2f} RMB",
        f"2. Average daily sales: {avg_daily_sales:,.2f} RMB",
        f"3. Top performing region: {top_region} ({top_region_sales:,.2f} RMB, {top_region_sales/total_sales*100:.1f}% of total)",
        f"4. Data coverage: October 1-31, 2025 (total {df['日期'].nunique()} valid days)"
    ]

    for text in summary_text:
        pdf.cell(0, 6, text, 0, 1, "L")
    pdf.ln(8)

    # 2. Visual Analysis
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "II. Visual Analysis", 0, 1, "L")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, "(Daily sales trend and regional distribution)", 0, 1, "L")
    pdf.ln(3)

    if os.path.exists(chart_path):
        pdf.image(chart_path, x=10, y=pdf.get_y(), w=180)
        pdf.ln(80)

    # 3. November Forecast
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "III. November Sales Forecast (First 5 Days)", 0, 1, "L")
    pdf.set_font("Arial", "", 12)
    pdf.ln(3)

    # Forecast table
    pdf.set_font("Arial", "B", 11)
    pdf.cell(30, 7, "Nov Date", 1, 0, "C")
    pdf.cell(30, 7, "Region Code", 1, 0, "C")
    pdf.cell(30, 7, "Product Code", 1, 0, "C")
    pdf.cell(60, 7, "Forecast Sales (RMB)", 1, 1, "C")

    pdf.set_font("Arial", "", 11)
    for _, row in predict_df.iterrows():
        pdf.cell(30, 7, f"Nov {int(row['日序'])}", 1, 0, "C")
        pdf.cell(30, 7, str(int(row['区域编码'])), 1, 0, "C")
        pdf.cell(30, 7, str(int(row['产品编码'])), 1, 0, "C")
        pdf.cell(60, 7, f"{row['预测销售额（元）']:,.2f}", 1, 1, "C")

    # 4. Conclusions & Recommendations
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "IV. Conclusions & Recommendations", 0, 1, "L")
    pdf.set_font("Arial", "", 12)
    pdf.ln(3)

    suggestions = [
        f"1. Performance highlight: {top_region} region performed exceptionally. Recommend replicating its promotion strategies to other regions;",
        f"2. Improvement areas: Pay attention to underperforming regions (e.g., {df.groupby('区域')['销售额'].sum().idxmin()}) and analyze demand gaps;",
        f"3. Forecast reference: Total forecast sales for first 5 days of November: {predict_df['预测销售额（元）'].sum():,.2f} RMB. Suggest preparing inventory in advance;",
        f"4. Data quality: Outliers and missing values have been cleaned. Recommend strengthening data entry standards to reduce preprocessing costs."
    ]

    for suggestion in suggestions:
        pdf.multi_cell(0, 6, suggestion, 0, "L")
        pdf.ln(2)

    pdf.output(pdf_path)
    print(f"✅ PDF report saved to: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    dates = pd.date_range(start="2025-10-01", end="2025-10-31", freq="D")
    test_df = pd.DataFrame({
        "日期": dates,
        "产品ID": ["001", "002"] * 15 + ["001"],
        "销售额": np.random.randint(10000, 30000, size=31),
        "区域": ["North", "East"] * 15 + ["North"]  # English regions
    })

    test_predict_df = pd.DataFrame({
        "日序": [1,2,3,4,5],
        "区域编码": [0,1,0,1,0],
        "产品编码": [0,1,0,1,0],
        "预测销售额（元）": [15000, 18000, 16000, 19000, 17000]
    })

    test_save_dir = r"D:/DataMind_Reports/202510"
    export_area_excel(test_df, test_save_dir)
    test_chart_path = os.path.join(test_save_dir, "Charts/sales_analysis_charts.png")
    if os.path.exists(test_chart_path):
        export_sales_pdf(test_df, test_chart_path, test_predict_df, test_save_dir)