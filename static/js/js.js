$(document).ready(function() {
    let currentData = [];  // 存储当前表格数据
    let currentFilename = '';  // 存储当前文件名

    // 1. 文件上传处理
    $('#uploadForm').submit(function(e) {
        e.preventDefault();
        const formData = new FormData();
        const file = $('#fileInput')[0].files[0];

        if (!file) {
            showStatus('请选择要上传的文件', 'error');
            return;
        }

        formData.append('file', file);

        // 显示加载状态
        showStatus('<i class="fa fa-spinner fa-spin"></i> 正在解析数据...', 'info');

        // 发送上传请求
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(res) {
                if (res.status === 'success') {
                    showStatus(res.msg, 'success');
                    currentData = res.data;
                    currentFilename = res.filename;
                    renderTable(res.columns, res.data);
                    $('#dataTableCard').removeClass('d-none');
                } else {
                    showStatus(res.msg, 'error');
                }
            },
            error: function() {
                showStatus('服务器错误，请重试', 'error');
            }
        });
    });

    // 2. 渲染数据表格
    function renderTable(columns, data) {
        // 渲染表头
        let theadHtml = '<tr>';
        columns.forEach(col => {
            theadHtml += `<th>${col.title}</th>`;
        });
        theadHtml += '</tr>';
        $('#salesTable thead').html(theadHtml);

        // 渲染表体
        let tbodyHtml = '';
        data.forEach((row, rowIndex) => {
            tbodyHtml += '<tr>';
            columns.forEach(col => {
                const cellValue = row[col.data] || '';
                // 可编辑单元格（添加contenteditable属性）
                tbodyHtml += `<td class="editable-cell"
                            data-row="${rowIndex}"
                            data-col="${col.data}"
                            contenteditable="true">${cellValue}</td>`;
            });
            tbodyHtml += '</tr>';
        });
        $('#salesTable tbody').html(tbodyHtml);

        // 绑定单元格编辑事件
        $('.editable-cell').on('blur', function() {
            const rowIndex = $(this).data('row');
            const colName = $(this).data('col');
            const newValue = $(this).text().trim();

            // 更新内存中的数据
            currentData[rowIndex][colName] = newValue;
        });
    }

    // 3. 保存修改后的数据
    $('#saveDataBtn').click(function() {
        if (!currentData.length || !currentFilename) {
            showStatus('无数据可保存', 'warning');
            return;
        }

        // 显示保存状态
        $(this).html('<i class="fa fa-spinner fa-spin"></i> 保存中...').prop('disabled', true);

        // 发送保存请求
        $.ajax({
            url: '/update-data',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                data: currentData,
                filename: currentFilename
            }),
            success: function(res) {
                if (res.status === 'success') {
                    showStatus(res.msg, 'success');
                } else {
                    showStatus(res.msg, 'error');
                }
                // 恢复按钮状态
                $('#saveDataBtn').html('<i class="fa fa-save"></i> 保存修改').prop('disabled', false);
            },
            error: function() {
                showStatus('保存失败，请重试', 'error');
                $('#saveDataBtn').html('<i class="fa fa-save"></i> 保存修改').prop('disabled', false);
            }
        });
    });

    // 4. 显示状态提示
    function showStatus(msg, type) {
        const statusEl = $('#uploadStatus');
        statusEl.removeClass('d-none alert-success alert-danger alert-info alert-warning');

        let alertClass = '';
        let icon = '';
        switch(type) {
            case 'success':
                alertClass = 'alert-success';
                icon = '<i class="fa fa-check-circle"></i> ';
                break;
            case 'error':
                alertClass = 'alert-danger';
                icon = '<i class="fa fa-exclamation-circle"></i> ';
                break;
            case 'info':
                alertClass = 'alert-info';
                icon = '<i class="fa fa-info-circle"></i> ';
                break;
            case 'warning':
                alertClass = 'alert-warning';
                icon = '<i class="fa fa-warning"></i> ';
                break;
        }

        statusEl.addClass(`alert ${alertClass}`).html(icon + msg);

        // 3秒后自动隐藏（除了加载状态）
        if (type !== 'info') {
            setTimeout(() => {
                statusEl.fadeOut(500, function() {
                    statusEl.addClass('d-none').show();
                });
            }, 3000);
        }
    }
});