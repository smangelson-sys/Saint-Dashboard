"""
Build the GitHub Pages dashboard HTML from dashboard_data.json.
Produces: public/index.html
Uses Chart.js from CDN (works on GitHub Pages).
"""
import json, os, html

DATA_FILE = 'data/dashboard_data.json'
OUT_DIR = 'public'
OUT_FILE = OUT_DIR + '/index.html'

with open(DATA_FILE) as f:
    data = json.load(f)

os.makedirs(OUT_DIR, exist_ok=True)

data_json = json.dumps(data, separators=(',', ':'))

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Saint Wine Lounge - Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg: #1a1a2e; --card: #16213e; --accent: #e94560;
  --accent2: #0f3460; --text: #eee; --muted: #999;
  --green: #4ecca3; --gold: #f0c040; --border: #333;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--text); font-family:'Segoe UI',system-ui,sans-serif; }}
.header {{ background:linear-gradient(135deg,#16213e,#0f3460); padding:16px 20px; text-align:center; border-bottom:2px solid var(--accent); }}
.header h1 {{ font-size:1.4em; letter-spacing:1px; }}
.header .sub {{ color:var(--muted); font-size:0.85em; margin-top:4px; }}
.tabs {{ display:flex; flex-wrap:wrap; gap:4px; padding:8px 12px; background:#111; justify-content:center; }}
.tab {{ padding:8px 16px; cursor:pointer; border-radius:20px; font-size:0.85em;
  background:var(--card); color:var(--muted); border:1px solid var(--border); transition:all 0.2s; }}
.tab:hover {{ color:var(--text); border-color:var(--accent); }}
.tab.active {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
.panel {{ display:none; padding:12px; }}
.panel.active {{ display:block; }}
.card {{ background:var(--card); border-radius:10px; padding:16px; margin-bottom:12px; border:1px solid var(--border); }}
.card h3 {{ color:var(--accent); margin-bottom:10px; font-size:1em; }}
.kpi-row {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; margin-bottom:16px; }}
.kpi {{ background:var(--card); border-radius:10px; padding:14px; text-align:center; border:1px solid var(--border); }}
.kpi .val {{ font-size:1.6em; font-weight:700; color:var(--green); }}
.kpi .lbl {{ font-size:0.75em; color:var(--muted); margin-top:4px; }}
.chart-box {{ position:relative; width:100%; max-height:350px; }}
table {{ width:100%; border-collapse:collapse; font-size:0.85em; }}
th {{ text-align:left; padding:8px; border-bottom:2px solid var(--accent); color:var(--accent); }}
td {{ padding:6px 8px; border-bottom:1px solid var(--border); }}
tr:hover {{ background:rgba(233,69,96,0.1); }}
.money {{ color:var(--green); font-weight:600; }}
.filter-row {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:12px; }}
.filter-row select, .filter-row input {{ padding:6px 10px; border-radius:6px; border:1px solid var(--border);
  background:var(--card); color:var(--text); font-size:0.85em; }}
.filter-row button {{ padding:6px 14px; border-radius:6px; border:none;
  background:var(--accent); color:#fff; cursor:pointer; font-size:0.85em; }}
.yoy-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:12px; }}
@media(max-width:600px) {{
  .kpi-row {{ grid-template-columns:repeat(2,1fr); }}
  .tab {{ padding:6px 10px; font-size:0.78em; }}
}}
</style>
</head>
<body>
<div class="header">
  <h1>THE SAINT WINE LOUNGE</h1>
  <div class="sub" id="lastUpdate"></div>
</div>
<div class="tabs" id="tabBar"></div>
<div id="panels"></div>

<script>
const D = {data_json};

const TABS = [
  {{id:'kpi', label:'Monthly KPIs'}},
  {{id:'yoy', label:'Year vs Year'}},
  {{id:'daily', label:'Daily Trends'}},
  {{id:'items', label:'Top Items'}},
  {{id:'today', label:'Today'}},
  {{id:'market', label:'Market Items'}}
];

const fmt = n => '$' + Number(n).toLocaleString('en-US', {{minimumFractionDigits:0, maximumFractionDigits:0}});
const fmt2 = n => '$' + Number(n).toLocaleString('en-US', {{minimumFractionDigits:2, maximumFractionDigits:2}});

// Build tab bar
const tabBar = document.getElementById('tabBar');
const panels = document.getElementById('panels');
TABS.forEach((t, i) => {{
  const btn = document.createElement('div');
  btn.className = 'tab' + (i===0?' active':'');
  btn.textContent = t.label;
  btn.onclick = () => {{
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('p-'+t.id).classList.add('active');
  }};
  tabBar.appendChild(btn);
  const panel = document.createElement('div');
  panel.id = 'p-' + t.id;
  panel.className = 'panel' + (i===0?' active':'');
  panels.appendChild(panel);
}});

// Last update
if (D.daily && D.daily.length) {{
  document.getElementById('lastUpdate').textContent = 'Data through ' + D.daily[D.daily.length-1].d;
}}

// ===== Monthly KPIs =====
(function() {{
  const p = document.getElementById('p-kpi');
  const m = D.monthly || [];
  if (!m.length) {{ p.innerHTML = '<div class="card">No monthly data</div>'; return; }}
  const last = m[m.length - 1];
  const prev = m.length > 1 ? m[m.length - 2] : null;
  const pctChg = (a,b) => b ? ((a-b)/b*100).toFixed(1)+'%' : 'N/A';

  let kpiHtml = '<div class="kpi-row">';
  kpiHtml += `<div class="kpi"><div class="val">${{fmt(last.ns)}}</div><div class="lbl">Net Sales (${{last.m}})</div></div>`;
  kpiHtml += `<div class="kpi"><div class="val">${{last.o.toLocaleString()}}</div><div class="lbl">Orders</div></div>`;
  kpiHtml += `<div class="kpi"><div class="val">${{fmt(last.t)}}</div><div class="lbl">Tips</div></div>`;
  kpiHtml += `<div class="kpi"><div class="val">${{fmt(last.ns/Math.max(last.o,1))}}</div><div class="lbl">Avg Ticket</div></div>`;
  if (prev) {{
    kpiHtml += `<div class="kpi"><div class="val">${{pctChg(last.ns, prev.ns)}}</div><div class="lbl">vs Prev Month</div></div>`;
  }}
  kpiHtml += '</div>';

  kpiHtml += '<div class="card"><h3>Monthly Net Sales Trend</h3><div class="chart-box"><canvas id="monthlyChart"></canvas></div></div>';
  kpiHtml += '<div class="card"><h3>Monthly Orders Trend</h3><div class="chart-box"><canvas id="ordersChart"></canvas></div></div>';
  p.innerHTML = kpiHtml;

  const labels = m.map(x => x.m);
  const colors = m.map(x => x.s === 'T' ? '#e94560' : x.s === 'B' ? '#9b59b6' : '#0f3460');

  new Chart(document.getElementById('monthlyChart'), {{
    type: 'bar',
    data: {{ labels, datasets: [{{ label: 'Net Sales', data: m.map(x => x.ns), backgroundColor: colors }}] }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ color: '#999', maxRotation: 90, font: {{ size: 10 }} }}, grid: {{ color: '#333' }} }},
        y: {{ ticks: {{ color: '#999', callback: v => '$'+v.toLocaleString() }}, grid: {{ color: '#333' }} }}
      }}
    }}
  }});

  new Chart(document.getElementById('ordersChart'), {{
    type: 'line',
    data: {{ labels, datasets: [{{ label: 'Orders', data: m.map(x => x.o), borderColor: '#4ecca3', backgroundColor: 'rgba(78,204,163,0.1)', fill: true, tension: 0.3 }}] }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ color: '#999', maxRotation: 90, font: {{ size: 10 }} }}, grid: {{ color: '#333' }} }},
        y: {{ ticks: {{ color: '#999' }}, grid: {{ color: '#333' }} }}
      }}
    }}
  }});
}})();

