import React from 'react';
import {
  Box,
  CircularProgress,
  Typography,
  Backdrop,
} from '@mui/material';

interface LoadingSpinnerProps {
  size?: number | string;
  message?: string;
  variant?: 'default' | 'overlay' | 'inline' | 'minimal';
  color?: 'primary' | 'secondary' | 'inherit';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 40,
  message = 'Đang tải...',
  variant = 'default',
  color = 'primary',
}) => {
  if (variant === 'overlay') {
    return (
      <Backdrop
        sx={{ 
          color: '#fff', 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
        }}
        open={true}
      >
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          gap={2}
        >
          <CircularProgress color={color} size={size} />
          {message && (
            <Typography variant="body1" color="inherit">
              {message}
            </Typography>
          )}
        </Box>
      </Backdrop>
    );
  }

  if (variant === 'minimal') {
    return (
      <Box display="flex" justifyContent="center" p={1}>
        <CircularProgress size={size} color={color} />
      </Box>
    );
  }

  if (variant === 'inline') {
    return (
      <Box
        display="flex"
        alignItems="center"
        gap={1}
        sx={{ py: 1 }}
      >
        <CircularProgress size={20} color={color} />
        {message && (
          <Typography variant="body2" color="text.secondary">
            {message}
          </Typography>
        )}
      </Box>
    );
  }

  // Default variant
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="200px"
      p={3}
    >
      <CircularProgress size={size} color={color} />
      {message && (
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ mt: 2 }}
        >
          {message}
        </Typography>
      )}
    </Box>
  );
};

export default LoadingSpinner;