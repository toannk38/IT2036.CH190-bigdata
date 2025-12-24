import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { StockSummary } from '@/types';

export interface UseStockSummaryOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  retry?: number;
  retryDelay?: number | ((attemptIndex: number) => number);
}

export const useStockSummary = (
  symbol: string,
  options: UseStockSummaryOptions = {}
): UseQueryResult<StockSummary, Error> => {
  const {
    enabled = true,
    staleTime = 30000, // 30 seconds
    gcTime = 300000, // 5 minutes
    retry = 3,
    retryDelay = (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  } = options;

  return useQuery<StockSummary, Error>({
    queryKey: ['stockSummary', symbol],
    queryFn: () => apiService.getStockSummary(symbol),
    enabled: enabled && !!symbol,
    staleTime,
    gcTime,
    retry,
    retryDelay,
    // Refetch on window focus for fresh data
    refetchOnWindowFocus: true,
    // Don't refetch on reconnect to avoid excessive requests
    refetchOnReconnect: false,
  });
};