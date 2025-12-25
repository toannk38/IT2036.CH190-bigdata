import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  ShowChart,
  VolumeUp,
} from '@mui/icons-material';
import { PriceInfoCardProps } from '@/types';
import {
  formatPrice,
  formatVolume,
  formatTimestamp,
  formatPriceChange,
  formatPercentageChange,
} from '@/utils';

const PriceInfoCard: React.FC<PriceInfoCardProps> = ({ priceData }) => {
  if (!priceData) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Thông Tin Giá
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Không có dữ liệu giá
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Format number with Vietnamese locale
  // API returns price in thousands VND, so multiply by 1000 to get actual VND
  // Using centralized formatter functions for consistency

  // Calculate price change and percentage
  const priceChange = priceData.close - priceData.open;
  const priceChangePercent = (priceChange / priceData.open) * 100;
  const isPositive = priceChange >= 0;

  // Format price change with proper styling
  const formattedPriceChange = formatPriceChange(priceChange);
  const formattedPercentChange = formatPercentageChange(priceChangePercent);

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <ShowChart sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            Thông Tin Giá
          </Typography>
        </Box>

        {/* Current Price and Change */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="div" gutterBottom>
            {formatPrice(priceData.close)}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              icon={isPositive ? <TrendingUp /> : <TrendingDown />}
              label={formattedPriceChange.value}
              color={formattedPriceChange.color as 'success' | 'error'}
              size="small"
            />
            <Chip
              label={formattedPercentChange}
              color={isPositive ? 'success' : 'error'}
              variant="outlined"
              size="small"
            />
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Price Details */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            gap: 2,
          }}
        >
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Giá Mở Cửa
            </Typography>
            <Typography variant="h6" color="primary.main">
              {formatPrice(priceData.open)}
            </Typography>
          </Box>

          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Giá Đóng Cửa
            </Typography>
            <Typography
              variant="h6"
              color={isPositive ? 'success.main' : 'error.main'}
            >
              {formatPrice(priceData.close)}
            </Typography>
          </Box>

          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Giá Cao Nhất
            </Typography>
            <Typography variant="h6" color="success.main">
              {formatPrice(priceData.high)}
            </Typography>
          </Box>

          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Giá Thấp Nhất
            </Typography>
            <Typography variant="h6" color="error.main">
              {formatPrice(priceData.low)}
            </Typography>
          </Box>
        </Box>

        {/* Volume */}
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 3 }}>
          <VolumeUp sx={{ mr: 1, color: 'text.secondary' }} />
          <Box>
            <Typography variant="body2" color="text.secondary">
              Khối Lượng Giao Dịch
            </Typography>
            <Typography variant="h6">
              {formatVolume(priceData.volume)} cổ phiếu
            </Typography>
          </Box>
        </Box>

        {/* Timestamp */}
        <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            Cập nhật: {formatTimestamp(priceData.timestamp)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PriceInfoCard;
