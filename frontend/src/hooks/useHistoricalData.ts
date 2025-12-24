import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { HistoricalData } from '@/types';

export interface UseHistoricalDataOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  retry?: number;
  retryDelay?: number | ((attemptIndex: number) => number);
}

export const useHistoricalData = (
  symbol: string,
  startDate: string,
  endDate: string,
  options: UseHistoricalDataOptions = {}
): UseQueryResult<HistoricalData, Error> => {
  const {
    enabled = true,
    staleTime = 300000, // 5 minutes (historical data is relatively stable)
    gcTime = 600000, // 10 minutes
    retry = 3,
    retryDelay = (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  } = options;

  // Only enable query if all required parameters are provided
  const isEnabled = enabled && !!symbol && !!startDate && !!endDate;

  return useQuery<HistoricalData, Error>({
    queryKey: ['historicalData', symbol, startDate, endDate],
    queryFn: () => apiService.getHistoricalData(symbol, startDate, endDate),
    enabled: isEnabled,
    staleTime,
    gcTime,
    retry,
    retryDelay,
    // Don't refetch on window focus for historical data
    refetchOnWindowFocus: false,
    // Don't refetch on reconnect to avoid excessive requests
    refetchOnReconnect: false,
  });
};