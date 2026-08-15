import api from './api';
import type { WeatherData } from '../types';

export interface WeatherApiResponse {
  status: string;
  data: {
    temperature_c: number | null;
    humidity_pct: number | null;
    irradiance_wpm2: number | null;
    wind_speed_mps: number | null;
    wind_direction: string | null;
    precipitation_mm: number | null;
    description: string | null;
    timestamp?: string;
  };
}

export interface WeatherHistoryPoint {
  timestamp: string | null;
  temperature_c: number | null;
  humidity_pct: number | null;
  irradiance_wpm2: number | null;
  wind_speed_mps: number | null;
  wind_direction: string | null;
  precipitation_mm: number | null;
}

export const weatherService = {
  // Weather comes from the backend (which reads it from the provider). No
  // hardcoded/demo weather values remain in the frontend.
  getCurrent: async (): Promise<WeatherData | null> => {
    const { data } = await api.get<WeatherApiResponse>('/weather/current');
    const w = data?.data;
    if (!w) return null;
    const temp = w.temperature_c ?? 0;
    return {
      temperature: temp,
      feelsLike: temp - 2,
      condition: w.description ?? 'Unknown',
      humidity: w.humidity_pct ?? 0,
      irradiance: w.irradiance_wpm2 ?? 0,
      windSpeed: w.wind_speed_mps ?? 0,
      windDirection: w.wind_direction ?? 'N/A',
      precipitation: w.precipitation_mm ?? 0,
      description: w.description ?? '',
      timestamp: w.timestamp ?? new Date().toISOString(),
    };
  },

  // Stored 10-min weather time series from the backend (TimescaleDB). Used to
  // visualise the live 10-min changes sent by the data source.
  getHistory: async (hours = 24): Promise<WeatherHistoryPoint[]> => {
    const { data } = await api.get<{ status: string; data: WeatherHistoryPoint[] }>(
      '/weather/history',
      { params: { hours } },
    );
    return data?.data ?? [];
  },
};
