import React from 'react';
import { Box, Typography, Button, Paper, Alert } from '@mui/material';
import { ErrorOutline, Refresh, Home } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface ErrorFallbackProps {
  error?: Error | null;
  resetError?: () => void;
  title?: string;
  message?: string;
  showRetry?: boolean;
  showHome?: boolean;
  variant?: 'default' | 'minimal' | 'inline';
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetError,
  title = 'Đã xảy ra lỗi',
  message = 'Rất tiếc, đã xảy ra lỗi không mong muốn. Vui lòng thử lại.',
  showRetry = true,
  showHome = true,
  variant = 'default',
}) => {
  const navigate = useNavigate();

  const handleRetry = () => {
    if (resetError) {
      resetError();
    } else {
      window.location.reload();
    }
  };

  const handleGoHome = () => {
    navigate('/');
  };

  if (variant === 'minimal') {
    return (
      <Box textAlign="center" p={2}>
        <Typography variant="body2" color="error" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          {message}
        </Typography>
        {showRetry && (
          <Button size="small" onClick={handleRetry}>
            Thử lại
          </Button>
        )}
      </Box>
    );
  }

  if (variant === 'inline') {
    return (
      <Alert
        severity="error"
        action={
          showRetry ? (
            <Button color="inherit" size="small" onClick={handleRetry}>
              Thử lại
            </Button>
          ) : undefined
        }
      >
        <Typography variant="body2">{message}</Typography>
      </Alert>
    );
  }

  // Default variant
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="300px"
      p={3}
    >
      <Paper
        elevation={2}
        sx={{
          p: 4,
          maxWidth: 500,
          width: '100%',
          textAlign: 'center',
        }}
      >
        <ErrorOutline
          sx={{
            fontSize: 48,
            color: 'error.main',
            mb: 2,
          }}
        />

        <Typography variant="h6" gutterBottom color="error">
          {title}
        </Typography>

        <Typography variant="body2" color="text.secondary" paragraph>
          {message}
        </Typography>

        {process.env.NODE_ENV === 'development' && error && (
          <Alert severity="error" sx={{ mt: 2, mb: 2, textAlign: 'left' }}>
            <Typography
              variant="body2"
              component="pre"
              sx={{ fontSize: '0.75rem' }}
            >
              {error.message}
            </Typography>
          </Alert>
        )}

        <Box
          sx={{
            mt: 3,
            display: 'flex',
            gap: 2,
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}
        >
          {showRetry && (
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={handleRetry}
              size="small"
            >
              Thử lại
            </Button>
          )}

          {showHome && (
            <Button
              variant="outlined"
              startIcon={<Home />}
              onClick={handleGoHome}
              size="small"
            >
              Về trang chủ
            </Button>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default ErrorFallback;
