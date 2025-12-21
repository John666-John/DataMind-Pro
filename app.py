from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import pandas as pd
import uuid
from datetime import datetime
from data_loader import load_data
from data_preprocessor import preprocess_data
from data_analyzer import generate_sales_charts
from model_trainer import prepare_model_data, train_rf_model, evaluate_model, predict_nov_sales
from report_exporter import export_area_excel, export_sales_pdf

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 全局变量存储当前处理的数据路径
current_data_path = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    global current_data_path
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '未选择文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': '文件名为空'})

    if file:
        # 生成唯一文件名
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        current_data_path = filepath
        return jsonify({
            'status': 'success',
            'message': f'文件上传成功: {filename}',
            'path': filepath
        })


@app.route('/api/save-data', methods=['POST'])
def save_data():
    global current_data_path
    data = request.json.get('data')
    if not data:
        return jsonify({'status': 'error', 'message': '无数据可保存'})

    # 转换为DataFrame
    df = pd.DataFrame(data)
    df.columns = ['日期', '产品ID', '销售额', '区域']

    # 生成文件名
    filename = f"custom_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df.to_excel(filepath, index=False)

    current_data_path = filepath
    return jsonify({
        'status': 'success',
        'message': f'数据保存成功: {filename}',
        'path': filepath
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    global current_data_path
    report_dir = request.json.get('report_dir')

    if not current_data_path:
        return jsonify({'status': 'error', 'message': '请先上传或创建数据文件'})

    if not report_dir:
        report_dir = os.path.join(os.getcwd(), 'reports', datetime.now().strftime('%Y%m%d%H%M%S'))
    os.makedirs(report_dir, exist_ok=True)
    chart_dir = os.path.join(report_dir, 'charts')

    try:
        # 执行分析流程
        df_raw = load_data(current_data_path)
        df_clean = preprocess_data(df_raw)

        # 生成图表
        chart_path = generate_sales_charts(df_clean, chart_dir)

        # 模型训练与预测
        X_train, y_train, X_test, y_test = prepare_model_data(df_clean)
        model = train_rf_model(X_train, y_train)
        mae, rmse = evaluate_model(model, X_test, y_test)

        # 预测11月销售
        area_codes = list(pd.factorize(df_clean["区域"])[0].unique())
        product_codes = list(pd.factorize(df_clean["产品ID"])[0].unique())
        predict_df = predict_nov_sales(model, area_codes, product_codes)

        # 导出报告
        excel_path = export_area_excel(df_clean, report_dir)
        pdf_path = export_sales_pdf(df_clean, chart_path, predict_df, report_dir)

        # 整理结果
        total_sales = df_clean['销售额'].sum()
        avg_daily_sales = df_clean['销售额'].mean()
        top_region = df_clean.groupby('区域')['销售额'].sum().idxmax()
        data_days = df_clean['日期'].nunique()

        return jsonify({
            'status': 'success',
            'results': {
                'data': {
                    'total_sales': total_sales,
                    'avg_daily_sales': avg_daily_sales,
                    'top_region': top_region,
                    'data_days': data_days
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
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)