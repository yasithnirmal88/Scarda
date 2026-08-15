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
};
