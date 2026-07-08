export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const NAV_ITEMS = [
  { label: 'Dashboard', path: '/dashboard', icon: 'Dashboard' },
  { label: 'Sections', path: '/sections', icon: 'Sections' },
  { label: 'Inverters', path: '/inverters', icon: 'Inverters' },
  { label: 'Strings', path: '/strings', icon: 'Strings' },
  { label: 'Alerts', path: '/alerts', icon: 'Alerts' },
  { label: 'Reports', path: '/reports', icon: 'Reports' },
  { label: 'Settings', path: '/settings', icon: 'Settings' },
];

export const ROLES = ['admin', 'engineer', 'manager'] as const;
