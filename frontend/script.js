'use strict';

/* =========================================
   API
========================================= */

const API_BASE = '';

let allSlots = [];

let dashPage = 1;

const PER_PAGE = 200;

/* =========================================
   NAVIGATION
========================================= */

document.querySelectorAll('.nav-item').forEach(btn => {

    btn.addEventListener('click', () => {

        document.querySelectorAll('.nav-item')
            .forEach(b => b.classList.remove('active'));

        document.querySelectorAll('.view')
            .forEach(v => v.classList.remove('active'));

        btn.classList.add('active');

        const view = btn.dataset.view;

        document
            .getElementById('view-' + view)
            .classList.add('active');

        if (view === 'dashboard') {

            loadDashboardData();
        }

        if (view === 'slots') {

            loadSlots();
        }

        if (view === 'logs') {

            loadLogs(1);
        }
    });
});

/* =========================================
   ALERTS
========================================= */

function showAlert(message, type = 'success') {

    const box =
        document.getElementById('alertBox');

    if (!box) return;

    box.textContent = message;

    box.className = `alert ${type}`;

    box.classList.remove('hidden');

    setTimeout(() => {

        box.classList.add('hidden');

    }, 3000);
}

/* =========================================
   API HELPER
========================================= */

async function api(path, options = {}) {

    try {

        const response = await fetch(
            API_BASE + path,
            {
                headers: {
                    'Content-Type': 'application/json'
                },
                ...options
            }
        );

        const data = await response.json();

        return {
            ok: response.ok,
            data
        };

    } catch (error) {

        console.error(error);

        return {
            ok: false,
            data: null
        };
    }
}

/* =========================================
   SUMMARY
========================================= */

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

    const occupancy =
        ((data.occupied / data.total) * 100).toFixed(1);

    document.getElementById('statPct').textContent =
        occupancy + '%';
}

/* =========================================
   LOAD DASHBOARD
========================================= */

async function loadDashboardData() {

    await loadSummary();

    await loadRevenueChart();

    await loadFloorOccupancy();

    loadVehicleDistribution();
}

/* =========================================
   LOAD SLOTS
========================================= */

async function loadSlots() {

    const { ok, data } =
        await api('/slots');

    if (!ok) return;

    allSlots = data;

    renderSlots();
}

/* =========================================
   RENDER SLOTS
========================================= */

function renderSlots() {

    const grid =
        document.getElementById('slotGrid');

    if (!grid) return;

    grid.innerHTML = '';
    
    const floorFilter =
        document.getElementById('floorFilter')?.value;

    const statusFilter =
        document.getElementById('statusFilter')?.value;

    let filteredSlots =
        allSlots;
        
    if (
        floorFilter &&
        floorFilter !== 'all'
    ) {

        filteredSlots =
            filteredSlots.filter(
                slot =>
                    slot.floor === floorFilter
            );
    }

    if (
        statusFilter &&
        statusFilter !== 'all'
    ) {

        filteredSlots =
            filteredSlots.filter(
                slot =>
                    slot.status === statusFilter
            );
    }

    filteredSlots.forEach(slot => {

        grid.innerHTML += `

            <div
                class="slot ${slot.status}"
                data-slot-id="${slot.slot_id}"
            >

                <h3>${slot.slot_id}</h3>

                <p>
                    ${slot.status}
                </p>

            </div>
        `;
    });
}

/* =========================================
   REVENUE CHART
========================================= */

