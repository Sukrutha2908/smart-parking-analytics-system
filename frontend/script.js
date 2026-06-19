'use strict';

/* ─────────────────────────────────────────────
   API
───────────────────────────────────────────── */

const API_BASE = '';

let allSlots = [];

let dashPage = 1;

const PER_PAGE = 200;

/* ─────────────────────────────────────────────
   Navigation
───────────────────────────────────────────── */

document.querySelectorAll('.nav-item').forEach(btn => {

  btn.addEventListener('click', () => {

    document
      .querySelectorAll('.nav-item')
      .forEach(b => b.classList.remove('active'));

    document
      .querySelectorAll('.view')
      .forEach(v => v.classList.remove('active'));

    btn.classList.add('active');

    const view = btn.dataset.view;

    document
      .getElementById('view-' + view)
      .classList.add('active');

    clearAlert();

    if (view === 'dashboard') {

      loadSummary();
    }

    if (view === 'slots') {

      loadDashboard();

      setTimeout(() => {
        
        renderSlots();
      
      }, 100);

    }

    if (view === 'logs') {

      loadLogs(1);
    }
  });
});

/* ─────────────────────────────────────────────
   Alerts
───────────────────────────────────────────── */

function showAlert(msg, type = 'success') {

  const box =
    document.getElementById('alertBox');

  box.textContent = msg;

  box.className = `alert ${type}`;

  box.classList.remove('hidden');

  setTimeout(() => {

    clearAlert();

  }, 4000);
}

function clearAlert() {

  document
    .getElementById('alertBox')
    .className = 'alert hidden';
}

/* ─────────────────────────────────────────────
   API Helper
───────────────────────────────────────────── */

async function api(path, options = {}) {

  try {

    const res = await fetch(
      API_BASE + path,
      {
        headers: {
          'Content-Type': 'application/json'
        },

        ...options
      }
    );

    const data = await res.json();

    return {
      ok: res.ok,
      status: res.status,
      data
    };

  } catch (err) {

    showAlert(
      'Cannot connect to backend',
      'error'
    );

    return {
      ok: false,
      status: 500,
      data: null
    };
  }
}

/* ─────────────────────────────────────────────
   Dashboard Summary
───────────────────────────────────────────── */

async function loadSummary() {

  const { ok, data } =
    await api('/slots/summary');

  if (!ok) return;

  document.getElementById('statTotal').textContent =
    data.total || 0;

  document.getElementById('statFree').textContent =
    data.free || 0;

  document.getElementById('statOcc').textContent =
    data.occupied || 0;

  const pct =
    (
      (data.occupied || 0) /
      (data.total || 1)
    ) * 100;

  document.getElementById('statPct').textContent =
    pct.toFixed(1) + '%';
}

/* ─────────────────────────────────────────────
   Load Dashboard
───────────────────────────────────────────── */

async function loadDashboard() {

  await loadSummary();

  const { ok, data } = await api('/slots');

  console.log(data);

  if (!ok) {

    showAlert(
      'Failed to load slots',
      'error'
    );

    return;
  }

  allSlots = data;

  renderSlots();
}
/* ─────────────────────────────────────────────
   Render Slots
───────────────────────────────────────────── */

function renderSlots() {

  const sf =
    document.getElementById('filterStatus')?.value || 'all';

  const nf =
    (
      document
      .getElementById('filterSlot')?.value || ''
    )
    .trim();

  let list = allSlots;

  const floor =
    document.getElementById('floorFilter')?.value || '';
  
  if (floor) {
    list = list.filter(
      s => s.floor === floor
    );
  }

  if (sf !== 'all') {

    list = list.filter(
      s => s.status === sf
    );
  }

  if (nf) {

    list = list.filter(
      s =>
        s.slot_id.toLowerCase().includes(
          nf.toLowerCase()
        )
    );
  }

  const pages = Math.max(
    1,
    Math.ceil(list.length / PER_PAGE)
  );

  if (dashPage > pages) {

    dashPage = pages;
  }

  const paged = list.slice(
    (dashPage - 1) * PER_PAGE,
    dashPage * PER_PAGE
  );

  document.getElementById('slotGrid').innerHTML =

    paged.length

      ? paged.map(s => `

        <div 
          class="slot ${s.status}"
          data-slot-id="${s.slot_id}">

          <div class="slot-num">
            ${s.slot_id}
          </div>

          <div class="slot-status">
            ${
              s.status
                ? s.status.charAt(0).toUpperCase() +
                  s.status.slice(1)
                : 'Unknown'
            }
          </div>

        </div>

      `).join('')

      : `
        <p style="
          color:var(--muted);
          padding:1rem
        ">
          No slots found.
        </p>
      `;

  buildPagination(
    'dashPagination',
    pages,
    dashPage,
    p => {

      dashPage = p;

      renderSlots();
    }
  );
}

