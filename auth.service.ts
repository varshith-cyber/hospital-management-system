import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private api = 'http://localhost:5000/api';
  user = signal<User | null>(this.loadUser());

  constructor(private http: HttpClient, private router: Router) {}

  private loadUser(): User | null {
    const raw = localStorage.getItem('hospital_user');
    return raw ? JSON.parse(raw) : null;
  }

  login(email: string, password: string) {
    return this.http.post<{token: string, user: User}>(`${this.api}/auth/login`, {email, password});
  }

  saveSession(token: string, user: User) {
    localStorage.setItem('hospital_token', token);
    localStorage.setItem('hospital_user', JSON.stringify(user));
    this.user.set(user);
  }

  logout() {
    localStorage.removeItem('hospital_token');
    localStorage.removeItem('hospital_user');
    this.user.set(null);
    this.router.navigate(['/login']);
  }

  token() { return localStorage.getItem('hospital_token'); }
}
