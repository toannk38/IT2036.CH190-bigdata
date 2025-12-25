import React from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
  Paper,
} from '@mui/material';
import { ArrowBack, Refresh } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useStockSummary } from '@/hooks/useStockSummary';
import { StockAnalysisProps } from '@/types';
import {
  PriceInfoCard,
  RecommendationCard,
  ComponentScoresChart,
  AnalysisDetails,
  AlertsList,
} from './components';

const StockAnalysis: React.FC<StockAnalysisProps> = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();

  const {
    data: stockSummary,
    isLoading,
    error,
    refetch,
    isRefetching,
  } = useStockSummary(symbol || '');

  // Handle loading state
  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="400px"
        >
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Đang tải dữ liệu phân tích...
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Mã cổ phiếu: {symbol?.toUpperCase()}
          </Typography>
        </Box>
      </Container>
    );
  }

  // Handle error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate('/')}
            variant="outlined"
          >
            Quay lại Dashboard
          </Button>
        </Box>

        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Không thể tải dữ liệu phân tích
            </Typography>
            <Typography variant="body1">
              {error.message || 'Đã xảy ra lỗi khi tải dữ liệu'}
            </Typography>
          </Alert>

          <Box sx={{ mt: 3 }}>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={() => refetch()}
              disabled={isRefetching}
              sx={{ mr: 2 }}
            >
              {isRefetching ? 'Đang thử lại...' : 'Thử lại'}
            </Button>
            <Button variant="outlined" onClick={() => navigate('/')}>
              Quay lại Dashboard
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  // Handle case where no data is returned
  if (!stockSummary) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate('/')}
            variant="outlined"
          >
            Quay lại Dashboard
          </Button>
        </Box>

        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Alert severity="warning" sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Không tìm thấy dữ liệu
            </Typography>
            <Typography variant="body1">
              Không có dữ liệu phân tích cho mã cổ phiếu:{' '}
              {symbol?.toUpperCase()}
            </Typography>
          </Alert>

          <Box sx={{ mt: 3 }}>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={() => refetch()}
              disabled={isRefetching}
              sx={{ mr: 2 }}
            >
              {isRefetching ? 'Đang thử lại...' : 'Thử lại'}
            </Button>
            <Button variant="outlined" onClick={() => navigate('/')}>
              Quay lại Dashboard
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  // Main content when data is loaded successfully
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header with back button and stock info */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate('/')}
            variant="outlined"
            sx={{ mr: 2 }}
          >
            Dashboard
          </Button>
          <Button
            startIcon={<Refresh />}
            onClick={() => refetch()}
            disabled={isRefetching}
            variant="outlined"
            size="small"
          >
            {isRefetching ? 'Đang cập nhật...' : 'Cập nhật'}
          </Button>
        </Box>

        <Typography variant="h4" component="h1" gutterBottom>
          Phân Tích Cổ Phiếu: {symbol?.toUpperCase()}
        </Typography>

        {stockSummary.last_updated && (
          <Typography variant="body2" color="text.secondary">
            Cập nhật lần cuối:{' '}
            {new Date(stockSummary.last_updated).toLocaleString('vi-VN')}
          </Typography>
        )}
      </Box>

      {/* Main content */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 3,
        }}
      >
        {/* Top Row - Price and Recommendation */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            gap: 3,
          }}
        >
          <Box sx={{ flex: { md: '1 1 50%' } }}>
            <PriceInfoCard priceData={stockSummary.current_price} />
          </Box>
          <Box sx={{ flex: { md: '1 1 50%' } }}>
            <RecommendationCard
              finalScore={stockSummary.final_score}
              recommendation={stockSummary.recommendation}
            />
          </Box>
        </Box>

        {/* Second Row - Component Scores and Analysis Details */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', lg: 'row' },
            gap: 3,
          }}
        >
          <Box sx={{ flex: { lg: '1 1 33%' } }}>
            <ComponentScoresChart scores={stockSummary.component_scores} />
          </Box>
          <Box sx={{ flex: { lg: '1 1 67%' } }}>
            <AnalysisDetails
              aiAnalysis={stockSummary.ai_ml_analysis}
              llmAnalysis={stockSummary.llm_analysis}
            />
          </Box>
        </Box>

        {/* Third Row - Alerts (if any) */}
        {stockSummary.alerts && stockSummary.alerts.length > 0 && (
          <Box>
            <AlertsList alerts={stockSummary.alerts} />
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default StockAnalysis;