/* ─────────────────────────────────────────────
   Register Entry
───────────────────────────────────────────── */

async function registerEntry() {

  const num =
    document.getElementById('vehicleNum')
      .value
      .trim()
      .toUpperCase();

  const vehicle_type =
    document.getElementById('vehicleType')
      .value;

  if (!num || !vehicle_type) {

    showAlert(
      'Enter vehicle number and select vehicle type.',
      'error'
    );

    return;
  }

  const { ok, data } =
    await api('/entry', {

      method: 'POST',

      body: JSON.stringify({

        vehicle_number: num,

        vehicle_type
      })
    });

  if (!ok) {

    showAlert(
      data.detail || 'Error',
      'error'
    );

    return;
  }

  showAlert(
    `Vehicle parked at ${data.slot_allocated}`
  );

  document.getElementById('vehicleNum').value = '';

  document.getElementById('vehicleType').value = '';

  loadDashboard();
}

/* ─────────────────────────────────────────────
   Process Exit
───────────────────────────────────────────── */

async function processExit() {

  const num =
    document.getElementById('exitVehicleNum')
      .value
      .trim()
      .toUpperCase();

  const bill =
    document.getElementById('billCard');

  if (!num) {

    showAlert(
      'Enter vehicle number.',
      'error'
    );

    return;
  }

  const { ok, data } =
    await api('/exit', {

      method: 'POST',

      body: JSON.stringify({
        vehicle_number: num
      })
    });

  if (!ok) {

    showAlert(
      data.detail || 'Error',
      'error'
    );

    bill.classList.add('hidden');

    return;
  }

  document.getElementById('exitVehicleNum').value = '';

  showAlert(
    data.message,
    'success'
  );

  loadSummary();

  bill.classList.remove('hidden');

  bill.innerHTML = `

    <h3 class="bill-title">
      Billing Summary
    </h3>

    <div class="bill-grid">

      <div class="bill-row">
        <span class="bill-label">Vehicle</span>
        <span class="bill-value">${data.vehicle_number}</span>
      </div>

      <div class="bill-row">
        <span class="bill-label">Slot</span>
        <span class="bill-value">
          ${data.slot_id} (${data.floor})
        </span>
      </div>

      <div class="bill-row">
        <span class="bill-label">Entry</span>
        <span class="bill-value">
          ${formatTime(data.entry_time)}
        </span>
      </div>

      <div class="bill-row">
        <span class="bill-label">Exit</span>
        <span class="bill-value">
          ${formatTime(data.exit_time)}
        </span>
      </div>

      <div class="bill-row">
        <span class="bill-label">Total Time</span>

        <span class="bill-value">

          ${
            data.duration_minutes < 60

              ? `${data.duration_minutes} Minutes`

              : `${Math.floor(data.duration_minutes / 60)}h ${data.duration_minutes % 60}m`
          }

        </span>
      </div>

      <div class="bill-row">
        <span class="bill-label">Rate</span>
        <span class="bill-value">
          ₹20 / hr
        </span>
      </div>

      <div class="bill-row total">
        <span class="bill-label">Total Fee</span>
        <span class="bill-value">
          ₹${data.fee}
        </span>
      </div>

    </div>
  `;
}

/* ─────────────────────────────────────────────
   Load Logs
───────────────────────────────────────────── */

