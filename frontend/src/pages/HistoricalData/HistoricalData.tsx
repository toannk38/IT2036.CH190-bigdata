import React, { useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { SymbolSelector } from './components/SymbolSelector';
import { DateRangePicker } from './components/DateRangePicker';
import { FinalScoreChart } from './components/FinalScoreChart';
import { ComponentScoresChart } from './components/ComponentScoresChart';
import { RecommendationTimeline } from './components/RecommendationTimeline';
import { useHistoricalData } from '@/hooks/useHistoricalData';

export const HistoricalData: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>({
    start: '',
    end: '',
  });

  // Only fetch data when all required fields are filled
  const shouldFetch = selectedSymbol && dateRange.start && dateRange.end;

  const {
    data: historicalData,
    isLoading,
    error,
  } = useHistoricalData(selectedSymbol, dateRange.start, dateRange.end, {
    enabled: !!shouldFetch,
  });

  const handleSymbolChange = (symbol: string) => {
    setSelectedSymbol(symbol);
  };

  const handleDateRangeChange = (range: { start: string; end: string }) => {
    setDateRange(range);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Dữ Liệu Lịch Sử
      </Typography>

      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            gap: 3,
          }}
        >
          <Box sx={{ flex: 1 }}>
            <SymbolSelector
              value={selectedSymbol}
              onChange={handleSymbolChange}
            />
          </Box>

          <Box sx={{ flex: 1 }}>
            <DateRangePicker
              value={dateRange}
              onChange={handleDateRangeChange}
            />
          </Box>
        </Box>
      </Paper>

      {/* Loading State */}
      {isLoading && (
        <Box display="flex" justifyContent="center" alignItems="center" py={4}>
          <CircularProgress />
          <Typography variant="body1" sx={{ ml: 2 }}>
            Đang tải dữ liệu lịch sử...
          </Typography>
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error.message || 'Đã xảy ra lỗi khi tải dữ liệu lịch sử'}
        </Alert>
      )}

      {/* No Data State */}
      {!isLoading &&
        !error &&
        shouldFetch &&
        historicalData?.data.length === 0 && (
          <Alert severity="info" sx={{ mb: 3 }}>
            Không có dữ liệu cho khoảng thời gian được chọn. Vui lòng thử khoảng
            thời gian khác.
          </Alert>
        )}

      {/* Data Visualization */}
      {historicalData && historicalData.data.length > 0 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Điểm Số Cuối Cùng Theo Thời Gian
            </Typography>
            <FinalScoreChart data={historicalData.data} />
          </Paper>

          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Điểm Số Các Thành Phần
            </Typography>
            <ComponentScoresChart data={historicalData.data} />
          </Paper>

          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Lịch Sử Khuyến Nghị
            </Typography>
            <RecommendationTimeline data={historicalData.data} />
          </Paper>
        </Box>
      )}

      {/* Instructions when no symbol/date selected */}
      {!shouldFetch && !isLoading && (
        <Paper
          elevation={1}
          sx={{ p: 4, textAlign: 'center', bgcolor: 'grey.50' }}
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Chọn mã cổ phiếu và khoảng thời gian để xem dữ liệu lịch sử
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sử dụng các điều khiển ở trên để chọn mã cổ phiếu và khoảng thời
            gian bạn muốn phân tích
          </Typography>
        </Paper>
      )}
    </Container>
  );
};
