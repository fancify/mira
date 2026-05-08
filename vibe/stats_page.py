"""Stats dashboard page — GET /stats."""


def render_stats_page() -> str:
    from vibe.topbar import theme_vars_css, topbar_css, topbar_html, settings_overlay_html, topbar_js
    _theme_css = theme_vars_css()
    _tb_css    = topbar_css()
    _tb_html   = topbar_html(title="统计", back_url="javascript:history.back()")
    _overlays  = settings_overlay_html()
    _tb_js     = topbar_js()

    page_css = r"""
  a { color: inherit; text-decoration: none; }

  /* stats controls bar */
  .stats-controls {
    display: flex; align-items: center; gap: 8px; padding: 8px 20px;
    background: var(--panel); border-bottom: 1px solid var(--border);
  }
  .range-toggle, .mode-toggle { display: flex; gap: 4px; }
  .stats-btn { background: none; border: 1px solid var(--border); color: var(--sub);
               border-radius: var(--radius-sm); padding: 4px 12px; font-size: 12px;
               cursor: pointer; font-family: var(--mono); transition: all .15s; }
  .stats-btn.active { background: var(--accent); border-color: var(--accent); color: #fff; }
  .stats-btn.green.active { background: var(--green); border-color: var(--green); color: #fff; }
  .stats-sep { width: 1px; height: 18px; background: var(--border); margin: 0 4px; }

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

  /* trend chart */
  .trend-card { background: var(--panel); border: 1px solid var(--border);
                border-radius: var(--radius); padding: 16px; margin-bottom: 20px; }
  .trend-legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; font-size: 11px; color: var(--sub); }
  .trend-legend-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }

  /* heatmap */
  .heatmap-card { background: var(--panel); border: 1px solid var(--border);
                  border-radius: var(--radius); padding: 16px; margin-bottom: 20px; overflow-x: auto; }
  .heatmap-grid { display: flex; gap: 3px; }
  .heatmap-week { display: flex; flex-direction: column; gap: 3px; }
  .heatmap-day { width: 12px; height: 12px; border-radius: 2px; cursor: default;
                 background: rgba(255,255,255,.05); transition: opacity .1s; }
  .heatmap-day:hover { opacity: .7; }
  .heatmap-labels { display: flex; gap: 3px; margin-top: 4px; font-size: 9px; color: var(--sub); }
  .heatmap-month-label { width: 12px; text-align: center; overflow: visible; white-space: nowrap; }

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
  .rank-cost  { font-size: 11px; color: var(--blue,#4e9eff); text-align: right; }

  /* empty state */
  .empty-state { text-align: center; color: var(--sub); padding: 60px 20px;
                 font-size: 14px; }

  @media (max-width: 640px) {
    .summary-row { grid-template-columns: repeat(2, 1fr); }
    .chart-row   { grid-template-columns: 1fr; }
    .rank-row    { grid-template-columns: 80px 1fr 50px; }
    .rank-cost   { display: none; }
  }
"""

    page_js = r"""
// ── Pricing ────────────────────────────────────────────────────────────
const _CL_PRICE_IN      = 3.0   / 1e6;
const _CL_PRICE_OUT     = 15.0  / 1e6;
const _CL_PRICE_CACHE_W = 3.75  / 1e6;
const _CL_PRICE_CACHE_R = 0.30  / 1e6;

const _CX_PRICE_IN      = 15.0  / 1e6;
const _CX_PRICE_OUT     = 75.0  / 1e6;
const _CX_PRICE_CACHE   = 7.5   / 1e6;
const _CX_PRICE_REASON  = 75.0  / 1e6;

const _TREND_COLORS = ['#5cd08a','#4e9eff','#f0a050','#c792ea','#56b6c2'];

let _currentRange = '30d';
let _currentMode  = 'claude';  // 'claude' | 'codex'

function _esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

document.getElementById('btn-30d').addEventListener('click', function() { setRange('30d'); });
document.getElementById('btn-12w').addEventListener('click', function() { setRange('12w'); });
document.getElementById('btn-mode-claude').addEventListener('click', function() { setMode('claude'); });
document.getElementById('btn-mode-codex').addEventListener('click', function() { setMode('codex'); });

function setRange(r) {
  _currentRange = r;
  document.getElementById('btn-30d').classList.toggle('active', r === '30d');
  document.getElementById('btn-12w').classList.toggle('active', r === '12w');
  if (_currentMode === 'claude') loadClaudeStats();
}

function setMode(m) {
  _currentMode = m;
  document.getElementById('btn-mode-claude').classList.toggle('active', m === 'claude');
  document.getElementById('btn-mode-codex').classList.toggle('active', m === 'codex');
  // Show/hide range toggle for codex (codex has no daily data)
  document.getElementById('range-group').style.display = m === 'claude' ? '' : 'none';
  if (m === 'claude') loadClaudeStats();
  else loadCodexStats();
}

// ── Shared helpers ──────────────────────────────────────────────────────
function _fmtNum(n) {
  if (n >= 1e9) return (n/1e9).toFixed(1) + 'B';
  if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(0) + 'K';
  return String(n || 0);
}

function _clearAll() {
  ['summary-row', 'chart-hours', 'chart-cost', 'trend-svg', 'trend-legend',
   'heatmap-container', 'ranking-list'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.innerHTML = '';
  });
  document.getElementById('trend-card').style.display = 'none';
  document.getElementById('heatmap-card').style.display = 'none';
}

// ── Claude mode ─────────────────────────────────────────────────────────
async function loadClaudeStats() {
  _clearAll();
  document.getElementById('heatmap-card').style.display = '';
  try {
    const res = await fetch('/api/stats?range=' + _currentRange, { headers: _authHeaders() });
    if (res.status === 401) { openLoginModal(loadClaudeStats); return; }
    if (!res.ok) {
      document.getElementById('summary-row').innerHTML =
        '<div class="empty-state">加载失败</div>';
      return;
    }
    const data = await res.json();
    _renderClaudeSummary(data.totals);
    requestAnimationFrame(function() {
      _renderBarChart('chart-hours', data.days,
        function(d) { return d.active_hours; },
        function(v) { return v.toFixed(1) + 'h'; }, '#5cd08a');
      _renderBarChart('chart-cost', data.days,
        function(d) { return d.input_tokens * _CL_PRICE_IN + d.output_tokens * _CL_PRICE_OUT
                           + d.cache_creation_tokens * _CL_PRICE_CACHE_W
                           + d.cache_read_tokens * _CL_PRICE_CACHE_R; },
        function(v) { return '$' + v.toFixed(2); }, '#4e9eff');
      _renderClaudeTrend(data);
      _renderClaudeHeatmap(data.heatmap || {});
    });
    _renderClaudeRanking(data.projects);
  } catch(e) {
    console.warn('claude stats error:', e);
  }
}

function _renderClaudeSummary(t) {
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

function _renderBarChart(svgId, days, valFn, labelFn, color) {
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

function _renderClaudeTrend(data) {
  var el = document.getElementById('trend-svg');
  var legend = document.getElementById('trend-legend');
  if (!el || !data || !data.project_days || !data.days) return;
  document.getElementById('trend-card').style.display = '';

  var W = el.parentElement.clientWidth - 32;
  var H = 120;
  el.setAttribute('viewBox', '0 0 ' + W + ' ' + H);

  var days = data.days.map(function(d) { return d.date; });
  var projectDays = data.project_days;
  var projects = data.projects.slice(0, 5);
  if (!projects.length) { el.innerHTML = ''; return; }

  var maxCost = 0.001;
  projects.forEach(function(p) {
    var pd = projectDays[p.project_id] || {};
    days.forEach(function(d) { maxCost = Math.max(maxCost, pd[d] || 0); });
  });

  var html = '';
  var PAD = 4;
  var usableW = W - PAD * 2;
  var usableH = H - PAD * 2 - 16;

  projects.forEach(function(p, pi) {
    var pd = projectDays[p.project_id] || {};
    var color = _TREND_COLORS[pi % _TREND_COLORS.length];
    var pts = days.map(function(d, i) {
      var cost = pd[d] || 0;
      var x = PAD + (i / Math.max(days.length - 1, 1)) * usableW;
      var y = PAD + usableH - (cost / maxCost) * usableH;
      return x.toFixed(1) + ',' + y.toFixed(1);
    });
    html += '<polyline points="' + pts.join(' ') + '" fill="none" stroke="' + color +
            '" stroke-width="1.5" opacity="0.85"></polyline>';
    days.forEach(function(d, i) {
      var cost = pd[d] || 0;
      if (!cost) return;
      var x = PAD + (i / Math.max(days.length - 1, 1)) * usableW;
      var y = PAD + usableH - (cost / maxCost) * usableH;
      html += '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="2" fill="' + color + '">' +
              '<title>' + _esc(p.project_name || p.project_id) + ' ' + d + ': $' + cost.toFixed(3) + '</title></circle>';
    });
  });

  var lastMonth = '';
  days.forEach(function(d, i) {
    var month = d.slice(5, 7);
    if (month !== lastMonth) {
      lastMonth = month;
      var x = PAD + (i / Math.max(days.length - 1, 1)) * usableW;
      html += '<text x="' + x.toFixed(1) + '" y="' + (H - 2) + '" font-size="9" fill="var(--sub)" text-anchor="middle">' + d.slice(5, 10) + '</text>';
    }
  });

  el.innerHTML = html;
  legend.innerHTML = projects.map(function(p, pi) {
    var color = _TREND_COLORS[pi % _TREND_COLORS.length];
    return '<span><span class="trend-legend-dot" style="background:' + color + '"></span>' +
           _esc(p.project_name || p.project_id) + ' $' + (p.total_cost_usd || 0).toFixed(2) + '</span>';
  }).join('');
}

function _renderClaudeHeatmap(heatmap) {
  var el = document.getElementById('heatmap-container');
  if (!el) return;
  document.getElementById('heatmap-card').style.display = '';

  var today = new Date();
  today.setHours(0, 0, 0, 0);
  var startDate = new Date(today);
  startDate.setDate(startDate.getDate() - 364 - startDate.getDay());

  var maxHours = 0.001;
  Object.values(heatmap).forEach(function(v) { maxHours = Math.max(maxHours, v.hours || 0); });

  var weeks = [];
  var cur = new Date(startDate);
  var monthLabels = [];

  while (cur <= today) {
    var week = [];
    var startOfWeek = new Date(cur);
    for (var dow = 0; dow < 7; dow++) {
      var dateStr = cur.toISOString().slice(0, 10);
      var entry = heatmap[dateStr] || { hours: 0, sessions: 0 };
      var intensity = Math.min(1, (entry.hours || 0) / Math.max(maxHours * 0.8, 0.001));
      week.push({ date: dateStr, hours: entry.hours, sessions: entry.sessions, intensity: intensity, future: cur > today });
      cur.setDate(cur.getDate() + 1);
    }
    var m = startOfWeek.toLocaleString('zh', { month: 'short' });
    monthLabels.push(startOfWeek.getDate() <= 7 ? m : '');
    weeks.push(week);
  }

  function _intensityColor(v) {
    if (v <= 0) return 'rgba(255,255,255,.05)';
    var r = Math.round(92 * v);
    var g = Math.round(208 * (0.3 + 0.7 * v));
    var b = Math.round(138 * v);
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  var gridHtml = weeks.map(function(week) {
    var cells = week.map(function(day) {
      if (day.future) return '<div class="heatmap-day" style="background:transparent"></div>';
      var color = _intensityColor(day.intensity);
      var tip = day.date + ': ' + (day.hours || 0).toFixed(1) + 'h, ' + (day.sessions || 0) + ' sessions';
      return '<div class="heatmap-day" style="background:' + color + '" title="' + tip + '"></div>';
    }).join('');
    return '<div class="heatmap-week">' + cells + '</div>';
  }).join('');

  var labelsHtml = '<div class="heatmap-labels">' +
    monthLabels.map(function(m) {
      return '<div class="heatmap-month-label">' + (m || '') + '</div>';
    }).join('') + '</div>';

  el.innerHTML = '<div class="heatmap-grid">' + gridHtml + '</div>' + labelsHtml;
}

function _renderClaudeRanking(projects) {
  var el = document.getElementById('ranking-list');
  if (!projects || !projects.length) {
    el.innerHTML = '<div class="empty-state" style="padding:20px">暂无数据</div>';
    return;
  }
  var maxH = Math.max.apply(null, projects.map(function(p) { return p.total_hours || 0; }).concat([0.001]));
  el.innerHTML = projects.map(function(p) {
    var pct = ((p.total_hours || 0) / maxH * 100).toFixed(1);
    var name = _esc(p.project_name || p.project_id);
    return '<div class="rank-row">' +
      '<div class="rank-name" title="' + name + '">' + name + '</div>' +
      '<div class="rank-bar-bg"><div class="rank-bar" style="width:' + pct + '%"></div></div>' +
      '<div class="rank-hours">' + (p.total_hours || 0).toFixed(1) + 'h</div>' +
      '<div class="rank-cost">$' + (p.total_cost_usd || 0).toFixed(2) + '</div>' +
      '</div>';
  }).join('');
}

// ── Codex mode ──────────────────────────────────────────────────────────
async function loadCodexStats() {
  _clearAll();
  try {
    const res = await fetch('/api/codex-stats', { headers: _authHeaders() });
    if (res.status === 401) { openLoginModal(loadCodexStats); return; }
    const stats = res.ok ? await res.json() : null;

    if (!stats || !stats.session_count_30d) {
      document.getElementById('summary-row').innerHTML =
        '<div class="empty-state">暂无 Codex 数据</div>';
      return;
    }

    // Summary cards
    var costStr = '$' + (stats.estimated_cost_usd || 0).toFixed(1);
    document.getElementById('summary-row').innerHTML = [
      ['<div class="summary-card"><div class="summary-val" style="color:var(--green)">' + costStr + '</div><div class="summary-lbl">预估费用</div></div>',
       '<div class="summary-card"><div class="summary-val" style="color:var(--green)">' + (stats.session_count_30d||0) + '</div><div class="summary-lbl">30天会话</div></div>',
       '<div class="summary-card"><div class="summary-val" style="color:var(--green)">' + _fmtNum(stats.input_tokens||0) + '</div><div class="summary-lbl">输入 Tokens</div></div>',
       '<div class="summary-card"><div class="summary-val" style="color:var(--green)">' + _fmtNum(stats.output_tokens||0) + '</div><div class="summary-lbl">输出 Tokens</div></div>'
      ].join(''),
    ].join('');

    // Per-project ranking from codex-stats data
    _renderCodexRanking(stats);
    // Heatmap
    requestAnimationFrame(function() {
      _renderCodexHeatmap(stats.heatmap || {});
    });
    // Top 5 trend
    _renderCodexTrend(stats);
  } catch(e) {
    console.warn('codex stats error:', e);
  }
}

function _renderCodexHeatmap(heatmap) {
  var el = document.getElementById('heatmap-container');
  if (!el || !Object.keys(heatmap).length) return;
  document.getElementById('heatmap-card').style.display = '';

  var today = new Date();
  today.setHours(0, 0, 0, 0);
  var startDate = new Date(today);
  startDate.setDate(startDate.getDate() - 364 - startDate.getDay());

  var maxSess = 0.001;
  Object.values(heatmap).forEach(function(v) { maxSess = Math.max(maxSess, v.sessions || 0); });

  var weeks = [];
  var cur = new Date(startDate);
  var monthLabels = [];

  while (cur <= today) {
    var week = [];
    var startOfWeek = new Date(cur);
    for (var dow = 0; dow < 7; dow++) {
      var dateStr = cur.toISOString().slice(0, 10);
      var entry = heatmap[dateStr] || { sessions: 0 };
      var intensity = Math.min(1, (entry.sessions || 0) / Math.max(maxSess * 0.8, 0.001));
      week.push({ date: dateStr, sessions: entry.sessions, intensity: intensity, future: cur > today });
      cur.setDate(cur.getDate() + 1);
    }
    var m = startOfWeek.toLocaleString('zh', { month: 'short' });
    monthLabels.push(startOfWeek.getDate() <= 7 ? m : '');
    weeks.push(week);
  }

  function _intensityColor(v) {
    if (v <= 0) return 'rgba(255,255,255,.05)';
    var r = Math.round(34 * v);
    var g = Math.round(197 * (0.3 + 0.7 * v));
    var b = Math.round(94 * v);
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  var gridHtml = weeks.map(function(week) {
    var cells = week.map(function(day) {
      if (day.future) return '<div class="heatmap-day" style="background:transparent"></div>';
      var color = _intensityColor(day.intensity);
      var tip = day.date + ': ' + (day.sessions || 0) + ' Codex sessions';
      return '<div class="heatmap-day" style="background:' + color + '" title="' + tip + '"></div>';
    }).join('');
    return '<div class="heatmap-week">' + cells + '</div>';
  }).join('');

  var labelsHtml = '<div class="heatmap-labels">' +
    monthLabels.map(function(m) {
      return '<div class="heatmap-month-label">' + (m || '') + '</div>';
    }).join('') + '</div>';

  el.innerHTML = '<div class="heatmap-grid">' + gridHtml + '</div>' + labelsHtml;
}

function _renderCodexTrend(stats) {
  var el = document.getElementById('trend-svg');
  var legend = document.getElementById('trend-legend');
  if (!el) return;
  var topList = stats.project_trend || [];
  if (!topList.length) return;
  document.getElementById('trend-card').style.display = '';

  var W = el.parentElement.clientWidth - 32;
  var H = 120;
  el.setAttribute('viewBox', '0 0 ' + W + ' ' + H);

  var maxCost = Math.max.apply(null, topList.map(function(p) { return p.total_cost_usd; }).concat([0.001]));
  var PAD = 4;
  var usableW = W - PAD * 2;
  var usableH = H - PAD * 2 - 16;
  var html = '';
  var _TREND_COLORS = ['#5cd08a','#4e9eff','#f0a050','#c792ea','#56b6c2','#e06c75','#98c379','#56b6c2'];

  topList.slice(0, 8).forEach(function(p, i) {
    var costShare = p.total_cost_usd;
    var x = PAD + 30;
    var y = PAD + i * 13;
    var barW = Math.max(2, (costShare / maxCost) * (usableW - 30));
    var color = _TREND_COLORS[i % _TREND_COLORS.length];
    var label = (p.project_name || '').toString().slice(0, 14);
    html += '<text x="' + PAD + '" y="' + (y + 9) + '" font-size="10" fill="var(--sub)">' + _esc(label) + '</text>';
    html += '<rect x="' + (PAD + 30) + '" y="' + y + '" width="' + barW.toFixed(1) + '" height="10" fill="' + color + '" rx="2" opacity="0.8">' +
            '<title>' + _esc(p.project_name) + ': $' + costShare.toFixed(2) + '</title></rect>';
  });

  el.innerHTML = html;
  legend.innerHTML = '<span style="font-size:10px;color:var(--sub)">按费用排序</span>';
}

function _renderCodexRanking(stats) {
  var el = document.getElementById('ranking-list');
  var codexProjects = [];

  // Build list from stats.projects (workdir-based breakdown)
  if (stats.projects) {
    Object.keys(stats.projects).forEach(function(name) {
      var p = stats.projects[name];
      var inp = p.input || 0;
      var cached = p.cached || 0;
      var out = p.output || 0;
      var nonCached = Math.max(inp - cached, 0);
      var cost = nonCached * 15/1e6 + cached * 7.5/1e6 + out * 75/1e6;
      codexProjects.push({
        name: name,
        sessions: p.sessions || 0,
        cost: cost,
        input: inp,
        output: out,
      });
    });
  }

  // Add unclassified
  var unc = stats.unclassified;
  if (unc && unc.sessions > 0) {
    var inp = unc.input || 0;
    var cached = unc.cached || 0;
    var out = unc.output || 0;
    var nonCached = Math.max(inp - cached, 0);
    var cost = nonCached * 15/1e6 + cached * 7.5/1e6 + out * 75/1e6;
    codexProjects.push({
      name: '（未归类）',
      sessions: unc.sessions || 0,
      cost: cost,
      input: inp,
      output: out,
    });
  }

  if (!codexProjects.length) {
    el.innerHTML = '<div class="empty-state" style="padding:20px">暂无数据</div>';
    return;
  }

  // Sort by cost descending
  codexProjects.sort(function(a, b) { return b.cost - a.cost; });

  var maxCost = Math.max.apply(null, codexProjects.map(function(p) { return p.cost; }).concat([0.001]));
  el.innerHTML = codexProjects.map(function(p) {
    var pct = (p.cost / maxCost * 100).toFixed(1);
    return '<div class="rank-row">' +
      '<div class="rank-name" title="' + _esc(p.name) + '">' + _esc(p.name) + '</div>' +
      '<div class="rank-bar-bg"><div class="rank-bar" style="width:' + pct + '%;background:var(--green)"></div></div>' +
      '<div class="rank-hours">' + p.sessions + ' 会话</div>' +
      '<div class="rank-cost">$' + p.cost.toFixed(1) + '</div>' +
      '</div>';
  }).join('');

  // Summary bar chart: sessions per project
  var svg = document.getElementById('chart-hours');
  if (svg && codexProjects.length) {
    var W = svg.parentElement.clientWidth - 32;
    var H = 80;
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    var maxSess = Math.max.apply(null, codexProjects.map(function(p) { return p.sessions; }).concat([1]));
    var barW = Math.max(2, (W / codexProjects.length) - 1);
    var html = '';
    codexProjects.forEach(function(p, i) {
      var bh = Math.max(2, (p.sessions / maxSess) * (H - 16));
      var x = i * (W / codexProjects.length);
      html += '<rect x="' + x.toFixed(1) + '" y="' + (H - bh).toFixed(1) +
              '" width="' + barW.toFixed(1) + '" height="' + bh.toFixed(1) +
              '" fill="#4e9eff" opacity="0.75" rx="2">' +
              '<title>' + _esc(p.name) + ': ' + p.sessions + ' 会话</title></rect>';
    });
    svg.innerHTML = html;
  }

  // Cost bar chart
  var svg2 = document.getElementById('chart-cost');
  if (svg2 && codexProjects.length) {
    var W2 = svg2.parentElement.clientWidth - 32;
    var H2 = 80;
    svg2.setAttribute('viewBox', '0 0 ' + W2 + ' ' + H2);
    var maxCost2 = Math.max.apply(null, codexProjects.map(function(p) { return p.cost; }).concat([0.001]));
    var barW2 = Math.max(2, (W2 / codexProjects.length) - 1);
    var html2 = '';
    codexProjects.forEach(function(p, i) {
      var bh2 = Math.max(2, (p.cost / maxCost2) * (H2 - 16));
      var x = i * (W2 / codexProjects.length);
      html2 += '<rect x="' + x.toFixed(1) + '" y="' + (H2 - bh2).toFixed(1) +
               '" width="' + barW2.toFixed(1) + '" height="' + bh2.toFixed(1) +
               '" fill="#22c55e" opacity="0.75" rx="2">' +
               '<title>' + _esc(p.name) + ': $' + p.cost.toFixed(2) + '</title></rect>';
    });
    svg2.innerHTML = html2;
  }
}

// ── Init ────────────────────────────────────────────────────────────────
_initAuth().then(function() {
  setMode('claude');
});
"""

    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>开发统计 · Mira</title>\n"
        "<script>document.documentElement.dataset.theme = localStorage.getItem('mira-skin') || 'default';</script>\n"
        '<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">\n'
        '<link rel="stylesheet" href="/static/fonts/fonts.css">\n'
        "<style>\n"
        + _theme_css
        + _tb_css
        + page_css
        + "</style>\n</head>\n<body>\n\n"
        + _tb_html + "\n\n"
        + """\
<div class="stats-controls">
  <div class="range-toggle" id="range-group">
    <button class="stats-btn active" id="btn-30d">日 · 30天</button>
    <button class="stats-btn"        id="btn-12w">周 · 12周</button>
  </div>
  <div class="stats-sep"></div>
  <div class="mode-toggle">
    <button class="stats-btn active" id="btn-mode-claude">Claude</button>
    <button class="stats-btn"        id="btn-mode-codex">Codex</button>
  </div>
</div>

<div class="stats-main">
  <div id="summary-row" class="summary-row"></div>

  <div class="chart-row">
    <div class="chart-card">
      <div class="chart-title">会话数 / 项目</div>
      <svg id="chart-hours" class="chart-svg" height="80"></svg>
    </div>
    <div class="chart-card">
      <div class="chart-title">费用 / 项目</div>
      <svg id="chart-cost" class="chart-svg" height="80"></svg>
    </div>
  </div>

  <div class="trend-card" id="trend-card" style="display:none">
    <div class="chart-title">Top 5 项目费用趋势</div>
    <svg id="trend-svg" class="chart-svg" height="120"></svg>
    <div class="trend-legend" id="trend-legend"></div>
  </div>

  <div class="heatmap-card" id="heatmap-card" style="display:none">
    <div class="chart-title" style="margin-bottom:8px">活动热力图（近一年）</div>
    <div id="heatmap-container" style="min-height:80px"></div>
  </div>

  <div class="ranking-card">
    <div class="ranking-title">项目排行</div>
    <div id="ranking-list"></div>
  </div>
</div>

"""
        + _overlays + "\n\n"
        + "<script>\n"
        + _tb_js + "\n"
        + page_js
        + "</script>\n</body>\n</html>\n"
    )
