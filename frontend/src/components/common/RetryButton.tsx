import React, { useState } from 'react';
import {
  Button,
  CircularProgress,
  Box,
  Typography,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';

interface RetryButtonProps {
  onRetry: () => void | Promise<void>;
  disabled?: boolean;
  loading?: boolean;
  variant?: 'contained' | 'outlined' | 'text';
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
  children?: React.ReactNode;
  retryCount?: number;
  maxRetries?: number;
  showRetryCount?: boolean;
}

const RetryButton: React.FC<RetryButtonProps> = ({
  onRetry,
  disabled = false,
  loading = false,
  variant = 'contained',
  size = 'medium',
  fullWidth = false,
  children = 'Thử lại',
  retryCount = 0,
  maxRetries,
  showRetryCount = false,
}) => {
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    if (disabled || loading || isRetrying) return;

    setIsRetrying(true);
    try {
      await onRetry();
    } catch (error) {
      console.error('Retry failed:', error);
    } finally {
      setIsRetrying(false);
    }
  };

  const isDisabled = disabled || loading || isRetrying || (maxRetries !== undefined && retryCount >= maxRetries);

  return (
    <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
      <Button
        variant={variant}
        size={size}
        fullWidth={fullWidth}
        disabled={isDisabled}
        onClick={handleRetry}
        startIcon={
          isRetrying ? (
            <CircularProgress size={16} color="inherit" />
          ) : (
            <Refresh />
          )
        }
        sx={{
          minWidth: size === 'small' ? 100 : size === 'large' ? 140 : 120,
        }}
      >
        {isRetrying ? 'Đang thử lại...' : children}
      </Button>
      
      {showRetryCount && retryCount > 0 && (
        <Typography variant="caption" color="text.secondary">
          Đã thử {retryCount} lần
          {maxRetries && ` / ${maxRetries}`}
        </Typography>
      )}
      
      {maxRetries && retryCount >= maxRetries && (
        <Typography variant="caption" color="error">
          Đã đạt giới hạn thử lại
        </Typography>
      )}
    </Box>
  );
};

export default RetryButton;