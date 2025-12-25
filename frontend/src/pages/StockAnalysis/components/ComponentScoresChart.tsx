import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
} from '@mui/material';
import {
  BarChart,
  TrendingUp,
  Security,
  Psychology,
} from '@mui/icons-material';
import { ComponentScoresChartProps } from '@/types';

const ComponentScoresChart: React.FC<ComponentScoresChartProps> = ({
  scores,
}) => {
  if (!scores) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Điểm Thành Phần
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Không có dữ liệu điểm thành phần
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Format score as percentage
  const formatScore = (score: number): string => {
    return (score * 100).toFixed(1);
  };

  // Get color based on score value
  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return '#4caf50'; // Green
    if (score >= 0.4) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  // Get score level description
  const getScoreLevel = (score: number): string => {
    if (score >= 0.8) return 'Rất tốt';
    if (score >= 0.6) return 'Tốt';
    if (score >= 0.4) return 'Trung bình';
    if (score >= 0.2) return 'Kém';
    return 'Rất kém';
  };

  // Component score data
  const scoreComponents = [
    {
      key: 'technical_score',
      label: 'Phân Tích Kỹ Thuật',
      value: scores.technical_score,
      icon: <TrendingUp />,
      description: 'Đánh giá dựa trên các chỉ số kỹ thuật',
    },
    {
      key: 'risk_score',
      label: 'Đánh Giá Rủi Ro',
      value: scores.risk_score,
      icon: <Security />,
      description: 'Mức độ rủi ro của cổ phiếu',
    },
    {
      key: 'sentiment_score',
      label: 'Tâm Lý Thị Trường',
      value: scores.sentiment_score,
      icon: <Psychology />,
      description: 'Phân tích tâm lý từ tin tức và dữ liệu',
    },
  ];

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <BarChart sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            Điểm Thành Phần
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {scoreComponents.map((component) => (
            <Box key={component.key} sx={{ mb: 2 }}>
              {/* Component Header */}
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Box sx={{ color: getScoreColor(component.value), mr: 1 }}>
                  {component.icon}
                </Box>
                <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                  {component.label}
                </Typography>
                <Chip
                  label={`${formatScore(component.value)}%`}
                  size="small"
                  sx={{
                    backgroundColor: getScoreColor(component.value),
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                />
              </Box>

              {/* Progress Bar */}
              <LinearProgress
                variant="determinate"
                value={component.value * 100}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  mb: 1,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getScoreColor(component.value),
                    borderRadius: 6,
                  },
                }}
              />

              {/* Score Details */}
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  {component.description}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    color: getScoreColor(component.value),
                    fontWeight: 'medium',
                  }}
                >
                  {getScoreLevel(component.value)}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>

        {/* Summary */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Giải thích:</strong> Điểm thành phần được tính từ 0-100%,
            trong đó trên 70% là tốt, 40-70% là trung bình, dưới 40% cần thận
            trọng.
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ComponentScoresChart;
