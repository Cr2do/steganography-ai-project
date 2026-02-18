import { Component, signal } from '@angular/core';

import { Authentifier } from '../authentifier/authentifier';
import { Verfication } from '../verfication/verfication';

type DashboardMode = 'home' | 'verify' | 'sign';

@Component({
  selector: 'app-main-dashboard',
  imports: [Verfication, Authentifier],
  templateUrl: './main-dashboard.html',
  styleUrl: './main-dashboard.css',
})
export class MainDashboard {
  readonly mode = signal<DashboardMode>('home');

  setMode(mode: DashboardMode) {
    this.mode.set(mode);
  }
}
