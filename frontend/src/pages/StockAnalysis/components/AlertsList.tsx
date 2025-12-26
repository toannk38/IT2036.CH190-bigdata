import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Alert as MuiAlert,
  Divider,
  Paper,
  Badge,
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  NotificationImportant,
  TrendingUp,
  TrendingDown,
  ShowChart,
  Security,
} from '@mui/icons-material';
import { AlertsListProps } from '@/types';

const AlertsList: React.FC<AlertsListProps> = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <NotificationImportant sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">
              Cảnh Báo
            </Typography>
          </Box>
          <MuiAlert severity="info" sx={{ borderRadius: 2 }}>
            <Typography variant="body2">
              Không có cảnh báo nào cho mã cổ phiếu này. Tình hình hiện tại ổn định.
            </Typography>
          </MuiAlert>
        </CardContent>
      </Card>
    );
  }

  // Get alert priority details
  const getPriorityDetails = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return {
          color: '#f44336',
          bgColor: '#ffebee',
          borderColor: '#f44336',
          icon: <Error />,
          label: 'Cao',
          severity: 'error' as const,
        };
      case 'medium':
        return {
          color: '#ff9800',
          bgColor: '#fff3e0',
          borderColor: '#ff9800',
          icon: <Warning />,
          label: 'Trung bình',
          severity: 'warning' as const,
        };
      case 'low':
        return {
          color: '#2196f3',
          bgColor: '#e3f2fd',
          borderColor: '#2196f3',
          icon: <Info />,
          label: 'Thấp',
          severity: 'info' as const,
        };
      default:
        return {
          color: '#9e9e9e',
          bgColor: '#f5f5f5',
          borderColor: '#9e9e9e',
          icon: <NotificationImportant />,
          label: 'Không xác định',
          severity: 'info' as const,
        };
    }
  };

  // Get alert type details
  const getAlertTypeDetails = (type: string) => {
    const typeMap: { [key: string]: { label: string; icon: JSX.Element; color: string } } = {
      'BUY': { label: 'Tín hiệu MUA', icon: <TrendingUp />, color: '#4caf50' },
      'SELL': { label: 'Tín hiệu BÁN', icon: <TrendingDown />, color: '#f44336' },
      'HOLD': { label: 'Tín hiệu GIỮ', icon: <ShowChart />, color: '#ff9800' },
      'WATCH': { label: 'Theo dõi', icon: <ShowChart />, color: '#2196f3' },
      'price_movement': { label: 'Biến động giá', icon: <ShowChart />, color: '#ff9800' },
      'volume_spike': { label: 'Tăng khối lượng', icon: <TrendingUp />, color: '#4caf50' },
      'news_sentiment': { label: 'Tâm lý tin tức', icon: <Info />, color: '#2196f3' },
      'technical_signal': { label: 'Tín hiệu kỹ thuật', icon: <ShowChart />, color: '#9c27b0' },
      'risk_alert': { label: 'Cảnh báo rủi ro', icon: <Security />, color: '#f44336' },
      'recommendation_change': { label: 'Thay đổi khuyến nghị', icon: <NotificationImportant />, color: '#ff5722' },
    };
    return typeMap[type] || { label: type, icon: <Info />, color: '#9e9e9e' };
  };

  // Sort alerts by priority (high > medium > low)
  const sortedAlerts = [...alerts].sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    return (priorityOrder[b.priority as keyof typeof priorityOrder] || 0) - 
           (priorityOrder[a.priority as keyof typeof priorityOrder] || 0);
  });

  // Count alerts by priority
  const alertCounts = alerts.reduce((acc, alert) => {
    acc[alert.priority] = (acc[alert.priority] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <NotificationImportant sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h2">
              Cảnh Báo
            </Typography>
            <Badge 
              badgeContent={alerts.length} 
              color="primary" 
              sx={{ ml: 1 }}
            />
          </Box>
          
          {/* Priority summary */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            {alertCounts.high && (
              <Chip 
                label={`${alertCounts.high} Cao`} 
                size="small" 
                sx={{ backgroundColor: '#f44336', color: 'white' }}
              />
            )}
            {alertCounts.medium && (
              <Chip 
                label={`${alertCounts.medium} TB`} 
                size="small" 
                sx={{ backgroundColor: '#ff9800', color: 'white' }}
              />
            )}
            {alertCounts.low && (
              <Chip 
                label={`${alertCounts.low} Thấp`} 
                size="small" 
                sx={{ backgroundColor: '#2196f3', color: 'white' }}
              />
            )}
          </Box>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {sortedAlerts.map((alert, index) => {
            const priorityDetails = getPriorityDetails(alert.priority);
            const typeDetails = getAlertTypeDetails(alert.type);

            return (
              <Paper
                key={index}
                elevation={1}
                sx={{
                  p: 2,
                  border: `2px solid ${priorityDetails.borderColor}`,
                  backgroundColor: priorityDetails.bgColor,
                  borderRadius: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                  {/* Priority Icon */}
                  <Box
                    sx={{
                      color: priorityDetails.color,
                      backgroundColor: 'white',
                      borderRadius: '50%',
                      p: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minWidth: 40,
                      height: 40,
                    }}
                  >
                    {priorityDetails.icon}
                  </Box>

                  {/* Alert Content */}
                  <Box sx={{ flex: 1 }}>
                    {/* Header with chips */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                      <Chip
                        label={priorityDetails.label}
                        size="small"
                        sx={{
                          backgroundColor: priorityDetails.color,
                          color: 'white',
                          fontWeight: 'bold',
                          fontSize: '0.75rem',
                        }}
                      />
                      <Chip
                        icon={typeDetails.icon}
                        label={typeDetails.label}
                        size="small"
                        variant="outlined"
                        sx={{
                          borderColor: typeDetails.color,
                          color: typeDetails.color,
                          fontSize: '0.75rem',
                          '& .MuiChip-icon': {
                            color: typeDetails.color,
                          },
                        }}
                      />
                    </Box>

                    {/* Alert Message */}
                    <Typography
                      variant="body1"
                      sx={{
                        fontWeight: 'medium',
                        lineHeight: 1.5,
                        color: 'text.primary',
                        mb: 1,
                      }}
                    >
                      {alert.message}
                    </Typography>

                    {/* Alert Type Description */}
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ 
                        fontStyle: 'italic',
                        fontSize: '0.875rem'
                      }}
                    >
                      Loại cảnh báo: {typeDetails.label}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            );
          })}
        </Box>

        {/* Summary */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>📊 Tóm tắt:</strong> Có <strong>{alerts.length}</strong> cảnh báo cho mã cổ phiếu này.
            {alertCounts.high && (
              <span style={{ color: '#f44336' }}> Có <strong>{alertCounts.high}</strong> cảnh báo mức độ cao cần được chú ý đặc biệt.</span>
            )}
            {!alertCounts.high && alertCounts.medium && (
              <span> Cảnh báo mức độ trung bình cần theo dõi.</span>
            )}
            {!alertCounts.high && !alertCounts.medium && (
              <span> Tất cả đều là cảnh báo mức độ thấp.</span>
            )}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AlertsList;
