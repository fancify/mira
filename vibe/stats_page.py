"""Stats dashboard page — GET /stats."""


def render_stats_page() -> str:
    return '''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>开发统计 · Mira</title>
<script>document.documentElement.dataset.theme = localStorage.getItem('mira-skin') || 'default';</script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #080c14; --panel: rgba(14,20,36,.95); --border: rgba(255,255,255,.07);
    --text: #eef1f7; --sub: #7a8499; --muted: #4a5060;
    --accent: #4f46e5;
    --green: #5cd08a; --blue: #4e9eff; --gold: #d9b36b; --red: #e06c75;
    --mono: 'JetBrains Mono', monospace; --sans: 'Noto Sans SC', sans-serif;
    --radius: 8px;
  }
  [data-theme="neon-pixel"] {
    --bg: #0a0a0a; --panel: rgba(20,20,20,.95); --border: #00ff00;
    --text: #e0e0ff; --sub: #a0a0cc; --muted: #505070; --accent: #ff00ff;
    --green: #00ff00; --blue: #00ffff; --gold: #ffff00;
    --radius: 0px;
  }
  [data-theme="pixel-cyber"] {
    --bg: #020c1a; --panel: rgba(10,31,56,.95); --border: #00d4ff;
    --text: #eef8ff; --sub: #a8daf0; --muted: #6bbad8; --accent: #ff0055;
    --green: #00ff88; --blue: #00d4ff; --gold: #ffaa00;
    --radius: 0px;
  }
  body { background: var(--bg); color: var(--text); font-family: var(--mono);
         min-height: 100vh; padding: 0; }
  a { color: inherit; text-decoration: none; }

  /* topbar */
  .topbar { display: flex; align-items: center; gap: 10px; padding: 0 20px;
            height: 52px; background: var(--panel); border-bottom: 1px solid var(--border);
            position: sticky; top: 0; z-index: 100; }
  .topbar-title { font-size: 18px; font-weight: 700; color: var(--accent); }
  .topbar-spacer { flex: 1; }
  .back-btn { background: none; border: 1px solid var(--border); color: var(--sub);
              border-radius: var(--radius); padding: 4px 12px; font-size: 13px;
              cursor: pointer; font-family: var(--mono); }
  .back-btn:hover { border-color: var(--accent); color: var(--accent); }
  .range-toggle { display: flex; gap: 4px; }
  .range-btn { background: none; border: 1px solid var(--border); color: var(--sub);
               border-radius: var(--radius); padding: 4px 12px; font-size: 12px;
               cursor: pointer; font-family: var(--mono); transition: all .15s; }
  .range-btn.active { background: var(--accent); border-color: var(--accent);
                      color: #fff; }

  /* main layout */
  .stats-main { max-width: 960px; margin: 0 auto; padding: 24px 20px 60px; }

  /* summary cards */
  .summary-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
                 margin-bottom: 20px; }
  .summary-card { background: var(--panel); border: 1px solid var(--border);
                  border-radius: var(--radius); padding: 16px; text-align: center; }
  .summary-val { font-size: 24px; font-weight: 700; color: var(--text);
                 margin-bottom: 4px; }
  .summary-lbl { font-size: 11px; color: var(--sub); }

  /* chart row */
  .chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
               margin-bottom: 20px; }
  .chart-card { background: var(--panel); border: 1px solid var(--border);
                border-radius: var(--radius); padding: 16px; }
  .chart-title { font-size: 12px; color: var(--text); font-weight: 600;
                 margin-bottom: 12px; }
  .chart-svg { width: 100%; overflow: visible; }

  /* project ranking */
  .ranking-card { background: var(--panel); border: 1px solid var(--border);
                  border-radius: var(--radius); padding: 16px; }
  .ranking-title { font-size: 12px; color: var(--text); font-weight: 600;
                   margin-bottom: 12px; }
  .rank-row { display: grid; grid-template-columns: 110px 1fr 60px 60px;
              align-items: center; gap: 10px; margin-bottom: 10px; }
  .rank-name { font-size: 12px; color: var(--text); overflow: hidden;
               text-overflow: ellipsis; white-space: nowrap; }
  .rank-bar-bg { background: rgba(255,255,255,.06); border-radius: 3px; height: 8px; }
  .rank-bar { background: var(--green); border-radius: 3px; height: 8px;
              transition: width .3s; }
  .rank-hours { font-size: 11px; color: var(--sub); text-align: right; }
  .rank-cost  { font-size: 11px; color: var(--blue); text-align: right; }

  /* empty state */
  .empty-state { text-align: center; color: var(--sub); padding: 60px 20px;
                 font-size: 14px; }

  @media (max-width: 640px) {
    .summary-row { grid-template-columns: repeat(2, 1fr); }
    .chart-row   { grid-template-columns: 1fr; }
    .rank-row    { grid-template-columns: 80px 1fr 50px; }
    .rank-cost   { display: none; }
  }
</style>
</head>
<body>

<div class="topbar">
  <span class="topbar-title">&#128202; 开发统计</span>
  <div class="topbar-spacer"></div>
  <div class="range-toggle">
    <button class="range-btn active" id="btn-30d">日 · 30天</button>
    <button class="range-btn"        id="btn-12w">周 · 12周</button>
  </div>
  <button class="back-btn" onclick="location.href=\'/'">← 返回</button>
</div>

<div class="stats-main">
  <div id="summary-row" class="summary-row"></div>
  <div class="chart-row">
    <div class="chart-card">
      <div class="chart-title">活跃时长</div>
      <svg id="chart-hours" class="chart-svg" height="80"></svg>
    </div>
    <div class="chart-card">
      <div class="chart-title">Token 花费（USD）</div>
      <svg id="chart-cost" class="chart-svg" height="80"></svg>
    </div>
  </div>
  <div class="ranking-card">
    <div class="ranking-title">项目活跃度排行</div>
    <div id="ranking-list"></div>
  </div>
</div>

<script>
const _PRICE_IN  = 3.0  / 1e6;
const _PRICE_OUT = 15.0 / 1e6;

let _adminToken = localStorage.getItem('mira-admin-token') || '';
let _currentRange = '30d';

function _authHeaders() {
  return _adminToken ? { 'Authorization': 'Bearer ' + _adminToken } : {};
}

document.getElementById('btn-30d').addEventListener('click', function() { setRange('30d'); });
document.getElementById('btn-12w').addEventListener('click', function() { setRange('12w'); });

function setRange(r) {
  _currentRange = r;
  document.getElementById('btn-30d').classList.toggle('active', r === '30d');
  document.getElementById('btn-12w').classList.toggle('active', r === '12w');
  loadStats();
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats?range=' + _currentRange,
      { headers: _authHeaders() });
    if (res.status === 401) {
      const tok = prompt('请输入管理员密码：');
      if (!tok) return;
      _adminToken = tok;
      localStorage.setItem('mira-admin-token', tok);
      return loadStats();
    }
    if (!res.ok) {
      document.getElementById('summary-row').innerHTML =
        '<div class="empty-state">加载失败，请刷新重试</div>';
      return;
    }
    const data = await res.json();
    renderSummary(data.totals);
    renderBarChart('chart-hours', data.days, function(d) { return d.active_hours; },
                   function(v) { return v.toFixed(1) + 'h'; }, '#5cd08a');
    renderBarChart('chart-cost',  data.days,
                   function(d) { return d.input_tokens * _PRICE_IN + d.output_tokens * _PRICE_OUT; },
                   function(v) { return '$' + v.toFixed(2); }, '#4e9eff');
    renderRanking(data.projects);
  } catch(e) {
    console.warn('stats load error:', e);
  }
}

function renderSummary(t) {
  if (!t) return;
  var cards = [
    [(t.active_hours != null ? t.active_hours.toFixed(1) : '0.0') + 'h', '活跃时长'],
    ['$' + (t.estimated_cost_usd != null ? t.estimated_cost_usd.toFixed(2) : '0.00'), 'Token 花费'],
    [t.sessions != null ? t.sessions : 0, '会话数'],
    [_fmtNum(t.output_tokens != null ? t.output_tokens : 0), '输出 Tokens'],
  ];
  document.getElementById('summary-row').innerHTML = cards.map(function(pair) {
    return '<div class="summary-card"><div class="summary-val">' + pair[0] + '</div>' +
           '<div class="summary-lbl">' + pair[1] + '</div></div>';
  }).join('');
}

function _fmtNum(n) {
  if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(0) + 'K';
  return String(n);
}

function renderBarChart(svgId, days, valFn, labelFn, color) {
  var svg = document.getElementById(svgId);
  if (!svg || !days || !days.length) return;
  var W = svg.parentElement.clientWidth - 32;
  var H = 80;
  svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
  var vals = days.map(valFn);
  var maxVal = Math.max.apply(null, vals.concat([0.001]));
  var barW = Math.max(2, (W / days.length) - 1);
  var html = '';
  days.forEach(function(d, i) {
    var v = vals[i];
    var bh = Math.max(2, (v / maxVal) * (H - 16));
    var x = i * (W / days.length);
    var y = H - bh;
    var label = d.date.slice(5);
    html += '<rect x="' + x.toFixed(1) + '" y="' + y.toFixed(1) +
            '" width="' + barW.toFixed(1) + '" height="' + bh.toFixed(1) +
            '" fill="' + color + '" opacity="0.75" rx="2">' +
            '<title>' + label + ': ' + labelFn(v) + '</title></rect>';
  });
  svg.innerHTML = html;
}

function renderRanking(projects) {
  var el = document.getElementById('ranking-list');
  if (!projects || !projects.length) {
    el.innerHTML = '<div class="empty-state" style="padding:20px">暂无数据</div>';
    return;
  }
  var maxH = Math.max.apply(null, projects.map(function(p) { return p.total_hours || 0; }).concat([0.001]));
  el.innerHTML = projects.map(function(p) {
    var pct = ((p.total_hours || 0) / maxH * 100).toFixed(1);
    var name = p.project_name || p.project_id;
    return '<div class="rank-row">' +
      '<div class="rank-name" title="' + name + '">' + name + '</div>' +
      '<div class="rank-bar-bg"><div class="rank-bar" style="width:' + pct + '%"></div></div>' +
      '<div class="rank-hours">' + (p.total_hours || 0).toFixed(1) + 'h</div>' +
      '<div class="rank-cost">$' + (p.total_cost_usd || 0).toFixed(2) + '</div>' +
      '</div>';
  }).join('');
}

loadStats();
</script>
</body>
</html>'''
