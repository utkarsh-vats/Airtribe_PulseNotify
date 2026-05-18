# PulseNotify — Flight Price Alert System

## Overview

PulseNotify is a flight price monitoring backend that lets users set price alerts for flight routes. When prices drop below a user-defined threshold, the system automatically fires a notification. Built with Django REST Framework, Celery, Redis, and PostgreSQL — all containerized with Docker.

## Beyond the Assignment

Changes and enhancements made on top of the original spec:

| Area           | Assignment Spec                   | What We Did                                                                          |
| -------------- | --------------------------------- | ------------------------------------------------------------------------------------ |
| Primary keys   | Default integer IDs               | UUID4 via abstract BaseModel on all pulse models                                     |
| Mock routes    | 4 hardcoded routes                | 60+ Indian domestic routes in a separate `mock_data.py`                              |
| Price response | Route + price only                | Added origin/destination airport names                                               |
| Tests          | 3 required (model-level)          | 10 tests — 6 model-level + 4 endpoint-level                                          |
| API docs       | Not required                      | Auto-generated Swagger UI via drf-spectacular at `/api/docs/`                        |
| Logging        | Not required                      | Python logging in Celery tasks + LOGGING config in settings                          |
| Admin panel    | Not required                      | All models registered with list_display, filters, and search                         |
| Docker         | DB + Redis only, manual runserver | Fully containerized — web, db, redis, celery-worker, celery-beat in one compose file |
| Error handling | Not specified                     | try/except in send_notification for deleted alerts, request timeouts in check_prices |
| Timestamps     | created_at only                   | BaseModel adds updated_at (auto_now) to all models                                   |

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
- **API Docs:** drf-spectacular (Swagger UI)

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
│   ├── mock_data.py          # 60+ Indian domestic routes with price ranges
│   ├── admin.py              # Model registration with filters and search
│   ├── urls.py               # App URL routing
│   └── tests.py              # 10 unit tests
├── pulsenotify/              # Django project config
│   ├── celery.py             # Celery app configuration
│   ├── __init__.py           # Celery app import
│   ├── urls.py               # Root URL conf
│   └── settings/
│       ├── base.py           # Shared config (apps, JWT, Celery, DB, logging)
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

### 5. Create a superuser (for Django admin panel)

```bash
docker compose run --rm web python manage.py createsuperuser
```

### 6. Verify

- Open `http://localhost:8000` — Django should respond
- Open `http://localhost:8000/api/docs/` — Swagger API documentation
- Open `http://localhost:8000/admin/` — Django admin panel
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
| —   | GET    | `/api/docs/`                        | Public      | Swagger API documentation                |
| —   | GET    | `/api/schema/`                      | Public      | OpenAPI schema (JSON)                    |

### Available Mock Routes (60+)

Covers all major Indian domestic hubs. Sample routes:

| Route   | Price Range     | Origin                               | Destination                            |
| ------- | --------------- | ------------------------------------ | -------------------------------------- |
| DEL-BOM | ₹3,000 – ₹7,000 | Delhi (Indira Gandhi International)  | Mumbai (Chhatrapati Shivaji Maharaj)   |
| BLR-HYD | ₹1,500 – ₹4,000 | Bangalore (Kempegowda International) | Hyderabad (Rajiv Gandhi International) |
| DEL-BLR | ₹4,000 – ₹9,000 | Delhi                                | Bangalore                              |
| BOM-GOA | ₹2,000 – ₹5,000 | Mumbai                               | Goa (Manohar International)            |
| MAA-CCU | ₹3,500 – ₹7,000 | Chennai                              | Kolkata                                |
| DEL-SXR | ₹3,000 – ₹8,000 | Delhi                                | Srinagar                               |

Full route list available in `pulse/mock_data.py`. The price feed response includes origin and destination airport names.

## Celery Tasks

**check_prices** (scheduled every 60 seconds via Celery Beat)
- Fetches all distinct routes with active alerts
- Calls the mock price endpoint for each route
- Compares current price against each alert's threshold
- Fires `send_notification.delay()` if price ≤ threshold
- Logs every price check and error with Python logging

**send_notification** (async, triggered by check_prices)
- Creates a NotificationLog entry
- Marks the alert as TRIGGERED so it doesn't fire again
- Handles deleted alerts gracefully (DoesNotExist catch + warning log)

## Running Tests

```bash
docker compose run --rm web python manage.py test
```

10 tests covering:

