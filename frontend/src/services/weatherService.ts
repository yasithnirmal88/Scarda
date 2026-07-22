import api from './api';
import type { WeatherData } from '../types';
import { mockWeather } from '../mock/fakeData';

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
  getCurrent: async (): Promise<WeatherData> => {
    try {
      const { data } = await api.get<WeatherApiResponse>('/weather/current');
      if (data?.data) {
        const w = data.data;
        return {
          temperature: w.temperature_c ?? mockWeather.temperature,
          feelsLike: (w.temperature_c ?? mockWeather.temperature) - 2,
          condition: w.description ?? mockWeather.condition,
          humidity: w.humidity_pct ?? mockWeather.humidity,
          irradiance: w.irradiance_wpm2 ?? mockWeather.irradiance,
          windSpeed: w.wind_speed_mps ?? mockWeather.windSpeed,
          windDirection: w.wind_direction ?? mockWeather.windDirection,
          precipitation: w.precipitation_mm ?? mockWeather.precipitation,
          description: w.description ?? mockWeather.description,
          timestamp: w.timestamp ?? new Date().toISOString(),
        };
      }
    } catch {
      // fallback
    }
    return Promise.resolve({ ...mockWeather });
  },
};
