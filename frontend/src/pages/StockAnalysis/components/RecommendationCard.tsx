import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Assessment,
} from '@mui/icons-material';
import { RecommendationCardProps } from '@/types';
import { COLORS } from '@/constants';

const RecommendationCard: React.FC<RecommendationCardProps> = ({
  finalScore,
  recommendation,
}) => {
  // Get recommendation details
  const getRecommendationDetails = (rec?: 'BUY' | 'SELL' | 'HOLD') => {
    switch (rec) {
      case 'BUY':
        return {
          label: 'MUA',
          color: COLORS.BUY,
          icon: <TrendingUp />,
          severity: 'success' as const,
          description: 'Khuyến nghị mua cổ phiếu này',
        };
      case 'SELL':
        return {
          label: 'BÁN',
          color: COLORS.SELL,
          icon: <TrendingDown />,
          severity: 'error' as const,
          description: 'Khuyến nghị bán cổ phiếu này',
        };
      case 'HOLD':
        return {
          label: 'GIỮ',
          color: COLORS.HOLD,
          icon: <TrendingFlat />,
          severity: 'warning' as const,
          description: 'Khuyến nghị giữ cổ phiếu này',
        };
      default:
        return {
          label: 'CHƯA XÁC ĐỊNH',
          color: '#9e9e9e',
          icon: <Assessment />,
          severity: 'info' as const,
          description: 'Chưa có khuyến nghị',
        };
    }
  };

  const recommendationDetails = getRecommendationDetails(recommendation);

  // Format final score
  const formatScore = (score?: number): string => {
    if (score === undefined || score === null) return 'N/A';
    return (score * 100).toFixed(1);
  };

  // Get score color based on value
  const getScoreColor = (score?: number): string => {
    if (score === undefined || score === null) return '#9e9e9e';
    if (score >= 0.7) return COLORS.BUY;
    if (score >= 0.4) return COLORS.HOLD;
    return COLORS.SELL;
  };

  // Get score level description
  const getScoreLevel = (score?: number): string => {
    if (score === undefined || score === null) return 'Không xác định';
    if (score >= 0.8) return 'Rất tích cực';
    if (score >= 0.6) return 'Tích cực';
    if (score >= 0.4) return 'Trung tính';
    if (score >= 0.2) return 'Tiêu cực';
    return 'Rất tiêu cực';
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Assessment sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            Khuyến Nghị Đầu Tư
          </Typography>
        </Box>

        {/* Recommendation Badge */}
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Chip
            icon={recommendationDetails.icon}
            label={recommendationDetails.label}
            sx={{
              backgroundColor: recommendationDetails.color,
              color: 'white',
              fontSize: '1.1rem',
              fontWeight: 'bold',
              height: 48,
              '& .MuiChip-icon': {
                color: 'white',
              },
            }}
            size="medium"
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {recommendationDetails.description}
          </Typography>
        </Box>

        {/* Final Score Section */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Điểm Tổng Hợp
          </Typography>

          {finalScore !== undefined && finalScore !== null ? (
            <>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography
                  variant="h4"
                  sx={{ color: getScoreColor(finalScore), mr: 1 }}
                >
                  {formatScore(finalScore)}
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  /100
                </Typography>
              </Box>

              <LinearProgress
                variant="determinate"
                value={finalScore * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  mb: 1,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getScoreColor(finalScore),
                  },
                }}
              />

              <Typography variant="body2" color="text.secondary">
                Mức độ: {getScoreLevel(finalScore)}
              </Typography>
            </>
          ) : (
            <Alert severity="info" sx={{ mt: 1 }}>
              Chưa có điểm đánh giá
            </Alert>
          )}
        </Box>

        {/* Additional Information */}
        <Alert severity={recommendationDetails.severity} sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Lưu ý:</strong> Đây chỉ là khuyến nghị dựa trên phân tích dữ
            liệu. Vui lòng tham khảo thêm các nguồn thông tin khác và cân nhắc
            kỹ trước khi đầu tư.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );
};

export default RecommendationCard;
