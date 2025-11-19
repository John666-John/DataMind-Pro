"""
DataMind 销售分析 - 数据分析模块
功能：生成销售额趋势图、区域占比图（可视化真实业务指标）
"""
import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Optional


def setup_matplotlib():
    """配置 matplotlib 中文显示（避免乱码）"""
    plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]  # 中文支持
    plt.rcParams["axes.unicode_minus"] = False  # 负号显示正常
    plt.rcParams["figure.dpi"] = 100  # 图表分辨率
    plt.rcParams["savefig.dpi"] = 300  # 保存图片分辨率


def generate_sales_charts(df: pd.DataFrame, save_dir: str) -> str:
    """
    生成 每日销售额趋势图 + 区域销售额占比图，保存到指定目录
    
    Args:
        df: 清洗后的 DataFrame（需含日期、销售额、区域）
        save_dir: 图表保存目录（绝对路径）
    
    Returns:
        图表保存路径
    """
    setup_matplotlib()
    print("\n=== 开始数据分析与图表生成 ===")
    
    # 创建保存目录（不存在则自动创建）
    os.makedirs(save_dir, exist_ok=True)
    chart_path = os.path.join(save_dir, "销售分析图表.png")
    
    # 1. 计算核心分析数据
    daily_sales = df.groupby("日期")["销售额"].sum().reset_index()  # 每日销售额
    area_sales = df.groupby("区域")["销售额"].sum()  # 各区域总销售额
    
    # 2. 创建子图（1行2列）
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 子图1：每日销售额趋势图（标注国庆节点）
    ax1.plot(
        daily_sales["日期"], daily_sales["销售额"], 
        color="#2E86AB", linewidth=2.5, marker="o", markersize=4
    )
    # 标注10.1国庆（若数据包含该日期）
    national_day = pd.to_datetime("2025-10-01")
    if national_day in daily_sales["日期"].values:
        nd_sales = daily_sales[daily_sales["日期"] == national_day]["销售额"].values[0]
        ax1.annotate(
            "10.1国庆", xy=(national_day, nd_sales),
            xytext=(national_day, nd_sales + 5000),  # 文字位置偏移
            arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
            fontsize=11, color="red", fontweight="bold"
        )
    ax1.set_title("2025年10月每日销售额趋势", fontsize=14, fontweight="bold", pad=20)
    ax1.set_xlabel("日期", fontsize=12)
    ax1.set_ylabel("销售额（元）", fontsize=12)
    ax1.tick_params(axis="x", rotation=45)  # 日期标签旋转，避免重叠
    ax1.grid(alpha=0.3)  # 显示网格，便于读数
    
    # 子图2：各区域销售额占比饼图
    colors = ["#A23B72", "#F18F01", "#C73E1D", "#2E86AB", "#3F88C5"]  # 业务风配色
    wedges, texts, autotexts = ax2.pie(
        area_sales.values, labels=area_sales.index,
        autopct="%1.1f%%",  # 显示百分比（保留1位小数）
        colors=colors[:len(area_sales)],
        startangle=90,  # 饼图起始角度（90度为正上方）
        textprops={"fontsize": 11}
    )
    # 美化百分比文字（加粗、白色）
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    ax2.set_title("2025年10月各区域销售额占比", fontsize=14, fontweight="bold", pad=20)
    
    # 调整子图间距，避免重叠
    plt.tight_layout()
    # 保存图表（bbox_inches="tight" 避免标签被截断）
    plt.savefig(chart_path, bbox_inches="tight", facecolor="white")
    plt.close()
    
    print(f"✅ 图表生成完成，保存路径：{chart_path}")
    return chart_path


# 测试代码（单独运行该文件时验证）
if __name__ == "__main__":
    # 构造测试数据
    dates = pd.date_range(start="2025-10-01", end="2025-10-31", freq="D")
    test_df = pd.DataFrame({
        "日期": dates,
        "产品ID": ["001"] * 15 + ["002"] * 16,
        "销售额": np.random.randint(5000, 20000, size=31),
        "区域": ["华北"] * 10 + ["华东"] * 12 + ["华南"] * 9
    })
    
    # 生成图表（保存到测试目录）
    test_save_dir = r"D:/DataMind_Reports/202510/Charts"
    generate_sales_charts(test_df, test_save_dir)
