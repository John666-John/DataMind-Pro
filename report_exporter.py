"""
DataMind 销售分析 - 报告导出模块
功能：导出 Excel 统计表、PDF 分析报告（符合真实业务模板）
"""
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
from typing import Optional


class SalesReportPDF(FPDF):
    """自定义 PDF 报告类（含标题、页眉、内容布局）"""
    def header(self):
        """PDF 页眉（企业报告风格）"""
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "企业月度销售分析报告（2025年10月）", 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
        self.ln(10)  # 换行


def export_area_excel(df: pd.DataFrame, save_dir: str) -> str:
    """
    导出各区域销售额统计表（Excel 格式，含核心业务指标）
    
    Args:
        df: 清洗后的 DataFrame
        save_dir: 报告保存目录（绝对路径）
    
    Returns:
        Excel 文件保存路径
    """
    os.makedirs(save_dir, exist_ok=True)
    excel_path = os.path.join(save_dir, "202510区域销售额统计表.xlsx")
    
    # 计算区域核心指标
    area_summary = df.groupby("区域").agg({
        "销售额": [
            ("总销售额（元）", "sum"),
            ("日均销售额（元）", "mean"),
            ("销售额中位数（元）", "median")
        ],
        "产品ID": [("订单数", "count")],
        "日期": [("数据覆盖天数", "nunique")]
    }).round(2)
    
    # 合并多级列名（简化Excel表头）
    area_summary.columns = [col[1] for col in area_summary.columns]
    # 添加“区域排名”列
    area_summary["区域排名"] = area_summary["总销售额（元）"].rank(ascending=False, method="min").astype(int)
    # 按总销售额降序排列
    area_summary = area_summary.sort_values("总销售额（元）", ascending=False)
    
    # 导出Excel（依赖 openpyxl）
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        area_summary.to_excel(writer, sheet_name="区域销售汇总", index=True)
    
    print(f"\n✅ Excel统计表导出完成，路径：{excel_path}")
    return excel_path


