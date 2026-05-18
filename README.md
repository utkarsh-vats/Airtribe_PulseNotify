# PulseNotify — Flight Price Alert System

## Overview

PulseNotify is a flight price monitoring backend that lets users set price alerts for flight routes. When prices drop below a user-defined threshold, the system automatically fires a notification. Built with Django REST Framework, Celery, Redis, and PostgreSQL — all containerized with Docker.

## How It Works

```
User sets alert: route=DEL-BOM, threshold=₹4500
        ↓
POST /api/alerts/  →  PriceAlert saved to DB
        ↓
Celery Beat fires every 60 seconds
        ↓
check_prices task wakes up
        ↓
GET /api/flights/price/?route=DEL-BOM  (internal mock endpoint)
        ↓
Mock endpoint returns { "route": "DEL-BOM", "price": 4200 }
        ↓
4200 <= 4500 threshold? YES
        ↓
send_notification.delay()  (async Celery task)
        ↓
NotificationLog written to DB
        ↓
GET /api/admin/summary/  →  Admin sees stats
```

## Tech Stack

- **Backend:** Django 6.0, Django REST Framework
- **Auth:** SimpleJWT (Bearer token)
- **Task Queue:** Celery 5.6 with Redis broker
- **Scheduler:** Celery Beat (60-second interval)
- **Database:** PostgreSQL 18
- **Cache/Broker:** Redis 7
- **Containerization:** Docker & Docker Compose

## Project Structure

```
pulsenotify/
├── pulse/                    # Django app
│   ├── models.py             # UserProfile, PriceAlert, NotificationLog
│   ├── views.py              # All 7 API endpoints
│   ├── serializers.py        # DRF serializers
│   ├── signals.py            # post_save → auto-create UserProfile
│   ├── permissions.py        # IsAdminUser custom permission
│   ├── tasks.py              # check_prices (Beat) + send_notification (async)
│   ├── urls.py               # App URL routing
│   └── tests.py              # 6 unit tests
├── pulsenotify/              # Django project config
│   ├── celery.py             # Celery app configuration
│   ├── __init__.py           # Celery app import
│   ├── urls.py               # Root URL conf
│   └── settings/
│       ├── base.py           # Shared config (apps, JWT, Celery, DB)
│       ├── local.py          # Dev overrides (DEBUG=True)
│       └── production.py     # Prod overrides (DEBUG=False)
├── docker-compose.yml        # All 5 services
├── Dockerfile
├── requirements.txt
├── .env.local                # Environment variables (not committed)
├── .env.example              # Template for env vars
└── Airtribe_PulseNotify.postman_collection.json
```

## Setup & Installation

### Prerequisites

- Docker & Docker Compose installed
- Git
- Postman (for API testing)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/pulsenotify.git
cd pulsenotify
```

### 2. Create environment file

Copy the example env file and fill in your values:

```bash
cp .env.example .env.local
```

`.env.local` should contain:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=pulsenotify
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

POSTGRES_DB=pulsenotify
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-db-password

DJANGO_SETTINGS_MODULE=pulsenotify.settings.local
```

### 3. Build and start all services

```bash
docker compose up --build
```

This starts 5 containers:

| Service       | Description                  | Port        |
| ------------- | ---------------------------- | ----------- |
| web           | Django dev server            | 8000        |
| db            | PostgreSQL 18                | 8080 → 5432 |
| redis         | Redis 7 (Celery broker)      | 6379        |
| celery-worker | Processes async tasks        | —           |
| celery-beat   | Fires check_prices every 60s | —           |

### 4. Run migrations

```bash
docker compose run --rm web python manage.py migrate
```

### 5. Verify

- Open `http://localhost:8000` — Django should respond
- Watch terminal logs — Celery Beat fires `check_prices` every 60 seconds
- Celery Worker picks up tasks and processes them

## API Endpoints

| #   | Method | Endpoint                            | Auth        | Description                              |
| --- | ------ | ----------------------------------- | ----------- | ---------------------------------------- |
| 1   | POST   | `/api/auth/register/`               | Public      | Register new user, returns JWT           |
| 2   | POST   | `/api/auth/login/`                  | Public      | Login, returns JWT                       |
| 3   | POST   | `/api/alerts/`                      | JWT         | Create a price alert                     |
| 4   | GET    | `/api/alerts/`                      | JWT         | List logged-in user's alerts             |
| 5   | DELETE | `/api/alerts/<id>/`                 | JWT         | Deactivate an alert (soft delete)        |
| 6   | GET    | `/api/flights/price/?route=DEL-BOM` | Public      | Mock price feed (random price)           |
| 7   | GET    | `/api/admin/summary/`               | JWT + Admin | Platform-wide alert & notification stats |

