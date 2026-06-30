# Smart Parking Analytics System

## Overview


Smart Parking Analytics System is a full-stack web application developed using **FastAPI**, **MongoDB Atlas**, **HTML**, **CSS**, and **JavaScript**.
The application helps manage parking slots, vehicle entry/exit, billing, transactions, and parking analytics through a modern dashboard interface.

The system provides:

* Real-time slot management
* Vehicle parking allocation
* Exit and billing calculation
* Parking logs tracking
* Occupancy analytics
* MongoDB Atlas cloud database integration

Smart Parking Analytics System is a full-stack intelligent parking management application developed using **FastAPI**, **MongoDB Atlas**, **Jinja2 Templates**, **HTML**, **CSS**, and **JavaScript**.

The system provides real-time parking management, vehicle tracking, billing analytics, occupancy monitoring, and dynamic dashboard visualization for multi-level parking environments.


---

# Features

## Dashboard

* Total parking slots overview
* Available slots count
* Occupied slots count
* Occupancy percentage
* Real-time slot visualization

## Vehicle Entry

* Register vehicle entry
* Automatically allocate free parking slot
* Prevent duplicate active parking entries
## Dashboard Analytics

* Real-time parking occupancy monitoring
* Weekly revenue analytics
* Vehicle distribution analytics
* Dynamic Chart.js visualizations
* Filter-based analytics:

  * Current Week
  * Last Week
  * This Month

---

## Parking Slot Management

* Multi-level slot allocation
* Available slot tracking
* Occupied slot monitoring
* Automatic slot assignment

---

## Vehicle Entry System

* Register vehicle entry
* Prevent duplicate active entries
* Automatic free slot allocation
* Real-time parking updates

---

## Exit & Billing

* Process vehicle exit
* Calculate parking duration
* Generate parking fee automatically
* Display billing summary popup

## Parking Logs

* View active and completed parking records
* Pagination support
* Filter logs by status
* Cleanup completed logs

## Transactions & Billing

* Billing records stored in MongoDB Atlas
* Transaction records maintained
* Fee tracking system

## Additional Features

* Responsive UI design
* Popup-based slot allocation
* Dynamic dashboard updates
* Favicon support
* GitHub version control
* Automatic parking fee calculation
* Billing summary generation
* Revenue tracking
* MongoDB billing storage

---

## Parking Logs

* Active parking records
* Completed parking records
* Pagination support
* Cleanup completed logs
* Real-time updates

---

## Real-Time Features

* FastAPI WebSocket integration
* Live dashboard refresh
* Dynamic occupancy updates
* Real-time analytics synchronization

---

# Technologies Used

## Backend

* FastAPI
* Python
* Uvicorn
* Pydantic
* Python
* FastAPI
* Uvicorn
* Pydantic
* WebSockets

---

## Frontend

* HTML5
* CSS3
* JavaScript (Vanilla JS)
* Vanilla JavaScript
* Jinja2 Templates
* Chart.js

---

## Database

* MongoDB Atlas
* PyMongo

## Tools

* Git & GitHub
* VS Code
---

## Development Tools

* VS Code
* Git & GitHub

---

# Project Structure

```text
SMART-PARKING-ANALYTICS-SYSTEM/
│
├── app/
│   ├── models/
│   ├── routers/
│   ├── static/
│   │   └── favicon.ico
│   ├── __init__.py
│   ├── main.py
│   └── mongodb.py
│
├── frontend/
│   ├── index.html
│   ├── script.css
│   └── script.js
│   │   ├── analytics.py
│   │   ├── billing.py
│   │   ├── logs.py
│   │   ├── parking.py
│   │   ├── slots.py
│   │   ├── transaction.py
│   │   └── vehicle.py
│   │
│   ├── static/
│   │   └── favicon.ico
│   │
│   ├── websocket_manager.py
│   ├── mongodb.py
│   ├── main.py
│   └── __init__.py
│
├── frontend/
│   ├── script.js
│   └── script.css
│
├── templates/
│   └── dashboard.html
│
├── services/
├── venv/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
=======
├── requirements.txt
└── README.md
```

