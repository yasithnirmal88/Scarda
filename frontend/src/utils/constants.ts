export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const SECTIONS_COUNT = 4;
export const INVERTERS_PER_SECTION = 9;
export const STRINGS_PER_INVERTER = 24;
export const TOTAL_INVERTERS = SECTIONS_COUNT * INVERTERS_PER_SECTION;
export const TOTAL_STRINGS = TOTAL_INVERTERS * STRINGS_PER_INVERTER;

export const SEVERITY_COLORS: Record<string, string> = {
  info: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  critical: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
};

export const STATUS_COLORS: Record<string, string> = {
  healthy: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  critical: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  offline: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  online: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  inactive: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  maintenance: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
};
