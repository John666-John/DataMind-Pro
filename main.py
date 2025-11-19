"""
DataMind 企业月度销售分析 - 主程序
功能：一键调用所有模块，完成“数据导入→预处理→分析→建模→报告导出”
"""
import os
from data_loader import load_data
from data_preprocessor import preprocess_data
from data_analyzer import generate_sales_charts
from model_trainer import prepare_model_data, train_rf_model, evaluate_model, predict_nov_sales
from report_exporter import export_area_excel, export_sales_pdf


def main():
    # -------------------------- 1. 配置参数（用户需根据实际情况修改） --------------------------
    DATA_PATH = r"D:/DataMind_Data/202510销售数据.csv"  # 你的销售数据路径（CSV/Excel）
    REPORT_DIR = r"D:/DataMind_Reports/202510"          # 报告保存根目录
    CHART_DIR = os.path.join(REPORT_DIR, "Charts")       # 图表子目录
    
    print("="*60)
    print("        DataMind 企业月度销售分析（Python 3.7 版）")
    print("="*60)
    
    try:
        # -------------------------- 2. 数据导入 --------------------------
        df_raw = load_data(DATA_PATH)
        
        # -------------------------- 3. 数据预处理 --------------------------
        df_clean = preprocess_data(df_raw)
        
        # -------------------------- 4. 数据分析与图表生成 --------------------------
        chart_path = generate_sales_charts(df_clean, CHART_DIR)
        
        # -------------------------- 5. 建模与预测 --------------------------
        # 准备建模数据
        X_train, y_train, X_test, y_test = prepare_model_data(df_clean)
        # 训练模型
        rf_model = train_rf_model(X_train, y_train)
        # 评估模型
        evaluate_model(rf_model, X_test, y_test)
        # 预测11月前5天（区域编码/产品编码与建模数据一致，可根据实际业务调整）
        # 从原始数据提取区域/产品编码映射（确保预测时编码一致）
        area_codes = list(pd.factorize(df_clean["区域"])[0].unique())
        product_codes = list(pd.factorize(df_clean["产品ID"])[0].unique())
        predict_df = predict_nov_sales(rf_model, area_codes, product_codes)
        
        # -------------------------- 6. 报告导出 --------------------------
        print("\n=== 开始导出分析报告 ===")
        # 导出Excel统计表
        export_area_excel(df_clean, REPORT_DIR)
        # 导出PDF报告
        export_sales_pdf(df_clean, chart_path, predict_df, REPORT_DIR)
        
        # -------------------------- 7. 流程完成 --------------------------
        print("\n" + "="*60)
        print("✅ 全流程执行完成！")
        print(f"📁 所有结果已保存至：{REPORT_DIR}")
        print("包含文件：")
        print(f"  1. 图表：{CHART_DIR}/销售分析图表.png")
        print(f"  2. Excel统计表：{REPORT_DIR}/202510区域销售额统计表.xlsx")
        print(f"  3. PDF报告：{REPORT_DIR}/202510销售分析报告.pdf")
        print("="*60)
    
    except Exception as e:
        print(f"\n❌ 流程执行失败：{str(e)}")
        print("请检查以下项：")
        print("  1. 数据文件路径是否正确（需绝对路径）")
        print("  2. 依赖库是否已安装（执行 pip install -r requirements.txt）")
        print("  3. Python 版本是否为 3.7.x")


if __name__ == "__main__":
    main()
