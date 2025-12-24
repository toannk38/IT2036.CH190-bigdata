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
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  // Format volume with abbreviated notation
  const formatVolume = (volume: number): string => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`;
    }
    return volume.toLocaleString('vi-VN');
  };

  // Calculate price change and percentage
  const priceChange = priceData.close - priceData.open;
  const priceChangePercent = ((priceChange / priceData.open) * 100);
  const isPositive = priceChange >= 0;

  // Format timestamp
  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch (error) {
      return timestamp;
    }
  };

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
              label={`${isPositive ? '+' : ''}${formatPrice(priceChange)}`}
              color={isPositive ? 'success' : 'error'}
              size="small"
            />
            <Chip
              label={`${isPositive ? '+' : ''}${priceChangePercent.toFixed(2)}%`}
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
            <Typography variant="h6" color={isPositive ? 'success.main' : 'error.main'}>
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