def export_sales_pdf(
    df: pd.DataFrame,
    chart_path: str,
    predict_df: pd.DataFrame,
    save_dir: str
) -> str:
    """
    导出 PDF 分析报告（含文字分析、图表、预测结果）
    
    Args:
        df: 清洗后的 DataFrame
        chart_path: 销售分析图表路径
        predict_df: 11月销售额预测数据
        save_dir: 报告保存目录
    
    Returns:
        PDF 文件保存路径
    """
    os.makedirs(save_dir, exist_ok=True)
    pdf_path = os.path.join(save_dir, "202510销售分析报告.pdf")
    
    # 初始化 PDF（A4纸，纵向）
    pdf = SalesReportPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # -------------------------- 1. 报告摘要 --------------------------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "一、报告摘要", 0, 1, "L")
    pdf.set_font("Arial", "", 12)
    pdf.ln(3)
    
    # 计算摘要指标
    total_sales = df["销售额"].sum()
    avg_daily_sales = df["销售额"].mean()
    top_area = df.groupby("区域")["销售额"].sum().idxmax()
    top_area_sales = df.groupby("区域")["销售额"].sum().max()
    
    summary_text = [
        f"1. 10月总销售额：{total_sales:,.2f} 元",
        f"2. 10日平均销售额：{avg_daily_sales:,.2f} 元",
        f"3. 销售额最高区域：{top_area}（{top_area_sales:,.2f} 元，占比 {top_area_sales/total_sales*100:.1f}%）",
        f"4. 数据覆盖范围：2025年10月1日 - 2025年10月31日（共 {df['日期'].nunique()} 天有效数据）"
    ]
    
    for text in summary_text:
        pdf.cell(0, 6, text, 0, 1, "L")
    pdf.ln(8)
    
    # -------------------------- 2. 可视化分析 --------------------------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "二、可视化分析", 0, 1, "L")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, "（含每日销售额趋势与区域占比）", 0, 1, "L")
    pdf.ln(3)
    
    # 插入图表（调整尺寸适配A4纸）
    if os.path.exists(chart_path):
        pdf.image(chart_path, x=10, y=pdf.get_y(), w=180)  # 宽度180mm（A4宽度210mm，留边距）
        pdf.ln(80)  # 图表高度约80mm，换行避免覆盖
    
    # -------------------------- 3. 11月预测结果 --------------------------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "三、11月销售额预测（前5天）", 0, 1, "L")
    pdf.set_font("Arial", "", 12)
    pdf.ln(3)
    
    # 插入预测表格
    pdf.set_font("Arial", "B", 11)
    # 表格表头
    pdf.cell(30, 7, "11月日期", 1, 0, "C")
    pdf.cell(30, 7, "区域编码", 1, 0, "C")
    pdf.cell(30, 7, "产品编码", 1, 0, "C")
    pdf.cell(60, 7, "预测销售额（元）", 1, 1, "C")
    
    # 表格内容
    pdf.set_font("Arial", "", 11)
    for _, row in predict_df.iterrows():
        pdf.cell(30, 7, f"11月{int(row['日序'])}日", 1, 0, "C")
        pdf.cell(30, 7, str(int(row['区域编码'])), 1, 0, "C")
        pdf.cell(30, 7, str(int(row['产品编码'])), 1, 0, "C")
        pdf.cell(60, 7, f"{row['预测销售额（元）']:,.2f}", 1, 1, "C")
    
    # -------------------------- 4. 结论建议 --------------------------
    pdf.add_page()  # 新增一页
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "四、结论与建议", 0, 1, "L")
    pdf.set_font("Arial", "", 12)
    pdf.ln(3)
    
    suggestions = [
        f"1. 业绩亮点：{top_area}区域表现突出，可总结该区域推广经验并复制到其他区域；",
        f"2. 改进方向：需关注销售额较低区域（如 {df.groupby('区域')['销售额'].sum().idxmin()}），分析需求缺口；",
        f"3. 预测参考：11月前5天预测总销售额 {predict_df['预测销售额（元）'].sum():,.2f} 元，建议提前备货；",
        f"4. 数据质量：本次分析已清洗异常值/缺失值，后续需加强数据录入规范，减少预处理成本。"
    ]
    
    for i, suggestion in enumerate(suggestions, 1):
        pdf.multi_cell(0, 6, suggestion, 0, "L")  # 支持长文本换行
        pdf.ln(2)
    
    # 保存PDF
    pdf.output(pdf_path)
    print(f"✅ PDF报告导出完成，路径：{pdf_path}")
    return pdf_path


# 测试代码（单独运行该文件时验证）
if __name__ == "__main__":
    # 构造测试数据
    dates = pd.date_range(start="2025-10-01", end="2025-10-31", freq="D")
    test_df = pd.DataFrame({
        "日期": dates,
        "产品ID": ["001", "002"] * 15 + ["001"],
        "销售额": np.random.randint(10000, 30000, size=31),
        "区域": ["华北", "华东"] * 15 + ["华北"]
    })
    
    # 构造预测数据
    test_predict_df = pd.DataFrame({
        "日序": [1,2,3,4,5],
        "区域编码": [0,1,0,1,0],
        "产品编码": [0,1,0,1,0],
        "预测销售额（元）": [15000, 18000, 16000, 19000, 17000]
    })
    
    # 测试导出
    test_save_dir = r"D:/DataMind_Reports/202510"
    excel_path = export_area_excel(test_df, test_save_dir)
    # 用测试图表路径（需先运行 data_analyzer.py 生成图表）
    test_chart_path = os.path.join(test_save_dir, "Charts/销售分析图表.png")
    if os.path.exists(test_chart_path):
        export_sales_pdf(test_df, test_chart_path, test_predict_df, test_save_dir)
    else:
        print("⚠️  图表文件不存在，PDF中暂不插入图表")
