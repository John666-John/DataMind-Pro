import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from data_preprocessor import preprocess_data
from data_loader import load_data

# 初始化Flask应用
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'xls'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB上传限制

# 创建uploads文件夹（不存在则创建）
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# 检查文件后缀是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# 首页路由
@app.route('/')
def index():
    return render_template('index.html')


# 上传文件并解析数据
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'msg': '未选择文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'msg': '文件名为空'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # 加载并预处理数据
            df = load_data(file_path)
            df_clean = preprocess_data(df)

            # 转换为JSON格式（兼容前端表格）
            data = df_clean.to_dict('records')
            columns = [{'title': col, 'data': col} for col in df_clean.columns]

            return jsonify({
                'status': 'success',
                'msg': '文件上传成功',
                'data': data,
                'columns': columns,
                'filename': filename
            })
        except Exception as e:
            return jsonify({'status': 'error', 'msg': f'数据解析失败：{str(e)}'})
    else:
        return jsonify({'status': 'error', 'msg': '仅支持CSV/Excel文件'})


# 修改表格数据（保存到uploads目录）
@app.route('/update-data', methods=['POST'])
def update_data():
    try:
        data = request.json.get('data')
        filename = request.json.get('filename')

        if not data or not filename:
            return jsonify({'status': 'error', 'msg': '数据或文件名缺失'})

        # 转换为DataFrame并保存
        df = pd.DataFrame(data)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')

        return jsonify({'status': 'success', 'msg': '数据修改成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': f'数据保存失败：{str(e)}'})


# 静态文件访问（uploads）
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)