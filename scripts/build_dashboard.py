"""
Build mobile-first BI dashboard HTML from dashboard_data.json.
Writes: public/index.html
"""
import json, os

DATA = 'data/dashboard_data.json'
OUT = 'public/index.html'

with open(DATA) as f:
    raw = f.read()

os.makedirs('public', exist_ok=True)

CSS = r'''
:root {
  --bg: #0f0f0f; --surface: #1a1a1a; --card: #222; --border: #333;
  --text: #e8e8e8; --text2: #999; --accent: #c9a96e; --accent2: #8b6b3d;
  --green: #4caf50; --red: #ef5350; --blue: #42a5f5;
  --wine: #722f37; --wine2: #8b3a42;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); overflow-x: hidden; }
.header { background: linear-gradient(135deg, var(--wine) 0%, #1a1a1a 100%); padding: 16px; text-align: center; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid var(--accent2); }
.header h1 { font-size: 20px; letter-spacing: 4px; color: var(--accent); font-weight: 300; }
.header .subtitle { font-size: 11px; color: var(--text2); margin-top: 2px; }
.tabs { display: flex; overflow-x: auto; background: var(--surface); border-bottom: 1px solid var(--border); -webkit-overflow-scrolling: touch; scrollbar-width: none; }
.tabs::-webkit-scrollbar { display: none; }
.tab { flex: 0 0 auto; padding: 12px 16px; font-size: 13px; color: var(--text2); cursor: pointer; white-space: nowrap; border-bottom: 2px solid transparent; transition: all 0.2s; }
.tab.active { color: var(--accent); border-bottom-color: var(--accent); }
.content { padding: 12px; max-width: 900px; margin: 0 auto; }
.section { display: none; }
.section.active { display: block; }
.kpi-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px; }
.kpi { background: var(--card); border-radius: 8px; padding: 12px; border: 1px solid var(--border); }
.kpi-label { font-size: 11px; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; }
.kpi-value { font-size: 22px; font-weight: 600; color: var(--accent); margin-top: 4px; }
.kpi-delta { font-size: 12px; margin-top: 2px; }
.kpi-delta.up { color: var(--green); }
.kpi-delta.down { color: var(--red); }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.chip { padding: 6px 14px; border-radius: 20px; font-size: 12px; background: var(--card); border: 1px solid var(--border); color: var(--text2); cursor: pointer; transition: all 0.2s; user-select: none; }
.chip.active { background: var(--accent2); border-color: var(--accent); color: var(--text); }
.compare-row { display: flex; gap: 8px; margin-bottom: 12px; align-items: center; flex-wrap: wrap; }
.compare-row select, .compare-row input { background: var(--card); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: 6px; font-size: 14px; flex: 1; min-width: 0; }
.vs-label { color: var(--accent); font-weight: bold; flex: 0 0 auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 8px; color: var(--text2); border-bottom: 1px solid var(--border); font-size: 11px; text-transform: uppercase; cursor: pointer; white-space: nowrap; }
.data-table th:hover { color: var(--accent); }
.data-table td { padding: 8px; border-bottom: 1px solid var(--border); }
.data-table tr:hover { background: rgba(201,169,110,0.05); }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px; }
.compare-card { background: var(--card); border-radius: 8px; padding: 12px; border: 1px solid var(--border); }
.compare-card .metric-label { font-size: 11px; color: var(--text2); text-transform: uppercase; }
.compare-card .metric-row { display: flex; justify-content: space-between; margin-top: 6px; }
.compare-card .metric-val { font-size: 16px; font-weight: 600; }
.compare-card .metric-val.a { color: var(--accent); }
.compare-card .metric-val.b { color: var(--blue); }
.compare-card .metric-change { font-size: 12px; margin-top: 4px; }
.search-box { width: 100%; padding: 10px 14px; background: var(--card); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 14px; margin-bottom: 12px; }
.search-box::placeholder { color: var(--text2); }
.chart-wrap { background: var(--card); border-radius: 8px; padding: 12px; border: 1px solid var(--border); margin-bottom: 16px; position: relative; }
.chart-wrap canvas { width: 100% !important; }
.chart-title { font-size: 13px; color: var(--text2); margin-bottom: 8px; }
.period-select { display: flex; gap: 6px; margin-bottom: 12px; }
.period-btn { padding: 6px 12px; border-radius: 6px; font-size: 12px; background: var(--card); border: 1px solid var(--border); color: var(--text2); cursor: pointer; }
.period-btn.active { background: var(--accent2); border-color: var(--accent); color: var(--text); }
.table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; margin-bottom: 16px; }
.kpi.full { grid-column: 1 / -1; }
.toggle-row { display: flex; gap: 12px; margin-bottom: 12px; }
.toggle-btn { padding: 8px 16px; border-radius: 6px; font-size: 13px; background: var(--card); border: 1px solid var(--border); color: var(--text2); cursor: pointer; flex: 1; text-align: center; }
.toggle-btn.active { background: var(--accent2); border-color: var(--accent); color: var(--text); }
@media (min-width: 600px) {
  .kpi-grid { grid-template-columns: repeat(4, 1fr); }
  .compare-grid { grid-template-columns: repeat(4, 1fr); }
  .content { padding: 16px; }
}
'''

