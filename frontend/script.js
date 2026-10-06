'use strict';

/* =========================================
   AUTHENTICATION GUARD
========================================= */

'use strict';

/* =========================================
   AUTHENTICATION GUARD
========================================= */

const accessToken = localStorage.getItem('access_token');

if (!accessToken) {
    window.location.replace('/login');
}


/* =========================================
   WELCOME POPUP
========================================= */

function showWelcomePopup() {

    if (!accessToken) return;

    try {

        /*
         * Decode the JWT payload
         */
        const payload =
            JSON.parse(
                atob(
                    accessToken.split('.')[1]
                        .replace(/-/g, '+')
                        .replace(/_/g, '/')
                )
            );

        /*
         * Try common username fields
         */
        const username =
            payload.username ||
            payload.user_name ||
            payload.name ||
            payload.sub ||
            'User';

        /*
         * Show popup only for a new login token.
         * Refreshing the dashboard will not show it again.
         */
        const previousToken =
            sessionStorage.getItem(
                'welcome_token'
            );

        if (previousToken === accessToken) {
            return;
        }

        sessionStorage.setItem(
            'welcome_token',
            accessToken
        );


        const popup =
            document.createElement('div');

        popup.className =
            'welcome-popup';

        popup.innerHTML = `

            <div class="welcome-popup-content">

                <div class="welcome-icon">
                    👋
                </div>

                <div>

                    <h3>
                        Hi, ${username}!
                    </h3>

                    <p>
                        Welcome back to Smart Parking Analytics.
                    </p>

                </div>

            </div>

        `;

        document.body.appendChild(popup);


        setTimeout(() => {

            popup.classList.add('show');

        }, 50);


        setTimeout(() => {

            popup.classList.remove('show');

            setTimeout(() => {

                popup.remove();

            }, 300);

        }, 3000);


    } catch (error) {

        console.error(
            'Welcome popup error:',
            error
        );
    }
}

if (accessToken) {
    setTimeout(showWelcomePopup, 300);
}


/* =========================================
   API
========================================= */

const API_BASE = window.location.origin;

let allSlots = [];

const PER_PAGE = 50;

let currentLogsPage = 1;
let currentSlotsPage = 1;

/* =========================================
   TOAST NOTIFICATIONS
========================================= */

function showToast(message, type = 'info', duration = 3000) {

    let container =
        document.getElementById('toastContainer');

    // Create container if it doesn't exist
    if (!container) {

        container =
            document.createElement('div');

        container.id = 'toastContainer';

        container.className =
            'toast-container';

        document.body.appendChild(container);
    }


    const toast =
        document.createElement('div');

    toast.className =
        `toast ${type}`;


    let icon = 'ℹ';

    if (type === 'success') {
        icon = '✓';
    }

    if (type === 'error') {
        icon = '✕';
    }

    if (type === 'warning') {
        icon = '⚠';
    }


    toast.innerHTML = `
        <span class="toast-icon">
            ${icon}
        </span>

        <span class="toast-message">
            ${message}
        </span>
    `;


    container.appendChild(toast);


    // Show
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);


    // Remove
    setTimeout(() => {

        toast.classList.remove('show');

        setTimeout(() => {
            toast.remove();
        }, 300);

    }, duration);
}

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

        const targetView =
            document.getElementById('view-' + view);

        if (targetView) {
            targetView.classList.add('active');
        }

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
   API HELPER
========================================= */

async function api(path, options = {}) {

    try {

        const token =
            localStorage.getItem('access_token');

        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        if (token) {

            headers['Authorization'] =
                `Bearer ${token}`;
        }

        const response =
            await fetch(
                API_BASE + path,
                {
                    ...options,
                    headers
                }
            );


        /* JWT expired / invalid */

        if (response.status === 401) {

            localStorage.removeItem(
                'access_token'
            );

            window.location.replace('/login');

            return {
                ok: false,
                data: null
            };
        }


        const data =
            await response.json();


        return {
            ok: response.ok,
            data
        };


    } catch (error) {

        console.error(
            'API Error:',
            error
        );

        return {
            ok: false,
            data: null
        };
    }
}


/* =========================================
   COUNT-UP ANIMATION
========================================= */