---

# Installation & Setup

## 1. Clone Repository

```bash
git clone <repository-url>
cd smart-parking-analytics-system
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

### Windows
### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac
#### Linux / Mac

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure MongoDB Atlas

Create `.env` file:

```env
MONGO_URI=your_mongodb_atlas_connection_string
MONGO_URI=your_mongodb_connection_string
```

---

## 5. Run Application

```bash
uvicorn app.main:app --reload
```

---

## 6. Open Browser
## 6. Open Application

```text
http://127.0.0.1:8000
```

---

# API Endpoints

| Method | Endpoint       | Description            |
| ------ | -------------- | ---------------------- |
| GET    | /              | Load frontend          |
| GET    | /slots         | Get all parking slots  |
| GET    | /slots/summary | Dashboard analytics    |
| POST   | /entry         | Register vehicle entry |
| POST   | /exit          | Process vehicle exit   |
| GET    | /logs          | View parking logs      |
| DELETE | /logs/cleanup  | Delete completed logs  |
| POST   | /reset         | Reset parking system   |
| Method | Endpoint                        | Description            |
| ------ | ------------------------------- | ---------------------- |
| GET    | /                               | Load Dashboard         |
| GET    | /slots                          | Get Parking Slots      |
| GET    | /slots/summary                  | Slot Summary Analytics |
| POST   | /entry                          | Vehicle Entry          |
| POST   | /exit                           | Vehicle Exit & Billing |
| GET    | /logs                           | Parking Logs           |
| DELETE | /logs/cleanup                   | Cleanup Logs           |
| POST   | /reset                          | Reset Parking System   |
| GET    | /analytics/occupancy            | Occupancy Analytics    |
| GET    | /analytics/vehicle-count        | Vehicle Count          |
| GET    | /analytics/vehicle-distribution | Vehicle Distribution   |
| GET    | /analytics/weekly-revenue       | Revenue Analytics      |

---

# Analytics Features

## Weekly Revenue Analytics

The system dynamically calculates revenue from MongoDB billing records using aggregation pipelines.

Supported filters:

* Current Week
* Last Week
* Monthly Revenue

---

## Vehicle Distribution Analytics

Displays percentage distribution of:

* Cars
* Bikes
* Trucks

---

# Billing Calculation

Parking fee is calculated using:

```text
Parking Fee = Parking Duration × Rate Per Hour
```

Default rate:
### Default Rate

```text
₹20 / hour
```

---

# Future Enhancements

* Kafka Integration
* QR-based Parking Entry
* Online Payment Gateway
* Analytics Charts & Reports
* Real-time Notifications
* Dark Mode
* Mobile Responsive Improvements
* PDF Bill Generation
* Admin Authentication
# Real-Time Architecture

```text
Frontend Dashboard
        ↓
FastAPI Backend
        ↓
MongoDB Atlas
        ↓
WebSocket Updates
```

---

# Future Enhancements

* Kafka Integration
* Admin Authentication
* JWT Security
* QR-Based Parking Entry
* Online Payments
* PDF Bill Generation
* Excel Report Export
* Heatmap Visualization
* Email Notifications
* Mobile Responsive Enhancements
* Docker Deployment
* Azure Cloud Deployment

---

# Screenshots

## Dashboard

* Slot Overview
* Occupancy Analytics
* Billing Summary
* Parking Logs

(Add project screenshots here)

---

# GitHub

Repository Branch:
* Revenue Analytics
* Occupancy Analytics
* Vehicle Distribution
* Parking Logs

(Add screenshots here)

---

# GitHub Branch

```text
dev-1
```

---

# Author

Sukrutha, Veeramaheswari
# Authors

* Sukrutha
* Veeramaheswari

---

# License

This project is developed for educational and academic purposes.
