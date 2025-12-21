from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import pandas as pd
# 导入现有模块
from data_loader import load_data
from data_preprocessor import preprocess_data
from data_analyzer import generate_sales_charts
from model_trainer import prepare_model_data, train_rf_model, evaluate_model, predict_nov_sales
from report_exporter import export_area_excel, export_sales_pdf

app = Flask(__name__)
CORS(app)  # 解决跨域问题


@app.route('/')
def index():
    return render_template('index.html')  # 假设HTML文件在templates目录


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        # 获取前端传递的参数
        data = request.json
        data_path = data.get('data_path')
        report_dir = data.get('report_dir')

        if not data_path or not report_dir:
            return jsonify({
                'status': 'error',
                'message': '请提供数据路径和报告保存路径'
            })

        # 执行分析流程（复用main.py中的逻辑）
        df_raw = load_data(data_path)
        df_clean = preprocess_data(df_raw)

        # 验证必要列
        required_columns = ["区域", "产品ID", "销售额", "日期"]
        if not set(required_columns).issubset(df_clean.columns):
            missing = [col for col in required_columns if col not in df_clean.columns]
            return jsonify({
                'status': 'error',
                'message': f'缺少必要列: {missing}'
            })

        # 创建报告目录
        chart_dir = os.path.join(report_dir, "Charts")
        os.makedirs(chart_dir, exist_ok=True)

        # 生成图表
        chart_path = generate_sales_charts(df_clean, chart_dir)

        # 模型训练与预测
        X_train, y_train, X_test, y_test = prepare_model_data(df_clean)
        rf_model = train_rf_model(X_train, y_train)
        mae, rmse = evaluate_model(rf_model, X_test, y_test)

        # 获取区域和产品编码
        area_codes = list(pd.factorize(df_clean["区域"])[0].unique())
        product_codes = list(pd.factorize(df_clean["产品ID"])[0].unique())

        # 预测11月销售额
        predict_df = predict_nov_sales(rf_model, area_codes, product_codes)

        # 导出报告
        excel_path = export_area_excel(df_clean, report_dir)
        pdf_path = export_sales_pdf(df_clean, chart_path, predict_df, report_dir)

        # 准备返回结果
        return jsonify({
            'status': 'success',
            'results': {
                'data': {
                    'total_sales': df_clean["销售额"].sum(),
                    'avg_daily_sales': df_clean["销售额"].mean(),
                    'top_region': df_clean.groupby("区域")["销售额"].sum().idxmax(),
                    'data_days': df_clean["日期"].nunique()
                },
                'charts': chart_path,
                'prediction': predict_df.to_dict('records'),
                'metrics': {
                    'mae': mae,
                    'rmse': rmse
                },
                'reports': {
                    'excel': excel_path,
                    'pdf': pdf_path,
                    'charts_dir': chart_dir
                }
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


if __name__ == '__main__':
    app.run(debug=True)