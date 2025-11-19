"""
DataMind 销售分析 - 建模预测模块
功能：训练随机森林回归模型，预测11月销售额（无虚拟数据，基于真实历史数据）
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from typing import Tuple, List


def prepare_model_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    准备建模数据：特征工程 + 训练集/测试集拆分（按时间序列拆分，避免数据泄露）
    
    Args:
        df: 清洗后的 DataFrame（需含日期、产品ID、销售额、区域）
    
    Returns:
        X_train, y_train, X_test, y_test: 训练集特征、训练集标签、测试集特征、测试集标签
    """
    df_model = df.copy()
    
    # 1. 特征工程：将非数值特征转为数值（建模需）
    df_model["日序"] = df_model["日期"].dt.day  # 特征1：当月第几天（时间特征）
    df_model["区域编码"] = pd.factorize(df_model["区域"])[0]  # 特征2：区域编码（分类特征转数值）
    df_model["产品编码"] = pd.factorize(df_model["产品ID"])[0]  # 特征3：产品编码（分类特征转数值）
    
    # 2. 按时间拆分：前20天为训练集，后11天为测试集（真实时间序列逻辑）
    train_mask = df_model["日序"] <= 20
    test_mask = df_model["日序"] > 20
    
    # 3. 定义特征（X）和标签（y：预测目标为销售额）
    features = ["日序", "区域编码", "产品编码"]
    X_train = df_model[train_mask][features]
    y_train = df_model[train_mask]["销售额"]
    X_test = df_model[test_mask][features]
    y_test = df_model[test_mask]["销售额"]
    
    print(f"📊 建模数据准备完成：")
    print(f"  - 训练集：{len(X_train)} 条数据（前20天）")
    print(f"  - 测试集：{len(X_test)} 条数据（后11天）")
    print(f"  - 特征列：{features}")
    return X_train, y_train, X_test, y_test


def train_rf_model(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestRegressor:
    """
    训练随机森林回归模型（适配 Python 3.7，基于 scikit-learn 0.24.2）
    
    Args:
        X_train: 训练集特征
        y_train: 训练集标签
    
    Returns:
        训练完成的随机森林模型
    """
    # 模型参数（兼顾性能与解释性，适合销售预测场景）
    rf_model = RandomForestRegressor(
        n_estimators=100,  # 决策树数量
        max_depth=8,        # 最大树深（避免过拟合）
        random_state=42,    # 固定随机种子，结果可复现
        n_jobs=-1           # 多线程训练（加速）
    )
    
    # 训练模型
    print("\n=== 开始训练随机森林模型 ===")
    rf_model.fit(X_train, y_train)
    print("✅ 模型训练完成")
    return rf_model


def evaluate_model(model: RandomForestRegressor, X_test: pd.DataFrame, y_test: pd.Series) -> Tuple[float, float]:
    """
    评估模型性能（输出 MAE、RMSE 指标，符合真实业务评估标准）
    
    Args:
        model: 训练好的模型
        X_test: 测试集特征
        y_test: 测试集标签
    
    Returns:
        mae: 平均绝对误差（元）
        rmse: 均方根误差（元）
    """
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print("\n=== 模型评估结果 ===")
    print(f"  - 平均绝对误差（MAE）：{mae:.2f} 元")
    print(f"  - 均方根误差（RMSE）：{rmse:.2f} 元")
    return mae, rmse


def predict_nov_sales(model: RandomForestRegressor, area_codes: List[int], product_codes: List[int]) -> pd.DataFrame:
    """
    预测11月前5天销售额（基于真实业务场景的区域/产品分布）
    
    Args:
        model: 训练好的模型
        area_codes: 区域编码列表（与建模时的编码一致）
        product_codes: 产品编码列表（与建模时的编码一致）
    
    Returns:
        包含“日期、区域编码、产品编码、预测销售额”的 DataFrame
    """
    # 构造11月前5天的预测数据（假设区域/产品分布与10月一致）
    nov_days = [1, 2, 3, 4, 5]  # 11月1-5日
    predict_data = pd.DataFrame({
        "日序": nov_days,
        "区域编码": area_codes[:len(nov_days)],  # 取前5个区域编码
        "产品编码": product_codes[:len(nov_days)]  # 取前5个产品编码
    })
    
    # 执行预测
    nov_pred = model.predict(predict_data)
    predict_data["预测销售额（元）"] = np.round(nov_pred, 2)  # 保留2位小数（金额格式）
    
    print("\n=== 11月销售额预测结果（前5天） ===")
    print(predict_data[["日序", "区域编码", "产品编码", "预测销售额（元）"]])
    return predict_data


# 测试代码（单独运行该文件时验证）
if __name__ == "__main__":
    # 构造测试数据
    dates = pd.date_range(start="2025-10-01", end="2025-10-31", freq="D")
    test_df = pd.DataFrame({
        "日期": dates,
        "产品ID": ["001", "002", "003"] * 10 + ["001"],
        "销售额": np.random.randint(8000, 25000, size=31),
        "区域": ["华北", "华东", "华南"] * 10 + ["华北"]
    })
    
    # 流程测试：准备数据→训练模型→评估→预测
    X_train, y_train, X_test, y_test = prepare_model_data(test_df)
    model = train_rf_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    # 预测11月前5天（区域编码/产品编码与测试数据一致）
    predict_nov_sales(model, area_codes=[0,1,2,0,1], product_codes=[0,1,2,0,1])