async function loadRevenueChart(filter = "current") {

    try {

        const response =
            await fetch(
                `http://127.0.0.1:8000/analytics/weekly-revenue?filter=${filter}`
            );

        const data =
            await response.json();

        console.log("Revenue Data:", data);

        const labels = data.labels;

        const values = data.values;

        const canvas =
            document.getElementById(
                "revenueChart"
            );

        if (!canvas) return;

        const ctx =
            canvas.getContext("2d");

        if (window.revenueChartInstance) {

            window.revenueChartInstance.destroy();
        }

        window.revenueChartInstance =
            new Chart(ctx, {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [{

                        label: "Weekly Revenue",

                        data: values,

                        borderColor: "#28C7A1",

                        backgroundColor:
                            "rgba(93,248,216,0.18)",

                        fill: true,

                        tension: 0.4,

                        borderWidth: 3,

                        pointBackgroundColor:
                            "#28C7A1",

                        pointRadius: 5
                    }]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

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

/* =========================================
   FLOOR OCCUPANCY
========================================= */

async function loadFloorOccupancy() {

    const { ok, data } =
        await api('/slots');

    if (!ok) return;

    const floors = {};

    data.forEach(slot => {

        if (!floors[slot.floor]) {

            floors[slot.floor] = {

                total: 0,

                occupied: 0
            };
        }

        floors[slot.floor].total++;

        if (slot.status === 'occupied') {

            floors[slot.floor].occupied++;
        }
    });

    const floorGrid =
        document.getElementById('floorGrid');

    if (!floorGrid) return;

    floorGrid.innerHTML = '';

    let chartIndex = 0;

    Object.keys(floors).forEach(floor => {

        const stats = floors[floor];

        const occupied =
            Math.round(
                (stats.occupied / stats.total) * 100
            );

        const free =
            100 - occupied;

        const chartId =
            `floorChart${chartIndex}`;

        floorGrid.innerHTML += `

            <div class="floor-item">

                <h3>${floor}</h3>

                <div class="small-chart">

                    <canvas id="${chartId}"></canvas>

                </div>

                <p>${occupied}% Occupied</p>

            </div>
        `;

        chartIndex++;

        requestAnimationFrame(() => {

            const canvas =
                document.getElementById(chartId);

            if (!canvas) return;

            const ctx =
                canvas.getContext('2d');

            new Chart(ctx, {

                type: 'doughnut',

                data: {

                    labels: [
                        'Occupied',
                        'Free'
                    ],

                    datasets: [{

                        data: [
                            occupied,
                            free
                        ],

                        backgroundColor: [
                            '#ef4444',
                            '#10b981'
                        ],

                        borderWidth: 0
                    }]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    animation: false,

                    plugins: {

                        legend: {
                            display: false
                        }
                    },

                    cutout: '70%'
                }
            });
        });
    });
}

/* =========================================
   VEHICLE DISTRIBUTION
========================================= */

async function loadVehicleDistribution(){

    const response = await fetch(
        "http://127.0.0.1:8000/analytics/vehicle-distribution"
    );

    const data = await response.json();

    const total = data.total || 1;

    const carPercent =
        (data.cars / total) * 100;

    const bikePercent =
        (data.bikes / total) * 100;

    const truckPercent =
        (data.trucks / total) * 100;

    document.getElementById("carBar")
        .style.width = `${carPercent}%`;

    document.getElementById("bikeBar")
        .style.width = `${bikePercent}%`;

    document.getElementById("truckBar")
        .style.width = `${truckPercent}%`;

    document.getElementById("carPercent")
        .innerText = `${carPercent.toFixed(0)}%`;

    document.getElementById("bikePercent")
        .innerText = `${bikePercent.toFixed(0)}%`;

    document.getElementById("truckPercent")
        .innerText = `${truckPercent.toFixed(0)}%`;
}

loadVehicleDistribution();


/* =========================================
   ENTRY
========================================= */

async function registerEntry() {

    const vehicle_number =
        document.getElementById('vehicleNum')
            .value
            .trim()
            .toUpperCase();

    const vehicle_type =
        document.getElementById('vehicleType')
            .value;

    if (!vehicle_number || !vehicle_type) {

        showAlert(
            'Enter vehicle details',
            'error'
        );

        return;
    }

    const { ok, data } =
        await api('/entry', {

            method: 'POST',

            body: JSON.stringify({

                vehicle_number,
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
        `Allocated ${data.slot_allocated}`
    );

    loadDashboardData();

    loadSlots();
}

/* =========================================
   EXIT
========================================= */

async function processExit() {

    const vehicle_number =
        document.getElementById('exitVehicleNum')
            .value
            .trim()
            .toUpperCase();

    if (!vehicle_number) {

        showAlert(
            'Enter vehicle number',
            'error'
        );

        return;
    }

    const { ok, data } =
        await api('/exit', {

            method: 'POST',

            body: JSON.stringify({
                vehicle_number
            })
        });

    if (!ok) {

        showAlert(
            data.detail || 'Error',
            'error'
        );

        return;
    }

    showAlert(data.message);

    loadDashboardData();

    loadSlots();
}

/* =========================================
   LOAD LOGS
========================================= */

async function loadLogs(page = 1) {

    const { ok, data } =
        await api(`/logs?page=${page}&limit=50`);

    if (!ok) return;

    const tbody =
        document.getElementById('logsBody');

    if (!tbody) return;

    tbody.innerHTML = '';

    data.logs.forEach(log => {

        tbody.innerHTML += `

            <tr>

                <td>
                    ${log.vehicle_number || '-'}
                </td>

                <td>
                    ${log.slot_id || '-'}
                </td>

                <td>
                    ${
                        log.entry_time
                        ? formatTime(log.entry_time)
                        : '-'
                    }
                </td>

                <td>
                    ${
                        log.exit_time
                        ? formatTime(log.exit_time)
                        : '-'
                    }
                </td>

                <td>
                    ${log.duration || '-'}
                </td>

                <td>
                    ₹${log.fee || 0}
                </td>

                <td>

                    <span class="
                        status
                        ${log.status}
                    ">
                        ${log.status || 'occupied'}
                    </span>

                </td>

            </tr>
        `;
    });
}

/* =========================================
   FORMAT TIME
========================================= */

function formatTime(time) {

    if (!time) return '-';

    return new Date(time)
        .toLocaleString('en-IN');
}

/* =========================================
   WEBSOCKET
========================================= */

const socket =
    new WebSocket(
        'ws://127.0.0.1:8000/ws'
    );

socket.onopen = () => {

    console.log(
        'WebSocket Connected'
    );
};

socket.onmessage = async (event) => {

    const data =
        JSON.parse(event.data);

    console.log(
        'Live Update:',
        data
    );

    const slotCard =
        document.querySelector(

            `[data-slot-id="${data.slot_id}"]`
        );

    if (slotCard) {

        slotCard.classList.remove(
            'free',
            'occupied'
        );

        slotCard.classList.add(
            data.status
        );

        slotCard.innerHTML = `

            <h3>${data.slot_id}</h3>

            <p>${data.status}</p>
        `;
    }

    await loadSummary();

    await loadFloorOccupancy();

        loadVehicleDistribution();
};

/* =========================================
   CURRENT DATE
========================================= */

const dateBox =
    document.getElementById(
        'currentDate'
    );

if (dateBox) {

    dateBox.textContent =
        new Date().toLocaleDateString(
            'en-IN',
            {
                weekday: 'long',
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            }
        );
}

/* =========================================
   WINDOW LOAD
========================================= */

document
    .getElementById('floorFilter')
    ?.addEventListener(
        'change',
        renderSlots
    );

document
    .getElementById('statusFilter')
    ?.addEventListener(
        'change',
        renderSlots
    );

window.onload = async () => {

    await loadDashboardData();

    await loadSlots();

    await loadLogs();

    await loadRevenueChart();

    await loadFloorOccupancy();

     loadVehicleDistribution(); 

};

document
    .getElementById("weekFilter")
    .addEventListener("change", async function () {

        await loadRevenueChart(this.value);
    });