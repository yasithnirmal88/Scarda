import type { ChartDataPoint, PlantOverview, WeatherData } from '../types';

export const mockPlantOverview: PlantOverview = {
  totalPower: 2_450_500,
  dailyEnergy: 18_500_000,
  totalSections: 4,
  totalInverters: 36,
  totalStrings: 864,
  activeInverters: 34,
  healthyStrings: 812,
  warningStrings: 32,
  criticalStrings: 12,
  offlineStrings: 8,
  efficiency: 94.2,
};

export const mockWeather: WeatherData = {
  temperature: 28.5,
  feelsLike: 26.2,
  condition: 'partly cloudy',
  humidity: 65.0,
  irradiance: 850.0,
  windSpeed: 12.3,
  windDirection: 'NNE',
  precipitation: 0.0,
  description: 'Partly cloudy',
  timestamp: new Date().toISOString(),
};

export const mockPowerHistory = [
  { time: '00:00', power: 0 },
  { time: '04:00', power: 0 },
  { time: '06:00', power: 120 },
  { time: '07:00', power: 450 },
  { time: '08:00', power: 980 },
  { time: '09:00', power: 1520 },
  { time: '10:00', power: 1890 },
  { time: '11:00', power: 2150 },
  { time: '12:00', power: 2340 },
  { time: '13:00', power: 2280 },
  { time: '14:00', power: 2060 },
  { time: '15:00', power: 1720 },
  { time: '16:00', power: 1250 },
  { time: '17:00', power: 680 },
  { time: '18:00', power: 180 },
  { time: '20:00', power: 0 },
  { time: '24:00', power: 0 },
];

export const mockEfficiencyHistory = [
  { time: '00:00', efficiency: 0 },
  { time: '06:00', efficiency: 88 },
  { time: '07:00', efficiency: 91 },
  { time: '08:00', efficiency: 93 },
  { time: '09:00', efficiency: 94 },
  { time: '10:00', efficiency: 95 },
  { time: '11:00', efficiency: 95 },
  { time: '12:00', efficiency: 94 },
  { time: '13:00', efficiency: 94 },
  { time: '14:00', efficiency: 93 },
  { time: '15:00', efficiency: 92 },
  { time: '16:00', efficiency: 91 },
  { time: '17:00', efficiency: 89 },
  { time: '18:00', efficiency: 85 },
  { time: '24:00', efficiency: 0 },
];

export function generateMockChartData(): ChartDataPoint[] {
  return [
    { time: '00:00', power: 0, voltage: 0, current: 0, temperature: 20, irradiance: 0, efficiency: 0 },
    { time: '04:00', power: 0, voltage: 0, current: 0, temperature: 18, irradiance: 0, efficiency: 0 },
    { time: '06:00', power: 120, voltage: 350, current: 0.34, temperature: 22, irradiance: 150, efficiency: 88 },
    { time: '07:00', power: 450, voltage: 480, current: 0.94, temperature: 27, irradiance: 380, efficiency: 91 },
    { time: '08:00', power: 980, voltage: 540, current: 1.81, temperature: 32, irradiance: 620, efficiency: 93 },
    { time: '09:00', power: 1520, voltage: 580, current: 2.62, temperature: 36, irradiance: 820, efficiency: 94 },
    { time: '10:00', power: 1890, voltage: 610, current: 3.10, temperature: 39, irradiance: 960, efficiency: 95 },
    { time: '11:00', power: 2150, voltage: 630, current: 3.41, temperature: 42, irradiance: 1040, efficiency: 95 },
    { time: '12:00', power: 2340, voltage: 650, current: 3.60, temperature: 44, irradiance: 1080, efficiency: 94 },
    { time: '13:00', power: 2280, voltage: 640, current: 3.56, temperature: 45, irradiance: 1050, efficiency: 94 },
    { time: '14:00', power: 2060, voltage: 620, current: 3.32, temperature: 44, irradiance: 950, efficiency: 93 },
    { time: '15:00', power: 1720, voltage: 590, current: 2.92, temperature: 42, irradiance: 780, efficiency: 92 },
    { time: '16:00', power: 1250, voltage: 550, current: 2.27, temperature: 39, irradiance: 580, efficiency: 91 },
    { time: '17:00', power: 680, voltage: 480, current: 1.42, temperature: 35, irradiance: 350, efficiency: 89 },
    { time: '18:00', power: 180, voltage: 380, current: 0.47, temperature: 31, irradiance: 120, efficiency: 85 },
    { time: '20:00', power: 0, voltage: 0, current: 0, temperature: 26, irradiance: 0, efficiency: 0 },
    { time: '24:00', power: 0, voltage: 0, current: 0, temperature: 22, irradiance: 0, efficiency: 0 },
  ];
}

export const mockNotifications = [
  { id: 1, message: 'Inverter INV-05 went offline', time: '2m ago', type: 'error' },
  { id: 2, message: 'String STR-012 power below threshold', time: '15m ago', type: 'warning' },
  { id: 3, message: 'Daily energy target exceeded', time: '1h ago', type: 'success' },
  { id: 4, message: 'Section B irradiance sensor warning', time: '2h ago', type: 'warning' },
  { id: 5, message: 'Scheduled maintenance INV-09 completed', time: '3h ago', type: 'info' },
];
