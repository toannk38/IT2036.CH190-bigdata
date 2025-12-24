export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const ROUTES = {
  DASHBOARD: '/',
  STOCK_ANALYSIS: '/stock/:symbol',
  ALERTS: '/alerts',
  HISTORICAL: '/historical',
} as const;

export const COLORS = {
  BUY: '#4caf50',
  SELL: '#f44336',
  HOLD: '#ff9800',
  HIGH_PRIORITY: '#f44336',
  MEDIUM_PRIORITY: '#ff9800',
  LOW_PRIORITY: '#4caf50',
} as const;
