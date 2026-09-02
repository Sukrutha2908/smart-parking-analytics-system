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
   COUNT-UP ANIMATION
   (one deliberate motion moment for stat values)
========================================= */

function animateValue(el, endValue, suffix = '') {

    if (!el) return;

    const start = parseFloat(el.dataset.raw || '0') || 0;
    const end = parseFloat(endValue) || 0;
    const duration = 500;
    const startTime = performance.now();

    function tick(now) {

        const progress = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * eased;

        el.textContent =
            (suffix === '%'
                ? current.toFixed(1)
                : Math.round(current)) + suffix;

        if (progress < 1) {
            requestAnimationFrame(tick);
        } else {
            el.dataset.raw = end;
        }
    }

    requestAnimationFrame(tick);
}

/* =========================================
   SUMMARY
========================================= */

async function loadSummary() {

    const { ok, data } =
        await api('/slots/summary');

    if (!ok) return;

    animateValue(document.getElementById('statTotal'), data.total || 0);
    animateValue(document.getElementById('statFree'), data.free || 0);
    animateValue(document.getElementById('statOcc'), data.occupied || 0);

    const occupancy =
        data.total ? ((data.occupied / data.total) * 100) : 0;

    animateValue(document.getElementById('statPct'), occupancy, '%');
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

        const { ok, data } =
            await api(
                `/analytics/revenue?filter=${filter}`
            );

        if (!ok || !data) {

            console.error(
                "Revenue API failed:",
                data
            );

            return;
        }

        console.log(
            "Revenue data:",
            data
        );


        const labels = data.labels || [];

        const values = data.values || [];


        const canvas =
            document.getElementById(
                "revenueChart"
            );

        if (!canvas) {

            console.error(
                "revenueChart canvas not found"
            );

            return;
        }


        const ctx =
            canvas.getContext("2d");


        // Destroy old chart
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

                        data: values,

                        borderColor: "#2A4F8F",

                        backgroundColor:
                            "rgba(42,79,143,0.10)",

                        fill: true,

                        tension: 0.35,

                        borderWidth: 2.5,

                        pointRadius: 4,

                        pointBackgroundColor:
                            "#2A4F8F",

                        pointBorderColor:
                            "#ffffff",

                        pointBorderWidth: 1.5

                    }]
                },


                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {
                            display: false
                        },

                        tooltip: {

                            callbacks: {

                                label: function(context) {

                                    return " ₹" +
                                        Number(
                                            context.raw
                                        ).toLocaleString(
                                            "en-IN"
                                        );
                                }

                            }

                        }

                    },


                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                callback: function(value) {

                                    return "₹" +
                                        Number(value)
                                            .toLocaleString(
                                                "en-IN"
                                            );

                                }

                            }

                        },


                        x: {

                            grid: {
                                display: false
                            }

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

                <h4>${floor}</h4>

                <div class="small-chart">

                    <canvas id="${chartId}"></canvas>

                </div>

                <p>${occupied}% occupied</p>

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
                            '#C4443A',
                            '#1E8E5A'
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

                    cutout: '72%'
                }
            });
        });
    });
}

/* =========================================
   VEHICLE DISTRIBUTION
========================================= */

/* =========================================
   VEHICLE DISTRIBUTION
========================================= */

async function loadVehicleDistribution() {

    try {

        const { ok, data } =
            await api('/analytics/vehicle-distribution');

        if (!ok || !data) {

            console.error(
                "Vehicle distribution API failed:",
                data
            );

            return;
        }

        /*
         * Backend already returns percentages:
         *
         * {
         *   cars: 14,
         *   bikes: 57,
         *   trucks: 29
         * }
         */

        const carPercent =
            Number(data.cars) || 0;

        const bikePercent =
            Number(data.bikes) || 0;

        const truckPercent =
            Number(data.trucks) || 0;


        document.getElementById(
            "carPercent"
        ).innerText =
            `${carPercent}%`;

        document.getElementById(
            "bikePercent"
        ).innerText =
            `${bikePercent}%`;

        document.getElementById(
            "truckPercent"
        ).innerText =
            `${truckPercent}%`;


        document.getElementById(
            "carBar"
        ).style.width =
            `${carPercent}%`;

        document.getElementById(
            "bikeBar"
        ).style.width =
            `${bikePercent}%`;

        document.getElementById(
            "truckBar"
        ).style.width =
            `${truckPercent}%`;


    } catch (error) {

        console.error(
            "Vehicle distribution error:",
            error
        );
    }
}

