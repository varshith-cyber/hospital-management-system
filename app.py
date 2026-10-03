from datetime import datetime
from decimal import Decimal
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Department, Doctor, Patient, Appointment, Prescription, PrescriptionItem, Bill
from auth import create_token, token_required

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

def user_json(user):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "hospital-api"})

@app.post("/api/auth/register")
def register():
    data = request.get_json() or {}
    required = ["name", "email", "password"]
    if any(not data.get(x) for x in required):
        return jsonify({"message": "Name, email and password are required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 409

    user = User(
        name=data["name"],
        email=data["email"].lower().strip(),
        password_hash=generate_password_hash(data["password"]),
        role="patient"
    )
    db.session.add(user)
    db.session.flush()

    patient = Patient(
        user_id=user.id,
        phone=data.get("phone"),
        gender=data.get("gender"),
        blood_group=data.get("blood_group")
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({"token": create_token(user), "user": user_json(user)}), 201

@app.post("/api/auth/login")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=(data.get("email") or "").lower().strip()).first()

    if not user or not check_password_hash(user.password_hash, data.get("password", "")):
        return jsonify({"message": "Invalid email or password"}), 401

    return jsonify({"token": create_token(user), "user": user_json(user)})

@app.get("/api/auth/me")
@token_required()
def me():
    user = User.query.get(request.current_user["user_id"])
    return jsonify(user_json(user))

@app.get("/api/departments")
def departments():
    rows = Department.query.order_by(Department.name).all()
    return jsonify([{"id": d.id, "name": d.name, "description": d.description} for d in rows])

@app.get("/api/doctors")
def doctors():
    rows = Doctor.query.all()
    return jsonify([
        {
            "id": d.id,
            "name": d.user.name,
            "email": d.user.email,
            "specialization": d.specialization,
            "department": d.department.name,
            "department_id": d.department_id,
            "phone": d.phone,
            "experience_years": d.experience_years
        } for d in rows
    ])

@app.get("/api/patients")
@token_required(["admin", "doctor"])
def patients():
    rows = Patient.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.user.name,
            "email": p.user.email,
            "phone": p.phone,
            "gender": p.gender,
            "blood_group": p.blood_group,
            "dob": p.dob.isoformat() if p.dob else None,
            "address": p.address
        } for p in rows
    ])

@app.post("/api/appointments")
@token_required(["patient", "admin"])
def create_appointment():
    data = request.get_json() or {}
    if not data.get("doctor_id") or not data.get("appointment_date"):
        return jsonify({"message": "Doctor and appointment date are required"}), 400

    if request.current_user["role"] == "patient":
        patient = Patient.query.filter_by(user_id=request.current_user["user_id"]).first()
    else:
        patient = Patient.query.get(data.get("patient_id"))

    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    try:
        date_value = datetime.fromisoformat(data["appointment_date"].replace("Z", "+00:00"))
        date_value = date_value.replace(tzinfo=None)
    except ValueError:
        return jsonify({"message": "Invalid appointment date"}), 400

    doctor = Doctor.query.get(data["doctor_id"])
    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404

    appt = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=date_value,
        reason=data.get("reason", "")
    )
    db.session.add(appt)
    db.session.commit()

    return jsonify(appointment_json(appt)), 201

def appointment_json(a):
    return {
        "id": a.id,
        "patient_id": a.patient_id,
        "patient_name": a.patient.user.name,
        "doctor_id": a.doctor_id,
        "doctor_name": a.doctor.user.name,
        "specialization": a.doctor.specialization,
        "appointment_date": a.appointment_date.isoformat(),
        "reason": a.reason,
        "status": a.status
    }

@app.get("/api/appointments")
@token_required()
def appointments():
    role = request.current_user["role"]
    if role == "patient":
        patient = Patient.query.filter_by(user_id=request.current_user["user_id"]).first()
        rows = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_date.desc()).all()
    elif role == "doctor":
        doctor = Doctor.query.filter_by(user_id=request.current_user["user_id"]).first()
        rows = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.appointment_date.desc()).all()
    else:
        rows = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify([appointment_json(a) for a in rows])