### Available Mock Routes

| Route   | Price Range     |
| ------- | --------------- |
| DEL-BOM | ₹3,000 – ₹7,000 |
| BLR-HYD | ₹1,500 – ₹4,000 |
| DEL-BLR | ₹4,000 – ₹9,000 |
| BOM-GOA | ₹2,000 – ₹5,000 |

## Celery Tasks

**check_prices** (scheduled every 60 seconds via Celery Beat)
- Fetches all distinct routes with active alerts
- Calls the mock price endpoint for each route
- Compares current price against each alert's threshold
- Fires `send_notification.delay()` if price ≤ threshold

**send_notification** (async, triggered by check_prices)
- Creates a NotificationLog entry
- Marks the alert as TRIGGERED so it doesn't fire again

## Running Tests

```bash
docker compose run --rm web python manage.py test
```

6 tests covering:
- Threshold comparison logic (below, above, equal)
- NotificationLog creation with correct message
- Alert scoping (users only see their own alerts)

## Postman Collection

Import `Airtribe_PulseNotify.postman_collection.json` into Postman. The collection includes 13 scenarios across 4 folders:

**Auth:** Register, duplicate register (400), login, wrong password (401)
**Alerts:** Create alert, list alerts, deactivate alert, unauthorized delete (404), no JWT (401)
**Flights:** Valid route (200), invalid route (404)
**Admin:** Summary as admin (200), summary as non-admin (403)

Collection variables auto-save tokens on register/login — no manual copy-paste needed.

## Screenshots

### Auth Endpoints
![Register Success](screenshots/Auth/%231%20-%20Register_User.png)
![Register Duplicate](screenshots/Auth/%232%20-%20Register_Duplicate_User.png)
![Login Success](screenshots/Auth/%233%20-%20Login_User.png)
![Invalid Login](screenshots/Auth/%234%20-%20Login_User_Wrong_Password.png)

### Alert Endpoints
![Get Alerts](screenshots/Alerts/%235%20-%20Get_Alerts.png)
![Set Alerts](screenshots/Alerts/%236%20-%20Set_Alerts.png)
![Delete Alert](screenshots/Alerts/%237%20-%20Delete_Alert_by_ID.png)
![Set Alerts without JWT](screenshots/Alerts/%2311%20-%20Set_Alerts_without_JWT.png)
![Delete Unauthorized](screenshots/Alerts/%2312%20-%20Delete_Alert_by_ID_Unauthorized.png)

### Flights
![Valid Route](screenshots/Flights/%238%20-%20Flight_Price_for_valid_route.png)
![Invalid Route](screenshots/Flights/%239%20-%20Flight_Price_for_invalid_route.png)

### Admin
![Admin Summary](screenshots/Admin/%2310%20-%20Admin_Summary.png)
![Non-Admin 403](screenshots/Admin/%2313%20-%20Admin_Summary_as_Non_Admin.png)

### Tests
![Test Results](screenshots/Tests/Ran_Test_Cases.png)

### Celery Tasks
<!-- ![Celery Beat Logs](screenshots/celery_beat_logs.png) -->
<!-- ![Notification Triggered](screenshots/notification_triggered.png) -->

### Database
<!-- ![PGAdmin Tables](screenshots/pgadmin_tables.png) -->
<!-- ![NotificationLog Entries](screenshots/notification_log_entries.png) -->

## Environment Configuration

Settings are split across three files:

- `base.py` — Shared config (installed apps, middleware, JWT, Celery, database)
- `local.py` — Development overrides (DEBUG=True, ALLOWED_HOSTS=['*'])
- `production.py` — Production overrides (DEBUG=False, restricted hosts)

Switch environments by changing `DJANGO_SETTINGS_MODULE` in `.env.local`:

```env
# Development
DJANGO_SETTINGS_MODULE=pulsenotify.settings.local

# Production
DJANGO_SETTINGS_MODULE=pulsenotify.settings.production
```