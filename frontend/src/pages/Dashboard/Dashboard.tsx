import React from 'react';
import { Container, Box, Typography } from '@mui/material';
import { useActiveSymbols } from '@/hooks/useActiveSymbols';
import { useTopAlerts } from '@/hooks/useAlerts';
import { ActiveSymbolsList } from './components/ActiveSymbolsList';
import { TopAlertsCard } from './components/TopAlertsCard';
import { LastUpdatedInfo } from './components/LastUpdatedInfo';

export const Dashboard: React.FC = () => {
  const { data: symbolsResponse, isLoading: symbolsLoading } = useActiveSymbols();
  const { data: alertsResponse, isLoading: alertsLoading } = useTopAlerts(5);

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom
          sx={{ 
            fontWeight: 'bold',
            color: 'primary.main',
            textAlign: { xs: 'center', md: 'left' }
          }}
        >
          Vietnam Stock AI Dashboard
        </Typography>
        <Typography 
          variant="subtitle1" 
          color="text.secondary"
          sx={{ textAlign: { xs: 'center', md: 'left' } }}
        >
          Tổng quan thị trường và phân tích cổ phiếu
        </Typography>
      </Box>

      {/* Main Content */}
      <Box 
        sx={{ 
          display: 'flex',
          flexDirection: { xs: 'column', lg: 'row' },
          gap: 3,
        }}
      >
        {/* Left Column - Active Symbols */}
        <Box sx={{ flex: { lg: '1 1 66%' } }}>
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
            gap: 3,
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