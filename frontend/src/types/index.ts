export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'engineer' | 'manager';
  isActive: boolean;
  createdAt: string;
}

export interface Section {
  id: number;
  name: string;
  description: string;
  inverterCount: number;
  stringCount: number;
  totalPower: number;
  status: 'healthy' | 'warning' | 'critical' | 'offline';
}

export interface Inverter {
  id: number;
  sectionId: number;
  name: string;
  modelNumber: string;
  status: 'online' | 'offline' | 'error' | 'maintenance';
  power: number;
  voltage: number;
  current: number;
  temperature: number;
  efficiency: number;
  stringCount: number;
}

export interface PVString {
  id: number;
  inverterId: number;
  name: string;
  panelCount: number;
  voltage: number;
  current: number;
  power: number;
  temperature: number;
  status: 'active' | 'inactive' | 'error';
  degradation: number;
}

export interface Alert {
  id: number;
  inverterId: number | null;
  stringId: number | null;
  type: string;
  severity: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  source: string;
  timestamp: string;
  status: 'active' | 'acknowledged' | 'resolved';
  createdAt: string;
  resolvedAt: string | null;
}

export interface WeatherData {
  temperature: number;
  feelsLike: number;
  condition: string;
  humidity: number;
  irradiance: number;
  windSpeed: number;
  windDirection: string;
  precipitation: number;
  description: string;
  timestamp: string;
}

export interface PlantOverview {
  totalPower: number;
  dailyEnergy: number;
  totalSections: number;
  totalInverters: number;
  totalStrings: number;
  activeInverters: number;
  healthyStrings: number;
  warningStrings: number;
  criticalStrings: number;
  offlineStrings: number;
  efficiency: number;
}

export interface MaintenanceLog {
  id: number;
  inverterId: number | null;
  stringId: number | null;
  userId: number;
  title: string;
  description: string;
  section: string;
  date: string;
  technician: string;
  scheduledDate: string;
  completedDate: string | null;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  createdAt: string;
}

export interface Report {
  id: number;
  title: string;
  type: 'daily' | 'weekly' | 'monthly' | 'custom';
  generatedAt: string;
  status: 'generating' | 'ready' | 'failed';
}

export type SortDirection = 'asc' | 'desc';

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
}

export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

export interface ChartDataPoint {
  time: string;
  power?: number;
  voltage?: number;
  current?: number;
  temperature?: number;
  irradiance?: number;
  efficiency?: number;
}

export interface HeatmapCell {
  stringId: string;
  inverterId: string;
  sectionId: string;
  value: number;
  status: 'healthy' | 'warning' | 'critical' | 'offline';
}
