/**
 * Sleep Paralysis AI — Main App JS
 * Handles auth, API calls, UI, charts, predictions
 */

const API = 'http://127.0.0.1:5000/api';
let token = localStorage.getItem('spa_token') || null;
let currentUser = JSON.parse(localStorage.getItem('spa_user') || 'null');
let selectedPosition = 'back';
let riskGaugeChart = null, predGaugeChart = null, stressSleepChart = null, riskHistChart = null;

/* ═══════════════════════════════════════════════
   BOOT
═══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  setDashboardDate();
  if (token && currentUser) {
    showApp();
  }
});

function showApp() {
  document.getElementById('auth-screen').classList.remove('active');
  document.getElementById('auth-screen').style.display = 'none';
  const shell = document.getElementById('app-shell');
  shell.classList.remove('hidden');
  shell.style.display = 'flex';
  shell.style.flexDirection = 'column';
  updateUserUI();
  showScreen('dashboard');
  loadDashboard();
}

function setDashboardDate() {
  const el = document.getElementById('dashboard-date');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  const hour = now.getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const grEl = document.getElementById('dashboard-greeting');
  if (grEl) grEl.textContent = `${greeting}, ${currentUser?.name?.split(' ')[0] || 'there'}! 👋`;
}

function updateUserUI() {
  const initials = currentUser?.name?.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() || '?';
  document.getElementById('user-initials').textContent = initials;
  document.getElementById('menu-user-name').textContent = currentUser?.name || 'User';
  document.getElementById('menu-user-email').textContent = currentUser?.email || '';
}

/* ═══════════════════════════════════════════════
   AUTH
═══════════════════════════════════════════════ */
function switchAuthTab(tab) {
  document.getElementById('login-tab').classList.toggle('active', tab === 'login');
  document.getElementById('signup-tab').classList.toggle('active', tab === 'signup');
  document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
  document.getElementById('signup-form').classList.toggle('hidden', tab !== 'signup');
}

function togglePassword(id) {
  const el = document.getElementById(id);
  el.type = el.type === 'password' ? 'text' : 'password';
}

async function handleLogin(e) {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  const errEl = document.getElementById('login-error');
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  setLoading(btn, true);
  errEl.classList.add('hidden');

  try {
    const res = await apiFetch('/auth/login', 'POST', { email, password }, false);
    token = res.token;
    currentUser = res.user;
    localStorage.setItem('spa_token', token);
    localStorage.setItem('spa_user', JSON.stringify(currentUser));
    showApp();
  } catch (err) {
    showError(errEl, err.message || 'Login failed');
  } finally {
    setLoading(btn, false);
  }
}

async function handleSignup(e) {
  e.preventDefault();
  const btn = document.getElementById('signup-btn');
  const errEl = document.getElementById('signup-error');
  const name = document.getElementById('signup-name').value.trim();
  const email = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;
  const age = document.getElementById('signup-age').value;

  setLoading(btn, true);
  errEl.classList.add('hidden');

  try {
    const body = { name, email, password };
    if (age) body.age = parseInt(age);
    const res = await apiFetch('/auth/signup', 'POST', body, false);
    token = res.token;
    currentUser = res.user;
    localStorage.setItem('spa_token', token);
    localStorage.setItem('spa_user', JSON.stringify(currentUser));
    showApp();
    showToast('Welcome to SleepAI! 🎉');
  } catch (err) {
    showError(errEl, err.message || 'Signup failed');
  } finally {
    setLoading(btn, false);
  }
}

function logout() {
  token = null; currentUser = null;
  localStorage.removeItem('spa_token');
  localStorage.removeItem('spa_user');
  location.reload();
}

