import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Skeleton,
  Box,
  Chip,
  Button,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  NotificationsActive,
  TrendingUp,
} from '@mui/icons-material';
import { TopAlertsCardProps } from '@/types';
import { touchTargetStyles } from '../../../utils/responsive';

const getPriorityIcon = (priority: string) => {
  switch (priority.toLowerCase()) {
    case 'high':
      return <Error sx={{ color: 'error.main' }} />;
    case 'medium':
      return <Warning sx={{ color: 'warning.main' }} />;
    case 'low':
      return <Info sx={{ color: 'info.main' }} />;
    default:
      return <Info sx={{ color: 'info.main' }} />;
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority.toLowerCase()) {
    case 'high':
      return 'error';
    case 'medium':
      return 'warning';
    case 'low':
      return 'info';
    default:
      return 'default';
  }
};

const formatTimestamp = (timestamp: string) => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return timestamp;
  }
};

export const TopAlertsCard: React.FC<TopAlertsCardProps> = ({
  alerts,
  loading,
}) => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleAlertClick = (symbol: string) => {
    navigate(`/stock/${symbol}`);
  };

  const handleViewAllAlerts = () => {
    navigate('/alerts');
  };

  if (loading) {
    return (
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <NotificationsActive sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h2">
              Cảnh Báo Quan Trọng
            </Typography>
          </Box>
          <List>
            {Array.from({ length: 5 }).map((_, index) => (
              <ListItem key={index} divider sx={touchTargetStyles.listItem}>
                <ListItemIcon>
                  <Skeleton variant="circular" width={24} height={24} />
                </ListItemIcon>
                <ListItemText
                  primary={<Skeleton variant="text" width="70%" />}
                  secondary={<Skeleton variant="text" width="90%" />}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <NotificationsActive sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h2">
              Cảnh Báo Quan Trọng
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <TrendingUp sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              Không có cảnh báo nào
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Thị trường đang ổn định
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <NotificationsActive sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            Cảnh Báo Quan Trọng
          </Typography>
          <Chip
            label={alerts.length}
            size="small"
            color="primary"
            sx={{ 
              ml: 2,
              ...touchTargetStyles.chip,
            }}
          />
        </Box>

        <List sx={{ p: 0 }}>
          {alerts.map((alert, index) => (
            <ListItem
              key={`${alert.symbol}-${alert.timestamp}-${index}`}
              divider={index < alerts.length - 1}
              sx={{ px: 0 }}
            >
              <ListItemButton
                onClick={() => handleAlertClick(alert.symbol)}
                sx={{
                  borderRadius: 1,
                  ...touchTargetStyles.listItem,
                  py: { xs: 2, sm: 1.5 }, // Extra padding on mobile
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                  '&:active': {
                    backgroundColor: 'action.selected',
                  },
                }}
              >
                <ListItemIcon sx={{ 
                  minWidth: { xs: 48, sm: 40 },
                  '& .MuiSvgIcon-root': {
                    fontSize: { xs: '1.5rem', sm: '1.25rem' },
                  },
                }}>
                  {getPriorityIcon(alert.priority)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: 1,
                      flexWrap: { xs: 'wrap', sm: 'nowrap' },
                    }}>
                      <Typography
                        variant="subtitle2"
                        component="span"
                        sx={{ 
                          fontWeight: 'bold', 
                          color: 'primary.main',
                          fontSize: { xs: '1rem', sm: '0.875rem' },
                        }}
                      >
                        {alert.symbol}
                      </Typography>
                      <Chip
                        label={alert.priority.toUpperCase()}
                        size="small"
                        color={
                          getPriorityColor(alert.priority) as
                            | 'default'
                            | 'primary'
                            | 'secondary'
                            | 'error'
                            | 'info'
                            | 'success'
                            | 'warning'
                        }
                        sx={{ 
                          fontSize: { xs: '0.75rem', sm: '0.7rem' }, 
                          height: { xs: 24, sm: 20 },
                          ...touchTargetStyles.chip,
                        }}
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          mb: 0.5,
                          display: '-webkit-box',
                          WebkitLineClamp: { xs: 3, sm: 2 },
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          fontSize: { xs: '0.875rem', sm: '0.75rem' },
                          lineHeight: 1.4,
                        }}
                      >
                        {alert.message}
                      </Typography>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ fontSize: { xs: '0.75rem', sm: '0.7rem' } }}
                      >
                        {formatTimestamp(alert.timestamp)}
                      </Typography>
                    </Box>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Button
            variant="outlined"
            size={isMobile ? "medium" : "small"}
            onClick={handleViewAllAlerts}
            sx={{ 
              textTransform: 'none',
              ...touchTargetStyles.button,
              fontSize: { xs: '1rem', sm: '0.875rem' },
            }}
          >
            Xem tất cả cảnh báo
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};
