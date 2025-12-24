import React from 'react';
import { Container, Grid, Typography, Box } from '@mui/material';
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
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ mb: 2 }}>
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
        </Grid>

        {/* Main Content */}
        <Grid item xs={12} lg={8}>
          <ActiveSymbolsList 
            symbols={symbolsResponse?.symbols} 
            loading={symbolsLoading} 
          />
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} lg={4}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TopAlertsCard 
                alerts={alertsResponse?.alerts} 
                loading={alertsLoading} 
              />
            </Grid>
            <Grid item xs={12}>
              <LastUpdatedInfo />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;