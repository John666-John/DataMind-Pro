# DataMind-Pro
# DataMind 企业月度销售分析代码包
适配 Python 3.7，基于 DataMind Pro 软件核心功能开发，实现“数据导入→分析→建模→报告”全流程。

## 一、环境准备
1. 确认本地 Python 版本为 3.7.x（终端执行：python --version）
2. 安装依赖库：终端进入代码目录，执行 `pip install -r requirements.txt`

## 二、核心文件说明
| 文件名               | 功能职责                                  |
|----------------------|-------------------------------------------|
| data_loader.py       | 加载本地 CSV/Excel 销售数据               |
| data_preprocessor.py | 缺失值填充、日期标准化、异常值清洗        |
| data_analyzer.py     | 生成销售额趋势图、区域占比图              |
| model_trainer.py     | 训练随机森林模型，预测11月销售额          |
| report_exporter.py   | 导出区域销售额Excel表、PDF分析报告        |
| main.py              | 主程序，一键运行全流程                    |

## 三、使用步骤
1. 准备销售数据文件（CSV/Excel，字段：日期、产品ID、销售额、区域）
2. 打开 main.py，修改 `DATA_PATH`（数据路径）、`REPORT_DIR`（报告保存路径）
3. 终端执行 `python main.py`，等待流程完成（会打印执行日志）
4. 到 REPORT_DIR 路径查看生成的图表、Excel、PDF 报告

## 四、注意事项
- 所有文件路径需用 **绝对路径**（如 D:/Data/202510销售数据.csv）
- 若提示“权限错误”，右键 Python 终端选择“以管理员身份运行”
- 日期格式需为“MM/DD/YYYY”（如 10/25/2025），否则需修改 data_preprocessor.py 中的格式参数
