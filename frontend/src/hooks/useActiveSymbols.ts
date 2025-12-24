import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { SymbolsResponse } from '@/types';

export interface UseActiveSymbolsOptions {
  enabled?: boolean;
  staleTime?: number;
  gcTime?: number;
  retry?: number;
  retryDelay?: number | ((attemptIndex: number) => number);
}

export const useActiveSymbols = (
  options: UseActiveSymbolsOptions = {}
): UseQueryResult<SymbolsResponse, Error> => {
  const {
    enabled = true,
    staleTime = 300000, // 5 minutes (symbols don't change frequently)
    gcTime = 600000, // 10 minutes
    retry = 3,
    retryDelay = (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  } = options;

  return useQuery<SymbolsResponse, Error>({
    queryKey: ['activeSymbols'],
    queryFn: () => apiService.getActiveSymbols(),
    enabled,
    staleTime,
    gcTime,
    retry,
    retryDelay,
    // Don't refetch on window focus since symbols are relatively static
    refetchOnWindowFocus: false,
    // Don't refetch on reconnect to avoid excessive requests
    refetchOnReconnect: false,
    // Keep data fresh in background
    refetchInterval: 600000, // 10 minutes
  });
};
