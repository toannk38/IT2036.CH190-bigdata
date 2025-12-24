import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import {
  Schedule,
  CheckCircle,
  Refresh,
} from '@mui/icons-material';
import { LastUpdatedInfoProps } from '@/types';

const formatTimestamp = (timestamp: string) => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('vi-VN', {
      weekday: 'long',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return timestamp;
  }
};

const getTimeAgo = (timestamp: string) => {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) {
      return 'Vừa xong';
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes} phút trước`;
    } else if (diffInMinutes < 1440) {
      const hours = Math.floor(diffInMinutes / 60);
      return `${hours} giờ trước`;
    } else {
      const days = Math.floor(diffInMinutes / 1440);
      return `${days} ngày trước`;
    }
  } catch {
    return 'Không xác định';
  }
};

const getStatusColor = (timestamp?: string) => {
  if (!timestamp) return 'default';
  
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 30) return 'success'; // Fresh data
    if (diffInMinutes < 120) return 'warning'; // Somewhat stale
    return 'error'; // Very stale
  } catch {
    return 'default';
  }
};

const getStatusIcon = (timestamp?: string) => {
  const color = getStatusColor(timestamp);
  
  switch (color) {
    case 'success':
      return <CheckCircle sx={{ color: 'success.main' }} />;
    case 'warning':
      return <Schedule sx={{ color: 'warning.main' }} />;
    case 'error':
      return <Refresh sx={{ color: 'error.main' }} />;
    default:
      return <Schedule sx={{ color: 'text.secondary' }} />;
  }
};

export const LastUpdatedInfo: React.FC<LastUpdatedInfoProps> = ({
  timestamp,
}) => {
  // Use current time as fallback if no timestamp provided
  const currentTimestamp = timestamp || new Date().toISOString();
  const statusColor = getStatusColor(timestamp);

  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {getStatusIcon(timestamp)}
          <Typogra