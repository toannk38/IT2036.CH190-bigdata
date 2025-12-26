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
    return score.toFixed(1);
  };

  // Get score color based on value (0-100 scale, higher is better)
  const getScoreColor = (score?: number): string => {
    if (score === undefined || score === null) return '#9e9e9e';
    if (score >= 70) return COLORS.BUY; // Green for good scores
    if (score >= 40) return COLORS.HOLD; // Orange for medium scores
    return COLORS.SELL; // Red for poor scores
  };

  // Get score level description (0-100 scale)
  const getScoreLevel = (score?: number): string => {
    if (score === undefined || score === null) return 'Không xác định';
    if (score >= 80) return 'Rất đáng mua';
    if (score >= 70) return 'Đáng mua';
    if (score >= 60) return 'Có thể mua';
    if (score >= 40) return 'Trung tính';
    if (score >= 30) return 'Ít hấp dẫn';
    if (score >= 20) return 'Không hấp dẫn';
    return 'Rất không hấp dẫn';
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
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography
                  variant="h3"
                  sx={{ 
                    color: getScoreColor(finalScore), 
                    mr: 1,
                    fontWeight: 'bold'
                  }}
                >
                  {formatScore(finalScore)}
                </Typography>
                <Typography variant="h5" color="text.secondary">
                  /100
                </Typography>
              </Box>

              <LinearProgress
                variant="determinate"
                value={finalScore}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  mb: 2,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getScoreColor(finalScore),
                  },
                }}
              />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Mức độ: <strong>{getScoreLevel(finalScore)}</strong>
                </Typography>
                <Chip
                  label={getScoreLevel(finalScore)}
                  size="small"
                  sx={{
                    backgroundColor: getScoreColor(finalScore),
                    color: 'white',
                    fontWeight: 'medium',
                  }}
                />
              </Box>

              {/* Score interpretation */}
              <Box sx={{ mt: 2, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  {finalScore >= 80 ? '🚀 Rất đáng mua - Cơ hội đầu tư xuất sắc' :
                   finalScore >= 70 ? '📈 Đáng mua - Cơ hội đầu tư tốt' :
                   finalScore >= 60 ? '📊 Có thể mua - Cơ hội đầu tư khá tốt' :
                   finalScore >= 40 ? '⚖️ Trung tính - Cần cân nhắc kỹ' :
                   finalScore >= 30 ? '⚠️ Ít hấp dẫn - Nên thận trọng' :
                   finalScore >= 20 ? '🔻 Không hấp dẫn - Không nên mua' : '🚨 Rất không hấp dẫn - Tránh mua'}
                </Typography>
              </Box>
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
            <strong>Lưu ý:</strong> Điểm số phản ánh mức độ hấp dẫn của cổ phiếu dựa trên phân tích dữ liệu. 
            Điểm càng cao càng có tiềm năng tăng trưởng tốt. Vui lòng tham khảo thêm các nguồn thông tin khác 
            và cân nhắc kỹ trước khi đầu tư.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );
};

export default RecommendationCard;
