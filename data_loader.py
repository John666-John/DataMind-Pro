"""
DataMind 销售分析 - 数据导入模块
功能：加载本地 CSV/Excel 真实数据，适配 Python 3.7
"""
import pandas as pd
import os
from typing import Optional


def load_data(file_path: str) -> pd.DataFrame:
    """
    加载本地 CSV 或 Excel 数据
    
    Args:
        file_path: 数据文件绝对路径（如 D:/Data/202510销售数据.csv）
    
    Returns:
        加载后的 DataFrame 数据
    
    Raises:
        FileNotFoundError: 文件不存在时抛出
        ValueError: 文件格式不支持时抛出
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件未找到，请检查路径：{file_path}")
    
    # 按文件后缀选择读取方式
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == ".csv":
        # 读取 CSV（支持中文编码）
        df = pd.read_csv(file_path, encoding="utf-8-sig")
    elif file_ext in [".xlsx", ".xls"]:
        # 读取 Excel（依赖 openpyxl）
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        raise ValueError(f"不支持的文件格式：{file_ext}，仅支持 CSV/Excel（.xlsx/.xls）")
    
    print(f"✅ 数据导入成功（{file_ext}），数据行数：{len(df)}，列名：{list(df.columns)}")
    return df


# 测试代码（单独运行该文件时验证）
if __name__ == "__main__":
    test_data_path = r"D:/DataMind_Data/202510销售数据.csv"  # 替换为你的测试路径
    try:
        test_df = load_data(test_data_path)
        print("数据预览：")
        print(test_df.head(3))
    except Exception as e:
        print(f"❌ 数据导入失败：{str(e)}")
