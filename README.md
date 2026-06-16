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

---

# Technologies Used

## Backend

* FastAPI
* Python
* Uvicorn
* Pydantic

## Frontend

* HTML5
* CSS3
* JavaScript (Vanilla JS)

## Database

* MongoDB Atlas
* PyMongo

## Tools

* Git & GitHub
* VS Code

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
│
├── services/
├── venv/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
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

```bash
venv\Scripts\activate
```

### Linux/Mac

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
```

---

## 5. Run Application

```bash
uvicorn app.main:app --reload
```

---

## 6. Open Browser

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

---

# Billing Calculation

Parking fee is calculated using:

```text
Parking Fee = Parking Duration × Rate Per Hour
```

Default rate:

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

```text
dev-1
```

---

# Author

Sukrutha, Veeramaheswari

---

# License

This project is developed for educational and academic purposes.
