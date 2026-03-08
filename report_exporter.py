"""Generate English PDF report"""
import os
import pandas as pd
from fpdf import FPDF

class SalesReportPDF(FPDF):
    """Custom PDF class for sales report"""
    def header(self):
        # Report header
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "DataMind Enterprise Sales Analysis Report - October 2025", 0, 1, "C")
        self.ln(5)

    def footer(self):
        # Page number
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def export_area_excel(df: pd.DataFrame, save_dir: str) -> str:
    """Export regional sales summary to Excel (对接main.py逻辑)"""
    os.makedirs(save_dir, exist_ok=True)
    excel_path = os.path.join(save_dir, "202510_regional_sales_summary.xlsx")

    # 按区域汇总销售额（与main.py保持一致）
    area_summary = df.groupby("区域").agg({
        "销售额": ["sum", "mean", "max"]
    }).round(2)
    area_summary.columns = ["Total Sales (RMB)", "Avg Daily Sales (RMB)", "Max Daily Sales (RMB)"]
    area_summary = area_summary.reset_index()

    # 保存Excel
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        area_summary.to_excel(writer, sheet_name="Regional Summary", index=False)

    print(f"✅ Excel summary saved to: {excel_path}")
    return excel_path

def export_sales_pdf(
    df: pd.DataFrame,
    chart_path: str,
    predict_df: pd.DataFrame,
    save_dir: str
) -> str:
    """Generate English PDF report (完整对接原有逻辑)"""
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