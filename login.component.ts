import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

@Component({
  standalone: true,
  imports: [FormsModule],
  template: `
  <div class="login-page">
    <div class="login-card">
      <div class="brand">✚ CarePoint</div>
      <h1>Hospital Management System</h1>
      <p class="muted">Sign in to continue</p>

      <form (ngSubmit)="login()">
        <label>Email
          <input type="email" [(ngModel)]="email" name="email" required>
        </label>
        <label>Password
          <input type="password" [(ngModel)]="password" name="password" required>
        </label>
        <button class="btn" style="width:100%" [disabled]="loading">
          {{ loading ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>

      @if (error) { <p class="error">{{ error }}</p> }

      <div class="demo">
        <strong>Demo accounts</strong>
        <div>Admin: admin@hospital.com / admin123</div>
        <div>Doctor: doctor@hospital.com / doctor123</div>
        <div>Patient: patient@hospital.com / patient123</div>
      </div>
    </div>
  </div>
  `,
  styles: [`
    .login-page { min-height:100vh; display:grid; place-items:center; padding:20px; background:linear-gradient(135deg,#eaf2ff,#f7fbff); }
    .login-card { width:min(450px,100%); background:#fff; padding:34px; border-radius:20px; box-shadow:0 20px 60px rgba(30,60,100,.12); }
    .brand { color:#2563eb; font-size:22px; font-weight:900; margin-bottom:20px; }
    h1 { margin:0 0 8px; font-size:28px; }
    .muted { color:#667085; }
    .error { color:#dc2626; background:#fef2f2; padding:10px; border-radius:8px; }
    .demo { margin-top:20px; background:#f5f7fb; padding:14px; border-radius:10px; font-size:12px; line-height:1.8; }
  `]
})
export class LoginComponent {
  email = 'patient@hospital.com';
  password = 'patient123';
  error = '';
  loading = false;

  private auth = inject(AuthService);
  private router = inject(Router);

  login() {
    this.loading = true;
    this.error = '';
    this.auth.login(this.email, this.password).subscribe({
      next: r => {
        this.auth.saveSession(r.token, r.user);
        this.router.navigate(['/dashboard']);
      },
      error: e => {
        this.error = e.error?.message || 'Unable to sign in';
        this.loading = false;
      }
    });
  }
}
