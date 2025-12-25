import React, { useState, useMemo } from 'react';
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
  Close as CloseIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import SearchBox from './SearchBox';
import { touchTargets } from '../../utils/responsive';
import { useFocusManagement } from '../../hooks';
import {
  generateAriaLabel,
  announceToScreenReader,
} from '../../utils/accessibility';

interface HeaderProps {
  onSearch?: (symbol: string) => void;
}

interface NavigationItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const Header: React.FC<HeaderProps> = React.memo(({ onSearch }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const navigate = useNavigate();
  const location = useLocation();

  // Focus management for mobile drawer
  const { containerRef: drawerRef } = useFocusManagement(mobileMenuOpen, {
    restoreFocus: true,
    trapFocus: true,
  });

  const navigationItems: NavigationItem[] = useMemo(
    () => [
      { path: '/', label: 'Dashboard', icon: <DashboardIcon /> },
      { path: '/alerts', label: 'Alerts', icon: <AlertIcon /> },
      { path: '/historical', label: 'Historical', icon: <HistoryIcon /> },
    ],
    []
  );

  const handleMenuClick = (path: string) => {
    navigate(path);
    setMobileMenuOpen(false);
    announceToScreenReader(`Đã chuyển đến trang ${getPageName(path)}`);
  };

  const getPageName = (path: string) => {
    switch (path) {
      case '/':
        return 'Dashboard';
      case '/alerts':
        return 'Cảnh báo';
      case '/historical':
        return 'Dữ liệu lịch sử';
      default:
        return 'Trang không xác định';
    }
  };

  const handleSearch = (symbol: string) => {
    if (onSearch) {
      onSearch(symbol);
    } else {
      navigate(`/stock/${symbol}`);
      announceToScreenReader(`Đã chuyển đến phân tích cổ phiếu ${symbol}`);
    }
  };

  const toggleMobileMenu = () => {
    const newState = !mobileMenuOpen;
    setMobileMenuOpen(newState);
    announceToScreenReader(
      newState ? 'Đã mở menu điều hướng' : 'Đã đóng menu điều hướng'
    );
  };

  const handleDrawerClose = () => {
    setMobileMenuOpen(false);
    announceToScreenReader('Đã đóng menu điều hướng');
  };

  const renderDesktopNavigation = () => (
    <Box
      sx={{
        display: { xs: 'none', md: 'flex' },
        alignItems: 'center',
        gap: { md: 1, lg: 2 },
        flexGrow: 1,
        justifyContent: 'center',
      }}
      role="navigation"
      aria-label="Main navigation"
    >
      {navigationItems.map((item) => (
        <Box
          key={item.path}
          component="button"
          onClick={() => handleMenuClick(item.path)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              handleMenuClick(item.path);
            }
          }}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            px: { md: 1.5, lg: 2 },
            py: 1,
            borderRadius: 1,
            cursor: 'pointer',
            minHeight: touchTargets.minimum,
            backgroundColor:
              location.pathname === item.path
                ? 'rgba(255, 255, 255, 0.1)'
                : 'transparent',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
            },
            '&:focus': {
              outline: '2px solid rgba(255, 255, 255, 0.8)',
              outlineOffset: '2px',
            },
            transition: 'background-color 0.2s ease',
            border: 'none',
            color: 'inherit',
          }}
          aria-label={generateAriaLabel.navigation(getPageName(item.path))}
          aria-current={location.pathname === item.path ? 'page' : undefined}
        >
          {item.icon}
          <Typography
            variant="body1"
            color="inherit"
            sx={{
              fontSize: { md: '0.875rem', lg: '1rem' },
              display: { md: isTablet ? 'none' : 'block' },
            }}
          >
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
      onClose={handleDrawerClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: { xs: '280px', sm: '320px' },
          boxSizing: 'border-box',
        },
      }}
      ModalProps={{
        keepMounted: true, // Better performance on mobile
      }}
    >
      <Box
        ref={drawerRef}
        sx={{ pt: 2 }}
        role="navigation"
        aria-label="Mobile navigation menu"
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            px: 2,
            pb: 2,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              color: 'primary.main',
              fontWeight: 'bold',
            }}
          >
            Vietnam Stock AI
          </Typography>
          <IconButton
            onClick={handleDrawerClose}
            aria-label="Đóng menu điều hướng"
            sx={{
              minWidth: touchTargets.minimum,
              minHeight: touchTargets.minimum,
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </Box>
      <List>
        {navigationItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              onClick={() => handleMenuClick(item.path)}
              selected={location.pathname === item.path}
              sx={{
                minHeight: touchTargets.recommended,
                px: 3,
              }}
              aria-label={generateAriaLabel.navigation(getPageName(item.path))}
              aria-current={
                location.pathname === item.path ? 'page' : undefined
              }
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  fontSize: '1rem',
                  fontWeight: location.pathname === item.path ? 600 : 400,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );

  return (
    <>
      <AppBar
        position="static"
        sx={{
          backgroundColor: '#1976d2',
          boxShadow: theme.shadows[2],
        }}
        role="banner"
      >
        <Toolbar
          sx={{
            minHeight: { xs: '56px', sm: '64px' },
            px: { xs: 1, sm: 2, md: 3 },
          }}
        >
          {/* Mobile menu button */}
          {isMobile && (
            <IconButton
              edge="start"
              color="inherit"
              aria-label="Mở menu điều hướng"
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-navigation-menu"
              onClick={toggleMobileMenu}
              sx={{
                mr: { xs: 1, sm: 2 },
                minWidth: touchTargets.minimum,
                minHeight: touchTargets.minimum,
              }}
            >
              <MenuIcon />
            </IconButton>
          )}

          {/* Logo/App name */}
          <Typography
            variant="h6"
            component="div"
            sx={{
              flexGrow: { xs: 1, md: 0 },
              mr: { md: 2, lg: 4 },
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: {
                xs: '1rem',
                sm: '1.125rem',
                md: '1.25rem',
              },
              textAlign: { xs: 'center', md: 'left' },
              '&:focus': {
                outline: '2px solid rgba(255, 255, 255, 0.8)',
                outlineOffset: '2px',
                borderRadius: '4px',
              },
            }}
            onClick={() => navigate('/')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                navigate('/');
              }
            }}
            tabIndex={0}
            role="button"
            aria-label="Về trang chủ Vietnam Stock AI"
          >
            {isMobile ? 'VSA' : 'Vietnam Stock AI'}
          </Typography>

          {/* Desktop navigation */}
          {renderDesktopNavigation()}

          {/* Search box */}
          <Box sx={{ flexShrink: 0 }}>
            <SearchBox onSearch={handleSearch} />
          </Box>
        </Toolbar>
      </AppBar>

      {/* Mobile drawer */}
      {renderMobileDrawer()}
    </>
  );
});

export default Header;
