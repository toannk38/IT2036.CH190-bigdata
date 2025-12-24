import React from 'react';
import {
  Box,
  Typography,
  Container,
  Divider,
  useTheme,
} from '@mui/material';

interface FooterProps {
  lastUpdated?: string;
}

const Footer: React.FC<FooterProps> = ({ lastUpdated }) => {
  const theme = useTheme();
  
  const formatLastUpdated = (timestamp?: string) => {
    if (!timestamp) return 'Chưa có dữ liệu';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch (error) {
      return 'Không xác định';
    }
  };

  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: theme.palette.grey[100],
        borderTop: `1px solid ${theme.palette.divider}`,
        mt: 'auto',
        py: 3,
      }}
    >
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'center', sm: 'flex-start' },
            gap: 2,
          }}
        >
          {/* App Info */}
          <Box sx={{ textAlign: { xs: 'center', sm: 'left' } }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Vietnam Stock AI
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Hệ thống phân tích cổ phiếu thông minh
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Cung cấp dữ liệu và phân tích chuyên sâu cho thị trường chứng khoán Việt Nam
            </Typography>
          </Box>

          {/* Last Updated Info */}
          <Box sx={{ textAlign: { xs: 'center', sm: 'right' } }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Cập nhật lần cuối:
            </Typography>
            <Typography variant="body2" color="text.primary" sx={{ fontWeight: 'medium' }}>
              {formatLastUpdated(lastUpdated)}
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Copyright */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} Vietnam Stock AI. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;