// ===== Year vs Year =====
(function() {{
  const p = document.getElementById('p-yoy');
  const m = D.monthly || [];
  if (!m.length) {{ p.innerHTML = '<div class="card">No data</div>'; return; }}

  // Group by year
  const years = {{}};
  m.forEach(x => {{
    const y = x.m.substring(0,4);
    if (!years[y]) years[y] = [];
    years[y].push(x);
  }});
  const yKeys = Object.keys(years).sort();
  const palette = ['#0f3460','#e94560','#4ecca3','#f0c040','#a855f7','#f97316'];

  let html = '<div class="card"><h3>Net Sales by Year</h3><div class="chart-box"><canvas id="yoyChart"></canvas></div></div>';

  // Year summary table
  html += '<div class="card"><h3>Year Summary</h3><table><tr><th>Year</th><th>Net Sales</th><th>Orders</th><th>Tips</th><th>Avg Ticket</th></tr>';
  yKeys.forEach(y => {{
    const ns = years[y].reduce((s,x)=>s+x.ns,0);
    const o = years[y].reduce((s,x)=>s+x.o,0);
    const t = years[y].reduce((s,x)=>s+x.t,0);
    html += `<tr><td>${{y}}</td><td class="money">${{fmt(ns)}}</td><td>${{o.toLocaleString()}}</td><td class="money">${{fmt(t)}}</td><td class="money">${{fmt(ns/Math.max(o,1))}}</td></tr>`;
  }});
  html += '</table></div>';
  p.innerHTML = html;

  const months = ['01','02','03','04','05','06','07','08','09','10','11','12'];
  const monthLabels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const datasets = yKeys.map((y, i) => ({{
    label: y,
    data: months.map(mm => {{
      const r = years[y].find(x => x.m.endsWith('-'+mm));
      return r ? r.ns : null;
    }}),
    borderColor: palette[i % palette.length],
    backgroundColor: palette[i % palette.length] + '33',
    tension: 0.3, spanGaps: false
  }}));

  new Chart(document.getElementById('yoyChart'), {{
    type: 'line',
    data: {{ labels: monthLabels, datasets }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: '#ccc' }} }} }},
      scales: {{
        x: {{ ticks: {{ color: '#999' }}, grid: {{ color: '#333' }} }},
        y: {{ ticks: {{ color: '#999', callback: v => '$'+v.toLocaleString() }}, grid: {{ color: '#333' }} }}
      }}
    }}
  }});
}})();

