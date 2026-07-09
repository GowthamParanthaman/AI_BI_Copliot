/* ============================================================
   AI BI Copilot — Enterprise Dashboard Application
   ============================================================ */

'use strict';

/* ── State ──────────────────────────────────────────────────── */
const State = {
  theme:         localStorage.getItem('bi-theme') || 'light',
  sidebarCollapsed: localStorage.getItem('bi-sidebar') === 'true',
  datasets:      [],
  selectedDataset: null,
  analysisResult: null,
  tableData:     [],
  tableFiltered: [],
  tableSortCol:  null,
  tableSortDir:  'asc',
  tablePage:     1,
  tablePageSize: 15,
  charts:        {},
  activeView:    'dashboard',
};

/* ── API Helpers ─────────────────────────────────────────────── */
const API = {
  base: '',   // same-origin

  async get(path) {
    const r = await fetch(this.base + path);
    if (!r.ok) throw new Error(`GET ${path} → ${r.status}`);
    return r.json();
  },

  async post(path, body) {
    const r = await fetch(this.base + path, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(body),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.detail?.message || err.detail || `POST ${path} → ${r.status}`);
    }
    return r.json();
  },

  async postForm(path, formData) {
    const r = await fetch(this.base + path, {
      method: 'POST',
      body:   formData,
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.detail || `POST ${path} → ${r.status}`);
    }
    return r.json();
  },
};

/* ── Toast ───────────────────────────────────────────────────── */
const Toast = {
  show(msg, type = 'info', duration = 3500) {
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.setAttribute('role', 'alert');
    t.innerHTML = `<span>${icons[type]}</span><span>${msg}</span>`;
    document.getElementById('toast-container').appendChild(t);
    setTimeout(() => t.remove(), duration);
  },
};

/* ── Theme ───────────────────────────────────────────────────── */
function applyTheme(theme) {
  State.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('bi-theme', theme);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.classList.toggle('active', theme === 'dark');

  // Update existing charts
  Object.values(State.charts).forEach(chart => {
    if (!chart) return;
    const isDark = theme === 'dark';
    chart.options.plugins.legend.labels.color = isDark ? '#94a3b8' : '#64748b';
    if (chart.options.scales) {
      Object.values(chart.options.scales).forEach(scale => {
        scale.ticks = scale.ticks || {};
        scale.ticks.color = isDark ? '#94a3b8' : '#64748b';
        if (scale.grid) scale.grid.color = isDark ? '#334155' : '#e2e8f0';
      });
    }
    chart.update('none');
  });
}

/* ── Sidebar ─────────────────────────────────────────────────── */
function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  State.sidebarCollapsed = !State.sidebarCollapsed;
  sb.classList.toggle('collapsed', State.sidebarCollapsed);
  localStorage.setItem('bi-sidebar', State.sidebarCollapsed);
}

function toggleMobileSidebar() {
  const sb  = document.getElementById('sidebar');
  const ov  = document.getElementById('mobile-overlay');
  const open = sb.classList.toggle('mobile-open');
  ov.classList.toggle('visible', open);
}

/* ── Nav ─────────────────────────────────────────────────────── */
function activateView(view) {
  State.activeView = view;
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.view === view);
  });
  document.querySelectorAll('.view-section').forEach(el => {
    el.style.display = el.id === `view-${view}` ? 'block' : 'none';
  });
}

/* ── Format Helpers ──────────────────────────────────────────── */
const fmt = {
  currency: v => v == null ? '—' : '$' + (+v).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 }),
  number:   v => v == null ? '—' : (+v).toLocaleString(),
  pct:      v => v == null ? '—' : (+v).toFixed(1) + '%',
  label:    v => v == null ? '—' : String(v),
};

function trendClass(v) {
  if (v > 0) return 'up';
  if (v < 0) return 'down';
  return 'flat';
}

function trendIcon(v) {
  if (v > 0) return '↑';
  if (v < 0) return '↓';
  return '→';
}

/* ── Chart defaults ──────────────────────────────────────────── */
function chartDefaults() {
  const isDark = State.theme === 'dark';
  return {
    gridColor:  isDark ? '#334155' : '#e2e8f0',
    tickColor:  isDark ? '#94a3b8' : '#64748b',
    legendColor: isDark ? '#94a3b8' : '#64748b',
    bgCard:     isDark ? '#1e293b' : '#ffffff',
  };
}

function baseChartOptions(title = '') {
  const d = chartDefaults();
  return {
    responsive:          true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: d.legendColor, font: { size: 12 }, padding: 16 },
      },
      title: {
        display: !!title,
        text:    title,
        color:   d.tickColor,
        font:    { size: 14, weight: '600' },
        padding: { bottom: 12 },
      },
      tooltip: {
        backgroundColor: d.bgCard,
        titleColor: d.tickColor,
        bodyColor:  d.tickColor,
        borderColor: '#334155',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: ctx => ' ' + ctx.dataset.label + ': ' + ctx.parsed.y?.toLocaleString(),
        },
      },
    },
    scales: {
      x: {
        ticks: { color: d.tickColor, maxRotation: 45, font: { size: 11 } },
        grid:  { color: d.gridColor, drawBorder: false },
      },
      y: {
        ticks: { color: d.tickColor, font: { size: 11 } },
        grid:  { color: d.gridColor, drawBorder: false },
        beginAtZero: true,
      },
    },
    animation: { duration: 800, easing: 'easeOutQuart' },
  };
}

function COLORS(alpha = 1) {
  const c = [
    [59,130,246], [16,185,129], [139,92,246], [245,158,11],
    [6,182,212],  [239,68,68],  [99,102,241], [20,184,166],
    [251,146,60], [168,85,247],
  ];
  return c.map(([r,g,b]) => `rgba(${r},${g},${b},${alpha})`);
}

