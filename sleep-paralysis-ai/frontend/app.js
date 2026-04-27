/* ═══════════════════════════════════════════════
   SLEEP PARALYSIS AI - CORE LOGIC (Auth Version)
═══════════════════════════════════════════════ */

const API = `http://${window.location.hostname}:5005/api`;
let token = localStorage.getItem('spa_token');
let currentUser = JSON.parse(localStorage.getItem('spa_user') || 'null');

document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();
  
  if (token && currentUser) {
    showApp();
  } else {
    showAuth();
  }
});

/* ═══════════════════════════════════════════════
   AUTH FLOW
═══════════════════════════════════════════════ */

function showAuth() {
  document.getElementById('auth-screen').classList.remove('hidden');
  document.getElementById('app-shell').classList.add('hidden');
}

function showApp() {
  document.getElementById('auth-screen').classList.add('hidden');
  document.getElementById('app-shell').classList.remove('hidden');
  loadDashboard();
}

function switchAuthTab(type) {
  const isLogin = type === 'login';
  document.getElementById('login-tab').classList.toggle('active', isLogin);
  document.getElementById('signup-tab').classList.toggle('active', !isLogin);
  document.getElementById('login-form').classList.toggle('hidden', !isLogin);
  document.getElementById('signup-form').classList.toggle('hidden', isLogin);
}

async function handleLogin(e) {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  const errorEl = document.getElementById('login-error');
  setLoading(btn, true);
  errorEl.classList.add('hidden');

  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;

  try {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Login failed');

    token = data.token;
    currentUser = data.user;
    localStorage.setItem('spa_token', token);
    localStorage.setItem('spa_user', JSON.stringify(currentUser));
    showApp();
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.classList.remove('hidden');
  } finally {
    setLoading(btn, false);
  }
}