// ===== Daily Trends =====
(function() {{
  const p = document.getElementById('p-daily');
  const d = D.daily || [];
  if (!d.length) {{ p.innerHTML = '<div class="card">No daily data</div>'; return; }}

  // Last 90 days
  const recent = d.slice(-90);
  let html = '<div class="card"><h3>Last 90 Days - Net Sales</h3><div class="chart-box"><canvas id="dailyChart"></canvas></div></div>';

  // Day of week averages
  const dow = [0,0,0,0,0,0,0].map(()=>({{s:0,c:0}}));
  const dowNames = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  d.forEach(x => {{
    if (!x.d) return;
    const di = new Date(x.d + 'T12:00:00').getDay();
    if (isNaN(di)) return;
    dow[di].s += x.ns;
    dow[di].c++;
  }});
  html += '<div class="card"><h3>Average Sales by Day of Week</h3><div class="chart-box"><canvas id="dowChart"></canvas></div></div>';

  // Heatmap - monthly daily averages
  html += '<div class="card"><h3>Daily Sales Heatmap (Monthly Avg)</h3><div style="overflow-x:auto"><canvas id="heatChart"></canvas></div></div>';

  p.innerHTML = html;

  new Chart(document.getElementById('dailyChart'), {{
    type: 'bar',
    data: {{
      labels: recent.map(x => x.d.substring(5)),
      datasets: [{{ label: 'Net Sales', data: recent.map(x => x.ns), backgroundColor: '#e94560aa' }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ color: '#999', maxRotation: 90, font: {{ size: 9 }} }}, grid: {{ display: false }} }},
        y: {{ ticks: {{ color: '#999', callback: v => '$'+v.toLocaleString() }}, grid: {{ color: '#333' }} }}
      }}
    }}
  }});

  new Chart(document.getElementById('dowChart'), {{
    type: 'bar',
    data: {{
      labels: dowNames,
      datasets: [{{ label: 'Avg Sales', data: dow.map(x => x.c ? Math.round(x.s/x.c) : 0),
        backgroundColor: ['#666','#e94560','#e94560','#e94560','#e94560','#4ecca3','#4ecca3'] }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ color: '#999' }}, grid: {{ display: false }} }},
        y: {{ ticks: {{ color: '#999', callback: v => '$'+v.toLocaleString() }}, grid: {{ color: '#333' }} }}
      }}
    }}
  }});
}})();

