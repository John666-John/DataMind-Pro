"""
DataMind 销售分析 - 数据预处理模块
功能：缺失值填充、日期标准化、异常值清洗（贴合真实业务场景）
"""
import pandas as pd
import numpy as np
from typing import pd as pd_type


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    全流程数据预处理：缺失值→日期标准化→异常值
    
    Args:
        df: 原始 DataFrame（需包含字段：日期、产品ID、销售额）
    
    Returns:
        清洗后的 DataFrame
    """
    print("\n=== 开始数据预处理 ===")
    df_clean = df.copy()  # 避免修改原始数据
    
    # 1. 缺失值处理：按“产品ID”分组，用该产品当月均值填充销售额（真实业务逻辑）
    if "销售额" in df_clean.columns and df_clean["销售额"].isnull().sum() > 0:
        missing_count = df_clean["销售额"].isnull().sum()
        df_clean["销售额"] = df_clean.groupby("产品ID")["销售额"].transform(
            lambda x: x.fillna(x.mean())
        )
        print(f"1. 缺失值处理：填充 {missing_count} 个销售额缺失值（按产品均值）")
    
    # 2. 日期格式标准化：MM/DD/YYYY → YYYY-MM-DD（适配后续时间分析）
    if "日期" in df_clean.columns:
        # 转换日期格式，无效日期会转为 NaT
        df_clean["日期"] = pd.to_datetime(df_clean["日期"], format="%m/%d/%Y", errors="coerce")
        # 删除无效日期行
        invalid_date_count = df_clean["日期"].isnull().sum()
        df_clean = df_clean.dropna(subset=["日期"])
        print(f"2. 日期标准化：删除 {invalid_date_count} 行无效日期，格式统一为 YYYY-MM-DD")
    
    # 3. 异常值清洗：IQR法则删除销售额异常值（排除负数、极端值）
    if "销售额" in df_clean.columns:
        # 先过滤负数销售额（业务上不可能存在）
        negative_count = (df_clean["销售额"] < 0).sum()
        df_clean = df_clean[df_clean["销售额"] >= 0]
        
        # IQR法则处理极端值
        Q1 = df_clean["销售额"].quantile(0.25)
        Q3 = df_clean["销售额"].quantile(0.75)
        IQR = Q3 - Q1
        before_clean = len(df_clean)
        df_clean = df_clean[
            (df_clean["销售额"] >= Q1 - 1.5 * IQR) & 
            (df_clean["销售额"] <= Q3 + 1.5 * IQR)
        ]
        extreme_count = before_clean - len(df_clean)
        print(f"3. 异常值清洗：删除 {negative_count} 行负销售额 + {extreme_count} 行极端值")
    
    print(f"✅ 预处理完成：原始数据 {len(df)} 行 → 清洗后 {len(df_clean)} 行")
    return df_clean


# 测试代码（单独运行该文件时验证）
if __name__ == "__main__":
    # 构造测试数据
    test_df = pd.DataFrame({
        "日期": ["10/25/2025", "10/26/2025", "无效日期", "10/28/2025", "10/29/2025"],
        "产品ID": ["001", "001", "002", "002", "001"],
        "销售额": [1000, None, 2000, -500, 100000],  # 含缺失值、负数、极端值
        "区域": ["华北", "华北", "华东", "华东", "华北"]
    })
    
    print("原始测试数据：")
    print(test_df)
    
    # 执行预处理
    cleaned_df = preprocess_data(test_df)
    print("\n清洗后数据：")
    print(cleaned_df)
