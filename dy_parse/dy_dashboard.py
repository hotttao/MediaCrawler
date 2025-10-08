import os
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

PWD = os.path.realpath(os.path.dirname(__file__))

def generate_html_report(target_date: str, result_df1: pd.DataFrame, result_df2: pd.DataFrame, output_path: str = "report"):
    """
    生成交互式 HTML 报表
    - 支持 X 轴切换、数值过滤、日期过滤
    - 支持最近5天/清空日期 快捷设置
    - DataTable 展示更多字段 (digg_tt / collect_tt / share_tt)
    - create_time 以日期格式展示
    """

    # 计算 target_date 往前5天
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    last5_date = (target_dt - timedelta(days=5)).strftime("%Y-%m-%d")

    html_template = f"""
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <title>数据可视化报表 - {target_date}</title>
  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css" />
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
  <style>
    body {{ font-family: sans-serif; margin: 20px; }}
    #chart {{ width: 100%; height: 500px; margin-bottom: 30px; }}
    #table_container {{ margin-top: 20px; }}
    #backBtn {{ display:none; margin-bottom:10px; padding:6px 12px; background:#1976d2; color:#fff; border:none; border-radius:6px; cursor:pointer; }}
    #backBtn:hover {{ background:#1259a7; }}
    .filter-bar {{ margin: 10px 0; }}
    input[type=number], input[type=date] {{ padding:4px; }}
    button.quick {{ margin-left: 5px; padding:4px 8px; border:none; border-radius:4px; cursor:pointer; background:#eee; }}
    button.quick:hover {{ background:#ddd; }}
  </style>
</head>
<body>
  <h2>📊 数据可视化报表 - {target_date}</h2>

  <!-- 控制区 -->
  <div class="filter-bar">
    <label>选择 X 轴：</label>
    <select id="xAxisSelector">
      <option value="digg_count">点赞数(digg_count)</option>
      <option value="collect_count">收藏数(collect_count)</option>
      <option value="share_count">分享数(share_count)</option>
    </select>

    <label style="margin-left:20px;">最小值过滤：</label>
    <input type="number" id="minValue" value="15" />

    <label style="margin-left:20px;">日期过滤 (create_time ≥)：</label>
    <input type="date" id="dateFilter" />
    <button class="quick" id="btnLast5">最近5天</button>
    <button class="quick" id="btnClearDate">清空</button>

    <button id="applyFilter" style="margin-left:20px;">应用过滤</button>
  </div>

  <!-- 图表区域 -->
  <div id="chart"></div>

  <!-- 表格区域 -->
  <div id="table_container">
    <button id="backBtn">返回总表</button>
    <table id="df1_table" class="display" style="width:100%">
      <thead>
        <tr>
          <th>nickname</th>
          <th>aweme_url</th>
          <th>elastic_title</th>
          <th>product_title</th>
          <th>create_time</th>
          <th>digg_count</th>
          <th>collect_count</th>
          <th>share_count</th>
          <th>digg_tt</th>
          <th>collect_tt</th>
          <th>share_tt</th>
        </tr>
      </thead>
    </table>
  </div>

  <script>
    // ======= 注入的 DataFrame 数据 =======
    const df1 = {result_df1.to_json(orient='records', force_ascii=False)};
    const df2 = {result_df2.to_json(orient='records', force_ascii=False)};
    const last5Date = "{last5_date}";

    // ======= 初始化 DataTable =======
    let table = $('#df1_table').DataTable({{
      data: df1,
      pageLength: 20,
      order: [[5, 'desc']],
      columns: [
        {{ data: 'nickname' }},
        {{ data: 'aweme_url', render: d => `<a href="${{d}}" target="_blank">查看</a>` }},
        {{ data: 'elastic_title' }},
        {{ data: 'product_title' }},
        {{
          data: 'create_time',
          render: d => {{
            if (!d) return '';
            const dt = new Date(d);
            if (isNaN(dt)) return d;
            return dt.toISOString().split('T')[0];
          }}
        }},
        {{ data: 'digg_count' }},
        {{ data: 'collect_count' }},
        {{ data: 'share_count' }},
        {{ data: 'digg_tt' }},
        {{ data: 'collect_tt' }},
        {{ data: 'share_tt' }},
      ]
    }});

    const chart = echarts.init(document.getElementById('chart'));
    let currentXKey = 'digg_count';

    function renderChart() {{
      const xKey = currentXKey;
      const minVal = parseFloat(document.getElementById('minValue').value) || 0;
      const dateVal = document.getElementById('dateFilter').value;

      // Step 1: 计算符合日期条件的 elastic_title
      let validTitles = new Set(df1.map(d => {{
        if (!dateVal) return d.elastic_title;
        if (!d.create_time) return null;
        const ct = new Date(d.create_time);
        const fDate = new Date(dateVal);
        return ct >= fDate ? d.elastic_title : null;
      }}).filter(Boolean));

      // Step 2: 基于 x 轴过滤 + 日期过滤
      const filteredData = df2.filter(d => d[xKey] >= minVal && validTitles.has(d.elastic_title));

      // Step 3: 渲染图表
      const option = {{
        tooltip: {{ trigger: 'item', formatter: p => `${{p.data[2]}}<br/>${{xKey}}: ${{p.data[0]}}<br/>pub_count: ${{p.data[1]}}` }},
        xAxis: {{ name: xKey, type: 'value' }},
        yAxis: {{ name: 'pub_count', type: 'value' }},
        series: [{{
          type: 'scatter',
          data: filteredData.map(d => [d[xKey], d.pub_count, d.elastic_title]),
          symbolSize: 12,
          label: {{
            show: true,
            position: 'top',
            formatter: (p) => p.data[2],
            fontSize: 10,
            color: '#333'
          }},
          emphasis: {{
            scale: 1.3,
            focus: 'series'
          }},
          itemStyle: {{
            color: '#3f51b5'
          }}
        }}]
      }};
      chart.setOption(option);
    }}

    renderChart(); // 初次渲染

    // ======= X轴切换事件 =======
    document.getElementById('xAxisSelector').addEventListener('change', (e) => {{
      currentXKey = e.target.value;
      renderChart();
    }});

    // ======= 应用过滤 =======
    document.getElementById('applyFilter').addEventListener('click', () => {{
      renderChart();
    }});

    // ======= 最近5天 =======
    document.getElementById('btnLast5').addEventListener('click', () => {{
      document.getElementById('dateFilter').value = last5Date;
      renderChart();
    }});

    // ======= 清空日期 =======
    document.getElementById('btnClearDate').addEventListener('click', () => {{
      document.getElementById('dateFilter').value = '';
      renderChart();
    }});

    // ======= 点击点展示 df1 明细 =======
    chart.on('click', (params) => {{
      const elasticTitle = params.data[2];
      const filtered = df1.filter(d => d.elastic_title === elasticTitle);
      table.clear().rows.add(filtered).draw();
      document.getElementById('backBtn').style.display = 'inline-block';
    }});

    // ======= 返回总表按钮 =======
    document.getElementById('backBtn').addEventListener('click', () => {{
      table.clear().rows.add(df1).draw();
      document.getElementById('backBtn').style.display = 'none';
    }});
  </script>
</body>
</html>
"""
    output_path = os.path.join(PWD, "report", f"{output_path}_{target_date}.html")
    Path(output_path).write_text(html_template, encoding="utf-8")
    print(f"✅ 报表已生成: {output_path}")





def main():
    from dy_incr import cal_day_incr
    target_date = "2025-10-08"  # 可改为传参或 datetime.today().strftime('%Y-%m-%d')
    result1, result2 = cal_day_incr(target_date)
    generate_html_report(target_date, result1, result2)


if __name__ == "__main__":
    main()