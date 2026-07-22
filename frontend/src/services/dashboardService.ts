import api from './api';

export interface DashboardResponse {
  power: {
    total_power_kw: number;
    daily_energy_kwh: number;
    peak_power_kw: number | null;
  };
  plant: {
    total_sections: number;
    total_inverters: number;
    total_strings: number;
    active_inverters: number;
  };
  weather: {
    temperature_c: number | null;
    humidity_pct: number | null;
    irradiance_wpm2: number | null;
    wind_speed_mps: number | null;
    wind_direction: string | null;
    precipitation_mm: number | null;
    description: string | null;
  };
  alerts: {
    total: number;
    critical: number;
    warning: number;
    info: number;
  };
  timestamp: string;
}

export const dashboardService = {
  get: async (): Promise<DashboardResponse> => {
    const { data } = await api.get('/dashboard');
    return data;
  },
};