/* ═══════════════════════════════════════════════
   SCREEN NAVIGATION
═══════════════════════════════════════════════ */
function showScreen(name) {
  document.querySelectorAll('.app-screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`screen-${name}`)?.classList.add('active');
  document.getElementById(`nav-${name}`)?.classList.add('active');
  document.getElementById('user-menu')?.classList.add('hidden');

  if (name === 'history') loadHistory();
  if (name === 'tips') loadTips();
  if (name === 'dashboard') loadDashboard();
  window.scrollTo(0, 0);
}

function toggleUserMenu() {
  document.getElementById('user-menu').classList.toggle('hidden');
}

/* ═══════════════════════════════════════════════
   DASHBOARD
═══════════════════════════════════════════════ */
async function loadDashboard() {
  setDashboardDate();
  try {
    const [statsRes, predRes, alarmRes] = await Promise.all([
      apiFetch('/tracker/stats'),
      apiFetch('/predict/latest'),
      apiFetch('/alarm/')
    ]);

    // Stats cards
    if (statsRes.stats) {
      document.getElementById('avg-stress').textContent = statsRes.stats.avg_stress;
      document.getElementById('avg-sleep').textContent = statsRes.stats.avg_sleep_hours + 'h';
      document.getElementById('avg-screen').textContent = statsRes.stats.avg_screen_time + 'h';
      document.getElementById('horror-pct').textContent = statsRes.stats.horror_exposure_pct + '%';
    }

    // Latest prediction
    if (predRes.prediction) {
      const p = predRes.prediction;
      updateRiskCard(p);
      renderInsights(p.insights, 'dashboard-insights');
      drawGauge('risk-gauge', p.risk_probability, p.risk_level);
      document.getElementById('gauge-pct-text').textContent = p.risk_probability + '%';
    }

    // Alarms
    renderAlarms(alarmRes.alarms || []);

    // Charts
    loadCharts();
  } catch (e) {
    console.error('Dashboard load error:', e);
  }
}

function updateRiskCard(p) {
  const lvl = document.getElementById('risk-level-text');
  lvl.textContent = p.risk_level;
  lvl.className = `risk-level-text ${p.risk_level}`;
  document.getElementById('risk-pct').textContent = `${p.risk_probability}% probability`;
  document.getElementById('episode-time-chip').textContent = `🕑 Episode: ${p.predicted_episode_time}`;
  document.getElementById('alarm-chip').textContent = `⏰ Alarm: ${p.rem_phase_start}`;
  const card = document.getElementById('risk-card');
  card.style.borderColor = p.risk_level === 'High' ? 'rgba(248,113,113,0.3)' :
    p.risk_level === 'Medium' ? 'rgba(251,191,36,0.3)' : 'rgba(52,211,153,0.3)';
}

async function loadCharts() {
  try {
    const [logsRes, predsRes] = await Promise.all([
      apiFetch('/tracker/logs?limit=7'),
      apiFetch('/predict/history?limit=7')
    ]);
    const logs = (logsRes.logs || []).reverse();
    const preds = (predsRes.predictions || []).reverse();

    // Stress & Sleep Chart
    const ctx1 = document.getElementById('stress-sleep-chart');
    if (stressSleepChart) stressSleepChart.destroy();
    stressSleepChart = new Chart(ctx1, {
      type: 'line',
      data: {
        labels: logs.map(l => new Date(l.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
        datasets: [
          { label: 'Stress', data: logs.map(l => l.stress_level), borderColor: '#f472b6', backgroundColor: 'rgba(244,114,182,0.1)', tension: 0.4, fill: true },
          { label: 'Sleep (h)', data: logs.map(l => l.sleep_hours), borderColor: '#60a5fa', backgroundColor: 'rgba(96,165,250,0.1)', tension: 0.4, fill: true }
        ]
      },
      options: chartOptions()
    });

    // Risk History Chart
    const ctx2 = document.getElementById('risk-history-chart');
    if (riskHistChart) riskHistChart.destroy();
    const riskColors = { Low: '#34d399', Medium: '#fbbf24', High: '#f87171' };
    riskHistChart = new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: preds.map(p => new Date(p.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
        datasets: [{
          label: 'Risk %',
          data: preds.map(p => p.risk_probability),
          backgroundColor: preds.map(p => riskColors[p.risk_level] + '99'),
          borderColor: preds.map(p => riskColors[p.risk_level]),
          borderWidth: 1, borderRadius: 6
        }]
      },
      options: chartOptions()
    });
  } catch (e) { console.error('Chart error:', e); }
}

function chartOptions() {
  return {
    responsive: true, maintainAspectRatio: true,
    plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 }, boxWidth: 10 } } },
    scales: {
      x: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
      y: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
    }
  };
}

