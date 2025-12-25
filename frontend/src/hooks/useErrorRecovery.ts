import { useState, useCallback } from 'react';
import { useRetry } from './useRetry';
import { ApiError } from '@/types';

interface UseErrorRecoveryOptions {
  maxRetries?: number;
  retryDelay?: number;
  exponentialBackoff?: boolean;
  autoRetryOn?: string[]; // Error codes that should trigger automatic retry
  onError?: (error: Error | ApiError) => void;
  onRecovery?: () => void;
}

interface UseErrorRecoveryReturn {
  error: Error | ApiError | null;
  isRetrying: boolean;
  retryCount: number;
  canRetry: boolean;
  retry: () => Promise<void>;
  clearError: () => void;
  handleError: (error: Error | ApiError) => void;
  executeWithRecovery: <T>(operation: () => Promise<T>) => Promise<T>;
}

export const useErrorRecovery = (
  options: UseErrorRecoveryOptions = {}
): UseErrorRecoveryReturn => {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    exponentialBackoff = true,
    autoRetryOn = ['NETWORK_ERROR', 'TIMEOUT'],
    onError,
    onRecovery,
  } = options;

  const [error, setError] = useState<Error | ApiError | null>(null);
  const [lastOperation, setLastOperation] = useState<
    (() => Promise<unknown>) | null
  >(null);

  const retryWrapper = useCallback(async () => {
    if (!lastOperation) {
      throw new Error('No operation to retry');
    }

    try {
      await lastOperation();
      setError(null);
      if (onRecovery) {
        onRecovery();
      }
    } catch (err) {
      const apiError = err as Error | ApiError;
      setError(apiError);
      throw apiError;
    }
  }, [lastOperation, onRecovery]);

  const {
    retry,
    retryCount,
    isRetrying,
    canRetry,
    reset: resetRetry,
  } = useRetry(retryWrapper, {
    maxRetries,
    retryDelay,
    exponentialBackoff,
    onRetry: (attempt) => {
      console.log(`Retry attempt ${attempt}/${maxRetries}`);
    },
    onMaxRetriesReached: () => {
      console.log('Max retries reached');
    },
  });

  const handleError = useCallback(
    (err: Error | ApiError) => {
      setError(err);

      if (onError) {
        onError(err);
      }

      // Check if this error should trigger automatic retry
      const shouldAutoRetry = autoRetryOn.some((code) => {
        if ('code' in err) {
          return err.code === code;
        }
        return false;
      });

      if (shouldAutoRetry && canRetry) {
        console.log('Auto-retrying due to recoverable error:', err);
        setTimeout(() => {
          retry().catch(console.error);
        }, 100); // Small delay before auto-retry
      }
    },
    [onError, autoRetryOn, canRetry, retry]
  );

  const clearError = useCallback(() => {
    setError(null);
    setLastOperation(null);
    resetRetry();
  }, [resetRetry]);

  const executeWithRecovery = useCallback(
    async <T>(operation: () => Promise<T>): Promise<T> => {
      setLastOperation(() => operation);

      try {
        const result = await operation();
        setError(null);
        return result;
      } catch (err) {
        const apiError = err as Error | ApiError;
        handleError(apiError);
        throw apiError;
      }
    },
    [handleError]
  );

  return {
    error,
    isRetrying,
    retryCount,
    canRetry,
    retry,
    clearError,
    handleError,
    executeWithRecovery,
  };
};
