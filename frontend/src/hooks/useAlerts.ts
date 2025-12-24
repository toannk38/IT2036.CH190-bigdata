import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { AlertResponse, AlertsQueryParams } from '@/types';

export interface UseAlertsOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  retry?: number;
  retryDelay?: number | ((attemptIndex: number) => number);
  placeholderData?: (previousData: AlertResponse | undefined) => AlertResponse | undefined;
}

export const useAlerts = (
  params: AlertsQueryParams,
  options: UseAlertsOptions = {}
): UseQueryResult<AlertResponse, Error> => {
  const {
    enabled = true,
    staleTime = 60000, // 1 minute
    gcTime = 300000, // 5 minutes
    retry = 3,
    retryDelay = (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    placeholderData = (previousData) => previousData
  } = options;

  return useQuery<AlertResponse, Error>({
    queryKey: ['alerts', params],
    queryFn: () => apiService.getAlerts(params),
    enabled,
    staleTime,
    gcTime,
    retry,
    retryDelay,
    // Keep previous data for smooth pagination experience
    placeholderData,
    // Refetch on window focus for fresh alerts
    refetchOnWindowFocus: true,
    // Don't refetch on reconnect to avoid excessive requests
    refetchOnReconnect: false,
  });
};

// Convenience hook for top alerts (used in Dashboard)
export const useTopAlerts = (
  limit: number = 5,
  options: UseAlertsOptions = {}
): UseQueryResult<AlertResponse, Error> => {
  return useAlerts(
    { limit, offset: 0 },
    {
      ...options,
      staleTime: 30000, // 30 seconds for top alerts (more frequent updates)
    }
  );
};