BODY = '''
<div class="header">
  <h1>THE SAINT</h1>
  <div class="subtitle" id="lastUpdate"></div>
</div>
<div class="tabs" id="tabBar">
  <div class="tab active" data-tab="overview">Overview</div>
  <div class="tab" data-tab="compare">Compare</div>
  <div class="tab" data-tab="daily">Daily</div>
  <div class="tab" data-tab="items">Items</div>
  <div class="tab" data-tab="nightwines">Night Wines</div>
  <div class="tab" data-tab="food">Food</div>
  <div class="tab" data-tab="market">Market</div>
</div>
<div class="content">
  <div class="section active" id="sec-overview">
    <div class="period-select" id="overviewPeriod">
      <div class="period-btn active" data-months="3">3M</div>
      <div class="period-btn" data-months="6">6M</div>
      <div class="period-btn" data-months="12">1Y</div>
      <div class="period-btn" data-months="0">All</div>
    </div>
    <div class="kpi-grid" id="overviewKPIs"></div>
    <div class="chart-wrap"><div class="chart-title">Monthly Revenue</div><canvas id="chartRevenue" height="200"></canvas></div>
    <div class="chart-wrap"><div class="chart-title">Monthly Orders</div><canvas id="chartOrders" height="180"></canvas></div>
    <div class="chart-wrap"><div class="chart-title">Avg Check (Revenue / Orders)</div><canvas id="chartAvgCheck" height="180"></canvas></div>
  </div>
  <div class="section" id="sec-compare">
    <div class="toggle-row" id="compareMode">
      <div class="toggle-btn active" data-mode="month">Month vs Month</div>
      <div class="toggle-btn" data-mode="day">Day vs Day</div>
    </div>
    <div id="compareMonthControls">
      <div class="compare-row">
        <select id="cmpMonthA"></select>
        <span class="vs-label">vs</span>
        <select id="cmpMonthB"></select>
      </div>
    </div>
    <div id="compareDayControls" style="display:none">
      <div class="compare-row">
        <input type="date" id="cmpDayA">
        <span class="vs-label">vs</span>
        <input type="date" id="cmpDayB">
      </div>
    </div>
    <div class="compare-grid" id="compareCards"></div>
    <div class="chart-wrap"><div class="chart-title" id="compareChartTitle">Comparison</div><canvas id="chartCompare" height="220"></canvas></div>
  </div>
  <div class="section" id="sec-daily">
    <div class="compare-row"><select id="dailyMonth"></select></div>
    <div class="kpi-grid" id="dailyKPIs"></div>
    <div class="chart-wrap"><div class="chart-title">Daily Revenue</div><canvas id="chartDaily" height="200"></canvas></div>
    <div class="chart-wrap"><div class="chart-title">Day of Week Avg</div><canvas id="chartDOW" height="180"></canvas></div>
    <div class="table-wrap">
      <table class="data-table" id="dailyTable">
        <thead><tr><th>Date</th><th class="num">Revenue</th><th class="num">Tips</th><th class="num">Orders</th><th class="num">Avg Check</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
  <div class="section" id="sec-items">
    <div class="compare-row"><select id="itemMonth"></select></div>
    <div class="chips" id="itemCatChips"></div>
    <input class="search-box" id="itemSearch" placeholder="Search items...">
    <div class="kpi-grid" id="itemKPIs"></div>
    <div class="table-wrap">
      <table class="data-table" id="itemTable">
        <thead><tr><th>Item</th><th>Category</th><th class="num">Qty</th><th class="num">Revenue</th><th class="num">Avg Price</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
  <div class="section" id="sec-nightwines">
    <div class="period-select" id="nwPeriod">
      <div class="period-btn active" data-months="6">6M</div>
      <div class="period-btn" data-months="12">1Y</div>
      <div class="period-btn" data-months="0">All</div>
    </div>
    <div class="kpi-grid" id="nwKPIs"></div>
    <div class="chart-wrap"><div class="chart-title">Night Wines Monthly Revenue</div><canvas id="chartNW" height="200"></canvas></div>
    <div class="compare-row"><select id="nwMonth"></select></div>
    <div class="table-wrap">
      <table class="data-table" id="nwTable">
        <thead><tr><th>Item</th><th class="num">Qty</th><th class="num">Revenue</th><th class="num">Avg Price</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
  <div class="section" id="sec-food">
    <div class="period-select" id="foodPeriod">
      <div class="period-btn active" data-months="6">6M</div>
      <div class="period-btn" data-months="12">1Y</div>
      <div class="period-btn" data-months="0">All</div>
    </div>
    <div class="kpi-grid" id="foodKPIs"></div>
    <div class="chart-wrap"><div class="chart-title">Food Monthly Revenue</div><canvas id="chartFood" height="200"></canvas></div>
    <div class="compare-row"><select id="foodMonth"></select></div>
    <div class="table-wrap">
      <table class="data-table" id="foodTable">
        <thead><tr><th>Item</th><th class="num">Qty</th><th class="num">Revenue</th><th class="num">Avg Price</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
  <div class="section" id="sec-market">
    <div class="compare-row"><select id="marketMonth"></select></div>
    <div class="kpi-grid" id="marketKPIs"></div>
    <div class="chart-wrap"><div class="chart-title">Market Items by Month</div><canvas id="chartMarket" height="200"></canvas></div>
    <div class="table-wrap">
      <table class="data-table" id="marketTable">
        <thead><tr><th>Item</th><th class="num">Qty</th><th class="num">Revenue</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
</div>
'''