function renderInsights(insights, containerId) {
  const el = document.getElementById(containerId);
  if (!el || !insights?.length) return;
  el.innerHTML = insights.slice(0, 4).map(i => `
    <div class="insight-card ${i.type}">
      <span class="insight-icon">${i.icon}</span>
      <div>
        <p class="insight-title">${i.title}</p>
        <p class="insight-msg">${i.message}</p>
      </div>
    </div>`).join('');
}

function renderAlarms(alarms) {
  const el = document.getElementById('alarms-list');
  if (!alarms.length) {
    el.innerHTML = '<p class="no-alarms">No active alarms. High/Medium risk predictions auto-schedule alarms.</p>';
    return;
  }
  el.innerHTML = alarms.map(a => `
    <div class="alarm-item" id="alarm-${a.id}">
      <div>
        <p class="alarm-time">⏰ ${a.alarm_time}</p>
        <p class="alarm-label">${a.label}</p>
      </div>
      <button class="alarm-dismiss" onclick="dismissAlarm(${a.id})">Dismiss</button>
    </div>`).join('');
}

async function dismissAlarm(id) {
  try {
    await apiFetch(`/alarm/${id}/dismiss`, 'PUT');
    document.getElementById(`alarm-${id}`)?.remove();
    showToast('Alarm dismissed');
  } catch (e) { showToast('Error dismissing alarm'); }
}

/* ═══════════════════════════════════════════════
   TRACKER
═══════════════════════════════════════════════ */
function updateSlider(sliderId, valueId, suffix) {
  const slider = document.getElementById(sliderId);
  const val = parseFloat(slider.value);
  document.getElementById(valueId).textContent = val + suffix;
  // Update slider gradient
  const pct = ((val - slider.min) / (slider.max - slider.min)) * 100;
  slider.style.background = `linear-gradient(to right, #a78bfa 0%, #a78bfa ${pct}%, rgba(255,255,255,0.15) ${pct}%)`;
}

function toggleOption(cardId, inputId) {
  const card = document.getElementById(cardId);
  const input = document.getElementById(inputId);
  const isOn = card.classList.toggle('on');
  input.value = isOn ? 'true' : 'false';
}

function selectPosition(pos) {
  selectedPosition = pos;
  document.getElementById('sleep-position').value = pos;
  ['back', 'side', 'stomach'].forEach(p => {
    document.getElementById(`pos-${p}`)?.classList.toggle('active', p === pos);
  });
}

async function submitTracker(e) {
  e.preventDefault();
  const btn = document.getElementById('analyze-btn');
  const errEl = document.getElementById('tracker-error');
  setLoading(btn, true);
  errEl.classList.add('hidden');

  // Parse bedtime HH:MM → float hour
  const bedtimeStr = document.getElementById('bedtime-input').value || '23:00';
  const [bh, bm] = bedtimeStr.split(':').map(Number);
  const bedtimeHour = bh + (bm / 60);

  const payload = {
    stress_level: parseFloat(document.getElementById('stress-slider').value),
    sleep_hours: parseFloat(document.getElementById('sleep-slider').value),
    screen_time: parseFloat(document.getElementById('screen-slider').value),
    caffeine_intake: parseFloat(document.getElementById('caffeine-slider').value),
    physical_activity: parseFloat(document.getElementById('activity-slider').value),
    watched_horror: document.getElementById('watched-horror').value === 'true',
    nap_taken: document.getElementById('nap-taken').value === 'true',
    sleep_position: document.getElementById('sleep-position').value || 'back',
    bedtime_hour: bedtimeHour
  };

  try {
    // Save log first
    const logRes = await apiFetch('/tracker/log', 'POST', payload);
    // Run prediction
    const predRes = await apiFetch('/predict/analyze', 'POST', { log_id: logRes.log.id });
    const pred = predRes.prediction;

    // Update prediction screen
    renderPredictionScreen(pred, predRes.alarm);
    showScreen('prediction');
    if (predRes.alarm) showAlarmModal(predRes.alarm);
  } catch (err) {
    showError(errEl, err.message || 'Analysis failed. Is the backend running?');
  } finally {
    setLoading(btn, false);
  }
}