**Model-level tests:**
- Threshold comparison logic (below, above, equal)
- NotificationLog creation with correct message
- Alert scoping (users only see their own alerts)

**Endpoint-level tests:**
- Register returns 400 on duplicate username
- Admin summary returns 403 for regular user
- Alert deactivation changes status to INACTIVE
- Mock price feed returns 404 for unknown route

## Postman Collection

Import `Airtribe_PulseNotify.postman_collection.json` into Postman. The collection includes 13 scenarios across 4 folders:

**Auth:** Register, duplicate register (400), login, wrong password (401)
**Alerts:** Create alert, list alerts, deactivate alert, unauthorized delete (404), no JWT (401)
**Flights:** Valid route (200), invalid route (404)
**Admin:** Summary as admin (200), summary as non-admin (403)

Collection variables auto-save tokens on register/login — no manual copy-paste needed.

## Screenshots

### Auth Endpoints
---
*New user registered successfully — returns JWT access token and role.*
![Register Success](screenshots/Auth/%231%20-%20Register_User.png)

---
*Attempting to register an existing username — returns 400 with error message.*
![Register Duplicate](screenshots/Auth/%232%20-%20Register_Duplicate_User.png)

---
*Valid credentials — returns 200 with fresh JWT access and refresh tokens.*
![Login Success](screenshots/Auth/%233%20-%20Login_User.png)

---
*Wrong password — returns 401 Unauthorized.*
![Invalid Login](screenshots/Auth/%234%20-%20Login_User_Wrong_Password.png)

### Alert Endpoints
---
*Listing all alerts for the authenticated user — scoped to request.user only.*
![Get Alerts](screenshots/Alerts/%235%20-%20Get_Alerts.png)

---
*Creating a new price alert for DEL-BOM with ₹4500 threshold — returns 201.*
![Set Alerts](screenshots/Alerts/%236%20-%20Set_Alerts.png)

---
*Soft-deleting an alert — status set to inactive, row preserved in DB.*
![Delete Alert](screenshots/Alerts/%237%20-%20Delete_Alert_by_ID.png)

---
*Attempting to create an alert without a JWT token — returns 401.*
![Set Alerts without JWT](screenshots/Alerts/%2311%20-%20Set_Alerts_without_JWT.png)

---
*User2 attempting to delete User1's alert — returns 404, never exposing another user's data.*
![Delete Unauthorized](screenshots/Alerts/%2312%20-%20Delete_Alert_by_ID_Unauthorized.png)

### Flights
---
*Mock price feed returning a random price for DEL-BOM within the ₹3000–₹7000 range.*
![Valid Route](screenshots/Flights/%238%20-%20Flight_Price_for_valid_route.png)

---
*Requesting an unknown route — returns 404 with error message.*
![Invalid Route](screenshots/Flights/%239%20-%20Flight_Price_for_invalid_route.png)

### Admin
---
*Admin-only endpoint returning platform-wide stats — total alerts, active/triggered counts, top routes.*
![Admin Summary](screenshots/Admin/%2310%20-%20Admin_Summary.png)

---
*Regular user attempting to access admin summary — returns 403 Forbidden.*
![Non-Admin 403](screenshots/Admin/%2313%20-%20Admin_Summary_as_Non_Admin.png)

### Celery Tasks
---
*Celery Beat firing check_prices every 60 seconds on schedule.*
![Celery Beat Logs](screenshots/Celery/celery_beat_logs.png)

---
*Worker processing check_prices → price below threshold → send_notification task received and succeeded.*
![Notification Triggered](screenshots/Celery/notification_triggered.png)

### Tests
---
*All 6 unit tests passing — threshold logic, notification log creation, and alert scoping.*
![Test Results](screenshots/Tests/Ran_Test_Cases.png)

---
*10 tests passing — unit tests + duplicate user, admin summary, alert deactivation and mock price feed.*
![Test Results 02](screenshots/Tests/Ran_Test_Cases_02.png)

## Environment Configuration

Settings are split across three files:

- `base.py` — Shared config (installed apps, middleware, JWT, Celery, database, logging)
- `local.py` — Development overrides (DEBUG=True, ALLOWED_HOSTS=['*'])
- `production.py` — Production overrides (DEBUG=False, restricted hosts)

Switch environments by changing `DJANGO_SETTINGS_MODULE` in `.env.local`:

```env
# Development
DJANGO_SETTINGS_MODULE=pulsenotify.settings.local

# Production
DJANGO_SETTINGS_MODULE=pulsenotify.settings.production
```