// ===== Top Items =====
(function() {{
  const p = document.getElementById('p-items');
  const items = D.items || {{}};
  const allMonths = Object.keys(items).filter(k => !k.startsWith('C_')).sort((a,b) => b.localeCompare(a));
  const catMonths = Object.keys(items).filter(k => k.startsWith('C_')).sort();

  let html = '<div class="filter-row"><select id="itemMonthSel">';
  allMonths.forEach(m => {{
    html += `<option value="${{m}}">${{m}}</option>`;
  }});
  html += '</select></div>';

  html += '<div class="card"><h3>Top Items by Revenue</h3><div class="chart-box"><canvas id="itemsChart"></canvas></div></div>';
  html += '<div class="card" id="itemsTable"></div>';

  // Categories
  if (catMonths.length) {{
    html += '<div class="card"><h3>Sales by Category (Toast)</h3><div class="chart-box"><canvas id="catChart"></canvas></div></div>';
  }}

  p.innerHTML = html;

  let itemsChartInst = null;
  let catChartInst = null;

  function updateItems(month) {{
    const data = items[month] || [];
    const top = data.slice(0, 15);

    if (itemsChartInst) itemsChartInst.destroy();
    itemsChartInst = new Chart(document.getElementById('itemsChart'), {{
      type: 'bar',
      data: {{
        labels: top.map(x => x.n.length > 20 ? x.n.substring(0,20)+'...' : x.n),
        datasets: [{{ label: 'Revenue', data: top.map(x => x.r), backgroundColor: '#e94560' }}]
      }},
      options: {{
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: {{ color: '#999', callback: v => '$'+v }}, grid: {{ color: '#333' }} }},
          y: {{ ticks: {{ color: '#ccc', font: {{ size: 11 }} }}, grid: {{ display: false }} }}
        }}
      }}
    }});

    let tbl = '<table><tr><th>Item</th><th>Qty</th><th>Revenue</th></tr>';
    data.forEach(x => {{
      tbl += `<tr><td>${{x.n}}</td><td>${{x.q}}</td><td class="money">${{fmt2(x.r)}}</td></tr>`;
    }});
    tbl += '</table>';
    document.getElementById('itemsTable').innerHTML = '<h3>All Items</h3>' + tbl;

    // Update category chart
    const cm = 'C_' + month.replace('T_','');
    const catData = items[cm] || [];
    if (catData.length && document.getElementById('catChart')) {{
      if (catChartInst) catChartInst.destroy();
      catChartInst = new Chart(document.getElementById('catChart'), {{
        type: 'doughnut',
        data: {{
          labels: catData.map(x => x.n),
          datasets: [{{ data: catData.map(x => x.r),
            backgroundColor: ['#e94560','#0f3460','#4ecca3','#f0c040','#a855f7','#f97316','#06b6d4','#84cc16','#ec4899','#8b5cf6'] }}]
        }},
        options: {{
          responsive: true, maintainAspectRatio: false,
          plugins: {{ legend: {{ position: 'right', labels: {{ color: '#ccc', font: {{ size: 11 }} }} }} }}
        }}
      }});
    }}
  }}

  const sel = document.getElementById('itemMonthSel');
  sel.onchange = () => updateItems(sel.value);
  if (allMonths.length) updateItems(allMonths[0]);
}})();

// ===== Today =====
(function() {{
  const p = document.getElementById('p-today');
  const ts = D.todaySales || [];
  const ti = D.todayItems || [];
  if (!ts.length) {{ p.innerHTML = '<div class="card">No data for today</div>'; return; }}
  const t = ts[0];

  let html = '<div class="kpi-row">';
  html += `<div class="kpi"><div class="val">${{fmt(t.ns)}}</div><div class="lbl">Net Sales (${{t.d}})</div></div>`;
  html += `<div class="kpi"><div class="val">${{t.o}}</div><div class="lbl">Orders</div></div>`;
  html += `<div class="kpi"><div class="val">${{fmt(t.t)}}</div><div class="lbl">Tips</div></div>`;
  html += `<div class="kpi"><div class="val">${{fmt(t.ns/Math.max(t.o,1))}}</div><div class="lbl">Avg Ticket</div></div>`;
  html += '</div>';

  if (ti.length) {{
    html += '<div class="card"><h3>Items Sold</h3><div class="chart-box"><canvas id="todayChart"></canvas></div></div>';
    html += '<div class="card"><table><tr><th>Item</th><th>Qty</th><th>Revenue</th></tr>';
    ti.forEach(x => {{
      html += `<tr><td>${{x.n}}</td><td>${{x.q}}</td><td class="money">${{fmt2(x.r)}}</td></tr>`;
    }});
    html += '</table></div>';
  }}
  p.innerHTML = html;

  if (ti.length) {{
    const top = ti.slice(0, 12);
    new Chart(document.getElementById('todayChart'), {{
      type: 'bar',
      data: {{
        labels: top.map(x => x.n.length > 18 ? x.n.substring(0,18)+'...' : x.n),
        datasets: [{{ label: 'Revenue', data: top.map(x => x.r), backgroundColor: '#4ecca3' }}]
      }},
      options: {{
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: {{ color: '#999', callback: v => '$'+v }}, grid: {{ color: '#333' }} }},
          y: {{ ticks: {{ color: '#ccc', font: {{ size: 11 }} }}, grid: {{ display: false }} }}
        }}
      }}
    }});
  }}
}})();

