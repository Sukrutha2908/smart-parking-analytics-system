'use strict';

const API_BASE = '';

let allSlots = [];
let dashPage = 1;
const PER_PAGE = 200;

// ── Nav ───────────────────────────────────────────────────────────────────────
document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    btn.classList.add('active');
    const view = btn.dataset.view;
    document.getElementById('view-' + view).classList.add('active');
    clearAlert();
    if (view === 'dashboard') { dashPage = 1; loadDashboard(); }
    if (view === 'logs')      loadLogs(1);
  });
});

// ── Alert ─────────────────────────────────────────────────────────────────────
function showAlert(msg, type) {
  const box = document.getElementById('alertBox');
  box.textContent = msg;
  box.className = 'alert ' + type;
  setTimeout(() => clearAlert(), 5000);
}
function clearAlert() {
  document.getElementById('alertBox').className = 'alert hidden';
}

// ── API helper ────────────────────────────────────────────────────────────────
async function api(path, options = {}) {
  try {
    const res = await fetch(API_BASE + path, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    const data = await res.json();
    document.getElementById('apiBanner').classList.add('hidden');
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    document.getElementById('apiBanner').classList.remove('hidden');
    return { ok: false, status: 0, data: { detail: 'Cannot reach server.' } };
  }
}

// ── Stats ─────────────────────────────────────────────────────────────────────
async function loadSummary() {
  const { ok, data } = await api('/slots/summary');
  if (!ok) return;
  document.getElementById('statTotal').textContent = data.total;
  document.getElementById('statFree').textContent  = data.free;
  document.getElementById('statOcc').textContent   = data.occupied;
  document.getElementById('statPct').textContent = ((data.occupied / data.total) * 100).toFixed(1) + '%';
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
async function loadDashboard() {
  await loadSummary();
  const { ok, data } = await api('/slots');
  if (!ok) return;
  allSlots = data;
  renderSlots();
}

function renderSlots() {
  const sf = document.getElementById('filterStatus').value;
  const nf = (document.getElementById('filterSlot').value || '').trim();

  let list = allSlots;
  if (sf !== 'all') list = list.filter(s => s.status === sf);
  if (nf)           list = list.filter(s => String(s.slot_number).startsWith(nf));

  const pages = Math.max(1, Math.ceil(list.length / PER_PAGE));
  if (dashPage > pages) dashPage = pages;
  const paged = list.slice((dashPage - 1) * PER_PAGE, dashPage * PER_PAGE);

 document.getElementById('slotGrid').innerHTML = paged.length
  ? paged.map(s => `
      <div class="slot ${s.status}" onclick="${s.status === 'free' ? `quickPark(${s.slot_number})` : ''}">
        <div class="slot-num">P${String(s.slot_number).padStart(3, '0')}</div>

        <div class="slot-status">
          ${s.status.charAt(0).toUpperCase() + s.status.slice(1)}
        </div>

      </div>`).join('')
  : '<p style="color:var(--muted);padding:1rem">No slots match.</p>';
  buildPagination('dashPagination', pages, dashPage, p => { dashPage = p; renderSlots(); });
}

async function quickPark(slotNum) {
  const veh = prompt(`Park in slot P${String(slotNum).padStart(3, '0')} — enter vehicle number:`);
  if (!veh || !veh.trim()) return;
  const { ok, data } = await api('/entry', {
    method: 'POST',
    body: JSON.stringify({ vehicle_number: veh.trim().toUpperCase() })
  });
  showAlert(ok ? data.message : (data.detail || 'Error'), ok ? 'success' : 'error');
  if (ok) loadDashboard();
}

// ── Entry ─────────────────────────────────────────────────────────────────────
async function registerEntry() {
  const num = document.getElementById('vehicleNum').value.trim().toUpperCase();
  const box = document.getElementById('entryResult');
  if (!num) { showResult(box, 'Enter a vehicle number.', false); return; }

  const { ok, data } = await api('/entry', {
    method: 'POST',
    body: JSON.stringify({ vehicle_number: num })
  });
  showResult(box,
    ok ? `✅ ${data.message}  |  Entry: ${formatTime(data.entry_time)}`
       : `❌ ${data.detail || 'Error'}`, ok);
  if (ok) { document.getElementById('vehicleNum').value = ''; loadSummary(); }
}

function showResult(box, msg, ok) {
  box.className = 'result-box ' + (ok ? 'success' : 'error');
  box.textContent = msg;
}
nt   = data.occupied;
  
// ── Exit ──────────────────────────────────────────────────────────────────────
async function processExit() {
  const num  = document.getElementById('exitVehicleNum').value.trim().toUpperCase();
  const bill = document.getElementById('billCard');
  if (!num) { showAlert('Enter a vehicle number.', 'error'); return; }

  const { ok, data } = await api('/exit', {
    method: 'POST',
    body: JSON.stringify({ vehicle_number: num })
  });

  if (!ok) { showAlert(data.detail || 'Error', 'error'); bill.classList.add('hidden'); return; }

  document.getElementById('exitVehicleNum').value = '';
  showAlert(data.message, 'success');
  loadSummary();

  bill.classList.remove('hidden');
  bill.innerHTML = `
    <h3>Billing Summary</h3>
    <div class="bill-row"><span>Vehicle</span><span>${data.vehicle_number}</span></div>
    <div class="bill-row"><span>Slot</span><span>P${String(data.slot_number).padStart(3,'0')}</span></div>
    <div class="bill-row"><span>Entry</span><span>${formatTime(data.entry_time)}</span></div>
    <div class="bill-row"><span>Exit</span><span>${formatTime(data.exit_time)}</span></div>
    <div class="bill-row"><span>Duration</span><span>${data.duration}</span></div>
    <div class="bill-row"><span>Rate</span><span>₹20 / hr</span></div>
    <div class="bill-row"><span>Total Fee</span><span>₹${data.fee}</span></div>`;
}

// ── Logs ──────────────────────────────────────────────────────────────────────
async function loadLogs(page) {
  const status = document.getElementById('logStatus').value;
  const qs = `?page=${page}&limit=50${status ? '&status=' + status : ''}`;
  const { ok, data } = await api('/logs' + qs);
  if (!ok) return;

  const tbody = document.getElementById('logsBody');
  if (!data.logs.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty">No records found.</td></tr>';
    document.getElementById('logPagination').innerHTML = '';
    return;
  }

  tbody.innerHTML = data.logs.map(l => {
    const dur = l.exit_time && l.entry_time ? calcDur(l.entry_time, l.exit_time) : '—';
    return `<tr>
      <td><strong>${l.vehicle_number}</strong></td>
      <td>P${String(l.slot_number).padStart(3,'0')}</td>
      <td>${formatTime(l.entry_time)}</td>
      <td>${l.exit_time ? formatTime(l.exit_time) : '—'}</td>
      <td>${dur}</td>
      <td>${l.fee != null ? '₹' + l.fee : '—'}</td>
      <td><span class="badge ${l.exit_time ? 'done' : 'active'}">${l.exit_time ? 'Exited' : 'Parked'}</span></td>
    </tr>`;
  }).join('');

  const pages = Math.ceil(data.total / 50);
  buildPagination('logPagination', pages, page, p => loadLogs(p));
}

async function cleanupLogs() {
  if (!confirm('Delete all completed parking logs?')) return;
  const { ok, data } = await api('/logs/cleanup', { method: 'DELETE' });
  showAlert(ok ? `Deleted ${data.deleted} completed log(s).` : 'Error', ok ? 'success' : 'error');
  if (ok) loadLogs(1);
}

async function resetAll() {
  if (!confirm('Reset ALL slots to free and clear all logs? This cannot be undone.')) return;
  const { ok, data } = await api('/reset', { method: 'POST' });
  showAlert(ok ? data.message : 'Error', ok ? 'success' : 'error');
  if (ok) loadDashboard();
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
  });
}

function calcDur(entry, exit) {
  const m = Math.floor((new Date(exit) - new Date(entry)) / 60000);
  return m >= 60 ? `${Math.floor(m/60)}h ${m%60}m` : `${m}m`;
}

function buildPagination(id, total, current, onClick) {
  const el = document.getElementById(id);
  if (total <= 1) { el.innerHTML = ''; return; }
  let html = '';
  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || Math.abs(i - current) <= 2) {
      html += `<button class="page-btn ${i === current ? 'active' : ''}" onclick="(${onClick})(${i})">${i}</button>`;
    } else if (Math.abs(i - current) === 3) {
      html += `<span class="page-btn" style="cursor:default">…</span>`;
    }
  }
  el.innerHTML = html;
}

// ── Init ──────────────────────────────────────────────────────────────────────
loadDashboard();