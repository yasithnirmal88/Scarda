export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'engineer' | 'manager';
  is_active: boolean;
  created_at: string;
}

export interface Section {
  id: number;
  name: string;
  description: string | null;
}

export interface Inverter {
  id: number;
  section_id: number;
  name: string;
  model_number: string | null;
  status: string;
}

export interface String {
  id: number;
  inverter_id: number;
  name: string;
  panel_count: number;
  status: string;
}

export interface Alert {
  id: number;
  inverter_id: number | null;
  string_id: number | null;
  type: string;
  severity: string;
  message: string;
  status: string;
  created_at: string;
}

export interface WeatherReading {
  id: number;
  recorded_at: string;
  temperature: number | null;
  humidity: number | null;
  irradiance: number | null;
  wind_speed: number | null;
}

export interface StringReading {
  id: number;
  string_id: number;
  recorded_at: string;
  voltage: number | null;
  current: number | null;
  power: number | null;
}