// ===== Market Items =====
(function() {{
  const p = document.getElementById('p-market');
  const mk = D.market || {{}};
  const dates = Object.keys(mk).sort().reverse();
  if (!dates.length) {{ p.innerHTML = '<div class="card">No market data</div>'; return; }}

  let html = '<div class="filter-row">';
  html += '<select id="mktDateSel"><option value="all">All Dates</option>';
  dates.forEach(d => {{ html += `<option value="${{d}}">${{d}}</option>`; }});
  html += '</select>';
  html += '<label>From: <input type="date" id="mktFrom"></label>';
  html += '<label>To: <input type="date" id="mktTo"></label>';
  html += '<button id="mktReset">Reset</button>';
  html += '</div>';
  html += '<div id="mktContent"></div>';
  p.innerHTML = html;

  function renderMarket(filterDates) {{
    let items = {{}};
    let totalNet = 0;
    filterDates.forEach(d => {{
      (mk[d]||[]).forEach(x => {{
        if (!items[x.n]) items[x.n] = {{q:0, net:0}};
        items[x.n].q += x.q;
        items[x.n].net += x.net;
        totalNet += x.net;
      }});
    }});
    const sorted = Object.entries(items).sort((a,b) => b[1].net - a[1].net);
    let h = `<div class="kpi-row"><div class="kpi"><div class="val">${{fmt(totalNet)}}</div><div class="lbl">Market Revenue (${{filterDates.length}} days)</div></div>`;
    h += `<div class="kpi"><div class="val">${{sorted.length}}</div><div class="lbl">Unique Items</div></div></div>`;
    h += '<div class="card"><table><tr><th>Item</th><th>Qty</th><th>Revenue</th></tr>';
    sorted.forEach(([n,v]) => {{
      h += `<tr><td>${{n}}</td><td>${{v.q}}</td><td class="money">${{fmt2(v.net)}}</td></tr>`;
    }});
    h += '</table></div>';
    document.getElementById('mktContent').innerHTML = h;
  }}

  function getFilteredDates() {{
    const sel = document.getElementById('mktDateSel').value;
    const from = document.getElementById('mktFrom').value;
    const to = document.getElementById('mktTo').value;
    let fd = dates;
    if (sel !== 'all') fd = [sel];
    else {{
      if (from) fd = fd.filter(d => d >= from);
      if (to) fd = fd.filter(d => d <= to);
    }}
    return fd;
  }}

  document.getElementById('mktDateSel').onchange = () => renderMarket(getFilteredDates());
  document.getElementById('mktFrom').onchange = () => {{ document.getElementById('mktDateSel').value='all'; renderMarket(getFilteredDates()); }};
  document.getElementById('mktTo').onchange = () => {{ document.getElementById('mktDateSel').value='all'; renderMarket(getFilteredDates()); }};
  document.getElementById('mktReset').onclick = () => {{
    document.getElementById('mktDateSel').value='all';
    document.getElementById('mktFrom').value='';
    document.getElementById('mktTo').value='';
    renderMarket(dates);
  }};

  renderMarket(dates);
}})();
</script>
</body>
</html>'''

with open(OUT_FILE, 'w') as f:
    f.write(page)

print(f"Dashboard written to {OUT_FILE} ({os.path.getsize(OUT_FILE):,} bytes)")
