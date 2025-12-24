import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Notifications as AlertIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import SearchBox from './SearchBox';

interface HeaderProps {
  onSearch?: (symbol: string) => void;
}

interface NavigationItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const Header: React.FC<HeaderProps> = ({ onSearch }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems: NavigationItem[] = [
    { path: '/', label: 'Dashboard', icon: <DashboardIcon /> },
    { path: '/alerts', label: 'Alerts', icon: <AlertIcon /> },
    { path: '/historical', label: 'Historical', icon: <HistoryIcon /> },
  ];

  const handleMenuClick = (path: string) => {
    navigate(path);
    setMobileMenuOpen(false);
  };

  const handleSearch = (symbol: string) => {
    if (onSearch) {
      onSearch(symbol);
    } else {
      navigate(`/stock/${symbol}`);
    }
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const renderDesktopNavigation = () => (
    <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 2 }}>
      {navigationItems.map((item) => (
        <Box
          key={item.path}
          onClick={() => handleMenuClick(item.path)}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            px: 2,
            py: 1,
            borderRadius: 1,
            cursor: 'pointer',
            backgroundColor: location.pathname === item.path ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
            },
          }}
        >
          {item.icon}
          <Typography variant="body1" color="inherit">
            {item.label}
          </Typography>
        </Box>
      ))}
    </Box>
  );

  const renderMobileDrawer = () => (
    <Drawer
      anchor="left"
      open={mobileMenuOpen}
      onClose={() => setMobileMenuOpen(false)}
      sx={{
        '& .MuiDrawer-paper': {
          width: 250,
        },
      }}
    >
      <List>
        {navigationItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              onClick={() => handleMenuClick(item.path)}
              selected={location.pathname === item.path}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );

  return (
    <>
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          {/* Mobile menu button */}
          {isMobile && (
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={toggleMobileMenu}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}

          {/* Logo/App name */}
          <Typography
            variant="h6"
            component="div"
            sx={{
              flexGrow: 0,
              mr: 4,
              cursor: 'pointer',
              fontWeight: 'bold',
            }}
            onClick={() => navigate('/')}
          >
            Vietnam Stock AI
          </Typography>

          {/* Desktop navigation */}
          {renderDesktopNavigation()}

          {/* Spacer */}
          <Box sx={{ flexGrow: 1 }} />

          {/* Search box */}
          <SearchBox onSearch={handleSearch} />
        </Toolbar>
      </AppBar>

      {/* Mobile drawer */}
      {renderMobileDrawer()}
    </>
  );
};

export default Header;