/* =========================================
   ENTRY
========================================= */

async function registerEntry() {

    const vehicleNumber =
        document.getElementById(
            "vehicleNum"
        ).value
        .trim()
        .toUpperCase();

    const vehicleType =
        document.getElementById(
            "vehicleType"
        ).value;

    if (!vehicleNumber || !vehicleType) {

        showAlert(
            "Enter vehicle number and select vehicle type",
            "error"
        );

        return;
    }

    try {

        const response = await fetch(

            "http://127.0.0.1:8000/entry",

            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    vehicle_number: vehicleNumber,

                    vehicle_type: vehicleType
                })
            }
        );

        const data = await response.json();

        if (data.error || data.detail) {

            showAlert(
                data.error || data.detail,
                "error"
            );

            return;
        }

        showAlert(
            `Vehicle registered — slot ${data.slot_allocated} assigned`
        );

        // Clear fields

        document.getElementById(
            "vehicleNum"
        ).value = "";

        document.getElementById(
            "vehicleType"
        ).value = "";

        // Reload dashboard

        loadDashboardData();

        loadSlots();

        loadLogs();

    } catch (error) {

        console.log(error);

        showAlert("Entry failed", "error");
    }
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
            data?.detail || 'Error processing exit',
            'error'
        );

        return;
    }

    showAlert(data.message);

    document.getElementById(
        "billingResult"
    ).innerHTML = `

        <div class="receipt">

            <div class="receipt-head">
                <h3>Billing receipt</h3>
                <span>#${data.billing_id}</span>
            </div>

            <div class="receipt-row">
                <span class="label">Vehicle number</span>
                <span class="value">${data.vehicle_number}</span>
            </div>

            <div class="receipt-row">
                <span class="label">Slot</span>
                <span class="value">${data.slot_id} · ${data.floor}</span>
            </div>

            <div class="receipt-row">
                <span class="label">Entry time</span>
                <span class="value">${formatTime(data.entry_time)}</span>
            </div>

            <div class="receipt-row">
                <span class="label">Exit time</span>
                <span class="value">${formatTime(data.exit_time)}</span>
            </div>

            <div class="receipt-row">
                <span class="label">Duration</span>
                <span class="value">${data.duration_minutes} min</span>
            </div>

            <div class="receipt-row">
                <span class="label">Rate</span>
                <span class="value">₹${data.rate_per_hour}/hour</span>
            </div>

            <div class="receipt-total">
                <span class="label">Total fee</span>
                <span class="value">₹${data.fee}</span>
            </div>

        </div>
    `;

    loadDashboardData();

    loadSlots();
}

/* =========================================
   LOAD LOGS
========================================= */

async function loadLogs(page = 1) {

    const search =
        document.getElementById('searchVehicle')?.value || '';

    const status =
        document.getElementById('logStatusFilter')?.value || '';

    const { ok, data } =
        await api(
            `/logs?page=${page}&limit=50&vehicle_number=${search}&status=${status}`
        );

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

const connStatusEl = document.getElementById('connStatus');
const connStatusLabel = document.getElementById('connStatusLabel');

function setConnStatus(live) {

    if (!connStatusEl) return;

    connStatusEl.classList.toggle('live', live);

    if (connStatusLabel) {
        connStatusLabel.textContent = live ? 'Live' : 'Reconnecting…';
    }
}

const socket =
    new WebSocket(
        'ws://127.0.0.1:8000/ws'
    );

socket.onopen = () => {

    setConnStatus(true);
};

socket.onclose = () => {

    setConnStatus(false);
};

socket.onerror = () => {

    setConnStatus(false);
};

socket.onmessage = async (event) => {

    const data =
        JSON.parse(event.data);

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
   FILTER LISTENERS
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

document
    .getElementById("weekFilter")
    ?.addEventListener("change", async function () {

        await loadRevenueChart(this.value);
    });

/* =========================================
   WINDOW LOAD
========================================= */

window.onload = async () => {

    await loadDashboardData();

    await loadSlots();

    await loadLogs();

};