@app.patch("/api/appointments/<int:appointment_id>")
@token_required(["admin", "doctor"])
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.get_json() or {}
    status = data.get("status")
    if status not in {"scheduled", "completed", "cancelled"}:
        return jsonify({"message": "Invalid status"}), 400
    appointment.status = status
    db.session.commit()
    return jsonify(appointment_json(appointment))

@app.post("/api/prescriptions")
@token_required(["doctor"])
def create_prescription():
    data = request.get_json() or {}
    appointment = Appointment.query.get(data.get("appointment_id"))
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404

    doctor = Doctor.query.filter_by(user_id=request.current_user["user_id"]).first()
    if appointment.doctor_id != doctor.id:
        return jsonify({"message": "You can only prescribe for your appointments"}), 403

    prescription = Prescription(
        appointment_id=appointment.id,
        diagnosis=data.get("diagnosis", ""),
        notes=data.get("notes", "")
    )
    db.session.add(prescription)
    db.session.flush()

    for item in data.get("items", []):
        if item.get("medicine") and item.get("dosage"):
            db.session.add(PrescriptionItem(
                prescription_id=prescription.id,
                medicine=item["medicine"],
                dosage=item["dosage"],
                duration=item.get("duration", "")
            ))

    db.session.commit()
    return prescription_json(prescription), 201

def prescription_json(p):
    return {
        "id": p.id,
        "appointment_id": p.appointment_id,
        "patient_name": p.appointment.patient.user.name,
        "doctor_name": p.appointment.doctor.user.name,
        "diagnosis": p.diagnosis,
        "notes": p.notes,
        "created_at": p.created_at.isoformat(),
        "items": [
            {"medicine": i.medicine, "dosage": i.dosage, "duration": i.duration}
            for i in p.items
        ]
    }

@app.get("/api/prescriptions")
@token_required()
def prescriptions():
    role = request.current_user["role"]
    if role == "patient":
        patient = Patient.query.filter_by(user_id=request.current_user["user_id"]).first()
        rows = Prescription.query.join(Appointment).filter(Appointment.patient_id == patient.id).all()
    elif role == "doctor":
        doctor = Doctor.query.filter_by(user_id=request.current_user["user_id"]).first()
        rows = Prescription.query.join(Appointment).filter(Appointment.doctor_id == doctor.id).all()
    else:
        rows = Prescription.query.all()
    return jsonify([prescription_json(p) for p in rows])

@app.get("/api/bills")
@token_required()
def bills():
    role = request.current_user["role"]
    if role == "patient":
        patient = Patient.query.filter_by(user_id=request.current_user["user_id"]).first()
        rows = Bill.query.filter_by(patient_id=patient.id).all()
    else:
        rows = Bill.query.order_by(Bill.created_at.desc()).all()

    return jsonify([
        {
            "id": b.id,
            "patient_id": b.patient_id,
            "patient_name": b.patient.user.name,
            "appointment_id": b.appointment_id,
            "amount": float(b.amount),
            "status": b.status,
            "description": b.description,
            "created_at": b.created_at.isoformat()
        } for b in rows
    ])

@app.post("/api/bills")
@token_required(["admin"])
def create_bill():
    data = request.get_json() or {}
    patient = Patient.query.get(data.get("patient_id"))
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    bill = Bill(
        patient_id=patient.id,
        appointment_id=data.get("appointment_id"),
        amount=Decimal(str(data.get("amount", 0))),
        status=data.get("status", "unpaid"),
        description=data.get("description", "")
    )
    db.session.add(bill)
    db.session.commit()
    return jsonify({"id": bill.id}), 201

@app.get("/api/admin/stats")
@token_required(["admin"])
def stats():
    return jsonify({
        "patients": Patient.query.count(),
        "doctors": Doctor.query.count(),
        "appointments": Appointment.query.count(),
        "scheduled": Appointment.query.filter_by(status="scheduled").count(),
        "completed": Appointment.query.filter_by(status="completed").count(),
        "bills": Bill.query.count()
    })

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
