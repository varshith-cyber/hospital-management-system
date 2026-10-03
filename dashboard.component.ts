import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { ApiService } from './api.service';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
  <header class="topbar">
    <div class="container nav">
      <div class="brand">✚ CarePoint</div>
      <div class="user">
        <span>{{ auth.user()?.name }} · {{ auth.user()?.role }}</span>
        <button class="btn secondary" (click)="logout()">Logout</button>
      </div>
    </div>
  </header>

  <main class="container page">
    <section class="hero">
      <div>
        <h1>Good day, {{ auth.user()?.name }}</h1>
        <p>Manage hospital operations from one place.</p>
      </div>
    </section>

    @if (auth.user()?.role === 'admin') {
      <div class="grid grid-3 stats">
        <div class="card stat"><span>Patients</span><strong>{{stats.patients}}</strong></div>
        <div class="card stat"><span>Doctors</span><strong>{{stats.doctors}}</strong></div>
        <div class="card stat"><span>Appointments</span><strong>{{stats.appointments}}</strong></div>
        <div class="card stat"><span>Scheduled</span><strong>{{stats.scheduled}}</strong></div>
        <div class="card stat"><span>Completed</span><strong>{{stats.completed}}</strong></div>
        <div class="card stat"><span>Bills</span><strong>{{stats.bills}}</strong></div>
      </div>
    }

    @if (auth.user()?.role === 'patient') {
      <div class="grid grid-2">
        <div class="card">
          <h2>Book appointment</h2>
          <form (ngSubmit)="book()">
            <label>Doctor
              <select [(ngModel)]="appointment.doctor_id" name="doctor_id" required>
                <option value="" disabled>Select doctor</option>
                @for (d of doctors; track d.id) {
                  <option [value]="d.id">{{d.name}} — {{d.specialization}}</option>
                }
              </select>
            </label>
            <label>Date and time
              <input type="datetime-local" [(ngModel)]="appointment.appointment_date" name="appointment_date" required>
            </label>
            <label>Reason
              <textarea [(ngModel)]="appointment.reason" name="reason" rows="3"></textarea>
            </label>
            <button class="btn">Book appointment</button>
          </form>
          @if (message) { <p class="success">{{message}}</p> }
        </div>

        <div class="card">
          <h2>Available doctors</h2>
          @for (d of doctors; track d.id) {
            <div class="doctor">
              <div class="avatar">DR</div>
              <div><strong>{{d.name}}</strong><br>{{d.specialization}} · {{d.department}}</div>
            </div>
          }
        </div>
      </div>
    }

    <div class="grid grid-2 section">
      <div class="card">
        <h2>Appointments</h2>
        @if (!appointments.length) { <p>No appointments found.</p> }
        @if (appointments.length) {
          <table>
            <thead><tr><th>Date</th><th>Doctor</th><th>Status</th><th>Reason</th></tr></thead>
            <tbody>
              @for (a of appointments; track a.id) {
                <tr>
                  <td>{{a.appointment_date | date:'medium'}}</td>
                  <td>{{a.doctor_name}}</td>
                  <td><span class="badge">{{a.status}}</span></td>
                  <td>{{a.reason}}</td>
                </tr>
              }
            </tbody>
          </table>
        }
      </div>

      <div class="card">
        <h2>Prescriptions</h2>
        @if (!prescriptions.length) { <p>No prescriptions found.</p> }
        @for (p of prescriptions; track p.id) {
          <div class="record">
            <strong>{{p.diagnosis}}</strong>
            <div>{{p.doctor_name}} · {{p.created_at | date:'mediumDate'}}</div>
            @for (item of p.items; track item.medicine) {
              <p>💊 {{item.medicine}} — {{item.dosage}} — {{item.duration}}</p>
            }
          </div>
        }
      </div>
    </div>

    @if (auth.user()?.role === 'admin' || auth.user()?.role === 'doctor') {
      <div class="card section">
        <h2>Patient directory</h2>
        <table>
          <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Blood group</th></tr></thead>
          <tbody>
            @for (p of patients; track p.id) {
              <tr><td>{{p.name}}</td><td>{{p.email}}</td><td>{{p.phone}}</td><td>{{p.blood_group}}</td></tr>
            }
          </tbody>
        </table>
      </div>
    }

    <div class="card section">
      <h2>Bills</h2>
      <table>
        <thead><tr><th>Patient</th><th>Description</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
          @for (b of bills; track b.id) {
            <tr><td>{{b.patient_name}}</td><td>{{b.description}}</td><td>₹{{b.amount}}</td><td><span class="badge">{{b.status}}</span></td></tr>
          }
        </tbody>
      </table>
    </div>
  </main>
  `,
  styles: [`
    .topbar { background:#fff; border-bottom:1px solid #e8edf5; position:sticky; top:0; z-index:5; }
    .nav { height:70px; display:flex; align-items:center; justify-content:space-between; }
    .brand { color:#2563eb; font-size:21px; font-weight:900; }
    .user { display:flex; align-items:center; gap:14px; font-size:14px; }
    .page { padding:30px 0 60px; }
    .hero { margin-bottom:22px; }
    .hero h1 { margin-bottom:5px; }
    .hero p { color:#667085; }
    .stats { margin-bottom:20px; }
    .stat span { color:#667085; font-size:13px; }
    .stat strong { display:block; font-size:30px; margin-top:7px; }
    .section { margin-top:20px; }
    .doctor { display:flex; gap:12px; padding:13px 0; border-bottom:1px solid #edf0f5; }
    .avatar { width:40px; height:40px; display:grid; place-items:center; border-radius:50%; background:#e8eefc; color:#2563eb; font-weight:800; }
    .record { border-bottom:1px solid #edf0f5; padding:12px 0; }
    .success { color:#15803d; }
    h2 { margin-top:0; }
  `]
})
export class DashboardComponent implements OnInit {
  auth = inject(AuthService);
  private api = inject(ApiService);
  private router = inject(Router);

  doctors: any[] = [];
  appointments: any[] = [];
  patients: any[] = [];
  prescriptions: any[] = [];
  bills: any[] = [];
  stats: any = {};
  message = '';

  appointment = {doctor_id: '', appointment_date: '', reason: ''};

  ngOnInit() {
    if (!this.auth.user() || !this.auth.token()) {
      this.router.navigate(['/login']);
      return;
    }

    this.api.doctors().subscribe(x => this.doctors = x);
    this.api.appointments().subscribe(x => this.appointments = x);
    this.api.prescriptions().subscribe(x => this.prescriptions = x);
    this.api.bills().subscribe(x => this.bills = x);

    if (this.auth.user()?.role === 'admin' || this.auth.user()?.role === 'doctor') {
      this.api.patients().subscribe(x => this.patients = x);
    }
    if (this.auth.user()?.role === 'admin') {
      this.api.stats().subscribe(x => this.stats = x);
    }
  }

  book() {
    this.message = '';
    this.api.createAppointment({
      doctor_id: Number(this.appointment.doctor_id),
      appointment_date: this.appointment.appointment_date,
      reason: this.appointment.reason
    }).subscribe({
      next: () => {
        this.message = 'Appointment booked successfully.';
        this.appointment = {doctor_id:'', appointment_date:'', reason:''};
        this.api.appointments().subscribe(x => this.appointments = x);
      },
      error: e => this.message = e.error?.message || 'Unable to book appointment.'
    });
  }

  logout() { this.auth.logout(); }
}
