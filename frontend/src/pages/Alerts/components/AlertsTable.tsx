import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Typography,
  Skeleton,
  Link,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { AlertItem } from '@/types';

interface AlertsTableProps {
  alerts: AlertItem[];
  loading: boolean;
}

const AlertsTable: React.FC<AlertsTableProps> = ({ alerts, loading }) => {
  const navigate = useNavigate();

  const getPriorityColor = (
    priority: string
  ): 'error' | 'warning' | 'success' => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'success';
    }
  };

  const getRecommendationColor = (
    recommendation: string
  ): 'error' | 'warning' | 'success' => {
    switch (recommendation.toUpperCase()) {
      case 'SELL':
        return 'error';
      case 'HOLD':
        return 'warning';
      case 'BUY':
        return 'success';
      default:
        return 'warning';
    }
  };

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

  const handleSymbolClick = (symbol: string) => {
    navigate(`/stock/${symbol}`);
  };

  // Sort alerts by priority (high > medium > low) then by timestamp (newest first)
  const sortedAlerts = [...alerts].sort((a, b) => {
    // Priority sorting
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    const aPriority =
      priorityOrder[a.priority.toLowerCase() as keyof typeof priorityOrder] ||
      1;
    const bPriority =
      priorityOrder[b.priority.toLowerCase() as keyof typeof priorityOrder] ||
      1;

    if (aPriority !== bPriority) {
      return bPriority - aPriority; // Higher priority first
    }

    // Timestamp sorting (newest first)
    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
  });

  if (loading) {
    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Mã CK</TableCell>
              <TableCell>Loại</TableCell>
              <TableCell>Mức độ</TableCell>
              <TableCell>Thông điệp</TableCell>
              <TableCell>Khuyến nghị</TableCell>
              <TableCell>Điểm số</TableCell>
              <TableCell>Thời gian</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Array.from({ length: 5 }).map((_, index) => (
              <TableRow key={index}>
                <TableCell>
                  <Skeleton width={60} />
                </TableCell>
                <TableCell>
                  <Skeleton width={80} />
                </TableCell>
                <TableCell>
                  <Skeleton width={70} />
                </TableCell>
                <TableCell>
                  <Skeleton width={200} />
                </TableCell>
                <TableCell>
                  <Skeleton width={60} />
                </TableCell>
                <TableCell>
                  <Skeleton width={50} />
                </TableCell>
                <TableCell>
                  <Skeleton width={120} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  if (sortedAlerts.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Không có cảnh báo nào
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Hiện tại không có cảnh báo nào trong hệ thống
        </Typography>
      </Paper>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>
              <Typography variant="subtitle2" fontWeight="bold">
                Mã CK
              </Typography>
            </TableCell>
            <TableCell>
              <Typography variant="subtitle2" fontWeight="bold">
                Loại
              </Typography>
            </TableCell>
            <TableCell>
              <Typography variant="subtitle2" fontWeight="bold">
                Mức độ
              </Typography>
            </TableCell>
            <TableCell>
              <Typography variant="subtitle2" fontWeight="bold">
                Thông điệp
              </Typography>
            </TableCell>
            <TableCell>
              <Typography variant="subtitle2" fontWeight="bold">
                Khuyến nghị
              </Typography>
            </TableCell>
            <TableCell>
              <Typography variant="subtitle2" fontWeight="bold">
                Điểm số
              </Typography>
            </TableCell>
            <TableCell>
              <Typography variant="subtitle2" fontWeight="bold">
                Thời gian
              </Typography>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sortedAlerts.map((alert, index) => (
            <TableRow
              key={`${alert.symbol}-${alert.timestamp}-${index}`}
              hover
              sx={{ '&:hover': { backgroundColor: 'action.hover' } }}
            >
              <TableCell>
                <Link
                  component="button"
                  variant="body2"
                  onClick={() => handleSymbolClick(alert.symbol)}
                  sx={{
                    fontWeight: 'bold',
                    color: 'primary.main',
                    textDecoration: 'none',
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  {alert.symbol}
                </Link>
              </TableCell>
              <TableCell>
                <Typography variant="body2">{alert.type}</Typography>
              </TableCell>
              <TableCell>
                <Chip
                  label={alert.priority.toUpperCase()}
                  color={getPriorityColor(alert.priority)}
                  size="small"
                  variant="filled"
                />
              </TableCell>
              <TableCell>
                <Typography variant="body2" sx={{ maxWidth: 300 }}>
                  {alert.message}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip
                  label={alert.recommendation}
                  color={getRecommendationColor(alert.recommendation)}
                  size="small"
                  variant="outlined"
                />
              </TableCell>
              <TableCell>
                <Typography variant="body2" fontWeight="medium">
                  {alert.final_score ? alert.final_score.toFixed(2) : 'N/A'}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2" color="text.secondary">
                  {formatTimestamp(alert.timestamp)}
                </Typography>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default AlertsTable;