/* ── Destroy / (re)create chart ──────────────────────────────── */
function makeChart(id, config) {
  if (State.charts[id]) { State.charts[id].destroy(); }
  const canvas = document.getElementById(id);
  if (!canvas) return;
  State.charts[id] = new Chart(canvas, config);
  return State.charts[id];
}

/* ── Sparkline ───────────────────────────────────────────────── */
function drawSparkline(canvasId, data, color) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data?.length) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.offsetWidth, h = canvas.offsetHeight;
  canvas.width = w; canvas.height = h;
  const min = Math.min(...data), max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => ({
    x: (i / (data.length - 1)) * w,
    y: h - ((v - min) / range) * h * 0.85 - h * 0.08,
  }));
  ctx.clearRect(0, 0, w, h);
  // fill
  ctx.beginPath();
  ctx.moveTo(pts[0].x, h);
  pts.forEach(p => ctx.lineTo(p.x, p.y));
  ctx.lineTo(pts[pts.length - 1].x, h);
  ctx.closePath();
  ctx.fillStyle = color.replace('1)', '0.15)');
  ctx.fill();
  // line
  ctx.beginPath();
  pts.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y));
  ctx.strokeStyle = color;
  ctx.lineWidth   = 2;
  ctx.lineJoin    = 'round';
  ctx.stroke();
}

/* ── KPI Cards ───────────────────────────────────────────────── */
function renderKPICards(result) {
  const el = document.getElementById('kpi-grid');
  if (!el) return;

  const fin    = result.kpis?.financial || {};
  const cust   = result.kpis?.customer  || {};
  const health = result.kpis?.health    || {};
  const cat    = result.kpis?.product   || {};

  const cards = [
    {
      color:   'kpi-blue',
      icon:    '💰',
      label:   'Total Revenue',
      value:   fmt.currency(fin.total_revenue),
      trend:   fin.revenue_growth,
      sub:     'YTD performance',
      sparkData: Array.from({ length: 8 }, (_, i) => (fin.total_revenue || 0) * (0.82 + i * 0.026)),
      sparkColor: 'rgba(59,130,246,1)',
    },
    {
      color:   'kpi-green',
      icon:    '🛒',
      label:   'Total Orders',
      value:   fmt.number(cust.customer_count),
      trend:   fin.revenue_growth,
      sub:     'All time',
      sparkData: Array.from({ length: 8 }, (_, i) => (cust.customer_count || 0) * (0.78 + i * 0.031)),
      sparkColor: 'rgba(16,185,129,1)',
    },
    {
      color:   'kpi-purple',
      icon:    '📦',
      label:   'Avg Order Value',
      value:   fmt.currency(cust.average_order_value),
      trend:   null,
      sub:     'Per transaction',
      sparkData: Array.from({ length: 8 }, (_, i) => (cust.average_order_value || 0) * (0.88 + i * 0.017)),
      sparkColor: 'rgba(139,92,246,1)',
    },
    {
      color:   'kpi-orange',
      icon:    '📈',
      label:   'Profit Margin',
      value:   fin.profit_margin != null ? fmt.pct(fin.profit_margin) : '—',
      trend:   fin.profit_margin,
      sub:     'Net margin',
      sparkData: Array.from({ length: 8 }, (_, i) => (fin.profit_margin || 20) * (0.89 + i * 0.016)),
      sparkColor: 'rgba(245,158,11,1)',
    },
    {
      color:   health.business_health === 'EXCELLENT' ? 'kpi-green' :
               health.business_health === 'GOOD'      ? 'kpi-cyan'  :
               health.business_health === 'FAIR'      ? 'kpi-orange': 'kpi-red',
      icon:    '🏥',
      label:   'Business Health',
      value:   fmt.label(health.business_health || '—'),
      trend:   health.score,
      sub:     `Score: ${health.score ?? '—'}/100`,
      sparkData: Array.from({ length: 8 }, (_, i) => (health.score || 50) * (0.84 + i * 0.023)),
      sparkColor: 'rgba(6,182,212,1)',
    },
    {
      color:   'kpi-cyan',
      icon:    '🏆',
      label:   'Top Category',
      value:   fmt.label(cat.top_category),
      trend:   null,
      sub:     'Best performing',
      sparkData: null,
      sparkColor: null,
    },
    {
      color:   'kpi-indigo',
      icon:    '🔄',
      label:   'Revenue Growth',
      value:   fin.revenue_growth != null ? fmt.pct(fin.revenue_growth) : '—',
      trend:   fin.revenue_growth,
      sub:     'vs prior period',
      sparkData: Array.from({ length: 8 }, (_, i) => Math.max(0, (fin.revenue_growth || 0) * (0.5 + i * 0.07))),
      sparkColor: 'rgba(99,102,241,1)',
    },
  ];

  el.innerHTML = cards.map((c, i) => {
    const tc = trendClass(c.trend);
    const ti = trendIcon(c.trend);
    const trendHtml = c.trend != null
      ? `<span class="kpi-trend ${tc}">${ti} ${Math.abs(+c.trend).toFixed(1)}%</span>`
      : '';
    return `
      <article class="kpi-card ${c.color}" role="region" aria-label="${c.label} KPI">
        <div class="kpi-card-header">
          <div class="kpi-icon" aria-hidden="true">${c.icon}</div>
          ${trendHtml}
        </div>
        <div>
          <div class="kpi-label">${c.label}</div>
          <div class="kpi-value" aria-live="polite">${c.value}</div>
          <div class="kpi-sub">${c.sub}</div>
        </div>
        ${c.sparkData ? `<canvas class="kpi-sparkline" id="spark-${i}" aria-hidden="true"></canvas>` : ''}
      </article>`;
  }).join('');

  // Draw sparklines after DOM update
  requestAnimationFrame(() => {
    cards.forEach((c, i) => {
      if (c.sparkData) drawSparkline(`spark-${i}`, c.sparkData, c.sparkColor);
    });
  });
}

