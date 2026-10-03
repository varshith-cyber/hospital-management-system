from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from models import db, User, Department, Doctor, Patient, Appointment, Bill, Prescription, PrescriptionItem

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(name="Hospital Admin", email="admin@hospital.com",
                 password_hash=generate_password_hash("admin123"), role="admin")
    doctor_user = User(name="Dr. Ananya Sharma", email="doctor@hospital.com",
                       password_hash=generate_password_hash("doctor123"), role="doctor")
    patient_user = User(name="Rahul Kumar", email="patient@hospital.com",
                        password_hash=generate_password_hash("patient123"), role="patient")

    db.session.add_all([admin, doctor_user, patient_user])
    db.session.flush()

    cardio = Department(name="Cardiology", description="Heart and cardiovascular care")
    general = Department(name="General Medicine", description="General medical care")
    ortho = Department(name="Orthopedics", description="Bone and joint care")
    db.session.add_all([cardio, general, ortho])
    db.session.flush()

    doctor = Doctor(user_id=doctor_user.id, department_id=cardio.id,
                    specialization="Cardiologist", phone="9876543210", experience_years=8)
    patient = Patient(user_id=patient_user.id, dob=date(2003, 5, 14),
                      gender="Male", phone="9876501234", address="Durg, Chhattisgarh",
                      blood_group="B+")
    db.session.add_all([doctor, patient])
    db.session.flush()

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=datetime.now() + timedelta(days=1),
        reason="Routine cardiac consultation"
    )
    db.session.add(appointment)
    db.session.flush()

    prescription = Prescription(
        appointment_id=appointment.id,
        diagnosis="Routine follow-up",
        notes="Continue prescribed medication and maintain regular activity."
    )
    db.session.add(prescription)
    db.session.flush()

    db.session.add(PrescriptionItem(
        prescription_id=prescription.id,
        medicine="Sample Medicine",
        dosage="1 tablet twice daily",
        duration="5 days"
    ))

    db.session.add(Bill(
        patient_id=patient.id,
        appointment_id=appointment.id,
        amount=750,
        status="unpaid",
        description="Consultation fee"
    ))

    db.session.commit()
    print("Seed data created successfully.")