function renderPredictionScreen(pred, alarm) {
  const badge = document.getElementById('pred-risk-badge');
  badge.textContent = pred.risk_level + ' Risk';
  badge.className = `pred-risk-badge ${pred.risk_level}`;

  document.getElementById('pred-gauge-pct').textContent = pred.risk_probability + '%';
  document.getElementById('pred-episode-time').textContent = pred.predicted_episode_time;
  document.getElementById('pred-rem-time').textContent = pred.rem_phase_start;
  document.getElementById('pred-alarm-time').textContent = alarm ? alarm.alarm_time : '—';

  drawGauge('pred-gauge', pred.risk_probability, pred.risk_level);

  const probs = pred.risk_probabilities;
  animateBar('bar-low', 'pct-low', probs.Low);
  animateBar('bar-medium', 'pct-medium', probs.Medium);
  animateBar('bar-high', 'pct-high', probs.High);

  renderInsights(pred.insights, 'pred-insights');

  const alarmInfo = document.getElementById('pred-alarm-info');
  if (alarm) {
    alarmInfo.innerHTML = `
      <div class="alarm-set-box">
        <p class="alarm-set-time">${alarm.alarm_time}</p>
        <p class="alarm-set-label">${alarm.label}</p>
      </div>`;
  } else {
    alarmInfo.innerHTML = '<p style="color:var(--text-muted);font-size:13px">No alarm scheduled (Low risk detected)</p>';
  }
}

function animateBar(barId, pctId, value) {
  const pct = Math.round(value);
  document.getElementById(pctId).textContent = pct + '%';
  setTimeout(() => { document.getElementById(barId).style.width = pct + '%'; }, 100);
}

/* ═══════════════════════════════════════════════
   GAUGE CHART (Doughnut)
═══════════════════════════════════════════════ */
function drawGauge(canvasId, pct, level) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const colors = { Low: '#34d399', Medium: '#fbbf24', High: '#f87171' };
  const color = colors[level] || '#a78bfa';

  const existing = Chart.getChart(canvas);
  if (existing) existing.destroy();

  new Chart(canvas, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [pct, 100 - pct],
        backgroundColor: [color, 'rgba(255,255,255,0.06)'],
        borderWidth: 0,
        circumference: 270,
        rotation: 225
      }]
    },
    options: {
      responsive: false, cutout: '75%',
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { animateRotate: true, duration: 1000 }
    }
  });
}