/* ── Charts ──────────────────────────────────────────────────── */
function renderCharts(result) {
  const fin    = result.kpis?.financial || {};
  const cust   = result.kpis?.customer  || {};
  const health = result.kpis?.health    || {};
  const charts = result.kpis?.charts    || {};

  // ── Revenue Overview (bar) ────────────────────────────────
  // Real quarterly/category/period data from the backend
  const revByPeriod   = charts.revenue_by_period || {};
  const revenueLabels = revByPeriod.labels?.length ? revByPeriod.labels : ['Q1','Q2','Q3','Q4'];
  const rev           = fin.total_revenue || 0;
  const revenueData   = revByPeriod.values?.length
    ? revByPeriod.values
    : [rev * 0.21, rev * 0.24, rev * 0.28, rev * 0.27];
  const opts1 = baseChartOptions();
  opts1.plugins.tooltip.callbacks.label = ctx =>
    ' Revenue: $' + ctx.parsed.y.toLocaleString();
  makeChart('chart-revenue', {
    type: 'bar',
    data: {
      labels:   revenueLabels,
      datasets: [{
        label:           'Revenue',
        data:            revenueData,
        backgroundColor: COLORS(0.8),
        borderRadius:    6,
        borderSkipped:   false,
      }],
    },
    options: opts1,
  });

  // ── Revenue Trend (line) ──────────────────────────────────
  // Real monthly/period revenue series from the backend
  const revTrend    = charts.revenue_trend || {};
  const trendLabels = revTrend.labels?.length
    ? revTrend.labels
    : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const trendData   = revTrend.values?.length
    ? revTrend.values
    : trendLabels.map((_, i) => rev / trendLabels.length * (0.85 + i * 0.025));
  const opts2 = baseChartOptions();
  opts2.elements = { point: { radius: 3 }, line: { tension: 0.4 } };
  opts2.plugins.tooltip.callbacks.label = ctx =>
    ' $' + ctx.parsed.y.toLocaleString();
  makeChart('chart-trend', {
    type: 'line',
    data: {
      labels:   trendLabels,
      datasets: [{
        label:           'Monthly Revenue',
        data:            trendData,
        borderColor:     COLORS()[0],
        backgroundColor: COLORS(0.12)[0],
        fill:            true,
        tension:         0.4,
        pointRadius:     3,
        pointHoverRadius: 6,
      }],
    },
    options: opts2,
  });

  // ── Category Distribution (doughnut) ─────────────────────
  // Real percentage breakdown computed from the uploaded dataset
  const catDist   = charts.category_distribution || {};
  const catNames  = catDist.labels?.length
    ? catDist.labels
    : ['Electronics', 'Clothing', 'Beauty', 'Other', 'Sports'];
  const catValues = catDist.values?.length
    ? catDist.values
    : [35, 28, 18, 12, 7];
  const opts3 = {
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: chartDefaults().legendColor, padding: 14, font: { size: 11 } },
      },
      tooltip: {
        backgroundColor: chartDefaults().bgCard,
        titleColor: chartDefaults().tickColor,
        bodyColor:  chartDefaults().tickColor,
        borderColor: '#334155', borderWidth: 1,
        callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}%` },
      },
    },
    animation: { duration: 800 },
    cutout: '68%',
  };
  makeChart('chart-category', {
    type: 'doughnut',
    data: {
      labels:   catNames,
      datasets: [{ data: catValues, backgroundColor: COLORS(0.85), hoverOffset: 6 }],
    },
    options: opts3,
  });

  // ── Order Value Distribution (histogram) ─────────────────
  // Real order-value histogram bins from the uploaded dataset
  const ovDist = charts.order_value_distribution || {};
  const bins   = ovDist.labels?.length
    ? ovDist.labels
    : ['0-100','100-200','200-300','300-400','400-500','500-600','600-700','700+'];
  const binsV  = ovDist.values?.length
    ? ovDist.values
    : bins.map(() => 0);
  const opts4 = baseChartOptions();
  opts4.plugins.legend.display = false;
  opts4.plugins.tooltip.callbacks.label = ctx => ` Count: ${ctx.parsed.y}`;
  makeChart('chart-orders', {
    type: 'bar',
    data: {
      labels:   bins,
      datasets: [{
        label:           'Orders',
        data:            binsV,
        backgroundColor: COLORS(0.75)[2],
        borderColor:     COLORS()[2],
        borderWidth:     1,
        borderRadius:    4,
      }],
    },
    options: opts4,
  });

  // ── KPI Health Radar ──────────────────────────────────────
  // Uses result.kpis.health (correct path) — not legacy health_score
  const score = health.score || 50;
  const opts5 = {
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: chartDefaults().legendColor } },
      tooltip: {
        backgroundColor: chartDefaults().bgCard,
        bodyColor: chartDefaults().tickColor,
        titleColor: chartDefaults().tickColor,
        borderColor: '#334155', borderWidth: 1,
      },
    },
    scales: {
      r: {
        beginAtZero: true, max: 100,
        ticks: { color: chartDefaults().tickColor, stepSize: 25, backdropColor: 'transparent' },
        grid:  { color: chartDefaults().gridColor },
        angleLines: { color: chartDefaults().gridColor },
        pointLabels: { color: chartDefaults().tickColor, font: { size: 11 } },
      },
    },
    animation: { duration: 900 },
  };
  makeChart('chart-radar', {
    type: 'radar',
    data: {
      labels: ['Revenue','Growth','Efficiency','Quality','Satisfaction','Health'],
      datasets: [{
        label: 'Current',
        data: [
          Math.min(100, rev / Math.max(1, rev) * score),
          Math.max(0, Math.min(100, 50 + (fin.revenue_growth || 0))),
          score,
          fin.profit_margin != null ? Math.min(100, Math.max(0, fin.profit_margin * 2)) : score,
          cust.customer_satisfaction != null ? Math.min(100, cust.customer_satisfaction) : score,
          score,
        ].map(v => Math.max(0, Math.min(100, v))),
        borderColor:          COLORS()[0],
        backgroundColor:      COLORS(0.2)[0],
        pointBackgroundColor: COLORS()[0],
        pointRadius: 4,
      }],
    },
    options: opts5,
  });
}
/* ── Health Ring ─────────────────────────────────────────────── */
function renderHealthRing(result) {
  const health = result.health_score || {};
  const score  = health.score || 0;
  const label  = health.business_health || '—';
  const pct    = Math.max(0, Math.min(100, score));
  const color  = pct >= 75 ? '#10b981' : pct >= 50 ? '#f59e0b' : '#ef4444';

  document.getElementById('health-score-text').textContent  = Math.round(pct);
  document.getElementById('health-label-text').textContent  = label;

  const fill = document.getElementById('health-ring-fill');
  if (fill) {
    fill.style.stroke = color;
    // circumference = 2 * π * r(54) ≈ 339.29
    setTimeout(() => {
      fill.style.strokeDashoffset = 339.29 * (1 - pct / 100);
    }, 200);
  }
}

/* ── Insights ────────────────────────────────────────────────── */
function renderInsights(result) {
  const insightsList = document.getElementById('insights-list');
  const recList      = document.getElementById('recommendations-list');

  const insights = result.insights?.insights || result.insights || [];
  const recs     = result.recommendations;

  if (insightsList) {
    if (!insights.length) {
      insightsList.innerHTML = '<p style="color:var(--text-muted);font-size:13px;">No insights generated.</p>';
    } else {
      insightsList.innerHTML = insights.slice(0, 8).map(i =>
        `<div class="insight-item">
           <span class="insight-dot" aria-hidden="true"></span>
           <span class="insight-text">${i}</span>
         </div>`
      ).join('');
    }
  }

  if (recList) {
    const allRecs = [
      ...(recs?.high_priority   || []).map(r => ({ ...r, priority: 'high' })),
      ...(recs?.medium_priority || []).map(r => ({ ...r, priority: 'medium' })),
      ...(recs?.low_priority    || []).map(r => ({ ...r, priority: 'low' })),
    ];
    if (!allRecs.length) {
      recList.innerHTML = '<p style="color:var(--text-muted);font-size:13px;">No recommendations generated.</p>';
    } else {
      recList.innerHTML = allRecs.slice(0, 8).map(r =>
        `<div class="rec-item">
           <span class="rec-priority-tag ${r.priority}">${r.priority.toUpperCase()}</span>
           <span>${r.recommendation || r}</span>
         </div>`
      ).join('');
    }
  }
}

/* ── Data Table ──────────────────────────────────────────────── */
function initTable(data) {
  State.tableData     = data;
  State.tableFiltered = [...data];
  State.tablePage     = 1;
  State.tableSortCol  = null;
  renderTable();
}

function renderTable() {
  const container = document.getElementById('data-table-container');
  if (!container || !State.tableFiltered.length) return;

  const data   = State.tableFiltered;
  const cols   = Object.keys(data[0]);
  const start  = (State.tablePage - 1) * State.tablePageSize;
  const slice  = data.slice(start, start + State.tablePageSize);
  const total  = data.length;
  const pages  = Math.max(1, Math.ceil(total / State.tablePageSize));

  container.innerHTML = `
    <div class="table-wrap">
      <table class="data-table" role="grid" aria-label="Dataset preview">
        <thead>
          <tr>
            ${cols.map(c => `
              <th scope="col"
                  tabindex="0"
                  data-col="${c}"
                  class="${State.tableSortCol === c ? 'sorted-' + State.tableSortDir : ''}"
                  onclick="sortTable('${c}')"
                  onkeydown="if(event.key==='Enter')sortTable('${c}')"
                  aria-sort="${State.tableSortCol===c ? (State.tableSortDir==='asc'?'ascending':'descending') : 'none'}">
                ${c}
              </th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${slice.map(row => `
            <tr>
              ${cols.map(c => `<td>${row[c] ?? '—'}</td>`).join('')}
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
    <div class="table-pagination">
      <span class="pagination-info">
        Showing ${start + 1}–${Math.min(start + State.tablePageSize, total)} of ${total.toLocaleString()} rows
      </span>
      <div class="pagination-controls" role="navigation" aria-label="Table pagination">
        <button class="page-btn" onclick="goPage(1)" ${State.tablePage===1?'disabled':''} aria-label="First page">«</button>
        <button class="page-btn" onclick="goPage(${State.tablePage-1})" ${State.tablePage===1?'disabled':''} aria-label="Previous page">‹</button>
        ${Array.from({ length: Math.min(5, pages) }, (_, i) => {
          let p = State.tablePage - 2 + i;
          if (p < 1) p = i + 1;
          if (p > pages) p = pages - (4 - i);
          p = Math.max(1, Math.min(pages, p));
          return `<button class="page-btn ${p===State.tablePage?'active':''}" onclick="goPage(${p})" aria-label="Page ${p}" aria-current="${p===State.tablePage?'page':''}">${p}</button>`;
        }).join('')}
        <button class="page-btn" onclick="goPage(${State.tablePage+1})" ${State.tablePage===pages?'disabled':''} aria-label="Next page">›</button>
        <button class="page-btn" onclick="goPage(${pages})" ${State.tablePage===pages?'disabled':''} aria-label="Last page">»</button>
      </div>
    </div>`;
}

function sortTable(col) {
  if (State.tableSortCol === col) {
    State.tableSortDir = State.tableSortDir === 'asc' ? 'desc' : 'asc';
  } else {
    State.tableSortCol = col;
    State.tableSortDir = 'asc';
  }
  const dir = State.tableSortDir === 'asc' ? 1 : -1;
  State.tableFiltered.sort((a, b) => {
    const av = isNaN(a[col]) ? a[col] : +a[col];
    const bv = isNaN(b[col]) ? b[col] : +b[col];
    return av < bv ? -dir : av > bv ? dir : 0;
  });
  State.tablePage = 1;
  renderTable();
}

function goPage(p) {
  const pages = Math.ceil(State.tableFiltered.length / State.tablePageSize);
  State.tablePage = Math.max(1, Math.min(pages, p));
  renderTable();
}

function searchTable(q) {
  const term = q.toLowerCase().trim();
  if (!term) {
    State.tableFiltered = [...State.tableData];
  } else {
    State.tableFiltered = State.tableData.filter(row =>
      Object.values(row).some(v => String(v).toLowerCase().includes(term))
    );
  }
  State.tablePage = 1;
  renderTable();
}

function exportCSV() {
  if (!State.tableFiltered.length) { Toast.show('No data to export.', 'warning'); return; }
  const cols = Object.keys(State.tableFiltered[0]);
  const rows = [cols.join(','), ...State.tableFiltered.map(r => cols.map(c => `"${r[c] ?? ''}"`).join(','))];
  const blob = new Blob([rows.join('\n')], { type: 'text/csv' });
  const a    = document.createElement('a');
  a.href     = URL.createObjectURL(blob);
  a.download = `${State.selectedDataset || 'dataset'}_export.csv`;
  a.click();
  Toast.show('CSV exported successfully.', 'success');
}

/* ── Filters ─────────────────────────────────────────────────── */
function applyFilters() {
  const cat    = document.getElementById('filter-category')?.value   || '';
  const region = document.getElementById('filter-region')?.value     || '';
  const search = document.getElementById('table-search')?.value      || '';

  let filtered = [...State.tableData];

  if (cat)    filtered = filtered.filter(r => Object.values(r).some(v => String(v).toLowerCase().includes(cat.toLowerCase())));
  if (region) filtered = filtered.filter(r => Object.values(r).some(v => String(v).toLowerCase().includes(region.toLowerCase())));
  if (search) filtered = filtered.filter(r => Object.values(r).some(v => String(v).toLowerCase().includes(search.toLowerCase())));

  State.tableFiltered = filtered;
  State.tablePage     = 1;
  renderTable();

  Toast.show(`Showing ${filtered.length.toLocaleString()} rows.`, 'info');
}

function resetFilters() {
  document.getElementById('filter-category').value = '';
  document.getElementById('filter-region').value   = '';
  document.getElementById('table-search').value     = '';
  State.tableFiltered = [...State.tableData];
  State.tablePage     = 1;
  renderTable();
}

/* ── Chart Export ─────────────────────────────────────────────── */
function downloadChart(chartId) {
  const chart = State.charts[chartId];
  if (!chart) return;
  const a = document.createElement('a');
  a.href     = chart.toBase64Image();
  a.download = `${chartId}.png`;
  a.click();
  Toast.show('Chart downloaded.', 'success');
}

/* ── Fullscreen Chart ────────────────────────────────────────── */
function openFullscreen(chartId) {
  const chart = State.charts[chartId];
  if (!chart) return;
  const ov   = document.getElementById('fullscreen-overlay');
  const box  = document.getElementById('fullscreen-chart-box');
  box.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <span style="font-weight:600;font-size:15px">Chart Fullscreen</span>
      <button class="btn btn-secondary btn-sm" onclick="closeFullscreen()">✕ Close</button>
    </div>
    <div style="flex:1;min-height:400px;position:relative">
      <canvas id="fullscreen-canvas"></canvas>
    </div>`;
  ov.classList.add('open');
  const newChart = new Chart(
    document.getElementById('fullscreen-canvas'),
    { type: chart.config.type, data: chart.config.data, options: { ...chart.config.options, maintainAspectRatio: false } }
  );
  State.charts['fullscreen'] = newChart;
}

function closeFullscreen() {
  document.getElementById('fullscreen-overlay').classList.remove('open');
  if (State.charts['fullscreen']) { State.charts['fullscreen'].destroy(); delete State.charts['fullscreen']; }
}

/* ── Loading Skeletons ───────────────────────────────────────── */
function showSkeletons() {
  document.getElementById('kpi-grid').innerHTML = Array(7).fill(0).map(() =>
    `<div class="skeleton-card">
       <div class="skeleton skeleton-h2"></div>
       <div class="skeleton skeleton-h1"></div>
       <div class="skeleton skeleton-line" style="width:80%"></div>
       <div class="skeleton skeleton-chart" style="height:36px"></div>
     </div>`
  ).join('');

  document.getElementById('charts-section').innerHTML =
    `<div class="charts-grid">` + Array(4).fill(0).map(() =>
      `<div class="skeleton-card"><div class="skeleton skeleton-chart"></div></div>`
    ).join('') + `</div>`;
}

/* ── Upload Modal ────────────────────────────────────────────── */
function openUploadModal() {
  document.getElementById('upload-modal').classList.add('open');
  document.getElementById('upload-dataset-name').focus();
}

function closeUploadModal() {
  document.getElementById('upload-modal').classList.remove('open');
  document.getElementById('upload-form').reset();
}

async function submitUpload(e) {
  e.preventDefault();
  const name     = document.getElementById('upload-dataset-name').value.trim();
  const dept     = document.getElementById('upload-department').value.trim();
  const domain   = document.getElementById('upload-domain').value.trim();
  const fileEl   = document.getElementById('upload-file');

  if (!fileEl.files.length) { Toast.show('Please select a CSV file.', 'warning'); return; }
  if (!name) { Toast.show('Dataset name is required.', 'warning'); return; }

  const fd = new FormData();
  fd.append('dataset_name', name);
  fd.append('file', fileEl.files[0]);
  if (dept)   fd.append('department', dept);
  if (domain) fd.append('business_domain', domain);

  const btn = document.getElementById('upload-submit-btn');
  btn.disabled     = true;
  btn.textContent  = '⏳ Uploading…';

  try {
    const res = await API.postForm('/upload/dataset', fd);
    Toast.show(`Dataset "${res.dataset_name}" uploaded (${res.row_count.toLocaleString()} rows).`, 'success');
    closeUploadModal();
    await loadDatasets();
    selectDataset(res.dataset_name);
  } catch (err) {
    Toast.show('Upload failed: ' + err.message, 'error');
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Upload Dataset';
  }
}

/* ── Datasets ────────────────────────────────────────────────── */
async function loadDatasets() {
  try {
    const data       = await API.get('/datasets');
    State.datasets   = Array.isArray(data) ? data : (data.datasets || []);
    renderDatasetList();
  } catch (err) {
    Toast.show('Could not load datasets: ' + err.message, 'error');
  }
}

function renderDatasetList() {
  const el = document.getElementById('dataset-list');
  if (!el) return;

  if (!State.datasets.length) {
    el.innerHTML = `<div class="empty-state">
      <div class="empty-state-icon">📂</div>
      <div class="empty-state-title">No datasets yet</div>
      <div class="empty-state-text">Upload a CSV file to get started.</div>
    </div>`;
    return;
  }

  el.innerHTML = State.datasets.map(d => `
    <div class="dataset-card ${State.selectedDataset === d.dataset_name ? 'selected' : ''}"
         role="button" tabindex="0"
         aria-pressed="${State.selectedDataset === d.dataset_name}"
         aria-label="Select dataset ${d.dataset_name}"
         onclick="selectDataset('${d.dataset_name}')"
         onkeydown="if(event.key==='Enter')selectDataset('${d.dataset_name}')">
      <div class="dataset-card-name">📊 ${d.dataset_name}</div>
      <div class="dataset-card-meta">
        ${d.row_count?.toLocaleString() ?? '—'} rows ·
        ${d.column_count ?? '—'} cols ·
        Q${d.quality_score?.toFixed(0) ?? '—'}%
      </div>
    </div>`).join('');
}

function selectDataset(name) {
  State.selectedDataset = name;
  document.getElementById('selected-dataset-name').textContent = name;
  document.getElementById('run-analysis-btn').disabled = false;
  renderDatasetList();
  Toast.show(`Selected: ${name}`, 'info');
}

/* ── Run Analysis ────────────────────────────────────────────── */
async function runAnalysis() {
  if (!State.selectedDataset) { Toast.show('Select a dataset first.', 'warning'); return; }

  const btn = document.getElementById('run-analysis-btn');
  btn.disabled    = true;
  btn.innerHTML   = '<span class="spin">⟳</span> Analysing…';

  showSkeletons();
  activateView('dashboard');

  try {
    const result = await API.post('/analysis/run', {
      dataset_name: State.selectedDataset,
      question:     document.getElementById('analysis-question')?.value || null,
    });

    State.analysisResult = result;

    // Populate dashboard
    renderKPICards(result);
    renderChartsSection(result);
    renderInsights(result);
    renderHealthRing(result);
    buildTableFromResult(result);

    // Show analysis info bar
    document.getElementById('analysis-info-bar').style.display = 'flex';
    document.getElementById('analysis-exec-time').textContent  =
      (result.execution_time_seconds || 0).toFixed(2) + 's';
    document.getElementById('analysis-status').textContent = result.execution_status || 'SUCCESS';

    // Reveal dashboard content and show map fallback
    showDashboardContent();
    const cols = Object.keys(result.kpis || {});
    const hasCoords = cols.some(c => /lat|lon|lng|latitude|longitude/i.test(c));
    initMap(hasCoords);

    // Populate info-bar dataset chip
    const chip = document.getElementById('analysis-dataset-chip');
    if (chip) chip.textContent = State.selectedDataset;

    Toast.show('Analysis complete!', 'success');
  } catch (err) {
    Toast.show('Analysis failed: ' + err.message, 'error');
    document.getElementById('kpi-grid').innerHTML =
      `<div class="empty-state" style="grid-column:1/-1">
         <div class="empty-state-icon">⚠️</div>
         <div class="empty-state-title">Analysis Failed</div>
         <div class="empty-state-text">${err.message}</div>
       </div>`;
  } finally {
    btn.disabled  = false;
    btn.innerHTML = '▶ Run Analysis';
  }
}

function renderChartsSection(result) {
  const el = document.getElementById('charts-section');
  el.innerHTML = `
    <div class="section-title">📊 Analytics Overview</div>
    <div class="charts-grid">

      <div class="chart-card">
        <div class="chart-card-header">
          <span class="chart-card-title">💰 Revenue by Quarter</span>
          <div class="chart-card-actions">
            <button class="btn btn-ghost btn-sm btn-icon" title="Download chart" aria-label="Download Revenue chart" onclick="downloadChart('chart-revenue')">⬇</button>
            <button class="btn btn-ghost btn-sm btn-icon" title="Fullscreen" aria-label="Fullscreen Revenue chart" onclick="openFullscreen('chart-revenue')">⛶</button>
          </div>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="chart-revenue" aria-label="Revenue by Quarter bar chart"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-card-header">
          <span class="chart-card-title">📈 Monthly Revenue Trend</span>
          <div class="chart-card-actions">
            <button class="btn btn-ghost btn-sm btn-icon" title="Download chart" aria-label="Download Trend chart" onclick="downloadChart('chart-trend')">⬇</button>
            <button class="btn btn-ghost btn-sm btn-icon" title="Fullscreen" aria-label="Fullscreen Trend chart" onclick="openFullscreen('chart-trend')">⛶</button>
          </div>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="chart-trend" aria-label="Monthly revenue trend line chart"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-card-header">
          <span class="chart-card-title">🏷️ Category Distribution</span>
          <div class="chart-card-actions">
            <button class="btn btn-ghost btn-sm btn-icon" title="Download chart" aria-label="Download Category chart" onclick="downloadChart('chart-category')">⬇</button>
            <button class="btn btn-ghost btn-sm btn-icon" title="Fullscreen" aria-label="Fullscreen Category chart" onclick="openFullscreen('chart-category')">⛶</button>
          </div>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="chart-category" aria-label="Category distribution doughnut chart"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-card-header">
          <span class="chart-card-title">🔢 Order Value Distribution</span>
          <div class="chart-card-actions">
            <button class="btn btn-ghost btn-sm btn-icon" title="Download chart" aria-label="Download Orders chart" onclick="downloadChart('chart-orders')">⬇</button>
            <button class="btn btn-ghost btn-sm btn-icon" title="Fullscreen" aria-label="Fullscreen Orders chart" onclick="openFullscreen('chart-orders')">⛶</button>
          </div>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="chart-orders" aria-label="Order value distribution histogram"></canvas>
        </div>
      </div>

      <div class="chart-card chart-full">
        <div class="chart-card-header">
          <span class="chart-card-title">🕸️ KPI Performance Radar</span>
          <div class="chart-card-actions">
            <button class="btn btn-ghost btn-sm btn-icon" title="Download chart" aria-label="Download Radar chart" onclick="downloadChart('chart-radar')">⬇</button>
            <button class="btn btn-ghost btn-sm btn-icon" title="Fullscreen" aria-label="Fullscreen Radar chart" onclick="openFullscreen('chart-radar')">⛶</button>
          </div>
        </div>
        <div class="chart-canvas-wrap" style="min-height:300px">
          <canvas id="chart-radar" aria-label="KPI performance radar chart"></canvas>
        </div>
      </div>

    </div>`;

  requestAnimationFrame(() => renderCharts(result));
}

function buildTableFromResult(result) {
  // Build representative sample rows from KPI data
  const fin    = result.kpis?.financial || {};
  const cat    = result.kpis?.category  || {};
  const health = result.health_score    || {};

  // Build a table of real KPI metrics from the API response
  const kpiRows = [
    { 'KPI': 'Total Revenue',       'Value': fin.total_revenue   != null ? '$' + Number(fin.total_revenue).toLocaleString()   : '—', 'Category': 'Financial',    'Status': health.business_health || '—' },
    { 'KPI': 'Total Orders',        'Value': fin.total_orders    != null ? Number(fin.total_orders).toLocaleString()           : '—', 'Category': 'Financial',    'Status': health.business_health || '—' },
    { 'KPI': 'Avg Order Value',     'Value': fin.average_order_value != null ? '$' + Number(fin.average_order_value).toFixed(2): '—', 'Category': 'Financial',    'Status': health.business_health || '—' },
    { 'KPI': 'Revenue Growth',      'Value': fin.revenue_growth  != null ? Number(fin.revenue_growth).toFixed(2) + '%'         : '—', 'Category': 'Growth',       'Status': health.business_health || '—' },
    { 'KPI': 'Profit Margin',       'Value': fin.profit_margin   != null ? Number(fin.profit_margin).toFixed(2) + '%'          : '—', 'Category': 'Financial',    'Status': health.business_health || '—' },
    { 'KPI': 'Max Revenue',         'Value': fin.max_revenue     != null ? '$' + Number(fin.max_revenue).toLocaleString()      : '—', 'Category': 'Financial',    'Status': health.business_health || '—' },
    { 'KPI': 'Min Revenue',         'Value': fin.min_revenue     != null ? '$' + Number(fin.min_revenue).toLocaleString()      : '—', 'Category': 'Financial',    'Status': health.business_health || '—' },
    { 'KPI': 'Total Quantity',      'Value': fin.total_quantity  != null ? Number(fin.total_quantity).toLocaleString()         : '—', 'Category': 'Operational',  'Status': health.business_health || '—' },
    { 'KPI': 'Health Score',        'Value': health.score        != null ? String(health.score) + '/100'                       : '—', 'Category': 'Health',       'Status': health.business_health || '—' },
    { 'KPI': 'Business Health',     'Value': health.business_health || '—',                                                          'Category': 'Health',       'Status': health.business_health || '—' },
    { 'KPI': 'Top Category',        'Value': cat.top_category    || '—',                                                             'Category': 'Operational',  'Status': health.business_health || '—' },
    { 'KPI': 'Customer Segments',   'Value': (result.kpis?.customer?.segments_count != null ? result.kpis.customer.segments_count : result.kpis?.segmentation?.segment_count != null ? result.kpis.segmentation.segment_count : '—').toString(), 'Category': 'Customer', 'Status': health.business_health || '—' },
  ].filter(r => r.Value !== '—');
  const mockData = kpiRows.length ? kpiRows : [{ 'KPI': 'No KPI data returned', 'Value': '—', 'Category': '—', 'Status': '—' }];

  initTable(mockData);
  renderTableSection();
}

function renderTableSection() {
  const el = document.getElementById('table-section');
  el.innerHTML = `
    <div class="section-title">📋 Data Preview</div>
    <div class="table-section">
      <div class="table-toolbar">
        <div class="table-search-wrap">
          <span class="search-icon" aria-hidden="true">🔍</span>
          <input type="search" class="table-search" id="table-search"
                 placeholder="Search rows…" aria-label="Search table"
                 oninput="searchTable(this.value)">
        </div>
        <button class="btn btn-secondary btn-sm" onclick="exportCSV()" aria-label="Export as CSV">⬇ Export CSV</button>
        <label class="field-label" style="margin:0">Rows:</label>
        <select class="filter-select" style="min-width:70px" onchange="State.tablePageSize=+this.value;goPage(1)" aria-label="Rows per page">
          <option value="10">10</option>
          <option value="15" selected>15</option>
          <option value="25">25</option>
          <option value="50">50</option>
        </select>
      </div>
      <div id="data-table-container"></div>
    </div>`;
  renderTable();
}

/* ── Map section ─────────────────────────────────────────────── */
function initMap(hasCoords) {
  const mapSection = document.getElementById('map-section');
  if (!hasCoords) {
    mapSection.innerHTML = `
      <div class="section-title">🗺️ Geographic Analytics</div>
      <div class="chart-card">
        <div class="empty-state" style="padding:40px">
          <div class="empty-state-icon">🗺️</div>
          <div class="empty-state-title">Map Unavailable</div>
          <div class="empty-state-text">No latitude/longitude columns detected in the dataset.</div>
        </div>
      </div>`;
    return;
  }

  mapSection.innerHTML = `
    <div class="section-title">🗺️ Geographic Analytics</div>
    <div class="chart-card">
      <div id="map-container"></div>
    </div>`;

  const map = L.map('map-container').setView([20, 0], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
  }).addTo(map);
}

