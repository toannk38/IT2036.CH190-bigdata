import React from 'react';
import {
  Box,
  Skeleton,
  Card,
  CardContent,
} from '@mui/material';

interface LoadingSkeletonProps {
  variant?: 'dashboard' | 'stock-analysis' | 'alerts-table' | 'chart' | 'card' | 'list';
  count?: number;
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'card',
  count = 1,
}) => {
  const renderSkeleton = () => {
    switch (variant) {
      case 'dashboard':
        return (
          <Box>
            {/* Header skeleton */}
            <Box sx={{ mb: 3 }}>
              <Skeleton variant="text" width="60%" height={40} />
            </Box>
            
            <Box display="flex" gap={3} flexWrap="wrap">
              {/* Active symbols list skeleton */}
              <Box sx={{ flex: '1 1 60%', minWidth: 300 }}>
                <Card>
                  <CardContent>
                    <Skeleton variant="text" width="40%" height={32} sx={{ mb: 2 }} />
                    <Box display="flex" flexWrap="wrap" gap={1}>
                      {Array.from({ length: 12 }).map((_, index) => (
                        <Skeleton
                          key={index}
                          variant="rectangular"
                          width={80}
                          height={32}
                          sx={{ borderRadius: 1 }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Box>
              
              {/* Top alerts skeleton */}
              <Box sx={{ flex: '1 1 35%', minWidth: 250 }}>
                <Card>
                  <CardContent>
                    <Skeleton variant="text" width="60%" height={32} sx={{ mb: 2 }} />
                    {Array.from({ length: 5 }).map((_, index) => (
                      <Box key={index} sx={{ mb: 2 }}>
                        <Skeleton variant="text" width="100%" height={20} />
                        <Skeleton variant="text" width="80%" height={16} />
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Box>
            </Box>
            
            {/* Last updated info skeleton */}
            <Box sx={{ mt: 3 }}>
              <Skeleton variant="text" width="30%" height={24} />
            </Box>
          </Box>
        );

      case 'stock-analysis':
        return (
          <Box>
            {/* Stock header */}
            <Box sx={{ mb: 3 }}>
              <Skeleton variant="text" width="50%" height={40} />
              <Skeleton variant="text" width="30%" height={24} />
            </Box>
            
            <Box display="flex" gap={3} flexWrap="wrap" sx={{ mb: 3 }}>
              {/* Price info card */}
              <Box sx={{ flex: '1 1 45%', minWidth: 300 }}>
                <Card>
                  <CardContent>
                    <Skeleton variant="text" width="40%" height={32} sx={{ mb: 2 }} />
                    <Box display="flex" flexWrap="wrap" gap={2}>
                      {Array.from({ length: 5 }).map((_, index) => (
                        <Box key={index} sx={{ flex: '1 1 45%', minWidth: 120 }}>
                          <Skeleton variant="text" width="100%" height={20} />
                          <Skeleton variant="text" width="60%" height={32} />
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Box>
              
              {/* Recommendation card */}
              <Box sx={{ flex: '1 1 45%', minWidth: 300 }}>
                <Card>
                  <CardContent>
                    <Skeleton variant="text" width="50%" height={32} sx={{ mb: 2 }} />
                    <Skeleton variant="rectangular" width="100%" height={60} sx={{ mb: 2 }} />
                    <Skeleton variant="text" width="40%" height={24} />
                  </CardContent>
                </Card>
              </Box>
            </Box>
            
            <Box display="flex" gap={3} flexWrap="wrap">
              {/* Component scores chart */}
              <Box sx={{ flex: '1 1 35%', minWidth: 250 }}>
                <Card>
                  <CardContent>
                    <Skeleton variant="text" width="60%" height={32} sx={{ mb: 2 }} />
                    <Skeleton variant="rectangular" width="100%" height={200} />
                  </CardContent>
                </Card>
              </Box>
              
              {/* Analysis details */}
              <Box sx={{ flex: '1 1 60%', minWidth: 400 }}>
                <Card>
                  <CardContent>
                    <Skeleton variant="text" width="50%" height={32} sx={{ mb: 2 }} />
                    {Array.from({ length: 4 }).map((_, index) => (
                      <Skeleton key={index} variant="text" width="100%" height={20} sx={{ mb: 1 }} />
                    ))}
                  </CardContent>
                </Card>
              </Box>
            </Box>
          </Box>
        );

      case 'alerts-table':
        return (
          <Box>
            <Skeleton variant="text" width="40%" height={40} sx={{ mb: 3 }} />
            {Array.from({ length: count }).map((_, index) => (
              <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                  <Skeleton variant="text" width="15%" height={24} />
                  <Skeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 1 }} />
                </Box>
                <Skeleton variant="text" width="100%" height={20} sx={{ mb: 1 }} />
                <Skeleton variant="text" width="30%" height={16} />
              </Box>
            ))}
          </Box>
        );

      case 'chart':
        return (
          <Card>
            <CardContent>
              <Skeleton variant="text" width="40%" height={32} sx={{ mb: 2 }} />
              <Skeleton variant="rectangular" width="100%" height={300} />
            </CardContent>
          </Card>
        );

      case 'list':
        return (
          <Box>
            {Array.from({ length: count }).map((_, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Skeleton variant="text" width="100%" height={20} />
                <Skeleton variant="text" width="80%" height={16} />
              </Box>
            ))}
          </Box>
        );

      case 'card':
      default:
        return (
          <Card>
            <CardContent>
              <Skeleton variant="text" width="60%" height={32} sx={{ mb: 2 }} />
              <Skeleton variant="rectangular" width="100%" height={120} sx={{ mb: 2 }} />
              <Skeleton variant="text" width="100%" height={20} />
              <Skeleton variant="text" width="80%" height={20} />
            </CardContent>
          </Card>
        );
    }
  };

  return <>{renderSkeleton()}</>;
};

export default LoadingSkeleton;