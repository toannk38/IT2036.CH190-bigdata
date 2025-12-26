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
  const formatScore = (score: number, isRiskScore = false): string => {
    return (score * 100).toFixed(1);
  };

  // Get color based on score value
  const getScoreColor = (score: number, isRiskScore = false): string => {
    if (isRiskScore) {
      // For risk score: lower is better (0-1 scale)
      if (score <= 0.2) return '#4caf50'; // Green for low risk
      if (score <= 0.5) return '#ff9800'; // Orange for medium risk
      return '#f44336'; // Red for high risk
    } else {
      // For other scores: higher is better (0-1 scale)
      if (score >= 0.7) return '#4caf50'; // Green
      if (score >= 0.4) return '#ff9800'; // Orange
      return '#f44336'; // Red
    }
  };

  // Get score level description
  const getScoreLevel = (score: number, isRiskScore = false): string => {
    if (isRiskScore) {
      // For risk score: lower is better
      if (score <= 0.1) return 'Rất thấp';
      if (score <= 0.2) return 'Thấp';
      if (score <= 0.4) return 'Trung bình';
      if (score <= 0.6) return 'Cao';
      return 'Rất cao';
    } else {
      // For other scores: higher is better
      if (score >= 0.8) return 'Rất tốt';
      if (score >= 0.6) return 'Tốt';
      if (score >= 0.4) return 'Trung bình';
      if (score >= 0.2) return 'Kém';
      return 'Rất kém';
    }
  };

  // Component score data
  const scoreComponents = [
    {
      key: 'technical_score',
      label: 'Phân Tích Kỹ Thuật',
      value: scores.technical_score,
      icon: <TrendingUp />,
      description: 'Đánh giá dựa trên các chỉ số kỹ thuật',
      isRiskScore: false,
    },
    {
      key: 'risk_score',
      label: 'Đánh Giá Rủi Ro',
      value: scores.risk_score,
      icon: <Security />,
      description: 'Mức độ rủi ro (thấp hơn là tốt hơn)',
      isRiskScore: true,
    },
    {
      key: 'sentiment_score',
      label: 'Tâm Lý Thị Trường',
      value: scores.sentiment_score,
      icon: <Psychology />,
      description: 'Phân tích tâm lý từ tin tức và dữ liệu',
      isRiskScore: false,
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
                <Box sx={{ color: getScoreColor(component.value, component.isRiskScore), mr: 1 }}>
                  {component.icon}
                </Box>
                <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                  {component.label}
                </Typography>
                <Chip
                  label={`${formatScore(component.value, component.isRiskScore)}%`}
                  size="small"
                  sx={{
                    backgroundColor: getScoreColor(component.value, component.isRiskScore),
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                />
              </Box>

              {/* Progress Bar */}
              <LinearProgress
                variant="determinate"
                value={component.isRiskScore ? (1 - component.value) * 100 : component.value * 100}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  mb: 1,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getScoreColor(component.value, component.isRiskScore),
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
                    color: getScoreColor(component.value, component.isRiskScore),
                    fontWeight: 'medium',
                  }}
                >
                  {getScoreLevel(component.value, component.isRiskScore)}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>

        {/* Summary */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Giải thích:</strong> 
            <br />• <strong>Phân tích kỹ thuật & Tâm lý thị trường:</strong> 0-100%, càng cao càng tốt
            <br />• <strong>Đánh giá rủi ro:</strong> 0-100%, càng thấp càng tốt (rủi ro thấp hơn)
            <br />• Trên 70% là tốt, 40-70% là trung bình, dưới 40% cần thận trọng
            <br />• Điểm số phản ánh tiềm năng tăng trưởng và mức độ hấp dẫn đầu tư
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ComponentScoresChart;
