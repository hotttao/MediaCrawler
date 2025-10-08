import os
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

PWD = os.path.realpath(os.path.dirname(__file__))

def generate_html_report(target_date: str, result_df1: pd.DataFrame, result_df2: pd.DataFrame, output_path: str = "report"):
    """
    完整 HTML 可视化报表
    """
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    last5_date = (target_dt - timedelta(days=5)).strftime("%Y-%m-%d")

    nickname_list = sorted(result_df1["nickname"].dropna().unique().tolist())

    html_template = f"""
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <title>数据可视化报表 - {target_date}</title>
  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" />
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
  <style>
    body {{ font-family: sans-serif; margin: 20px; }}
    #chart1, #chart2 {{ width: 100%; height: 400px; margin-bottom: 30px; }}
    #table_container {{ margin-top: 20px; }}
    #backBtn {{ display:none; margin-bottom:10px; padding:6px 12px; background:#1976d2; color:#fff; border:none; border-radius:6px; cursor:pointer; }}
    #backBtn:hover {{ background:#1259a7; }}
    .filter-bar {{ margin: 10px 0; }}
    input[type=number], input[type=date] {{ padding:4px; }}
    button.quick {{ margin-left: 5px; padding:4px 8px; border:none; border-radius:4px; cursor:pointer; background:#eee; }}
    button.quick:hover {{ background:#ddd; }}
    .select2-container {{ min-width: 200px; margin-left:10px; }}
  </style>
</head>
<body>
  <h2>📊 数据可视化报表 - {target_date}</h2>

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

    <label style="margin-left:20px;">nickname：</label>
    <select id="nicknameFilter" multiple>
      {''.join([f'<option value="{n}">{n}</option>' for n in nickname_list])}
    </select>
  </div>

  <div id="chart1"></div>
  <div id="chart2"></div>

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
    const df1 = {result_df1.to_json(orient='records', force_ascii=False)};
    const df2 = {result_df2.to_json(orient='records', force_ascii=False)};
    const last5Date = "{last5_date}";

    $('#nicknameFilter').select2({{ placeholder: '选择一个或多个用户', allowClear: true }});

    let table = $('#df1_table').DataTable({{
      data: df1,
      pageLength: 20,
      order: [[5, 'desc']],
      columns: [
        {{ data: 'nickname' }},
        {{ data: 'aweme_url', render: d => `<a href="${{d}}" target="_blank">查看</a>` }},
        {{ data: 'elastic_title' }},
        {{ data: 'product_title' }},
        {{ data: 'create_time', render: d => d ? new Date(d).toISOString().split('T')[0] : '' }},
        {{ data: 'digg_count' }},
        {{ data: 'collect_count' }},
        {{ data: 'share_count' }},
        {{ data: 'digg_tt' }},
        {{ data: 'collect_tt' }},
        {{ data: 'share_tt' }},
      ]
    }});

    const chart1 = echarts.init(document.getElementById('chart1'));
    const chart2 = echarts.init(document.getElementById('chart2'));
    let currentXKey = 'digg_count';

    function renderCharts() {{
      const xKey = currentXKey;
      const minVal = parseFloat(document.getElementById('minValue').value) || 0;
      const dateVal = document.getElementById('dateFilter').value;
      const selectedNicknames = $('#nicknameFilter').val() || [];

      let validTitles = new Set(df1.map(d => {{
        if (dateVal && new Date(d.create_time) < new Date(dateVal)) return null;
        if (selectedNicknames.length > 0 && !selectedNicknames.includes(d.nickname)) return null;
        return d.elastic_title;
      }}).filter(Boolean));

      const filteredData = df2.filter(d => d[xKey] >= minVal && validTitles.has(d.elastic_title));

      // 拆分图表
      const data1 = filteredData.filter(d => d[xKey] <= 80);
      const data2 = filteredData.filter(d => d[xKey] > 80);

      function getOption(data, xStart) {{
        return {{
          tooltip: {{ trigger: 'item', formatter: p => `${{p.data[2]}}<br/>${{xKey}}: ${{p.data[0]}}<br/>pub_count: ${{p.data[1]}}` }},
          xAxis: {{
            name: xKey,
            type: 'value',
            min: xStart,
            interval: 10,
          }},
          yAxis: {{ name: 'pub_count', type: 'value' }},
          series: [{{
            type: 'scatter',
            data: data.map(d => [d[xKey], d.pub_count, d.elastic_title]),
            symbolSize: 12,
            label: {{ show: true, position: 'top', formatter: p => p.data[2], fontSize: 10 }},
            itemStyle: {{ color: '#3f51b5' }},
            emphasis: {{ scale: 1.3, focus: 'series' }}
          }}]
        }};
      }}

      chart1.setOption(getOption(data1, minVal));
      chart2.setOption(getOption(data2, 70));

      // 更新表格
      const filteredDf1 = df1.filter(d =>
        (!dateVal || new Date(d.create_time) >= new Date(dateVal)) &&
        (selectedNicknames.length === 0 || selectedNicknames.includes(d.nickname))
      );
      table.clear().rows.add(filteredDf1).draw();
    }}

    renderCharts();

    // ===== 自动生效事件 =====
    $('#xAxisSelector').on('change', e => {{ currentXKey = e.target.value; renderCharts(); }});
    $('#minValue').on('input', renderCharts);
    $('#dateFilter').on('change', renderCharts);
    $('#nicknameFilter').on('change', renderCharts);
    $('#btnLast5').on('click', () => {{ document.getElementById('dateFilter').value = last5Date; renderCharts(); }});
    $('#btnClearDate').on('click', () => {{ document.getElementById('dateFilter').value = ''; renderCharts(); }});

    // 点击点展示 df1 明细
    function chartClickHandler(params) {{
      const elasticTitle = params.data[2];
      const filtered = df1.filter(d => d.elastic_title === elasticTitle);
      table.clear().rows.add(filtered).draw();
      document.getElementById('backBtn').style.display = 'inline-block';
    }}
    chart1.on('click', chartClickHandler);
    chart2.on('click', chartClickHandler);

    document.getElementById('backBtn').addEventListener('click', () => {{
      renderCharts();
      document.getElementById('backBtn').style.display = 'none';
    }});
  </script>
</body>
</html>
"""
    output_file = os.path.join(PWD, "report", f"{output_path}_{target_date}.html")
    Path(output_file).write_text(html_template, encoding="utf-8")
    print(f"✅ 报表已生成: {output_file}")


def main():
    from dy_incr import cal_day_incr
    # target_date = "2025-10-08"
    target_date = datetime.today().strftime('%Y-%m-%d')
    result1, result2 = cal_day_incr(target_date)
    generate_html_report(target_date, result1, result2)


if __name__ == "__main__":
    main()
