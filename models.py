from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("admin", "doctor", "patient"), nullable=False)

class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    specialization = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(30))
    experience_years = db.Column(db.Integer, default=0)
    user = db.relationship("User", backref=db.backref("doctor_profile", uselist=False))
    department = db.relationship("Department")

class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(30))
    phone = db.Column(db.String(30))
    address = db.Column(db.String(255))
    blood_group = db.Column(db.String(10))
    user = db.relationship("User", backref=db.backref("patient_profile", uselist=False))

class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.Enum("scheduled", "completed", "cancelled"), default="scheduled")
    patient = db.relationship("Patient")
    doctor = db.relationship("Doctor")

class Prescription(db.Model):
    __tablename__ = "prescriptions"
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    diagnosis = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointment = db.relationship("Appointment")

class PrescriptionItem(db.Model):
    __tablename__ = "prescription_items"
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey("prescriptions.id"), nullable=False)
    medicine = db.Column(db.String(160), nullable=False)
    dosage = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.String(120))
    prescription = db.relationship("Prescription", backref="items")

class Bill(db.Model):
    __tablename__ = "bills"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum("unpaid", "paid"), default="unpaid")
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship("Patient")