JS = r'''
const D = __DATA__;
const fmt = (n) => n == null ? '-' : '$' + Number(n).toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0});
const fmt2 = (n) => n == null ? '-' : '$' + Number(n).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
const fmtN = (n) => n == null ? '-' : Number(n).toLocaleString('en-US');
const pct = (a, b) => b ? ((a - b) / b * 100).toFixed(1) : null;
const months = (D.monthly || []).map(m => m.m).sort();
const dailyMap = {};
(D.daily || []).forEach(d => { dailyMap[d.d] = d; });
const allDates = Object.keys(dailyMap).sort();
if (allDates.length) document.getElementById('lastUpdate').textContent = 'Data through ' + allDates[allDates.length - 1];

document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.section').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById('sec-' + t.dataset.tab).classList.add('active');
    const init = inits[t.dataset.tab]; if (init) init();
  });
});

const charts = {};
function makeChart(id, cfg) { if (charts[id]) charts[id].destroy(); const ctx = document.getElementById(id); if (!ctx) return null; Chart.defaults.color = '#999'; Chart.defaults.borderColor = '#333'; charts[id] = new Chart(ctx, cfg); return charts[id]; }

function kpiCard(label, value, delta) {
  let dh = '';
  if (delta !== null && delta !== undefined) { const cls = parseFloat(delta) >= 0 ? 'up' : 'down'; const ar = parseFloat(delta) >= 0 ? '&#9650;' : '&#9660;'; dh = '<div class="kpi-delta ' + cls + '">' + ar + ' ' + Math.abs(parseFloat(delta)) + '% vs prior</div>'; }
  return '<div class="kpi"><div class="kpi-label">' + label + '</div><div class="kpi-value">' + value + '</div>' + dh + '</div>';
}

function compareCard(label, valA, valB, isCurrency) {
  const ff = isCurrency ? fmt2 : (v => typeof v === 'number' && v > 100 ? fmt(v) : fmtN(v));
  const ch = pct(valA, valB);
  const cls = ch !== null ? (parseFloat(ch) >= 0 ? 'up' : 'down') : '';
  const ar = ch !== null ? (parseFloat(ch) >= 0 ? '&#9650;' : '&#9660;') : '';
  return '<div class="compare-card"><div class="metric-label">' + label + '</div><div class="metric-row"><span class="metric-val a">' + ff(valA) + '</span><span class="metric-val b">' + ff(valB) + '</span></div>' + (ch !== null ? '<div class="metric-change ' + cls + '">' + ar + ' ' + Math.abs(parseFloat(ch)) + '%</div>' : '') + '</div>';
}

let overviewMonths = 3;
function renderOverview() {
  const ms = overviewMonths === 0 ? D.monthly : D.monthly.slice(-overviewMonths);
  const tR = ms.reduce((s,m) => s + m.ns, 0), tO = ms.reduce((s,m) => s + m.o, 0), tI = ms.reduce((s,m) => s + m.i, 0), aC = tO ? tR / tO : 0;
  const pMs = overviewMonths === 0 ? [] : D.monthly.slice(-(overviewMonths * 2), -overviewMonths);
  const pR = pMs.reduce((s,m) => s + m.ns, 0), pO = pMs.reduce((s,m) => s + m.o, 0), pA = pO ? pR / pO : 0;
  document.getElementById('overviewKPIs').innerHTML = [kpiCard('Revenue',fmt(tR),pct(tR,pR)), kpiCard('Orders',fmtN(tO),pct(tO,pO)), kpiCard('Items Sold',fmtN(tI),null), kpiCard('Avg Check',fmt2(aC),pct(aC,pA))].join('');
  makeChart('chartRevenue', {type:'bar',data:{labels:ms.map(m=>m.m),datasets:[{label:'Revenue',data:ms.map(m=>m.ns),backgroundColor:'rgba(201,169,110,0.7)',borderRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>'$'+(v/1000).toFixed(0)+'k'}}}}});
  makeChart('chartOrders', {type:'bar',data:{labels:ms.map(m=>m.m),datasets:[{label:'Orders',data:ms.map(m=>m.o),backgroundColor:'rgba(66,165,245,0.7)',borderRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}}}});
  makeChart('chartAvgCheck', {type:'line',data:{labels:ms.map(m=>m.m),datasets:[{label:'Avg Check',data:ms.map(m=>m.o?(m.ns/m.o):0),borderColor:'#c9a96e',backgroundColor:'rgba(201,169,110,0.1)',fill:true,tension:0.3}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>'$'+v}}}}});
}
document.querySelectorAll('#overviewPeriod .period-btn').forEach(b => { b.addEventListener('click', () => { document.querySelectorAll('#overviewPeriod .period-btn').forEach(x=>x.classList.remove('active')); b.classList.add('active'); overviewMonths=parseInt(b.dataset.months); renderOverview(); }); });

function initCompare() {
  const sA=document.getElementById('cmpMonthA'), sB=document.getElementById('cmpMonthB');
  if (sA.options.length===0) { months.forEach(m=>{sA.add(new Option(m,m));sB.add(new Option(m,m));}); if(months.length>=2){sA.value=months[months.length-1];const c=months[months.length-1],y=(parseInt(c)-1)+c.slice(4);sB.value=months.includes(y)?y:months[months.length-2];} }
  renderCompare();
}
function getCompareMode(){return document.querySelector('#compareMode .toggle-btn.active').dataset.mode;}
document.querySelectorAll('#compareMode .toggle-btn').forEach(b=>{b.addEventListener('click',()=>{document.querySelectorAll('#compareMode .toggle-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById('compareMonthControls').style.display=b.dataset.mode==='month'?'':'none';document.getElementById('compareDayControls').style.display=b.dataset.mode==='day'?'':'none';renderCompare();});});
function renderCompare() {
  const mode=getCompareMode(),cards=document.getElementById('compareCards');
  if(mode==='month'){const mA=document.getElementById('cmpMonthA').value,mB=document.getElementById('cmpMonthB').value;const a=D.monthly.find(m=>m.m===mA)||{},b=D.monthly.find(m=>m.m===mB)||{};const aA=a.o?a.ns/a.o:0,aB=b.o?b.ns/b.o:0;cards.innerHTML=[compareCard('Revenue',a.ns,b.ns),compareCard('Orders',a.o,b.o),compareCard('Items',a.i,b.i),compareCard('Avg Check',aA,aB,true)].join('');document.getElementById('compareChartTitle').textContent=mA+' vs '+mB;makeChart('chartCompare',{type:'bar',data:{labels:['Revenue','Orders','Items','Tips'],datasets:[{label:mA,data:[a.ns||0,a.o||0,a.i||0,a.t||0],backgroundColor:'rgba(201,169,110,0.8)'},{label:mB,data:[b.ns||0,b.o||0,b.i||0,b.t||0],backgroundColor:'rgba(66,165,245,0.8)'}]},options:{responsive:true,plugins:{legend:{position:'bottom'}}}});}
  else{const dA=document.getElementById('cmpDayA').value,dB=document.getElementById('cmpDayB').value;const a=dailyMap[dA]||{},b=dailyMap[dB]||{};const aA=a.o?a.ns/a.o:0,aB=b.o?b.ns/b.o:0;cards.innerHTML=[compareCard('Revenue',a.ns,b.ns),compareCard('Orders',a.o,b.o),compareCard('Tips',a.t,b.t),compareCard('Avg Check',aA,aB,true)].join('');document.getElementById('compareChartTitle').textContent=(dA||'?')+' vs '+(dB||'?');makeChart('chartCompare',{type:'bar',data:{labels:['Revenue','Orders','Tips'],datasets:[{label:dA||'A',data:[a.ns||0,a.o||0,a.t||0],backgroundColor:'rgba(201,169,110,0.8)'},{label:dB||'B',data:[b.ns||0,b.o||0,b.t||0],backgroundColor:'rgba(66,165,245,0.8)'}]},options:{responsive:true,plugins:{legend:{position:'bottom'}}}});}
}
document.getElementById('cmpMonthA').addEventListener('change',renderCompare);document.getElementById('cmpMonthB').addEventListener('change',renderCompare);document.getElementById('cmpDayA').addEventListener('change',renderCompare);document.getElementById('cmpDayB').addEventListener('change',renderCompare);

function initDaily(){const sel=document.getElementById('dailyMonth');if(sel.options.length===0){const dM=[...new Set(allDates.map(d=>d.slice(0,7)))].sort();dM.forEach(m=>sel.add(new Option(m,m)));sel.value=dM[dM.length-1];}renderDaily();}
function renderDaily(){
  const m=document.getElementById('dailyMonth').value;const days=allDates.filter(d=>d.startsWith(m)).map(d=>dailyMap[d]);
  const tR=days.reduce((s,d)=>s+(d.ns||0),0),tO=days.reduce((s,d)=>s+(d.o||0),0),tT=days.reduce((s,d)=>s+(d.t||0),0),aC=tO?tR/tO:0;
  document.getElementById('dailyKPIs').innerHTML=[kpiCard('Revenue',fmt(tR),null),kpiCard('Orders',fmtN(tO),null),kpiCard('Tips',fmt(tT),null),kpiCard('Avg Check',fmt2(aC),null)].join('');
  makeChart('chartDaily',{type:'bar',data:{labels:days.map(d=>d.d.slice(5)),datasets:[{data:days.map(d=>d.ns),backgroundColor:'rgba(201,169,110,0.7)',borderRadius:3}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>'$'+(v/1000).toFixed(0)+'k'}},x:{ticks:{maxTicksAutoSkip:true,maxRotation:45}}}}});
  const dow=[0,0,0,0,0,0,0].map(()=>({sum:0,count:0}));const dowNames=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  days.forEach(d=>{const day=new Date(d.d+'T12:00:00').getDay();dow[day].sum+=d.ns||0;dow[day].count++;});
  makeChart('chartDOW',{type:'bar',data:{labels:dowNames,datasets:[{data:dow.map(d=>d.count?+(d.sum/d.count).toFixed(0):0),backgroundColor:'rgba(114,47,55,0.8)',borderRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>'$'+v}}}}});
  const tbody=document.querySelector('#dailyTable tbody');
  tbody.innerHTML=days.map(d=>{const ac=d.o?(d.ns/d.o).toFixed(2):'0';const wd=dowNames[new Date(d.d+'T12:00:00').getDay()];return '<tr><td>'+d.d+' ('+wd+')</td><td class="num">'+fmt(d.ns)+'</td><td class="num">'+fmt(d.t)+'</td><td class="num">'+fmtN(d.o)+'</td><td class="num">'+fmt2(ac)+'</td></tr>';}).join('');
}
document.getElementById('dailyMonth').addEventListener('change',renderDaily);

let itemCatFilter='All',itemSortCol=3,itemSortAsc=false;
function initItems(){const sel=document.getElementById('itemMonth');if(sel.options.length===0){const iM=Object.keys(D.items||{}).sort();iM.forEach(m=>sel.add(new Option(m,m)));sel.value=iM[iM.length-1];}renderItems();}
function renderItems(){
  const m=document.getElementById('itemMonth').value;let items=D.items[m]||[];const search=document.getElementById('itemSearch').value.toLowerCase();
  const cats=['All',...new Set(items.map(i=>i.c||'Other').filter(c=>c))];
  const chipDiv=document.getElementById('itemCatChips');chipDiv.innerHTML=cats.map(c=>'<div class="chip'+(c===itemCatFilter?' active':'')+'" data-cat="'+c+'">'+c+'</div>').join('');
  chipDiv.querySelectorAll('.chip').forEach(ch=>{ch.addEventListener('click',()=>{itemCatFilter=ch.dataset.cat;renderItems();});});
  if(itemCatFilter!=='All')items=items.filter(i=>(i.c||'Other')===itemCatFilter);
  if(search)items=items.filter(i=>i.n.toLowerCase().includes(search));
  const sortFns=[(a,b)=>a.n.localeCompare(b.n),(a,b)=>(a.c||'').localeCompare(b.c||''),(a,b)=>a.q-b.q,(a,b)=>a.r-b.r,(a,b)=>(a.q?a.r/a.q:0)-(b.q?b.r/b.q:0)];
  if(sortFns[itemSortCol]){items=[...items].sort(sortFns[itemSortCol]);if(!itemSortAsc)items.reverse();}
  const tR=items.reduce((s,i)=>s+i.r,0),tQ=items.reduce((s,i)=>s+i.q,0);
  document.getElementById('itemKPIs').innerHTML=[kpiCard('Items',fmtN(items.length),null),kpiCard('Total Qty',fmtN(tQ),null),kpiCard('Total Rev',fmt(tR),null),kpiCard('Avg Price',fmt2(tQ?tR/tQ:0),null)].join('');
  document.querySelector('#itemTable tbody').innerHTML=items.slice(0,100).map(i=>{const avg=i.q?(i.r/i.q).toFixed(2):'0';return '<tr><td>'+i.n+'</td><td>'+(i.c||'Other')+'</td><td class="num">'+fmtN(i.q)+'</td><td class="num">'+fmt2(i.r)+'</td><td class="num">'+fmt2(avg)+'</td></tr>';}).join('');
}
document.getElementById('itemMonth').addEventListener('change',renderItems);document.getElementById('itemSearch').addEventListener('input',renderItems);
document.querySelectorAll('#itemTable th').forEach((th,idx)=>{th.addEventListener('click',()=>{if(itemSortCol===idx)itemSortAsc=!itemSortAsc;else{itemSortCol=idx;itemSortAsc=false;}renderItems();});});

let nwPeriodMonths=6;
function initNightWines(){const sel=document.getElementById('nwMonth');if(sel.options.length===0){const iM=Object.keys(D.items||{}).sort();iM.forEach(m=>sel.add(new Option(m,m)));sel.value=iM[iM.length-1];}renderNightWines();}
function renderNightWines(){
  const allM=Object.keys(D.items||{}).sort(),showM=nwPeriodMonths===0?allM:allM.slice(-nwPeriodMonths);
  const mNW=showM.map(m=>{const its=(D.items[m]||[]).filter(i=>i.c==='Night Wines'||(i.n&&i.n.toLowerCase().startsWith('night')));return{m,rev:its.reduce((s,i)=>s+i.r,0),qty:its.reduce((s,i)=>s+i.q,0)};});
  const tR=mNW.reduce((s,m)=>s+m.rev,0),tQ=mNW.reduce((s,m)=>s+m.qty,0);
  document.getElementById('nwKPIs').innerHTML=[kpiCard('Total Rev',fmt(tR),null),kpiCard('Total Qty',fmtN(tQ),null),kpiCard('Avg/Month',fmt(showM.length?tR/showM.length:0),null),kpiCard('Avg Price',fmt2(tQ?tR/tQ:0),null)].join('');
  makeChart('chartNW',{type:'bar',data:{labels:mNW.map(m=>m.m),datasets:[{data:mNW.map(m=>m.rev),backgroundColor:'rgba(114,47,55,0.8)',borderRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>'$'+(v/1000).toFixed(0)+'k'}},x:{ticks:{maxRotation:45}}}}});
  const selMonth=document.getElementById('nwMonth').value;
  const items=(D.items[selMonth]||[]).filter(i=>i.c==='Night Wines'||(i.n&&i.n.toLowerCase().startsWith('night'))).sort((a,b)=>b.r-a.r);
  document.querySelector('#nwTable tbody').innerHTML=items.map(i=>'<tr><td>'+i.n+'</td><td class="num">'+fmtN(i.q)+'</td><td class="num">'+fmt2(i.r)+'</td><td class="num">'+fmt2(i.q?i.r/i.q:0)+'</td></tr>').join('');
}
document.querySelectorAll('#nwPeriod .period-btn').forEach(b=>{b.addEventListener('click',()=>{document.querySelectorAll('#nwPeriod .period-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');nwPeriodMonths=parseInt(b.dataset.months);renderNightWines();});});
document.getElementById('nwMonth').addEventListener('change',renderNightWines);

let foodPeriodMonths=6;
function initFood(){const sel=document.getElementById('foodMonth');if(sel.options.length===0){const iM=Object.keys(D.items||{}).sort();iM.forEach(m=>sel.add(new Option(m,m)));sel.value=iM[iM.length-1];}renderFood();}
function renderFood(){
  const allM=Object.keys(D.items||{}).sort(),showM=foodPeriodMonths===0?allM:allM.slice(-foodPeriodMonths);
  const mF=showM.map(m=>{const its=(D.items[m]||[]).filter(i=>i.c==='Food');return{m,rev:its.reduce((s,i)=>s+i.r,0),qty:its.reduce((s,i)=>s+i.q,0)};});
  const tR=mF.reduce((s,m)=>s+m.rev,0),tQ=mF.reduce((s,m)=>s+m.qty,0);
  document.getElementById('foodKPIs').innerHTML=[kpiCard('Total Rev',fmt(tR),null),kpiCard('Total Qty',fmtN(tQ),null),kpiCard('Avg/Month',fmt(showM.length?tR/showM.length:0),null),kpiCard('Avg Price',fmt2(tQ?tR/tQ:0),null)].join('');
  makeChart('chartFood',{type:'bar',data:{labels:mF.map(m=>m.m),datasets:[{data:mF.map(m=>m.rev),backgroundColor:'rgba(76,175,80,0.7)',borderRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>'$'+(v/1000).toFixed(0)+'k'}},x:{ticks:{maxRotation:45}}}}});
  const selMonth=document.getElementById('foodMonth').value;
  const items=(D.items[selMonth]||[]).filter(i=>i.c==='Food').sort((a,b)=>b.r-a.r);
  document.querySelector('#foodTable tbody').innerHTML=items.map(i=>'<tr><td>'+i.n+'</td><td class="num">'+fmtN(i.q)+'</td><td class="num">'+fmt2(i.r)+'</td><td class="num">'+fmt2(i.q?i.r/i.q:0)+'</td></tr>').join('');
}
document.querySelectorAll('#foodPeriod .period-btn').forEach(b=>{b.addEventListener('click',()=>{document.querySelectorAll('#foodPeriod .period-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');foodPeriodMonths=parseInt(b.dataset.months);renderFood();});});
document.getElementById('foodMonth').addEventListener('change',renderFood);

function initMarket(){const sel=document.getElementById('marketMonth');if(sel.options.length===0){const mD=Object.keys(D.market||{}).sort();const mM=[...new Set(mD.map(d=>d.slice(0,7)))].sort();mM.forEach(m=>sel.add(new Option(m,m)));if(mM.length)sel.value=mM[mM.length-1];}renderMarket();}
function renderMarket(){
  const m=document.getElementById('marketMonth').value;const mDates=Object.keys(D.market||{}).filter(d=>d.startsWith(m)).sort();
  const agg={};mDates.forEach(d=>{(D.market[d]||[]).forEach(i=>{if(!agg[i.n])agg[i.n]={q:0,r:0};agg[i.n].q+=i.q;agg[i.n].r+=(i.net||i.r||0);});});
  const items=Object.entries(agg).map(([n,v])=>({n,q:v.q,r:v.r})).sort((a,b)=>b.r-a.r);
  const tR=items.reduce((s,i)=>s+i.r,0),tQ=items.reduce((s,i)=>s+i.q,0);
  document.getElementById('marketKPIs').innerHTML=[kpiCard('Items',fmtN(items.length),null),kpiCard('Total Qty',fmtN(tQ),null),kpiCard('Total Rev',fmt(tR),null),kpiCard('Days',fmtN(mDates.length),null)].join('');
  const allMD=Object.keys(D.market||{}).sort();const allMM=[...new Set(allMD.map(d=>d.slice(0,7)))].sort().slice(-12);
  const mTrend=allMM.map(mo=>{const ds=allMD.filter(d=>d.startsWith(mo));let rev=0;ds.forEach(d=>(D.market[d]||[]).forEach(i=>rev+=(i.net||i.r||0)));return{m:mo,rev};});
  makeChart('chartMarket',{type:'bar',data:{labels:mTrend.map(m=>m.m),datasets:[{data:mTrend.map(m=>m.rev),backgroundColor:'rgba(171,71,188,0.7)',borderRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>'$'+v}}}}});
  document.querySelector('#marketTable tbody').innerHTML=items.map(i=>'<tr><td>'+i.n+'</td><td class="num">'+fmtN(i.q)+'</td><td class="num">'+fmt2(i.r)+'</td></tr>').join('');
}
document.getElementById('marketMonth').addEventListener('change',renderMarket);

const inits={overview:renderOverview,compare:initCompare,daily:initDaily,items:initItems,nightwines:initNightWines,food:initFood,market:initMarket};
renderOverview();
'''

html = '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
html += '<meta charset="UTF-8">\n'
html += '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">\n'
html += '<title>The Saint - Dashboard</title>\n'
html += '<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.7/chart.umd.min.js"></scr' + 'ipt>\n'
html += '<style>' + CSS + '</style>\n'
html += '</head>\n<body>\n'
html += BODY
html += '<scr' + 'ipt>\n'
html += JS.replace('__DATA__', raw)
html += '\n</scr' + 'ipt>\n'
html += '</body>\n</html>'

with open(OUT, 'w') as f:
    f.write(html)
print(f"Dashboard written to {OUT} ({os.path.getsize(OUT):,} bytes)")
