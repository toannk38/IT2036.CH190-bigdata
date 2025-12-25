import React from 'react';
import { Box, Container } from '@mui/material';
import Header from './Header';
import Footer from './Footer';
import Breadcrumb from './Breadcrumb';

interface LayoutProps {
  children: React.ReactNode;
  lastUpdated?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, lastUpdated }) => {
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
        sx={{
          flexGrow: 1,
          width: '100%',
          py: 3,
        }}
      >
        <Container
          maxWidth="xl"
          sx={{
            width: '100%',
          }}
        >
          <Breadcrumb />
          {children}
        </Container>
      </Box>

      <Footer lastUpdated={lastUpdated} />
    </Box>
  );
};

export default Layout;
