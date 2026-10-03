# Hospital Management System

A full-stack hospital management application built with Angular, Flask, REST APIs, and MySQL.

## Features

- JWT-style token authentication
- Patient, doctor, and admin roles
- Patient registration and login
- Doctor and department listing
- Appointment booking and status updates
- Patient medical records
- Prescription management
- Billing records
- Admin dashboard statistics
- Responsive Angular UI
- MySQL schema and sample data

## Tech Stack

### Frontend
- Angular
- TypeScript
- HTML/CSS

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- PyJWT

### Database
- MySQL

## Project Structure

```text
hospital-management-system/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── auth.py
│   ├── requirements.txt
│   └── seed.py
├── database/
│   ├── schema.sql
│   └── seed.sql
├── frontend/
│   ├── package.json
│   ├── angular.json
│   ├── tsconfig.json
│   └── src/
└── .gitignore
```

## 1. Database Setup

Create a MySQL database:

```sql
CREATE DATABASE hospital_db;
```

Then run:

```bash
mysql -u root -p hospital_db < database/schema.sql
mysql -u root -p hospital_db < database/seed.sql
```

Update the database URL in `backend/config.py` if your MySQL username/password differs.

## 2. Run Backend

Windows:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Linux/macOS:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Backend runs on:

`http://localhost:5000`

## 3. Run Frontend

Install Node.js and Angular CLI.

```bash
cd frontend
npm install
npm start
```

Open:

`http://localhost:4200`

## Demo Accounts

The seed data creates:

- Admin: `admin@hospital.com` / `admin123`
- Doctor: `doctor@hospital.com` / `doctor123`
- Patient: `patient@hospital.com` / `patient123`

Change these credentials before using the application outside a local demo.

## Important

This is an educational/demo application. It is not designed for handling real patient medical data or production healthcare workloads.
