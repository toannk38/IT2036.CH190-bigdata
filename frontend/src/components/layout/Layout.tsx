import React from 'react';
import { Box, Container, useTheme } from '@mui/material';
import Header from './Header';
import Footer from './Footer';
import { getResponsiveSpacing } from '../../utils/responsive';

interface LayoutProps {
  children: React.ReactNode;
  lastUpdated?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, lastUpdated }) => {
  const theme = useTheme();
  const responsiveSpacing = getResponsiveSpacing(theme);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        width: '100%',
      }}
    >
      <Header />

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: '100%',
          py: {
            xs: responsiveSpacing.py.xs,
            sm: responsiveSpacing.py.sm,
            md: responsiveSpacing.py.md,
          },
          px: {
            xs: 0, // Let Container handle padding
          },
        }}
      >
        <Container
          maxWidth="xl"
          sx={{
            px: {
              xs: 1,
              sm: 2,
              md: 3,
            },
            width: '100%',
          }}
        >
          {children}
        </Container>
      </Box>

      <Footer lastUpdated={lastUpdated} />
    </Box>
  );
};

export default Layout;
