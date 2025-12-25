import { useState, useCallback } from 'react';

interface UseRetryOptions {
  maxRetries?: number;
  retryDelay?: number;
  exponentialBackoff?: boolean;
  onRetry?: (attempt: number) => void;
  onMaxRetriesReached?: () => void;
}

interface UseRetryReturn {
  retry: () => Promise<void>;
  retryCount: number;
  isRetrying: boolean;
  canRetry: boolean;
  reset: () => void;
}

export const useRetry = (
  operation: () => Promise<void> | void,
  options: UseRetryOptions = {}
): UseRetryReturn => {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    exponentialBackoff = true,
    onRetry,
    onMaxRetriesReached,
  } = options;

  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);

  const canRetry = retryCount < maxRetries;

  const retry = useCallback(async () => {
    if (!canRetry || isRetrying) {
      return;
    }

    setIsRetrying(true);

    try {
      // Calculate delay with exponential backoff if enabled
      const delay = exponentialBackoff
        ? retryDelay * Math.pow(2, retryCount)
        : retryDelay;

      // Wait before retrying (except for first retry)
      if (retryCount > 0) {
        await new Promise((resolve) => setTimeout(resolve, delay));
      }

      // Call the retry callback if provided
      if (onRetry) {
        onRetry(retryCount + 1);
      }

      // Execute the operation
      await operation();

      // Reset retry count on success
      setRetryCount(0);
    } catch (error) {
      // Increment retry count
      const newRetryCount = retryCount + 1;
      setRetryCount(newRetryCount);

      // Check if max retries reached
      if (newRetryCount >= maxRetries && onMaxRetriesReached) {
        onMaxRetriesReached();
      }

      // Re-throw the error so it can be handled by the caller
      throw error;
    } finally {
      setIsRetrying(false);
    }
  }, [
    operation,
    retryCount,
    canRetry,
    isRetrying,
    maxRetries,
    retryDelay,
    exponentialBackoff,
    onRetry,
    onMaxRetriesReached,
  ]);

  const reset = useCallback(() => {
    setRetryCount(0);
    setIsRetrying(false);
  }, []);

  return {
    retry,
    retryCount,
    isRetrying,
    canRetry,
    reset,
  };
};
