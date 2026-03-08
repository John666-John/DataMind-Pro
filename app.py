"""
DataMind Enterprise Sales Analysis - Web Service
完整对接Python核心分析模块，支持前端上传→分析→结果展示→文件下载
适配 Python 3.7，依赖 flask==2.0.3
"""
import os
import json
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file, make_response
from werkzeug.utils import secure_filename

# 导入项目核心模块
from data_loader import load_data
from data_preprocessor import preprocess_data
from data_analyzer import generate_sales_charts
from model_trainer import prepare_model_data, train_rf_model, evaluate_model, predict_nov_sales
from report_exporter import export_area_excel, export_sales_pdf, SalesReportPDF

# 初始化 Flask 应用
app = Flask(__name__)
# 配置路径（严格遵循README的绝对路径要求）
app.config['UPLOAD_FOLDER'] = r"D:/DataMind_Uploads"  # 上传文件保存目录
app.config['REPORT_FOLDER'] = r"D:/DataMind_Web_Reports"  # 分析报告保存目录
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大上传16MB
app.config['SECRET_KEY'] = 'datamind_pro_2025'

# 创建必要目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

# 全局变量存储分析结果（用于前端展示）
analysis_result = {
    "total_sales": 0,
    "avg_daily_sales": 0,
    "top_region": "",
    "top_region_sales": 0,
    "model_metrics": {"MAE": 0, "RMSE": 0},
    "predict_data": [],
    "file_paths": {},
    "valid_rows": 0
}


# 修复matplotlib中文/环境问题（必须在data_analyzer调用前执行）
def setup_matplotlib():
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]  # 适配英文避免乱码
    plt.rcParams["axes.unicode_minus"] = False
    plt.style.use("ggplot")


# 首页（上传+结果展示一体化页面）
@app.route('/')
def index():
    return render_template('index.html', result=analysis_result)


# 上传并执行全流程分析（核心接口）
@app.route('/analyze', methods=['POST'])
def analyze_sales():
    global analysis_result
    # 重置分析结果
    analysis_result = {
        "total_sales": 0,
        "avg_daily_sales": 0,
        "top_region": "",
        "top_region_sales": 0,
        "model_metrics": {"MAE": 0, "RMSE": 0},
        "predict_data": [],
        "file_paths": {},
        "valid_rows": 0,
        "error": ""
    }

    try:
        # 1. 接收上传文件
        if 'file' not in request.files:
            analysis_result["error"] = "未上传数据文件"
            return render_template('index.html', result=analysis_result)

        file = request.files['file']
        if file.filename == '':
            analysis_result["error"] = "上传文件为空"
            return render_template('index.html', result=analysis_result)

        # 2. 保存上传文件（安全处理）
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 3. 执行核心分析流程（完全对接原有Python模块）
        # 3.1 加载数据
        df_raw = load_data(file_path)

        # 3.2 数据预处理
        df_clean = preprocess_data(df_raw)

        # 验证必要列（严格匹配README要求）
        required_columns = ["区域", "产品ID", "销售额", "日期"]
        if not set(required_columns).issubset(df_clean.columns):
            missing = [col for col in required_columns if col not in df_clean.columns]
            analysis_result["error"] = f"数据缺少必要列：{missing}"
            return render_template('index.html', result=analysis_result)

        # 3.3 初始化matplotlib并生成可视化图表
        setup_matplotlib()
        chart_dir = os.path.join(app.config['REPORT_FOLDER'], "charts")
        chart_path = generate_sales_charts(df_clean, chart_dir)

        # 3.4 建模与预测
        X_train, y_train, X_test, y_test = prepare_model_data(df_clean)
        rf_model = train_rf_model(X_train, y_train)
        mae, rmse = evaluate_model(rf_model, X_test, y_test)

        # 获取区域/产品编码（兼容原逻辑）
        area_factor = pd.factorize(df_clean["区域"])
        area_codes = list(np.unique(area_factor[0].astype(np.int64)))
        product_factor = pd.factorize(df_clean["产品ID"])
        product_codes = list(np.unique(product_factor[0].astype(np.int64)))

        predict_df = predict_nov_sales(rf_model, area_codes, product_codes)

        # 3.5 导出报告文件
        excel_path = export_area_excel(df_clean, app.config['REPORT_FOLDER'])
        pdf_path = export_sales_pdf(df_clean, chart_path, predict_df, app.config['REPORT_FOLDER'])

        # 4. 计算核心分析数据（用于前端展示）
        total_sales = df_clean["销售额"].sum()
        avg_daily_sales = df_clean["销售额"].mean()
        regional_sales = df_clean.groupby("区域")["销售额"].sum()
        top_region = regional_sales.idxmax()
        top_region_sales = regional_sales.max()

        # 5. 整理预测数据（格式化给前端）
        predict_data = []
        for _, row in predict_df.iterrows():
            predict_data.append({
                "nov_date": f"11月{int(row['日序'])}日",
                "region_code": int(row["区域编码"]),
                "product_code": int(row["产品编码"]),
                "forecast_sales": round(row["预测销售额（元）"], 2)
            })

        # 6. 更新全局分析结果
        analysis_result = {
            "total_sales": round(total_sales, 2),
            "avg_daily_sales": round(avg_daily_sales, 2),
            "top_region": top_region,
            "top_region_sales": round(top_region_sales, 2),
            "top_region_ratio": round((top_region_sales / total_sales) * 100, 1),
            "model_metrics": {"MAE": round(mae, 2), "RMSE": round(rmse, 2)},
            "predict_data": predict_data,
            "file_paths": {
                "excel": excel_path,
                "pdf": pdf_path,
                "chart": chart_path
            },
            "valid_rows": len(df_clean),
            "error": ""
        }

        # 7. 返回结果页面
        return render_template('index.html', result=analysis_result)

    except Exception as e:
        analysis_result["error"] = f"分析失败：{str(e)}"
        return render_template('index.html', result=analysis_result)


# 下载Excel报告
@app.route('/download/excel')
def download_excel():
    excel_path = analysis_result["file_paths"].get("excel", "")
    if os.path.exists(excel_path):
        return send_file(excel_path, as_attachment=True)
    else:
        return make_response(jsonify({"code": 404, "msg": "Excel报告未生成"}), 404)


# 下载PDF报告
@app.route('/download/pdf')
def download_pdf():
    pdf_path = analysis_result["file_paths"].get("pdf", "")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        return make_response(jsonify({"code": 404, "msg": "PDF报告未生成"}), 404)


# 查看可视化图表
@app.route('/view/chart')
def view_chart():
    chart_path = analysis_result["file_paths"].get("chart", "")
    if os.path.exists(chart_path):
        return send_file(chart_path)
    else:
        return make_response(jsonify({"code": 404, "msg": "图表未生成"}), 404)


# 启动服务
if __name__ == '__main__':
    # 生产环境需替换为gunicorn，此处为开发环境
    app.run(host='127.0.0.1', port=5000, debug=True)