function animateValue(
    el,
    endValue,
    suffix = ''
) {

    if (!el) return;

    const start =
        parseFloat(
            el.dataset.raw || '0'
        ) || 0;

    const end =
        parseFloat(endValue) || 0;

    const duration = 500;

    const startTime =
        performance.now();


    function tick(now) {

        const progress =
            Math.min(
                (now - startTime) / duration,
                1
            );

        const eased =
            1 - Math.pow(
                1 - progress,
                3
            );

        const current =
            start +
            (end - start) *
            eased;


        el.textContent =
            (
                suffix === '%'
                    ? current.toFixed(1)
                    : Math.round(current)
            ) + suffix;


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

    if (!ok || !data) return;


    animateValue(
        document.getElementById('statTotal'),
        data.total || 0
    );


    animateValue(
        document.getElementById('statFree'),
        data.free || 0
    );


    animateValue(
        document.getElementById('statOcc'),
        data.occupied || 0
    );


    const occupancy =
        data.total
            ? (
                data.occupied /
                data.total
            ) * 100
            : 0;


    animateValue(
        document.getElementById('statPct'),
        occupancy,
        '%'
    );
}


/* =========================================
   LOAD DASHBOARD
========================================= */

async function loadDashboardData() {

    await loadSummary();

    await loadRevenueChart();

    await loadFloorOccupancy();

    await loadVehicleDistribution();
}


/* =========================================
   LOAD SLOTS
========================================= */

async function loadSlots() {

    const { ok, data } =
        await api('/slots');

    if (!ok || !data) return;

    allSlots = data;

    renderSlots();
}



/* =========================================
   RENDER SLOTS
========================================= */

function renderSlots(page = 1) {

    currentSlotsPage = page;

    const grid =
        document.getElementById('slotGrid');

    if (!grid) return;

    grid.innerHTML = '';

    const floorFilter =
        document.getElementById('floorFilter')?.value || 'all';

    const statusFilter =
        document.getElementById('statusFilter')?.value || 'all';


    /* -------------------------------------
       FILTER SLOTS
    ------------------------------------- */

    let filteredSlots = [...allSlots];


    // Floor filter
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


    // Status filter
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


    /* -------------------------------------
       PAGINATION
    ------------------------------------- */

    const totalSlots =
        filteredSlots.length;

    const totalPages =
        Math.ceil(
            totalSlots / PER_PAGE
        );


    // If current page is greater than
    // available pages, move to last page
    if (
        page > totalPages &&
        totalPages > 0
    ) {

        page = totalPages;

        currentSlotsPage = page;
    }


    const startIndex =
        (page - 1) * PER_PAGE;

    const endIndex =
        startIndex + PER_PAGE;


    const pageSlots =
        filteredSlots.slice(
            startIndex,
            endIndex
        );


    /* -------------------------------------
       NO SLOTS
    ------------------------------------- */

    if (!pageSlots.length) {

        grid.innerHTML = `

            <div
                style="
                    grid-column: 1 / -1;
                    text-align: center;
                    padding: 30px;
                    color: #6B7688;
                "
            >
                No parking slots found
            </div>

        `;

        renderSlotsPagination(
            totalPages,
            currentSlotsPage,
            totalSlots
        );

        return;
    }


    /* -------------------------------------
       RENDER CURRENT PAGE
    ------------------------------------- */

    pageSlots.forEach(slot => {

        grid.innerHTML += `

            <div
                class="slot ${slot.status}"
                data-slot-id="${slot.slot_id}"
            >

                <h3>
                    ${slot.slot_id}
                </h3>

                <p>
                    ${slot.status}
                </p>

            </div>

        `;
    });


    /* -------------------------------------
       RENDER PAGINATION
    ------------------------------------- */

    renderSlotsPagination(
        totalPages,
        currentSlotsPage,
        totalSlots
    );
}


/* =========================================
   SLOT DETAILS MODAL
========================================= */

async function openSlotDetails(slotId) {

    const slot = allSlots.find(
        s => s.slot_id === slotId
    );

    if (!slot) return;


    const modal =
        document.getElementById('slotDetailsModal');

    const title =
        document.getElementById('slotDetailsTitle');

    const content =
        document.getElementById('slotDetailsContent');


    if (!modal || !title || !content) return;


    title.textContent =
        `Slot ${slot.slot_id}`;


    /* -------------------------------------
       FREE SLOT
    ------------------------------------- */

    if (slot.status !== 'occupied') {

        content.innerHTML = `

            <div class="slot-detail-row">

                <span class="slot-detail-label">
                    Slot
                </span>

                <span class="slot-detail-value">
                    ${slot.slot_id}
                </span>

            </div>


            <div class="slot-detail-row">

                <span class="slot-detail-label">
                    Floor
                </span>

                <span class="slot-detail-value">
                    ${slot.floor || '-'}
                </span>

            </div>


            <div class="slot-detail-row">

                <span class="slot-detail-label">
                    Status
                </span>

                <span class="slot-detail-value">

                    <span class="slot-status free">
                        Free
                    </span>

                </span>

            </div>


            <div
                style="
                    text-align:center;
                    padding:20px 0 5px;
                    color:#64748b;
                "
            >
                No vehicle is currently parked.
            </div>

        `;

        modal.classList.add('show');

        return;
    }


    /* -------------------------------------
       SHOW LOADING
    ------------------------------------- */

    content.innerHTML = `

        <div
            style="
                text-align:center;
                padding:30px;
                color:#64748b;
            "
        >
            Loading slot details...
        </div>

    `;

    modal.classList.add('show');


    /* -------------------------------------
       GET ACTIVE PARKING LOG
    ------------------------------------- */

    try {

        const { ok, data } =
            await api(
                `/logs?vehicle_number=${encodeURIComponent(
                    slot.vehicle_number || ''
                )}&status=occupied`
            );


        let activeLog = null;


        if (ok && data) {

            const logs =
                Array.isArray(data)
                    ? data
                    : (data.logs || []);


            activeLog =
                logs.find(
                    log =>
                        log.slot_id === slot.slot_id &&
                        log.status === 'occupied'
                );
        }


        const entryTime =
            activeLog?.entry_time
                ? formatTime(activeLog.entry_time)
                : '-';


        /* -------------------------------------
           SHOW OCCUPIED SLOT DETAILS
        ------------------------------------- */

        content.innerHTML = `

            <div class="slot-detail-row">

                <span class="slot-detail-label">
                    Slot
                </span>

                <span class="slot-detail-value">
                    ${slot.slot_id}
                </span>

            </div>


            <div class="slot-detail-row">

                <span class="slot-detail-label">
                    Floor
                </span>

                <span class="slot-detail-value">
                    ${slot.floor || '-'}
                </span>

            </div>


            <div class="slot-detail-row">

                <span class="slot-detail-label">
                    Status
                </span>

                <span class="slot-detail-value">

                    <span class="slot-status occupied">
                        Occupied
                    </span>

                </span>

            </div>


            <div class="slot-detail-row">

                <span class="slot-detail-label">
                    Vehicle Number
                </span>

                <span class="slot-detail-value">
                    ${slot.vehicle_number || '-'}
                </span>

            </div>


            <div class="slot-detail-row">

                <span class="slot-detail-label">
                    Vehicle Type
                </span>

                <span class="slot-detail-value">
                    ${slot.vehicle_type || '-'}
                </span>

            </div>


            <div class="slot-detail-row">

                <span class="slot-detail-label">
                    Entry Time
                </span>

                <span class="slot-detail-value">
                    ${entryTime}
                </span>

            </div>

        `;

    } catch (error) {

        console.error(
            'Slot details error:',
            error
        );

        content.innerHTML = `

            <div
                style="
                    text-align:center;
                    padding:20px;
                    color:#b91c1c;
                "
            >
                Unable to load slot details.
            </div>

        `;
    }
}

/* =========================================
   CLOSE SLOT DETAILS MODAL
========================================= */

function closeSlotDetails() {

    const modal =
        document.getElementById('slotDetailsModal');

    if (modal) {

        modal.classList.remove('show');

    }
}


/* =========================================
   SLOT CLICK HANDLER
========================================= */

function setupSlotClickHandlers() {

    const grid =
        document.getElementById('slotGrid');

    if (!grid) return;


    grid.addEventListener(
        'click',
        function (event) {

            const slotCard =
                event.target.closest('.slot');

            if (!slotCard) return;


            const slotId =
                slotCard.dataset.slotId;


            if (slotId) {

                openSlotDetails(slotId);

            }

        }
    );
}
/* =========================================
   SLOTS PAGINATION
========================================= */

function renderSlotsPagination(
    totalPages,
    currentPage,
    totalRecords
) {

    const container =
        document.getElementById(
            'slotsPagination'
        );

    if (!container) return;


    if (
        !totalPages ||
        totalPages <= 1
    ) {

        container.innerHTML = '';

        return;
    }


    let html = '';


    const startRecord =
        ((currentPage - 1) * PER_PAGE) + 1;


    const endRecord =
        Math.min(
            currentPage * PER_PAGE,
            totalRecords
        );


    /* -------------------------------------
       INFORMATION
    ------------------------------------- */

    html += `

        <div class="logs-pagination-info">

            Showing
            ${startRecord}–${endRecord}
            of
            ${totalRecords}
            slots

        </div>

    `;


    /* -------------------------------------
       PREVIOUS
    ------------------------------------- */

    html += `

        <button
            type="button"
            ${currentPage === 1 ? 'disabled' : ''}
            onclick="renderSlots(${currentPage - 1})"
            aria-label="Previous page"
        >
            ‹
        </button>

    `;


    /* -------------------------------------
       PAGE NUMBERS
    ------------------------------------- */

    for (
        let i = 1;
        i <= totalPages;
        i++
    ) {

        html += `

            <button
                type="button"
                class="${i === currentPage ? 'active' : ''}"
                onclick="renderSlots(${i})"
            >
                ${i}
            </button>

        `;
    }


    /* -------------------------------------
       NEXT
    ------------------------------------- */

    html += `

        <button
            type="button"
            ${currentPage === totalPages ? 'disabled' : ''}
            onclick="renderSlots(${currentPage + 1})"
            aria-label="Next page"
        >
            ›
        </button>

    `;


    container.innerHTML = html;
}

/* =========================================
   REVENUE CHART
========================================= */

async function loadRevenueChart(filter = 'current') {

    try {

        const { ok, data } =
            await api(
                `/analytics/revenue?filter=${filter}`
            );

        if (!ok || !data) {
            console.error(
                'Revenue API failed:',
                data
            );
            return;
        }

        console.log(
            'Revenue:',
            filter,
            data
        );

        const labels = data.labels || [];
        const values = data.values || [];

        const canvas =
            document.getElementById('revenueChart');

        if (!canvas) {
            console.error(
                'revenueChart canvas not found'
            );
            return;
        }

        const ctx =
            canvas.getContext('2d');

        if (window.revenueChartInstance) {
            window.revenueChartInstance.destroy();
        }

        window.revenueChartInstance =
            new Chart(ctx, {

                type: 'line',

                data: {
                    labels: labels,

                    datasets: [{
                        label: 'Revenue',

                        data: values,

                        borderColor: '#2A4F8F',

                        backgroundColor:
                            'rgba(42,79,143,0.10)',

                        fill: true,

                        tension: 0.35,

                        borderWidth: 2.5,

                        pointRadius: 4,

                        pointBackgroundColor:
                            '#2A4F8F',

                        pointBorderColor:
                            '#ffffff',

                        pointBorderWidth: 1.5
                    }]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    animation: false,

                    plugins: {

                        legend: {
                            display: false
                        },

                        tooltip: {

                            callbacks: {

                                label:
                                    function(context) {

                                        return ' ₹' +
                                            Number(
                                                context.raw || 0
                                            ).toLocaleString(
                                                'en-IN'
                                            );
                                    }
                            }
                        }
                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                callback:
                                    function(value) {

                                        return '₹' +
                                            Number(value)
                                                .toLocaleString(
                                                    'en-IN'
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
            'Revenue chart error:',
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

    if (!ok || !data) return;


    const floors = {};


    data.forEach(slot => {

        if (!floors[slot.floor]) {

            floors[slot.floor] = {

                total: 0,

                occupied: 0
            };
        }


        floors[slot.floor].total++;


        if (
            slot.status === 'occupied'
        ) {

            floors[slot.floor].occupied++;
        }
    });


    const floorGrid =
        document.getElementById(
            'floorGrid'
        );


    if (!floorGrid) return;


    floorGrid.innerHTML = '';


    let chartIndex = 0;


    Object.keys(floors).forEach(
        floor => {

            const stats =
                floors[floor];


            const occupied =
                Math.round(
                    (
                        stats.occupied /
                        stats.total
                    ) * 100
                );


            const free =
                100 - occupied;


            const chartId =
                `floorChart${chartIndex}`;


            floorGrid.innerHTML += `

                <div class="floor-item">

                    <h4>
                        ${floor}
                    </h4>

                    <div class="small-chart">

                        <canvas
                            id="${chartId}"
                        ></canvas>

                    </div>

                    <p>
                        ${occupied}% occupied
                    </p>

                </div>

            `;


            chartIndex++;


            requestAnimationFrame(() => {

                const canvas =
                    document.getElementById(
                        chartId
                    );


                if (!canvas) return;


                const ctx =
                    canvas.getContext(
                        '2d'
                    );


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
        }
    );
}


/* =========================================
   VEHICLE DISTRIBUTION
========================================= */

async function loadVehicleDistribution() {

    try {

        const { ok, data } =
            await api(
                '/analytics/vehicle-distribution'
            );


        if (!ok || !data) {

            console.error(
                'Vehicle distribution API failed:',
                data
            );

            return;
        }


        const cars =
            Number(data.cars) || 0;


        const bikes =
            Number(data.bikes) || 0;


        const trucks =
            Number(data.trucks) || 0;


        const total =
            cars +
            bikes +
            trucks;


        let carPercent = 0;

        let bikePercent = 0;

        let truckPercent = 0;


        if (total > 0) {

            carPercent =
                Math.round(
                    (cars / total) * 100
                );


            bikePercent =
                Math.round(
                    (bikes / total) * 100
                );


            truckPercent =
                Math.round(
                    (trucks / total) * 100
                );


            const roundedTotal =
                carPercent +
                bikePercent +
                truckPercent;


            if (roundedTotal !== 100) {

                truckPercent +=
                    100 - roundedTotal;
            }
        }


        const carPercentEl =
            document.getElementById(
                'carPercent'
            );


        const bikePercentEl =
            document.getElementById(
                'bikePercent'
            );


        const truckPercentEl =
            document.getElementById(
                'truckPercent'
            );


        const carBar =
            document.getElementById(
                'carBar'
            );


        const bikeBar =
            document.getElementById(
                'bikeBar'
            );


        const truckBar =
            document.getElementById(
                'truckBar'
            );


        if (carPercentEl) {
            carPercentEl.innerText =
                `${carPercent}%`;
        }


        if (bikePercentEl) {
            bikePercentEl.innerText =
                `${bikePercent}%`;
        }


        if (truckPercentEl) {
            truckPercentEl.innerText =
                `${truckPercent}%`;
        }


        if (carBar) {
            carBar.style.width =
                `${carPercent}%`;
        }


        if (bikeBar) {
            bikeBar.style.width =
                `${bikePercent}%`;
        }


        if (truckBar) {
            truckBar.style.width =
                `${truckPercent}%`;
        }


        console.log(
            'Vehicle distribution:',
            {
                cars,
                bikes,
                trucks,
                total,
                percentages: {
                    cars: carPercent,
                    bikes: bikePercent,
                    trucks: truckPercent
                }
            }
        );


    } catch (error) {

        console.error(
            'Vehicle distribution error:',
            error
        );
    }
}


/* =========================================
   VEHICLE ENTRY
========================================= */

async function registerEntry() {

    const vehicleNumber =
        document.getElementById(
            'vehicleNum'
        )
        .value
        .trim()
        .toUpperCase();


    const vehicleType =
        document.getElementById(
            'vehicleType'
        ).value;


    if (
        !vehicleNumber ||
        !vehicleType
    ) {

        showToast(
            'Enter vehicle number and select vehicle type',
            'error'
        );

        return;
    }

    // Validate Indian vehicle number format
    const indianStateCodes = [
        "AP", "AR", "AS", "BR", "CG",
        "GA", "GJ", "HR", "HP", "JH",
        "KA", "KL", "MP", "MH", "MN",
        "ML", "MZ", "NL", "OD", "PB",
        "RJ", "SK", "TN", "TS", "TR",
        "UK", "UP", "WB",
        "AN", "CH", "DL", "JK", "LA",
        "LD", "PY", "DD", "DN"
    ];

    const vehiclePattern =
        /^([A-Z]{2})([0-9]{2})([A-Z]{1,3})([0-9]{4})$/;

    const match = vehicleNumber.match(vehiclePattern);

    if (!match || !indianStateCodes.includes(match[1])) {

        showToast(
            'Invalid vehicle number. Please enter a valid Indian registration number, e.g. AP23TR2345',
            'error'
        );

        return;
    }


    try {

        const { ok, data } =
            await api(
                '/entry',
                {

                    method: 'POST',

                    body: JSON.stringify({

                        vehicle_number:
                            vehicleNumber,

                        vehicle_type:
                            vehicleType
                    })
                }
            );


        if (!ok) {

            showToast(
                data?.error ||
                data?.detail ||
                'Entry failed',
                'error'
            );

            return;
        }


        showToast(
            `Vehicle registered — slot ${data.slot_allocated} assigned`,
            'success'
        );

        document.getElementById('vehicleNum').value = '';
        document.getElementById('vehicleType').value = '';


        document.getElementById(
            'vehicleNum'
        ).value = '';


        document.getElementById(
            'vehicleType'
        ).value = '';


        await loadDashboardData();

        await loadSlots();

        await loadLogs(1);


    } catch (error) {

        console.error(error);

        showToast(
            'Entry failed',
            'error'
        );
    }
}

function clearVehicleNumber() {
    const input = document.getElementById('vehicleNum');
    const clearBtn = document.getElementById('clearVehicleBtn');

    input.value = '';
    clearBtn.style.display = 'none';

    input.focus();
}

document.addEventListener('DOMContentLoaded', () => {

    const input = document.getElementById('vehicleNum');
    const clearBtn = document.getElementById('clearVehicleBtn');

    if (!input || !clearBtn) return;

    input.addEventListener('input', () => {

        if (input.value.trim() !== '') {
            clearBtn.style.display = 'flex';
        } else {
            clearBtn.style.display = 'none';
        }

    });

});

/* =========================================
   VEHICLE EXIT
========================================= */

async function processExit() {

    const vehicleNumber =
        document.getElementById(
            'exitVehicleNum'
        )
        .value
        .trim()
        .toUpperCase();


    if (!vehicleNumber) {

        showToast(
            'Enter vehicle number',
            'error'
        );

        return;
    }


    const { ok, data } =
        await api(
            '/exit',
            {

                method: 'POST',

                body: JSON.stringify({

                    vehicle_number:
                        vehicleNumber
                })
            }
        );


    if (!ok) {

        showToast(
            data?.detail ||
            'Error processing exit',
            'error'
        );

        return;
    }

    window.lastReceiptData = data;

    showToast(
        data.message,
        'success'
    );

    document.getElementById('exitVehicleNum').value = '';

    document.getElementById(
        'billingResult'
    ).innerHTML = `

        <div class="receipt">

            <div class="receipt-head">

                <h3>
                    Billing receipt
                </h3>

                <span>
                    #${data.billing_id}
                </span>

            </div>


            <div class="receipt-row">

                <span class="label">
                    Vehicle number
                </span>

                <span class="value">
                    ${data.vehicle_number}
                </span>

            </div>


            <div class="receipt-row">

                <span class="label">
                    Slot
                </span>

                <span class="value">
                    ${data.slot_id} · ${data.floor}
                </span>

            </div>


            <div class="receipt-row">

                <span class="label">
                    Entry time
                </span>

                <span class="value">
                    ${formatTime(data.entry_time)}
                </span>

            </div>


            <div class="receipt-row">

                <span class="label">
                    Exit time
                </span>

                <span class="value">
                    ${formatTime(data.exit_time)}
                </span>

            </div>


            <div class="receipt-row">

                <span class="label">
                    Duration
                </span>

                <span class="value">
                    ${Math.floor(data.duration_minutes / 60)} hours
                    ${data.duration_minutes % 60} minutes
                </span>

            </div}


            <div class="receipt-row">

                <span class="label">
                    Rate
                </span>

                <span class="value">
                    ₹${data.rate_per_hour}/hour
                </span>

            </div>


            <div class="receipt-total">

                <span class="label">
                    Total fee
                </span>

                <span class="value">
                    ₹${data.fee}
                </span>

            </div>

            <div class="receipt-actions">

                <button
                    type="button"
                    class="download-receipt-btn"
                    onclick="downloadReceiptPDF()"
                    onclick="clearBillingReceipt()"
                >
                    Download Receipt PDF
                </button>

                <button
                    type="button"
                    class="clear-receipt-btn"
                    onclick="clearBillingReceipt()"
                >
                    Clear
                </button>

            </div>

        </div>
    `;


    await loadDashboardData();

    await loadSlots();

    await loadLogs(1);
}

/* =========================================
   DOWNLOAD RECEIPT AS PDF
========================================= */

function downloadReceiptPDF() {

    if (!window.lastReceiptData) {

        showToast(
            'No billing receipt available',
            'warning'
        );

        return;
    }

    if (!window.jspdf) {

        showToast(
            'PDF library not loaded',
            'error'
        );

        return;
    }

    const data = window.lastReceiptData;

    const { jsPDF } = window.jspdf;

    const doc = new jsPDF();


    // ================================
    // HEADER
    // ================================

    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');

    doc.text(
        'SMART PARKING ANALYTICS',
        105,
        20,
        { align: 'center' }
    );


    doc.setFontSize(14);
    doc.setFont('helvetica', 'normal');

    doc.text(
        'Parking Billing Receipt',
        105,
        30,
        { align: 'center' }
    );


    doc.line(20, 38, 190, 38);


    // ================================
    // DETAILS
    // ================================

    let y = 55;

    doc.setFontSize(11);

    doc.setFont('helvetica', 'bold');
    doc.text('Billing ID:', 25, y);

    doc.setFont('helvetica', 'normal');
    doc.text(
        String(data.billing_id || '-'),
        75,
        y
    );

    y += 10;

    doc.setFont('helvetica', 'bold');
    doc.text('Vehicle Number:', 25, y);

    doc.setFont('helvetica', 'normal');
    doc.text(
        String(data.vehicle_number || '-'),
        75,
        y
    );

    y += 10;

    doc.setFont('helvetica', 'bold');
    doc.text('Slot:', 25, y);

    doc.setFont('helvetica', 'normal');
    doc.text(
        `${data.slot_id || '-'} · ${data.floor || '-'}`,
        75,
        y
    );

    y += 10;

    doc.setFont('helvetica', 'bold');
    doc.text('Entry Time:', 25, y);

    doc.setFont('helvetica', 'normal');
    doc.text(
        formatTime(data.entry_time),
        75,
        y
    );

    y += 10;

    doc.setFont('helvetica', 'bold');
    doc.text('Exit Time:', 25, y);

    doc.setFont('helvetica', 'normal');
    doc.text(
        formatTime(data.exit_time),
        75,
        y
    );

    y += 10;

    doc.setFont('helvetica', 'bold');
    doc.text('Duration:', 25, y);

    doc.setFont('helvetica', 'normal');
    doc.text(
        `${data.duration_minutes || 0} minutes`,
        75,
        y
    );

    y += 10;

    doc.setFont('helvetica', 'bold');
    doc.text('Rate:', 25, y);

    doc.setFont('helvetica', 'normal');
    doc.text(
        `Rs.${data.rate_per_hour || 0}/hour`,
        75,
        y
    );


    // ================================
    // TOTAL
    // ================================

    y += 18;

    doc.line(
        20,
        y - 6,
        190,
        y - 6
    );

    doc.setFontSize(15);
    doc.setFont('helvetica', 'bold');

    doc.text(
        'TOTAL FEE:',
        25,
        y
    );

    doc.text(
        `Rs.${data.fee || 0}`,
        165,
        y
    );


    // ================================
    // FOOTER
    // ================================

    y += 25;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');

    doc.text(
        'Thank you for using Smart Parking Analytics.',
        105,
        y,
        { align: 'center' }
    );


    // ================================
    // DOWNLOAD
    // ================================

    const vehicle =
        String(
            data.vehicle_number ||
            'vehicle'
        );

    doc.save(
        `Parking_Receipt_${vehicle}.pdf`
    );


    showToast(
        'Receipt downloaded successfully',
        'success'
    );
}


/* =========================================
   CLEAR BILLING RECEIPT
========================================= */

function clearBillingReceipt() {

    document.getElementById(
        'billingResult'
    ).innerHTML = '';

    document.getElementById(
        'exitVehicleNum'
    ).value = '';

    window.lastReceiptData = null;

    showToast(
        'Billing receipt cleared',
        'success'
    );
}

/* =========================================
   LOAD PARKING LOGS
========================================= */

async function loadLogs(page = 1) {

    currentLogsPage = page;

    const search =
        document.getElementById(
            'searchVehicle'
        )?.value
        ?.trim() || '';

    const status =
        document.getElementById(
            'logStatusFilter'
        )?.value || '';

    /* -------------------------------------
       Build query
    ------------------------------------- */

    const params =
        new URLSearchParams({

            page: String(page),

            limit: String(PER_PAGE),

            vehicle_number: search,

            status: status
        });

    console.log(
        'Loading parking logs:',
        params.toString()
    );

    const { ok, data } =
        await api(
            `/logs?${params.toString()}`
        );

    if (!ok || !data) {

        showToast(
            'Unable to load parking logs',
            'error'
        );

        return;
    }

    const tbody =
        document.getElementById(
            'logsBody'
        );

    if (!tbody) return;

    tbody.innerHTML = '';

    /* -------------------------------------
       Backend response
       
       Expected:
       {
           logs: [...],
           total: 823,
           page: 1,
           limit: 50,
           total_pages: 17
       }
    ------------------------------------- */

    const logs =
        Array.isArray(data)
            ? data
            : (data.logs || []);

    const total =
        Array.isArray(data)
            ? logs.length
            : Number(data.total || 0);

    const totalPages =
        Array.isArray(data)
            ? 1
            : Number(data.total_pages || 1);

    currentLogsPage =
        Number(data.page || page);

    /* -------------------------------------
       No logs
    ------------------------------------- */

    if (!logs.length) {

        tbody.innerHTML = `

            <tr>

                <td
                    colspan="10"
                    style="
                        text-align: center;
                        padding: 30px;
                        color: #6B7688;
                    "
                >
                    No parking logs found
                </td>

            </tr>

        `;

        renderLogsPagination(
            totalPages,
            currentLogsPage,
            total
        );

        return;
    }

    /* -------------------------------------
       Render logs
    ------------------------------------- */

    logs.forEach(log => {

        const vehicleNumber =
            log.vehicle_number || '-';

        const vehicleType =
            log.vehicle_type || '-';

        const slot =
            log.slot_id || '-';

        const floor =
            log.floor || '-';

        const entryTime =
            log.entry_time
                ? formatTime(
                    log.entry_time
                )
                : '-';

        const exitTime =
            log.exit_time
                ? formatTime(
                    log.exit_time
                )
                : '-';

        let duration = '-';

        if (
            log.duration !== undefined &&
            log.duration !== null
        ) {

            duration =
                log.duration;

        } else if (
            log.duration_minutes !== undefined &&
            log.duration_minutes !== null
        ) {

            duration =
                `${log.duration_minutes} mins`;
        }

        const fee =
            Number(
                log.fee || 0
            ).toLocaleString(
                'en-IN'
            );

        const status =
            log.status || 'occupied';

        tbody.innerHTML += `

            <tr>

                <td>
                    ${vehicleNumber}
                </td>

                <td>
                    ${vehicleType}
                </td>

                <td>
                    ${slot}
                </td>

                <td>
                    ${floor}
                </td>

                <td>
                    ${entryTime}
                </td>

                <td>
                    ${exitTime}
                </td>

                <td>
                    ${duration}
                </td>

                <td>
                    ₹${fee}
                </td>

                <td>

                    <span
                        class="status ${status}"
                    >
                        ${status}
                    </span>

                </td>

                <td>

                    <button
                        type="button"
                        class="delete-log-btn"
                        onclick="deleteLog('${log.id}')"
                    >
                        Delete
                    </button>

                </td>

            </tr>

        `;
    });

    console.log(
        `Loaded ${logs.length} parking logs — Page ${currentLogsPage} of ${totalPages}`
    );

    /* -------------------------------------
       Render pagination
    ------------------------------------- */

    renderLogsPagination(
        totalPages,
        currentLogsPage,
        total
    );
}

function clearVehicleSearch() {

    const input = document.getElementById('searchVehicle');
    const clearBtn = document.getElementById('clearSearchBtn');

    input.value = '';

    clearBtn.style.display = 'none';

    input.focus();

    loadLogs(1);
}


document.addEventListener('DOMContentLoaded', () => {

    const input = document.getElementById('searchVehicle');
    const clearBtn = document.getElementById('clearSearchBtn');

    if (!input || !clearBtn) return;

    input.addEventListener('input', () => {

        clearBtn.style.display =
            input.value.trim() !== ''
                ? 'flex'
                : 'none';

    });

});

/* =========================================
   PARKING LOG PAGINATION
========================================= */

function renderLogsPagination(
    totalPages,
    currentPage,
    totalRecords
) {

    const container =
        document.getElementById(
            'logsPagination'
        );

    if (!container) {
        console.warn(
            'logsPagination element not found'
        );
        return;
    }

    /* No pagination needed */

    if (
        !totalPages ||
        totalPages <= 1
    ) {

        container.innerHTML = '';

        return;
    }

    let html = '';

    const startRecord =
        ((currentPage - 1) * PER_PAGE) + 1;

    const endRecord =
        Math.min(
            currentPage * PER_PAGE,
            totalRecords
        );

    /* -------------------------------------
       Record information
    ------------------------------------- */

    html += `

        <div class="logs-pagination-info">

            Showing
            ${startRecord}–${endRecord}
            of
            ${totalRecords}
            records

        </div>

    `;

    /* -------------------------------------
       Previous button
    ------------------------------------- */

    html += `

        <button
            type="button"
            ${currentPage === 1 ? 'disabled' : ''}
            onclick="loadLogs(${currentPage - 1})"
            aria-label="Previous page"
        >
            ‹
        </button>

    `;

    /* -------------------------------------
       Page numbers
    ------------------------------------- */

    for (
        let i = 1;
        i <= totalPages;
        i++
    ) {

        html += `

            <button
                type="button"
                class="${i === currentPage ? 'active' : ''}"
                onclick="loadLogs(${i})"
            >
                ${i}
            </button>

        `;
    }

    /* -------------------------------------
       Next button
    ------------------------------------- */

    html += `

        <button
            type="button"
            ${currentPage === totalPages ? 'disabled' : ''}
            onclick="loadLogs(${currentPage + 1})"
            aria-label="Next page"
        >
            ›
        </button>

    `;

    container.innerHTML = html;
}

async function deleteLog(logId) {

    console.log("DELETE LOG ID:", logId);

    if (!logId || logId === "undefined") {

        showToast(
            "Invalid parking log ID",
            'error'
        );

        console.error(
            "Invalid log ID:",
            logId
        );

        return;
    }

    const confirmed = confirm(
        "Are you sure you want to delete this parking log?"
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `${API_BASE}/logs/${logId}`,
            {
                method: "DELETE",

                headers: {
                    "Authorization":
                        `Bearer ${localStorage.getItem("access_token")}`
                }
            }
        );

        console.log(
            "DELETE STATUS:",
            response.status
        );

        const data =
            await response.json();

        console.log(
            "DELETE RESPONSE:",
            data
        );

        if (!response.ok) {

            showToast(
                data.detail ||
                "Unable to delete parking log",
                'error'
            );

            return;
        }

        showToast(
            "Parking log deleted successfully",
            'success'
        );

        // Reload logs
        await loadLogs(1);

        // Refresh dashboard statistics
        await loadDashboardData();

        // Refresh parking slots
        await loadSlots();

    } catch (error) {

        console.error(
            "DELETE LOG ERROR:",
            error
        );

        showToast(
            "Unable to delete parking log",
            'error'
        );
    }
}

/* =========================================
   FORMAT TIME - INDIA STANDARD TIME
========================================= */

function formatTime(time) {

    if (!time) {
        return '-';
    }

    let timeString = String(time).trim();

    /*
     * Backend currently stores UTC timestamps
     * without an explicit timezone.
     *
     * Example:
     * 2026-09-04T14:58:07
     *
     * Treat these timestamps as UTC.
     */

    if (
        !timeString.endsWith('Z') &&
        !/[+-]\d{2}:\d{2}$/.test(timeString)
    ) {
        timeString += 'Z';
    }

    const date = new Date(timeString);

    if (Number.isNaN(date.getTime())) {
        return String(time);
    }

    return date.toLocaleString(
        'en-IN',
        {
            timeZone: 'Asia/Kolkata',

            day: 'numeric',
            month: 'numeric',
            year: 'numeric',

            hour: 'numeric',
            minute: '2-digit',
            second: '2-digit',

            hour12: true
        }
    );
}

const connStatusEl =
    document.getElementById('connStatus');

const connStatusLabel =
    document.getElementById('connStatusLabel');

function setConnStatus(live) {

    if (!connStatusEl) return;

    connStatusEl.classList.toggle(
        'live',
        live
    );

    if (connStatusLabel) {

        connStatusLabel.textContent =
            live
                ? 'Live'
                : 'Reconnecting…';
    }
}

/* -----------------------------------------
   WEBSOCKET URL
----------------------------------------- */

const WS_PROTOCOL =
    window.location.protocol === 'https:'
        ? 'wss:'
        : 'ws:';

const WS_URL =
    `${WS_PROTOCOL}//${window.location.host}/ws`;


/* -----------------------------------------
   SOCKET VARIABLES
----------------------------------------- */

let socket = null;

let reconnectTimer = null;

let reconnectAttempts = 0;


/* -----------------------------------------
   CONNECT WEBSOCKET
----------------------------------------- */

function connectWebSocket() {

    /* Prevent duplicate connections */

    if (
        socket &&
        (
            socket.readyState === WebSocket.OPEN ||
            socket.readyState === WebSocket.CONNECTING
        )
    ) {
        return;
    }


    console.log(
        'Connecting to WebSocket...'
    );


    socket =
        new WebSocket(WS_URL);


    /* -------------------------------------
       CONNECTION OPENED
    ------------------------------------- */

    socket.onopen = () => {

        console.log(
            'WebSocket connected'
        );

        reconnectAttempts = 0;

        setConnStatus(true);
    };


    /* -------------------------------------
       MESSAGE RECEIVED
    ------------------------------------- */

    socket.onmessage =
        async (event) => {

            try {

                const data =
                    JSON.parse(
                        event.data
                    );


                console.log(
                    'WebSocket update:',
                    data
                );


                /* Update slot card */

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
                        <h3>
                            ${data.slot_id}
                        </h3>

                        <p>
                            ${data.status}
                        </p>
                    `;
                }


                /* Refresh complete slot data */

                await loadSlots();


                /* Refresh dashboard */

                await loadSummary();

                await loadFloorOccupancy();

                await loadVehicleDistribution();


            } catch (error) {

                console.error(
                    'WebSocket message error:',
                    error
                );
            }
        };


    /* -------------------------------------
       CONNECTION CLOSED
    ------------------------------------- */

    socket.onclose = () => {

        console.warn(
            'WebSocket disconnected'
        );

        setConnStatus(false);

        scheduleReconnect();
    };


    /* -------------------------------------
       CONNECTION ERROR
    ------------------------------------- */

    socket.onerror = (error) => {

        console.error(
            'WebSocket error:',
            error
        );

        setConnStatus(false);

        /*
         * onclose will normally fire
         * after onerror, so reconnecting
         * is handled there.
         */
    };
}


/* -----------------------------------------
   RECONNECT
----------------------------------------- */

function scheduleReconnect() {

    if (reconnectTimer) {
        return;
    }


    reconnectAttempts++;


    /*
     * Increasing delay:
     *
     * 1st attempt  -> 2 sec
     * 2nd attempt  -> 4 sec
     * 3rd attempt  -> 6 sec
     * ...
     * Maximum     -> 10 sec
     */

    const delay =
        Math.min(
            reconnectAttempts * 2000,
            10000
        );


    console.log(
        `Reconnecting WebSocket in ${delay / 1000} seconds...`
    );


    reconnectTimer =
        setTimeout(() => {

            reconnectTimer = null;

            connectWebSocket();

        }, delay);
}


/* -----------------------------------------
   START WEBSOCKET
----------------------------------------- */

connectWebSocket();

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
            timeZone: 'Asia/Kolkata',

            weekday: 'long',

            day: 'numeric',

            month: 'long',

            year: 'numeric'
        }
    );
}


/* =========================================
   SLOT FILTER LISTENERS
========================================= */

document
    .getElementById('floorFilter')
    ?.addEventListener(
        'change',
        () => renderSlots(1)
    );


document
    .getElementById('statusFilter')
    ?.addEventListener(
        'change',
        () => renderSlots(1)
    );

/* =========================================
   REVENUE FILTER
========================================= */

document
    .getElementById(
        'weekFilter'
    )
    ?.addEventListener(
        'change',
        async function() {

            await loadRevenueChart(
                this.value
            );
        }
    );


/* =========================================
   PARKING LOG FILTER
========================================= */

document
    .getElementById(
        'logStatusFilter'
    )
    ?.addEventListener(
        'change',
        () => {

            loadLogs(1);
        }
    );


/*
 * Press Enter inside the vehicle
 * search box to apply the filter.
 */

document
    .getElementById(
        'searchVehicle'
    )
    ?.addEventListener(
        'keydown',
        event => {

            if (
                event.key === 'Enter'
            ) {

                loadLogs(1);
            }
        }
    );


/* =========================================
   WINDOW LOAD
========================================= */

window.onload = async () => {

    setupSlotClickHandlers();

    await loadDashboardData();

    await loadSlots();

    await loadLogs(1);
};