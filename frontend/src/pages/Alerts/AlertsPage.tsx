import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Pagination,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useAlerts } from '@/hooks/useAlerts';
import { AlertsTable } from './components';

const AlertsPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const {
    data: alertsResponse,
    isLoading,
    error,
  } = useAlerts({
    limit: pageSize,
    offset: (page - 1) * pageSize,
  });

  const handlePageChange = (
    _event: React.ChangeEvent<unknown>,
    newPage: number
  ) => {
    setPage(newPage);
  };

  const totalPages = alertsResponse
    ? Math.ceil(alertsResponse.total / pageSize)
    : 0;

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error.message || 'Đã xảy ra lỗi khi tải dữ liệu cảnh báo'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Cảnh Báo Thị Trường
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Theo dõi các cảnh báo quan trọng từ hệ thống phân tích
        </Typography>
      </Box>

      {isLoading ? (
        <Box display="flex" justifyContent="center" sx={{ mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <AlertsTable
            alerts={alertsResponse?.alerts || []}
            loading={isLoading}
          />

          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" sx={{ mt: 4 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                size="large"
                showFirstButton
                showLastButton
              />
            </Box>
          )}

          {alertsResponse && alertsResponse.alerts.length === 0 && (
            <Box textAlign="center" sx={{ mt: 4 }}>
              <Typography variant="h6" color="text.secondary">
                Không có cảnh báo nào
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Hiện tại không có cảnh báo nào trong hệ thống
              </Typography>
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default AlertsPage;
