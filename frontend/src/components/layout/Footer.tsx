import React from 'react';
import { Box, Typography, Container, Divider, useTheme, useMediaQuery } from '@mui/material';
import { getResponsiveSpacing } from '../../utils/responsive';

interface FooterProps {
  lastUpdated?: string;
}

const Footer: React.FC<FooterProps> = ({ lastUpdated }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const responsiveSpacing = getResponsiveSpacing(theme);

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
        py: {
          xs: responsiveSpacing.py.xs,
          sm: responsiveSpacing.py.sm,
          md: responsiveSpacing.py.md,
        },
      }}
    >
      <Container 
        maxWidth="xl"
        sx={{
          px: {
            xs: 2,
            sm: 3,
            md: 4,
          },
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'center', sm: 'flex-start' },
            gap: { xs: 2, sm: 3 },
          }}
        >
          {/* App Info */}
          <Box sx={{ 
            textAlign: { xs: 'center', sm: 'left' },
            flex: 1,
          }}>
            <Typography 
              variant="h6" 
              color="primary" 
              gutterBottom
              sx={{
                fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
              }}
            >
              Vietnam Stock AI
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                lineHeight: 1.4,
              }}
            >
              Hệ thống phân tích cổ phiếu thông minh
            </Typography>
            {!isMobile && (
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  lineHeight: 1.4,
                  mt: 0.5,
                }}
              >
                Cung cấp dữ liệu và phân tích chuyên sâu cho thị trường chứng
                khoán Việt Nam
              </Typography>
            )}
          </Box>

          {/* Last Updated Info */}
          <Box sx={{ 
            textAlign: { xs: 'center', sm: 'right' },
            flexShrink: 0,
          }}>
            <Typography 
              variant="body2" 
              color="text.secondary" 
              gutterBottom
              sx={{
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
              }}
            >
              Cập nhật lần cuối:
            </Typography>
            <Typography
              variant="body2"
              color="text.primary"
              sx={{ 
                fontWeight: 'medium',
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
              }}
            >
              {formatLastUpdated(lastUpdated)}
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ my: { xs: 1.5, sm: 2 } }} />

        {/* Copyright */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography 
            variant="body2" 
            color="text.secondary"
            sx={{
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
            }}
          >
            © {new Date().getFullYear()} Vietnam Stock AI. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
