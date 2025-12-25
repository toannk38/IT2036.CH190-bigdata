import React from 'react';
import { Container, Box, Typography, useTheme, useMediaQuery } from '@mui/material';
import { useActiveSymbols } from '@/hooks/useActiveSymbols';
import { useTopAlerts } from '@/hooks/useAlerts';
import { ActiveSymbolsList } from './components/ActiveSymbolsList';
import { TopAlertsCard } from './components/TopAlertsCard';
import { LastUpdatedInfo } from './components/LastUpdatedInfo';
import { getResponsiveSpacing, responsiveFontSizes } from '../../utils/responsive';

export const Dashboard: React.FC = () => {
  const { data: symbolsResponse, isLoading: symbolsLoading } =
    useActiveSymbols();
  const { data: alertsResponse, isLoading: alertsLoading } = useTopAlerts(5);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const responsiveSpacing = getResponsiveSpacing(theme);

  return (
    <Container 
      maxWidth="xl" 
      sx={{ 
        py: {
          xs: responsiveSpacing.py.xs,
          sm: responsiveSpacing.py.sm,
          md: responsiveSpacing.py.md,
        },
        px: {
          xs: 1,
          sm: 2,
          md: 3,
        },
      }}
    >
      {/* Header */}
      <Box sx={{ 
        mb: { xs: 2, sm: 3, md: 4 },
        textAlign: { xs: 'center', md: 'left' },
      }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{
            fontWeight: 'bold',
            color: 'primary.main',
            ...responsiveFontSizes.h1,
          }}
        >
          {isMobile ? 'VSA Dashboard' : 'Vietnam Stock AI Dashboard'}
        </Typography>
        <Typography
          variant="subtitle1"
          color="text.secondary"
          sx={{ 
            ...responsiveFontSizes.body1,
            display: { xs: 'none', sm: 'block' },
          }}
        >
          Tổng quan thị trường và phân tích cổ phiếu
        </Typography>
      </Box>

      {/* Main Content */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', lg: 'row' },
          gap: { xs: 2, sm: 3 },
          alignItems: { xs: 'stretch', lg: 'flex-start' },
        }}
      >
        {/* Left Column - Active Symbols */}
        <Box sx={{ 
          flex: { lg: '1 1 66%' },
          minWidth: 0, // Prevent flex item from overflowing
        }}>
          <ActiveSymbolsList
            symbols={symbolsResponse?.symbols}
            loading={symbolsLoading}
          />
        </Box>

        {/* Right Column - Sidebar */}
        <Box
          sx={{
            flex: { lg: '1 1 34%' },
            display: 'flex',
            flexDirection: 'column',
            gap: { xs: 2, sm: 3 },
            minWidth: 0, // Prevent flex item from overflowing
          }}
        >
          <TopAlertsCard
            alerts={alertsResponse?.alerts}
            loading={alertsLoading}
          />
          <LastUpdatedInfo />
        </Box>
      </Box>
    </Container>
  );
};

export default Dashboard;
