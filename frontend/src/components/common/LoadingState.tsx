import React from 'react';
import LoadingSpinner from './LoadingSpinner';
import LoadingSkeleton from './LoadingSkeleton';

interface LoadingStateProps {
  loading: boolean;
  children: React.ReactNode;
  type?: 'spinner' | 'skeleton';
  skeletonVariant?:
    | 'dashboard'
    | 'stock-analysis'
    | 'alerts-table'
    | 'chart'
    | 'card'
    | 'list';
  skeletonCount?: number;
  spinnerMessage?: string;
  spinnerVariant?: 'default' | 'overlay' | 'inline' | 'minimal';
}

const LoadingState: React.FC<LoadingStateProps> = ({
  loading,
  children,
  type = 'spinner',
  skeletonVariant = 'card',
  skeletonCount = 1,
  spinnerMessage = 'Đang tải...',
  spinnerVariant = 'default',
}) => {
  if (loading) {
    if (type === 'skeleton') {
      return (
        <LoadingSkeleton variant={skeletonVariant} count={skeletonCount} />
      );
    }

    return <LoadingSpinner message={spinnerMessage} variant={spinnerVariant} />;
  }

  return <>{children}</>;
};

export default LoadingState;
