import type { WeatherData } from '../types';
import { mockWeather } from '../mock/fakeData';

export const weatherService = {
  getCurrent: async (): Promise<WeatherData> => {
    return Promise.resolve({ ...mockWeather });
  },
};
