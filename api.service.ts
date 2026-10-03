import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({providedIn: 'root'})
export class ApiService {
  private api = 'http://localhost:5000/api';
  constructor(private http: HttpClient) {}

  doctors() { return this.http.get<any[]>(`${this.api}/doctors`); }
  departments() { return this.http.get<any[]>(`${this.api}/departments`); }
  appointments() { return this.http.get<any[]>(`${this.api}/appointments`); }
  patients() { return this.http.get<any[]>(`${this.api}/patients`); }
  prescriptions() { return this.http.get<any[]>(`${this.api}/prescriptions`); }
  bills() { return this.http.get<any[]>(`${this.api}/bills`); }
  stats() { return this.http.get<any>(`${this.api}/admin/stats`); }

  createAppointment(data: any) {
    return this.http.post(`${this.api}/appointments`, data);
  }

  updateAppointment(id: number, status: string) {
    return this.http.patch(`${this.api}/appointments/${id}`, {status});
  }
}