async function loadLogs(page) {

  const status =
    document.getElementById('logStatus').value;

  const qs =
    `?page=${page}&limit=50${
      status
        ? '&status=' + status
        : ''
    }`;

  const { ok, data } =
    await api('/logs' + qs);

  if (!ok) return;

  const tbody =
    document.getElementById('logsBody');

  if (!data.logs.length) {

    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="empty">
          No records found.
        </td>
      </tr>
    `;

    document
      .getElementById('logPagination')
      .innerHTML = '';

    return;
  }

  tbody.innerHTML = data.logs.map(l => {

    const dur =
      l.fee != null
        ? calcDur(
            l.entry_time,
            l.exit_time
          )
        : '—';

    return `

      <tr>

        <td>
          <strong>
            ${l.vehicle_number}
          </strong>
        </td>

        <td>
          ${l.slot_id}
        </td>

        <td>
          ${formatTime(l.entry_time)}
        </td>

        <td>
          ${
            l.exit_time
              ? formatTime(l.exit_time)
              : '—'
          }
        </td>

        <td>
          ${dur}
        </td>

        <td>
          ${
            l.fee != null
              ? '₹' + l.fee
              : '—'
          }
        </td>

        <td>

          <span
            class="badge ${
              l.exit_time
                ? 'done'
                : 'active'
            }"
          >

            ${
              l.exit_time
                ? 'Exited'
                : 'Parked'
            }

          </span>

        </td>

      </tr>
    `;

  }).join('');

  const pages =
    Math.ceil(data.total / 50);

  buildPagination(
    'logPagination',
    pages,
    page,
    p => loadLogs(p)
  );
}

/* ─────────────────────────────────────────────
   Cleanup Logs
───────────────────────────────────────────── */

async function cleanupLogs() {

  if (
    !confirm(
      'Delete completed logs?'
    )
  ) return;

  const { ok, data } =
    await api('/logs/cleanup', {

      method: 'DELETE'
    });

  showAlert(

    ok
      ? `Deleted ${data.deleted} logs`
      : 'Error',

    ok
      ? 'success'
      : 'error'
  );

  if (ok) {

    loadLogs(1);
  }
}

/* ─────────────────────────────────────────────
   Reset System
───────────────────────────────────────────── */

async function resetAll() {

  if (
    !confirm(
      'Reset ALL slots and logs?'
    )
  ) return;

  const { ok, data } =
    await api('/reset', {

      method: 'POST'
    });

  showAlert(

    ok
      ? data.message
      : 'Error',

    ok
      ? 'success'
      : 'error'
  );

  if (ok) {

    loadDashboard();
  }
}

/* ─────────────────────────────────────────────
   Helpers
───────────────────────────────────────────── */

function formatTime(iso) {

  if (!iso) return '—';

  return new Date(iso)
    .toLocaleString('en-IN', {

      day: '2-digit',

      month: 'short',

      hour: '2-digit',

      minute: '2-digit'
    });
}

function calcDur(entry, exit) {

  const m = Math.floor(
    (
      new Date(exit) -
      new Date(entry)
    ) / 60000
  );

  return m >= 60

    ? `${Math.floor(m / 60)}h ${m % 60}m`

    : `${m}m`;
}

function buildPagination(
  id,
  total,
  current,
  onClick
) {

  const el =
    document.getElementById(id);

  if (total <= 1) {

    el.innerHTML = '';

    return;
  }

  let html = `
    <button
      class="page-btn"

      ${current === 1 ? 'disabled' : ''}

      onclick="(${onClick})(${current - 1})"
    >
      ←
    </button>
  `;

  for (let i = 1; i <= total; i++) {

    html += `

      <button

        class="
          page-btn
          ${i === current ? 'active' : ''}
        "

        onclick="(${onClick})(${i})"
      >

        ${i}

      </button>
    `;
  }

  html += `
    <button
      class="page-btn"

      ${current === total ? 'disabled' : ''}

      onclick="(${onClick})(${current + 1})"
    >
      →
    </button>
  `;

  el.innerHTML = html;
}

async function loadRevenueChart() {

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/analytics/revenue"
        );

        const data = await response.json();

        console.log("Revenue Data:", data);

        const labels =
            data.map(item => item.date);

        const revenues =
            data.map(item => item.revenue);

        const canvas =
            document.getElementById("revenueChart");

        if (!canvas) {

            console.error(
                "Revenue canvas not found"
            );

            return;
        }

        const ctx =
            canvas.getContext("2d");

        // destroy old chart if exists

        if (window.revenueChartInstance) {

            window.revenueChartInstance.destroy();
        }

        window.revenueChartInstance =
            new Chart(ctx, {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [{

                        label: "Revenue",

                        data: revenues,

                        borderColor: "#10b981",

                        backgroundColor:
                            "rgba(16,185,129,0.15)",

                        borderWidth: 3,

                        fill: true,

                        tension: 0.4,

                        pointRadius: 4

                    }]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            display: true
                        }
                    },

                    scales: {

                        y: {

                            beginAtZero: true
                        }
                    }
                }
            });

    } catch (error) {

        console.error(
            "Revenue chart error:",
            error
        );
    }
}

// ==========================
// FLOOR OCCUPANCY
// ==========================

async function loadFloorOccupancyCharts() {

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/slots"
        );

        const slots = await response.json();

        const floorStats = {};

        slots.forEach(slot => {

            const floor = slot.floor || "Unknown";

            if (!floorStats[floor]) {

                floorStats[floor] = {
                    total: 0,
                    occupied: 0
                };
            }

            floorStats[floor].total++;

            if (slot.status === "occupied") {

                floorStats[floor].occupied++;
            }
        });

        const floorGrid =
            document.getElementById("floorGrid");

        if (!floorGrid) return;

        floorGrid.innerHTML = "";

        Object.keys(floorStats).forEach(floor => {

            const stats = floorStats[floor];

            const percent =
                Math.round(
                    (stats.occupied / stats.total) * 100
                );

            floorGrid.innerHTML += `

                <div class="floor-card">

                    <div class="floor-title">
                        ${floor}
                    </div>

                    <div class="progress-bar">

                        <div 
                            class="progress-fill"
                            style="width:${percent}%"
                        ></div>

                    </div>

                    <div class="floor-percent">
                        ${percent}% Occupied
                    </div>

                </div>
            `;
        });

    } catch (error) {

        console.error(
            "Floor occupancy error:",
            error
        );
    }
}

/* ─────────────────────────────────────────────
   Load Charts
───────────────────────────────────────────── */

window.addEventListener("resize", () => {

    if (window.myOccupancyChart) {

        window.myOccupancyChart.resize();
    }

    if (window.myVehicleChart) {

        window.myVehicleChart.resize();
    }
});

document.getElementById(
  "currentDate"
).textContent = new Date()
.toLocaleDateString(
  "en-IN",
  {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric"
  }
);

/* =========================
   WINDOW LOAD
========================= */

window.onload = async () => {

    // Dashboard cards
    await loadSummary();

    // Slot page
    await loadDashboard();

    // Logs
    await loadLogs(1);

    // Revenue chart
    setTimeout(() => {

        if (document.getElementById("revenueChart")) {

            loadRevenueChart();
        }

    }, 500);

    // Floor occupancy
    setTimeout(() => {

        if (document.getElementById("floorGrid")) {

            loadFloorOccupancyCharts();
        }

    }, 800);

    // Current date
    const dateElement =
        document.getElementById("currentDate");

    if (dateElement) {

        dateElement.textContent =
            new Date().toLocaleDateString(
                "en-IN",
                {
                    weekday: "long",
                    day: "numeric",
                    month: "long",
                    year: "numeric"
                }
            );
    }
};

/* =========================
   WINDOW RESIZE
========================= */

window.addEventListener("resize", () => {

    if (window.myOccupancyChart) {

        window.myOccupancyChart.resize();
    }

    if (window.myVehicleChart) {

        window.myVehicleChart.resize();
    }
});

const socket = new WebSocket(
    "ws://127.0.0.1:8000/ws"
);

socket.onopen = () => {

    console.log(
        "WebSocket Connected"
    );

    socket.send("connected");
};

socket.onmessage = (event) => {

    const data = JSON.parse(
        event.data
    );

    console.log(
        "Live Update:",
        data
    );

    const slotCard = document.querySelector(

        `[data-slot-id="${data.slot_id}"]`
    );

    if (slotCard) {

        if (data.status === "occupied") {

            slotCard.classList.remove(
                "free"
            );

            slotCard.classList.add(
                "occupied"
            );

            slotCard.innerHTML = `

                <h3>${data.slot_id}</h3>

                <p>Occupied</p>
            `;
        }

        else {

            slotCard.classList.remove(
                "occupied"
            );

            slotCard.classList.add(
                "free"
            );

            slotCard.innerHTML = `

                <h3>${data.slot_id}</h3>

                <p>Free</p>
            `;
        }
    }
};