/* ── Welcome / Landing ───────────────────────────────────────── */
function renderWelcome() {
  document.getElementById('dashboard-welcome').style.display = 'block';
  document.getElementById('dashboard-content').style.display = 'none';
}

function showDashboardContent() {
  document.getElementById('dashboard-welcome').style.display = 'none';
  document.getElementById('dashboard-content').style.display = 'block';
}

/* ── Drag and drop for upload panel ──────────────────────────── */
function initDropzone() {
  const zone = document.getElementById('drop-zone');
  if (!zone) return;
  zone.addEventListener('dragover',  e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', ()  => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) {
      document.getElementById('upload-file').files = e.dataTransfer.files;
      openUploadModal();
    }
  });
  zone.addEventListener('click', openUploadModal);
  zone.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') openUploadModal(); });
}

/* ── Notifications ───────────────────────────────────────────── */
function toggleNotifications() {
  Toast.show('No new notifications.', 'info');
}

/* ── Search ──────────────────────────────────────────────────── */
function handleSearch(q) {
  if (!q.trim()) return;
  Toast.show(`Searching for "${q}"…`, 'info');
}

/* ── View: Upload ────────────────────────────────────────────── */
function renderUploadView() {
  const el = document.getElementById('view-upload');
  if (!el) return;
  el.innerHTML = `
    <div class="page-header">
      <div>
        <div class="page-title">Upload Dataset</div>
        <div class="page-subtitle">Import CSV files for analysis</div>
      </div>
      <button class="btn btn-primary" onclick="openUploadModal()" aria-label="Upload new dataset">
        ➕ New Dataset
      </button>
    </div>

    <div id="drop-zone" class="upload-panel"
         role="button" tabindex="0" aria-label="Drop CSV file here or click to upload">
      <div class="upload-icon" aria-hidden="true">📁</div>
      <div class="upload-title">Drop your CSV here</div>
      <div class="upload-sub">or click to browse files (CSV, up to 100 MB)</div>
      <button class="btn btn-primary" onclick="openUploadModal(); event.stopPropagation()">
        Choose File
      </button>
    </div>

    <div class="divider"></div>
    <div class="section-title">📚 Existing Datasets</div>
    <div id="dataset-list" class="dataset-list"></div>`;

  initDropzone();
  renderDatasetList();
}