/* ═══════════════════════════════════════════════
   HISTORY SCREEN
═══════════════════════════════════════════════ */
async function loadHistory() {
  const el = document.getElementById('history-list');
  el.innerHTML = '<div class="loading-spinner">Loading...</div>';
  try {
    const [logsRes, predsRes] = await Promise.all([
      apiFetch('/tracker/logs?limit=30'),
      apiFetch('/predict/history?limit=30')
    ]);
    const logs = logsRes.logs || [];
    const preds = predsRes.predictions || [];
    const predByLog = {};
    preds.forEach(p => { if (p.log_id) predByLog[p.log_id] = p; });

    if (!logs.length) {
      el.innerHTML = '<div class="empty-state"><div class="empty-icon">📅</div><p>No history yet. Start tracking!</p></div>';
      return;
    }

    el.innerHTML = logs.map(l => {
      const p = predByLog[l.id];
      const riskLevel = p?.risk_level || 'none';
      return `
        <div class="history-item">
          <div>
            <p class="history-date">${new Date(l.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</p>
            <div class="history-metrics">
              <span class="h-metric">😰 <strong>${l.stress_level}</strong>/10</span>
              <span class="h-metric">😴 <strong>${l.sleep_hours}h</strong></span>
              <span class="h-metric">📱 <strong>${l.screen_time}h</strong></span>
              ${l.watched_horror ? '<span class="h-metric">👻 Horror</span>' : ''}
            </div>
          </div>
          <span class="risk-badge-sm ${riskLevel}">${p ? p.risk_level + ' ' + p.risk_probability + '%' : 'No Prediction'}</span>
        </div>`;
    }).join('');
  } catch (e) {
    el.innerHTML = '<div class="empty-state"><p>Error loading history.</p></div>';
  }
}

/* ═══════════════════════════════════════════════
   TIPS SCREEN
═══════════════════════════════════════════════ */
async function loadTips() {
  const el = document.getElementById('tips-list');
  try {
    const res = await apiFetch('/insights/tips', 'GET', null, false);
    el.innerHTML = res.tips.map(cat => `
      <div class="glass-card">
        <p class="tips-category">${cat.category}</p>
        ${cat.tips.map(t => `
          <div class="tip-item">
            <div class="tip-dot"></div>
            <p class="tip-text">${t}</p>
          </div>`).join('')}
      </div>`).join('');
  } catch (e) {
    el.innerHTML = '<div class="empty-state"><p>Could not load tips.</p></div>';
  }
}

/* ═══════════════════════════════════════════════
   ALARM MODAL
═══════════════════════════════════════════════ */
function showAlarmModal(alarm) {
  document.getElementById('alarm-modal-title').textContent = '⏰ Smart Alarm Set!';
  document.getElementById('alarm-modal-body').textContent =
    `Prevention alarm scheduled for ${alarm.alarm_time} — 30 min before your predicted REM phase. We'll wake you before the episode.`;
  document.getElementById('alarm-modal').classList.remove('hidden');
  document.getElementById('alarm-modal').style.display = 'flex';
}
function closeAlarmModal() {
  document.getElementById('alarm-modal').classList.add('hidden');
  document.getElementById('alarm-modal').style.display = 'none';
}

/* ═══════════════════════════════════════════════
   API HELPER
═══════════════════════════════════════════════ */
async function apiFetch(path, method = 'GET', body = null, auth = true) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth && token) headers['Authorization'] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(API + path, opts);
  const data = await res.json();

  if (!res.ok) throw new Error(data.error || data.message || `Error ${res.status}`);
  return data;
}

/* ═══════════════════════════════════════════════
   UI HELPERS
═══════════════════════════════════════════════ */
function setLoading(btn, loading) {
  btn.querySelector('.btn-text').classList.toggle('hidden', loading);
  btn.querySelector('.btn-loader').classList.toggle('hidden', !loading);
  btn.disabled = loading;
}

function showError(el, msg) {
  el.textContent = msg;
  el.classList.remove('hidden');
}

let toastTimer;
function showToast(msg) {
  const toast = document.getElementById('toast');
  document.getElementById('toast-msg').textContent = msg;
  toast.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add('hidden'), 3000);
}

// Init sliders on load
document.addEventListener('DOMContentLoaded', () => {
  ['stress-slider', 'sleep-slider', 'screen-slider', 'caffeine-slider', 'activity-slider'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      const suffix = id.includes('caffeine') ? ' cups' : id.includes('stress') ? '' : 'h';
      updateSlider(id, id.replace('-slider', '-value'), suffix);
    }
  });
});
