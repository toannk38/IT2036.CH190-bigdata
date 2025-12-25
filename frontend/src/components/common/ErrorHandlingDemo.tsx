import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Stack,
} from '@mui/material';
import {
  ErrorBoundary,
  ErrorMessage,
  LoadingState,
  RetryButton,
  ErrorRecovery,
} from './index';
import { useErrorRecovery } from '@/hooks';

// Demo component that throws errors
const ErrorThrowingComponent: React.FC<{ shouldThrow: boolean }> = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('This is a demo error from ErrorThrowingComponent');
  }
  return <Typography>Component rendered successfully!</Typography>;
};

// Demo component for API error simulation
const ApiErrorDemo: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const simulateApiCall = async () => {
    setLoading(true);
    setError(null);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Randomly succeed or fail
    if (Math.random() > 0.5) {
      setLoading(false);
      return 'API call successful!';
    } else {
      const apiError = new Error('Simulated API error');
      setError(apiError);
      setLoading(false);
      throw apiError;
    }
  };

  const handleRetry = async () => {
    try {
      await simulateApiCall();
    } catch (err) {
      // Error is already handled in simulateApiCall
    }
  };

  return (
    <Box>
      <LoadingState loading={loading} type="spinner" spinnerMessage="Calling API...">
        {error ? (
          <ErrorMessage
            error={error}
            onRetry={handleRetry}
            showRetry={true}
            title="API Call Failed"
          />
        ) : (
          <Box>
            <Typography variant="body1" gutterBottom>
              API Demo - Click to simulate API call
            </Typography>
            <Button variant="contained" onClick={simulateApiCall}>
              Call API
            </Button>
          </Box>
        )}
      </LoadingState>
    </Box>
  );
};

// Demo component using useErrorRecovery hook
const ErrorRecoveryHookDemo: React.FC = () => {
  const {
    error,
    isRetrying,
    retryCount,
    canRetry,
    retry,
    executeWithRecovery,
  } = useErrorRecovery({
    maxRetries: 3,
    autoRetryOn: ['NETWORK_ERROR'],
  });

  const simulateOperation = async () => {
    // Simulate random failure
    if (Math.random() > 0.6) {
      throw new Error('Random operation failure');
    }
    return 'Operation successful!';
  };

  const handleExecute = async () => {
    try {
      const result = await executeWithRecovery(simulateOperation);
      console.log(result);
    } catch (err) {
      console.error('Operation failed after retries:', err);
    }
  };

  return (
    <Box>
      <Typography variant="body1" gutterBottom>
        Error Recovery Hook Demo (Max 3 retries)
      </Typography>
      
      <Stack spacing={2}>
        <Button 
          variant="contained" 
          onClick={handleExecute}
          disabled={isRetrying}
        >
          {isRetrying ? 'Executing...' : 'Execute Operation'}
        </Button>
        
        {error && (
          <ErrorMessage
            error={error}
            onRetry={canRetry ? retry : undefined}
            showRetry={canRetry}
            retryCount={retryCount}
            maxRetries={3}
          />
        )}
        
        {retryCount > 0 && (
          <Typography variant="caption" color="text.secondary">
            Retry attempts: {retryCount}/3
          </Typography>
        )}
      </Stack>
    </Box>
  );
};

// Main demo component
const ErrorHandlingDemo: React.FC = () => {
  const [throwError, setThrowError] = useState(false);
  const [showLoading, setShowLoading] = useState(false);

  const simulateLoading = () => {
    setShowLoading(true);
    setTimeout(() => setShowLoading(false), 3000);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Error Handling Components Demo
      </Typography>
      
      <Stack spacing={4}>
        {/* Error Boundary Demo */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            1. Error Boundary Demo
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              onClick={() => setThrowError(!throwError)}
              color={throwError ? 'error' : 'primary'}
            >
              {throwError ? 'Fix Component' : 'Break Component'}
            </Button>
          </Box>
          <ErrorBoundary>
            <ErrorThrowingComponent shouldThrow={throwError} />
          </ErrorBoundary>
        </Paper>

        {/* Loading State Demo */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            2. Loading State Demo
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Button variant="outlined" onClick={simulateLoading}>
              Show Loading (3s)
            </Button>
          </Box>
          <LoadingState 
            loading={showLoading} 
            type="skeleton" 
            skeletonVariant="card"
          >
            <Typography>Content loaded successfully!</Typography>
          </LoadingState>
        </Paper>

        {/* API Error Demo */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            3. API Error Handling Demo
          </Typography>
          <ApiErrorDemo />
        </Paper>

        {/* Error Recovery Hook Demo */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            4. Error Recovery Hook Demo
          </Typography>
          <ErrorRecoveryHookDemo />
        </Paper>

        {/* Error Recovery Component Demo */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            5. Error Recovery Component Demo
          </Typography>
          <ErrorRecovery
            maxRetries={2}
            showRetryButton={true}
            showErrorDetails={true}
            loadingType="skeleton"
            skeletonVariant="card"
          >
            <Typography>
              This content is wrapped in ErrorRecovery component.
              It will handle errors automatically with retry functionality.
            </Typography>
          </ErrorRecovery>
        </Paper>
      </Stack>
    </Box>
  );
};

export default ErrorHandlingDemo;