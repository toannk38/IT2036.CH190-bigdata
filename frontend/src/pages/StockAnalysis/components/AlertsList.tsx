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
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  NotificationImportant,
} from '@mui/icons-material';
import { AlertsListProps } from '@/types';
import { COLORS } from '@/constants';

const AlertsList: React.FC<AlertsListProps> = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Cảnh Báo
          </Typography>
          <MuiAlert severity="info">
            Không có cảnh báo nào cho mã cổ phiếu này
          </MuiAlert>
        </CardContent>
      </Card>
    );
  }

  // Get alert priority details
  const getPriorityDetails = (priority: 'high' | 'medium' | 'low') => {
    switch (priority) {
      case 'high':
        return {
          color: COLORS.HIGH_PRIORITY,
          icon: <Error />,
          label: 'Cao',
          severity: 'error' as const,
        };
      case 'medium':
        return {
          color: COLORS.MEDIUM_PRIORITY,
          icon: <Warning />,
          label: 'Trung bình',
          severity: 'warning' as const,
        };
      case 'low':
        return {
          color: COLORS.LOW_PRIORITY,
          icon: <Info />,
          label: 'Thấp',
          severity: 'info' as const,
        };
      default:
        return {
          color: '#9e9e9e',
          icon: <NotificationImportant />,
          label: 'Không xác định',
          severity: 'info' as const,
        };
    }
  };

  // Get alert type display name
  const getAlertTypeDisplay = (type: string): string => {
    const typeMap: { [key: string]: string } = {
      'price_movement': 'Biến động giá',
      'volume_spike': 'Tăng đột biến khối lượng',
      'news_sentiment': 'Tâm lý tin tức',
      'technical_signal': 'Tín hiệu kỹ thuật',
      'risk_alert': 'Cảnh báo rủi ro',
      'recommendation_change': 'Thay đổi khuyến nghị',
    };
    return typeMap[type] || type;
  };

  // Sort alerts by priority (high > medium > low)
  const sortedAlerts = [...alerts].sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    return priorityOrder[b.priority] - priorityOrder[a.priority];
  });

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <NotificationImportant sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            Cảnh Báo ({alerts.length})
          </Typography>
        </Box>

        <List sx={{ p: 0 }}>
          {sortedAlerts.map((alert, index) => {
            const priorityDetails = getPriorityDetails(alert.priority);
            
            return (
              <React.Fragment key={index}>
                <ListItem
                  sx={{
                    px: 0,
                    py: 2,
                    alignItems: 'flex-start',
                  }}
                >
                  <ListItemIcon sx={{ mt: 0.5, minWidth: 40 }}>
                    <Box sx={{ color: priorityDetails.color }}>
                      {priorityDetails.icon}
                    </Box>
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box sx={{ mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Chip
                            label={priorityDetails.label}
                            size="small"
                            sx={{
                              backgroundColor: priorityDetails.color,
                              color: 'white',
                              fontWeight: 'medium',
                            }}
                          />
                          <Chip
                            label={getAlertTypeDisplay(alert.type)}
                            size="small"
                            variant="outlined"
                            sx={{
                              borderColor: priorityDetails.color,
                              color: priorityDetails.color,
                            }}
                          />
                        </Box>
                        <Typography
                          variant="body1"
                          sx={{
                            fontWeight: 'medium',
                            lineHeight: 1.4,
                          }}
                        >
                          {alert.message}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mt: 0.5 }}
                      >
                        Loại cảnh báo: {getAlertTypeDisplay(alert.type)}
                      </Typography>
                    }
                  />
                </ListItem>
                
                {index < sortedAlerts.length - 1 && (
                  <Divider variant="inset" component="li" />
                )}
              </React.Fragment>
            );
          })}
        </List>

        {/* Summary */}
        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Tóm tắt:</strong> Có {alerts.length} cảnh báo cho mã cổ phiếu này. 
            Cảnh báo mức độ cao cần được chú ý đặc biệt.
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AlertsList;