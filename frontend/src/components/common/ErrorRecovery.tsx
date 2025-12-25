import React from 'react';
import { Box } from '@mui/material';
import ErrorMessage from './ErrorMessage';
import LoadingState from './LoadingState';
import { useErrorRecovery } from '@/hooks';
import { ApiError } from '@/types';

interface ErrorRecoveryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  maxRetries?: number;
  retryDelay?: number;
  autoRetryOn?: string[];
  showRetryButton?: boolean;
  showErrorDetails?: boolean;
  loadingType?: 'spinner' | 'skeleton';
  skeletonVariant?:
    | 'dashboard'
    | 'stock-analysis'
    | 'alerts-table'
    | 'chart'
    | 'card'
    | 'list';
  onError?: (error: Error | ApiError) => void;
  onRecovery?: () => void;
}

const ErrorRecovery: React.FC<ErrorRecoveryProps> = ({
  children,
  fallback,
  maxRetries = 3,
  retryDelay = 1000,
  autoRetryOn = ['NETWORK_ERROR', 'TIMEOUT'],
  showRetryButton = true,
  showErrorDetails = false,
  loadingType = 'spinner',
  skeletonVariant = 'card',
  onError,
  onRecovery,
}) => {
  const { error, isRetrying, retryCount, canRetry, retry } = useErrorRecovery({
    maxRetries,
    retryDelay,
    exponentialBackoff: true,
    autoRetryOn,
    onError,
    onRecovery,
  });

  // Show loading state while retrying
  if (isRetrying) {
    return (
      <LoadingState
        loading={true}
        type={loadingType}
        skeletonVariant={skeletonVariant}
        spinnerMessage="Đang thử lại..."
      >
        {children}
      </LoadingState>
    );
  }

  // Show error state if there's an error
  if (error) {
    // Use custom fallback if provided
    if (fallback) {
      return <>{fallback}</>;
    }

    // Default error UI
    return (
      <Box sx={{ p: 2 }}>
        <ErrorMessage
          error={error}
          onRetry={canRetry && showRetryButton ? retry : undefined}
          showRetry={showRetryButton && canRetry}
          retryCount={retryCount}
          maxRetries={maxRetries}
          showDetails={showErrorDetails}
          collapsible={showErrorDetails}
        />
      </Box>
    );
  }

  // Show children if no error
  return <>{children}</>;
};

export default ErrorRecovery;