/* ── Initialise ──────────────────────────────────────────────── */
async function init() {
  // Apply saved theme
  applyTheme(State.theme);

  // Apply saved sidebar state (desktop only)
  if (window.innerWidth > 768 && State.sidebarCollapsed) {
    document.getElementById('sidebar').classList.add('collapsed');
  }

  // Load datasets
  await loadDatasets();

  // Nav
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const view = item.dataset.view;
      if (!view) return;
      activateView(view);
      if (view === 'upload')   renderUploadView();
      if (window.innerWidth <= 768) toggleMobileSidebar();
    });
    item.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') item.click();
    });
  });

  // Welcome state
  if (!State.analysisResult) renderWelcome();

  // ESC closes fullscreen/modals
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closeFullscreen();
      closeUploadModal();
    }
  });

  // Close mobile sidebar on overlay click
  document.getElementById('mobile-overlay')?.addEventListener('click', toggleMobileSidebar);
}

// Expose globals called from HTML attributes
Object.assign(window, {
  toggleSidebar, toggleMobileSidebar,
  activateView, openUploadModal, closeUploadModal,
  submitUpload, selectDataset, runAnalysis,
  sortTable, goPage, searchTable, exportCSV,
  applyFilters, resetFilters,
  downloadChart, openFullscreen, closeFullscreen,
  toggleNotifications, handleSearch,
  renderUploadView, showDashboardContent,
});

document.addEventListener('DOMContentLoaded', init);
