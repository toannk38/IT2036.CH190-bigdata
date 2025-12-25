import React from 'react';
import { Box, Typography, Chip, Paper } from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';
import { RecommendationTimelineProps } from '@/types';

export const RecommendationTimeline: React.FC<RecommendationTimelineProps> = ({
  data,
}) => {
  if (!data || data.length === 0) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height={200}
        bgcolor="grey.50"
        borderRadius={1}
      >
        <Typography variant="body1" color="text.secondary">
          Không có dữ liệu khuyến nghị để hiển thị
        </Typography>
      </Box>
    );
  }

  // Group consecutive recommendations to avoid too many timeline items
  const groupedRecommendations = data.reduce(
    (acc, point, index) => {
      const prevPoint = index > 0 ? data[index - 1] : null;

      // If this is the first point or recommendation changed, add it
      if (!prevPoint || prevPoint.recommendation !== point.recommendation) {
        acc.push(point);
      }

      return acc;
    },
    [] as typeof data
  );

  // Take only the most recent 10 changes to keep timeline manageable
  const recentRecommendations = groupedRecommendations.slice(-10);

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation.toUpperCase()) {
      case 'BUY':
        return {
          color: 'success' as const,
          bgcolor: '#e8f5e8',
          borderColor: '#4caf50',
        };
      case 'SELL':
        return {
          color: 'error' as const,
          bgcolor: '#ffebee',
          borderColor: '#f44336',
        };
      case 'HOLD':
      default:
        return {
          color: 'warning' as const,
          bgcolor: '#fff3e0',
          borderColor: '#ff9800',
        };
    }
  };

  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation.toUpperCase()) {
      case 'BUY':
        return <TrendingUp />;
      case 'SELL':
        return <TrendingDown />;
      case 'HOLD':
      default:
        return <TrendingFlat />;
    }
  };

  const getRecommendationText = (recommendation: string) => {
    switch (recommendation.toUpperCase()) {
      case 'BUY':
        return 'MUA';
      case 'SELL':
        return 'BÁN';
      case 'HOLD':
      default:
        return 'GIỮ';
    }
  };

  return (
    <Box>
      {recentRecommendations.length === 0 ? (
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          height={200}
          bgcolor="grey.50"
          borderRadius={1}
        >
          <Typography variant="body1" color="text.secondary">
            Không có thay đổi khuyến nghị trong khoảng thời gian này
          </Typography>
        </Box>
      ) : (
        <Timeline position="alternate">
          {recentRecommendations.map((point, index) => {
            const colors = getRecommendationColor(point.recommendation);
            const icon = getRecommendationIcon(point.recommendation);
            const text = getRecommendationText(point.recommendation);
            const isLast = index === recentRecommendations.length - 1;

            return (
              <TimelineItem key={`${point.timestamp}-${index}`}>
                <TimelineSeparator>
                  <TimelineDot
                    color={colors.color}
                    sx={{
                      bgcolor: colors.bgcolor,
                      border: `2px solid ${colors.borderColor}`,
                      p: 1,
                    }}
                  >
                    {icon}
                  </TimelineDot>
                  {!isLast && <TimelineConnector />}
                </TimelineSeparator>

                <TimelineContent sx={{ py: '12px', px: 2 }}>
                  <Paper
                    elevation={1}
                    sx={{
                      p: 2,
                      bgcolor: colors.bgcolor,
                      border: `1px solid ${colors.borderColor}`,
                    }}
                  >
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <Chip
                        label={text}
                        color={colors.color}
                        size="small"
                        variant="filled"
                      />
                      <Typography variant="body2" color="text.secondary">
                        Điểm: {point.final_score.toFixed(1)}
                      </Typography>
                    </Box>

                    <Typography variant="body2" color="text.secondary">
                      {new Date(point.timestamp).toLocaleDateString('vi-VN', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </Typography>
                  </Paper>
                </TimelineContent>
              </TimelineItem>
            );
          })}
        </Timeline>
      )}

      {groupedRecommendations.length > 10 && (
        <Box textAlign="center" mt={2}>
          <Typography variant="body2" color="text.secondary">
            Hiển thị 10 thay đổi khuyến nghị gần nhất (tổng cộng{' '}
            {groupedRecommendations.length} thay đổi)
          </Typography>
        </Box>
      )}
    </Box>
  );
};
