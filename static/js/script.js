document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysis-form');
    const progress = document.getElementById('progress');
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progress-text');
    const resultsSection = document.querySelector('.results-section');

    // 表单提交处理
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const dataPath = document.getElementById('data-path').value;
        const reportDir = document.getElementById('report-dir').value;

        // 显示进度条
        progress.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        progressBar.style.width = '10%';
        progressText.textContent = '正在准备分析...';

        // 发送分析请求
        fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data_path: dataPath,
                report_dir: reportDir
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('分析过程中出现错误');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                progressBar.style.width = '100%';
                progressText.textContent = '分析完成!';

                // 延迟显示结果，让用户看到完成状态
                setTimeout(() => {
                    progress.classList.add('hidden');
                    resultsSection.classList.remove('hidden');
                    displayResults(data.results);
                }, 1000);
            } else {
                throw new Error(data.message || '分析失败');
            }
        })
        .catch(error => {
            progressText.textContent = `错误: ${error.message}`;
            progressBar.style.backgroundColor = '#C73E1D';
        });
    });

    // 显示分析结果
    function displayResults(results) {
        // 填充销售摘要
        document.getElementById('total-sales').textContent = results.data.total_sales.toFixed(2) + ' 元';
        document.getElementById('avg-daily-sales').textContent = results.data.avg_daily_sales.toFixed(2) + ' 元';
        document.getElementById('top-region').textContent = results.data.top_region;
        document.getElementById('data-days').textContent = results.data.data_days;

        // 显示图表
        const chartPath = results.charts.replace('\\', '/');
        document.getElementById('sales-chart').src = '/' + chartPath;

        // 填充预测表格
        const tableBody = document.querySelector('#prediction-table tbody');
        tableBody.innerHTML = '';

        results.prediction.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>11月 ${item.日序} 日</td>
                <td>${item.区域编码}</td>
                <td>${item.产品编码}</td>
                <td>${item.预测销售额（元）.toFixed(2)}</td>
            `;
            tableBody.appendChild(row);
        });

        // 填充模型指标
        document.getElementById('mae').textContent = results.metrics.mae.toFixed(2);
        document.getElementById('rmse').textContent = results.metrics.rmse.toFixed(2);

        // 填充报告信息
        document.getElementById('excel-report').textContent = results.reports.excel;
        document.getElementById('pdf-report').textContent = results.reports.pdf;
        document.getElementById('charts-dir').textContent = results.reports.charts_dir;
    }
});