import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MainDashboard } from './main-dashboard/main-dashboard';

@Component({
  selector: 'app-root',
  imports: [MainDashboard],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('steganography');
}
