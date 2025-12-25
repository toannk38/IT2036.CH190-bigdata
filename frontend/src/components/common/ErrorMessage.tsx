import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Typography,
  Collapse,
  IconButton,
} from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import RetryButton from './RetryButton';
import { ApiError } from '@/types';

interface ErrorMessageProps {
  error: Error | ApiError | string;
  title?: string;
  onRetry?: () => void | Promise<void>;
  showRetry?: boolean;
  retryCount?: number;
  maxRetries?: number;
  variant?: 'standard' | 'filled' | 'outlined';
  severity?: 'error' | 'warning' | 'info';
  showDetails?: boolean;
  collapsible?: boolean;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  error,
  title,
  onRetry,
  showRetry = true,
  retryCount = 0,
  maxRetries,
  variant = 'standard',
  severity = 'error',
  showDetails = false,
  collapsible = false,
}) => {
  const [expanded, setExpanded] = React.useState(false);

  // Extract error information
  const getErrorInfo = () => {
    if (typeof error === 'string') {
      return {
        message: error,
        status: undefined,
        code: undefined,
        stack: undefined,
      };
    }

    if ('status' in error) {
      // ApiError
      return {
        message: error.message,
        status: error.status,
        code: error.code,
        stack: undefined,
      };
    }

    // Regular Error
    return {
      message: error.message,
      status: undefined,
      code: undefined,
      stack: (error as Error).stack,
    };
  };

  const errorInfo = getErrorInfo();

  const getErrorTitle = () => {
    if (title) return title;

    if (errorInfo.status) {
      switch (errorInfo.status) {
        case 404:
          return 'Không tìm thấy dữ liệu';
        case 500:
          return 'Lỗi hệ thống';
        case 503:
          return 'Dịch vụ không khả dụng';
        case 408:
          return 'Hết thời gian chờ';
        default:
          return 'Đã xảy ra lỗi';
      }
    }

    if (errorInfo.code === 'NETWORK_ERROR') {
      return 'Lỗi kết nối mạng';
    }

    return 'Đã xảy ra lỗi';
  };

  const getSeverity = () => {
    if (severity !== 'error') return severity;

    if (errorInfo.status) {
      if (errorInfo.status >= 500) return 'error';
      if (errorInfo.status === 404) return 'warning';
      if (errorInfo.status >= 400) return 'warning';
    }

    if (errorInfo.code === 'NETWORK_ERROR') return 'warning';

    return 'error';
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Alert
        severity={getSeverity()}
        variant={variant}
        action={
          <Box display="flex" alignItems="center" gap={1}>
            {collapsible && (showDetails || errorInfo.stack) && (
              <IconButton
                size="small"
                onClick={() => setExpanded(!expanded)}
                sx={{ color: 'inherit' }}
              >
                {expanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            )}
            {showRetry && onRetry && (
              <RetryButton
                onRetry={onRetry}
                variant="text"
                size="small"
                retryCount={retryCount}
                maxRetries={maxRetries}
                showRetryCount={false}
              />
            )}
          </Box>
        }
      >
        <AlertTitle>{getErrorTitle()}</AlertTitle>
        <Typography variant="body2">{errorInfo.message}</Typography>

        {errorInfo.status && (
          <Typography
            variant="caption"
            display="block"
            sx={{ mt: 1, opacity: 0.8 }}
          >
            Mã lỗi: {errorInfo.status}
            {errorInfo.code && ` (${errorInfo.code})`}
          </Typography>
        )}
      </Alert>

      {collapsible && (showDetails || errorInfo.stack) && (
        <Collapse in={expanded}>
          <Alert
            severity="info"
            variant="outlined"
            sx={{ mt: 1, borderTopLeftRadius: 0, borderTopRightRadius: 0 }}
          >
            <AlertTitle>Chi tiết lỗi</AlertTitle>
            {errorInfo.stack && (
              <Typography
                variant="body2"
                component="pre"
                sx={{
                  fontSize: '0.75rem',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  maxHeight: 200,
                  overflow: 'auto',
                }}
              >
                {errorInfo.stack}
              </Typography>
            )}
            {showDetails && !errorInfo.stack && (
              <Typography variant="body2">
                Không có thông tin chi tiết
              </Typography>
            )}
          </Alert>
        </Collapse>
      )}

      {showRetry && onRetry && retryCount > 0 && (
        <Box sx={{ mt: 1, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Đã thử {retryCount} lần
            {maxRetries && ` / ${maxRetries}`}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ErrorMessage;