async function handleSignup(e) {
  e.preventDefault();
  const btn = document.getElementById('signup-btn');
  const errorEl = document.getElementById('signup-error');
  setLoading(btn, true);
  errorEl.classList.add('hidden');

  const name = document.getElementById('signup-name').value;
  const email = document.getElementById('signup-email').value;
  const password = document.getElementById('signup-password').value;

  try {
    const res = await fetch(`${API}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Signup failed');

    token = data.token;
    currentUser = data.user;
    localStorage.setItem('spa_token', token);
    localStorage.setItem('spa_user', JSON.stringify(currentUser));
    showApp();
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.classList.remove('hidden');
  } finally {
    setLoading(btn, false);
  }
}

function logout() {
  localStorage.clear();
  location.reload();
}

/* ═══════════════════════════════════════════════
   UI NAVIGATION
═══════════════════════════════════════════════ */

function showScreen(name) {
  document.querySelectorAll('.app-screen').forEach(s => s.classList.remove('active'));
  const target = document.getElementById(`screen-${name}`);
  if (target) target.classList.add('active');

  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`nav-${name}`)?.classList.add('active');

  if (name === 'dashboard') loadDashboard();
  if (name === 'history') loadHistory();
  if (name === 'tips') loadTips();

  setTimeout(() => { if (window.lucide) lucide.createIcons(); }, 100);
}

function toggleTheme() {
  document.body.classList.toggle('light-mode');
  const isLight = document.body.classList.contains('light-mode');
  localStorage.setItem('spa_theme', isLight ? 'light' : 'dark');
  
  document.getElementById('theme-icon-sun').classList.toggle('hidden', !isLight);
  document.getElementById('theme-icon-moon').classList.toggle('hidden', isLight);
}

function toggleUserMenu() {
  document.getElementById('user-menu').classList.toggle('hidden');
}

// Global click listener to close menu on outside click
window.addEventListener('click', (e) => {
  const menu = document.getElementById('user-menu');
  const avatar = document.getElementById('user-avatar-btn');
  if (menu && avatar && !menu.contains(e.target) && !avatar.contains(e.target)) {
    menu.classList.add('hidden');
  }
});

// Load saved theme on boot
(function initTheme() {
  const saved = localStorage.getItem('spa_theme');
  if (saved === 'light') {
    document.body.classList.add('light-mode');
    setTimeout(() => {
        const sun = document.getElementById('theme-icon-sun');
        const moon = document.getElementById('theme-icon-moon');
        if(sun) sun.classList.remove('hidden');
        if(moon) moon.classList.add('hidden');
    }, 100);
  }
})();

/* ═══════════════════════════════════════════════
   API UTILS
═══════════════════════════════════════════════ */

async function apiFetch(endpoint, method = 'GET', body = null) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API}${endpoint}`, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

/* ═══════════════════════════════════════════════
   DASHBOARD & TRACKER
═══════════════════════════════════════════════ */

async function loadDashboard() {
  try {
    const [statsRes, predRes] = await Promise.all([
      apiFetch('/tracker/stats'),
      apiFetch('/predict/latest')
    ]);

    if (statsRes.stats) {
      document.getElementById('avg-stress').textContent = statsRes.stats.avg_stress;
      document.getElementById('avg-sleep').textContent = statsRes.stats.avg_sleep_hours + 'h';
    }

    if (predRes.prediction) {
      const p = predRes.prediction;
      document.getElementById('risk-level-text').textContent = p.risk_level + ' Risk';
      document.getElementById('episode-time-chip').innerHTML = `<i data-lucide="clock"></i> Episode: ${p.predicted_episode_time}`;
      drawGauge('risk-gauge', p.risk_probability, p.risk_level);
    }
    
    if (window.lucide) lucide.createIcons();
  } catch (e) { console.error('Dashboard load failed:', e); }
}

function updateSlider(sliderId, valueId, suffix) {
  const val = document.getElementById(sliderId).value;
  document.getElementById(valueId).textContent = val + suffix;
}

function toggleOption(cardId, inputId) {
  const card = document.getElementById(cardId);
  const input = document.getElementById(inputId);
  const isOn = card.classList.toggle('on');
  input.value = isOn ? 'true' : 'false';
}

function selectPosition(pos) {
  document.getElementById('sleep-position').value = pos;
  document.querySelectorAll('.pos-tile-new').forEach(b => b.classList.remove('active'));
  document.getElementById(`pos-${pos}`).classList.add('active');
}

async function submitTracker(e) {
  if (e) e.preventDefault();
  const btn = document.getElementById('analyze-btn');
  if (btn.disabled) return;
  
  setLoading(btn, true);

  try {
    const payload = {
      stress_level: parseInt(document.getElementById('stress-slider').value) || 5,
      sleep_hours: parseFloat(document.getElementById('sleep-slider').value) || 7,
      screen_time: parseFloat(document.getElementById('screen-slider').value) || 4,
      caffeine_intake: parseInt(document.getElementById('caffeine-slider').value) || 0,
      watched_horror: document.getElementById('watched-horror').value === 'true',
      nap_taken: document.getElementById('nap-taken').value === 'true',
      sleep_position: document.getElementById('sleep-position').value || 'back'
    };

    const logRes = await apiFetch('/tracker/log', 'POST', payload);
    if (!logRes.log || !logRes.log.id) throw new Error('Failed to save log');

    const predRes = await apiFetch('/predict/analyze', 'POST', { log_id: logRes.log.id });
    if (!predRes.prediction) throw new Error('AI analysis failed');
    
    renderPredictionScreen(predRes.prediction);
    showScreen('prediction');
  } catch (err) {
    console.error('Tracker submission error:', err);
    alert('Analysis Error: ' + err.message);
  } finally {
    setLoading(btn, false);
  }
}

function renderPredictionScreen(p) {
  document.getElementById('pred-risk-badge').textContent = p.risk_level + ' Risk';
  document.getElementById('pred-gauge-pct').textContent = p.risk_probability + '%';
  document.getElementById('pred-episode-time').textContent = p.predicted_episode_time;
  document.getElementById('pred-rem-time').textContent = p.rem_phase_start;
  
  drawGauge('pred-gauge', p.risk_probability, p.risk_level);
  
  const probs = p.risk_probabilities || { Low: 100, Medium: 0, High: 0 };
  animateBar('bar-low', 'pct-low', probs.Low);
  animateBar('bar-medium', 'pct-medium', probs.Medium);
  animateBar('bar-high', 'pct-high', probs.High);
}

function animateBar(barId, pctId, val) {
  const pct = Math.round(val);
  const pctEl = document.getElementById(pctId);
  const barEl = document.getElementById(barId);
  
  if (pctEl) pctEl.textContent = pct + '%';
  if (barEl) barEl.style.width = pct + '%';
}

async function loadHistory() {
  const el = document.getElementById('history-list');
  el.innerHTML = '<p style="text-align:center;padding:20px;">Loading logs...</p>';
  try {
    const res = await apiFetch('/tracker/logs?limit=20');
    el.innerHTML = res.logs.map(l => `
      <div class="glass-card" style="margin-bottom:15px;padding:15px;">
        <p style="font-weight:700;margin-bottom:5px;">${new Date(l.created_at).toLocaleDateString()}</p>
        <p style="font-size:12px;color:var(--text-muted);">Stress: ${l.stress_level} | Sleep: ${l.sleep_hours}h | Pos: ${l.sleep_position}</p>
      </div>
    `).join('');
  } catch (e) { el.innerHTML = '<p>No history found.</p>'; }
}

async function loadTips() {
  const el = document.getElementById('tips-list');
  el.innerHTML = '<p style="padding:20px;text-align:center;">Loading expert tips...</p>';
  try {
    const res = await apiFetch('/insights/tips');
    if (!res.tips || res.tips.length === 0) {
      el.innerHTML = '<p style="padding:20px;text-align:center;">No tips available.</p>';
      return;
    }
    el.innerHTML = res.tips.map(cat => `
      <div class="glass-card">
        <h4 style="color:var(--primary);margin-bottom:12px;font-size:16px;">${cat.category}</h4>
        <ul style="list-style:none;">
          ${cat.tips.map(t => `<li style="font-size:14px;color:var(--text-muted);margin-bottom:8px;line-height:1.5;">• ${t}</li>`).join('')}
        </ul>
      </div>
    `).join('');
  } catch (e) {
    el.innerHTML = '<p style="padding:20px;text-align:center;">Error loading tips.</p>';
  }
}

function setLoading(btn, loading) {
  btn.querySelector('.btn-text').classList.toggle('hidden', loading);
  btn.querySelector('.btn-loader').classList.toggle('hidden', !loading);
  btn.disabled = loading;
}

let gaugeChart = null;
function drawGauge(canvasId, value, level) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  if (gaugeChart) gaugeChart.destroy();
  const color = level === 'High' ? '#f87171' : level === 'Medium' ? '#fbbf24' : '#34d399';
  gaugeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [value, 100 - value],
        backgroundColor: [color, 'rgba(255,255,255,0.05)'],
        borderWidth: 0,
        circumference: 270,
        rotation: 225,
        cutout: '85%',
        borderRadius: 10
      }]
    },
    options: { plugins: { tooltip: { enabled: false } }, responsive: true, maintainAspectRatio: false }
  });
}
