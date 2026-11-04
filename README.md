# 🏔️ Trekking Management System
 
A multi-role web application for organising treks, built with **Flask**, **Jinja2**, **SQLAlchemy** and **SQLite**. Admins create and manage treks, staff run the treks they are assigned, and trekkers browse and book them, each through a dashboard built for their role.
 
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?logo=chartdotjs&logoColor=white)
 
---
 
 
## 🧭 Overview
 
The system covers the whole lifecycle of a trek, from creation and staff assignment through booking and cancellation to completion. Every route is protected by role-based access control, so each user sees only the pages and actions their role allows.
 
---
 
## 👥 User Roles
 
| Role | What they can do |
|---|---|
| **Admin** | Create, edit and delete treks; assign staff; approve or deactivate staff; activate, deactivate or blacklist users; view all bookings; see platform analytics |
| **Staff** | View the treks assigned to them; see participant lists; update trek status and available slots; download trek brochures; see participant analytics |
| **Trekker** | Search and browse open treks; book treks; cancel bookings; view booking history; download brochures; see a personal booking chart |
 
---
 
## ✨ Features
 
### 🔐 Authentication and access control
- Registration and login, with role selection on the landing page
- Passwords hashed with Werkzeug, and sessions managed with Flask-Login ("remember me" supported)
- Custom decorators (`admin_required`, `staff_required`, `trekker_required`) that enforce role-based access on every route
- Deactivated accounts are blocked at login
 
### 🛠️ Admin
- **Trek management:** create, edit and delete treks with name, location, difficulty, duration, dates, price, slots and status
- **Staff assignment:** every trek is assigned to a staff member
- **PDF brochures:** upload a brochure for each trek (PDF only, with file validation) and download it later
- **User management:** activate, deactivate or blacklist users
- **Staff management:** approve new staff accounts and deactivate existing ones
- **Booking overview:** view every booking on the platform
- **Analytics dashboard:** total treks, total bookings, active users, and bookings per trek (Chart.js)
 
### 🧑‍✈️ Staff
- Dashboard listing the staff member's assigned treks
- Participant list for each trek
- Update trek **status** (Open / Closed / Ongoing / Completed / Cancelled) and **available slots**, with validation
- Bookings are marked **Completed** automatically when their trek is completed
- Participant-count chart for each assigned trek
 
### 🥾 Trekker
- Browse open treks, with **search** by name, location or difficulty
- **One-click booking** with checks for:
  - closed treks
  - no remaining slots
  - duplicate bookings
- The trek **closes automatically** when its last slot is booked
- **Cancel** active bookings
- **Booking history** and a personal bookings chart
 
### 👤 For every role
- Profile page and account settings, including password change
- Responsive interface built with Bootstrap 5
 
---
 
## 🧰 Tech Stack
 
| Layer | Technology |
|---|---|
| Backend | Python, Flask 3 (Blueprints, application factory) |
| Templating | Jinja2 |
| Database | SQLite with Flask-SQLAlchemy (ORM) and Flask-Migrate |
| Authentication | Flask-Login, Werkzeug password hashing |
| Frontend | HTML, CSS, Bootstrap 5 |
| Charts | Chart.js |
| Configuration | python-dotenv |
 
---
 
## 🗄️ Database Design
 
| Table | Purpose | Key fields |
|---|---|---|
| `users_details` | All users (Admin, Staff, Trekker) | name, email, phone, password hash, role, active, approved, blacklisted |
| `staff_profiles` | Extra details for staff (one-to-one with users) | experience, specialization, address, emergency contact |
| `treks_events` | Treks | name, location, difficulty, duration, dates, price, slots, status, assigned staff, brochure |
| `bookings_details` | Bookings (links users and treks) | booking status, payment status, number of people, total amount, discount, coupon, payment method |
 
**Enumerations** (`database/enums.py`) keep the values consistent across the app:
- **User roles:** Admin, Staff, Trekker
- **Trek difficulty:** Easy, Moderate, Hard
- **Trek status:** Open, Closed, Ongoing, Completed, Cancelled
- **Payment status:** Pending, Paid, Refunded
 
---
 
## 📁 Project Structure
 
```
trekking-management-app/
├── app.py                 # Application factory and blueprint registration
├── config.py              # App configuration (database path, secret key, upload limits)
├── requirements.txt
├── database/
│   ├── database.py        # SQLAlchemy, Migrate and LoginManager instances
│   ├── models.py          # User, StaffProfile, Trek, Booking models
│   ├── enums.py           # Roles, difficulty, statuses
│   ├── create_db.py       # Creates all tables
│   └── seed_admin.py      # Creates the default admin account
├── routes/
│   ├── auth.py            # Register, login, logout, role selection
│   ├── admin.py           # Admin dashboard and management pages
│   ├── staff.py           # Staff dashboard and trek updates
│   ├── trek.py            # Trekker dashboard, search, profile
│   ├── booking.py         # Booking, history, cancellation
│   ├── charts.py          # Role-specific analytics
│   └── api.py             # JSON REST API
├── utils/
│   ├── decorators.py      # Role-based access decorators
│   └── auth_utils.py      # Password hashing and user loading
├── templates/             # Jinja2 templates (admin/, staff/, user/)
└── static/                # CSS, images, uploaded brochures
```
 
---
 
## 🔌 REST API
 
A JSON API (login required) under `/api`:
 
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/treks` | List all treks |
| `GET` | `/api/treks/<id>` | Get one trek |
| `POST` | `/api/treks` | Create a trek |
| `PUT` | `/api/treks/<id>` | Update a trek |
| `DELETE` | `/api/treks/<id>` | Delete a trek |
| `GET` | `/api/users` | List users |
| `PUT` | `/api/users/<id>` | Update a user's status |
| `GET` | `/api/bookings` | List bookings |
| `POST` | `/api/bookings` | Create a booking |
| `PUT` | `/api/bookings/<id>` | Update a booking |
| `DELETE` | `/api/bookings/<id>` | Delete a booking |
 
---
 
## 🚀 Getting Started
 
### 1. Clone the repository
```bash
git clone https://github.com/saianishgoteti2801-sys/trekking-management-app-v1.git
cd trekking-management-app-v1
```
 
### 2. Create a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
 
### 3. Create the database and the admin account
```bash
python -m database.create_db
python -m database.seed_admin
```
 
### 4. Run the app
```bash
python app.py
```
Then open **http://127.0.0.1:5000** in your browser.
 
### Default admin login (for local testing only)
| Email | Password |
|---|---|
| `admin@ds.study.iitm.ac.in` | `Admin@123` |
 
> ⚠️ Change the admin password and set a `SECRET_KEY` environment variable before running the app anywhere other than your own machine.
 
---
 
 
## 👨‍💻 Author
 
**Sai Anish Goteti**
BS-MS student, IISER Pune · BS in Data Science and Applications, IIT Madras
