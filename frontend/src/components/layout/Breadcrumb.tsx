import React, { useMemo } from 'react';
import { Breadcrumbs, Link, Typography, Box } from '@mui/material';
import { Link as RouterLink, useLocation, useParams } from 'react-router-dom';
import {
  NavigateNext as NavigateNextIcon,
  Home as HomeIcon,
} from '@mui/icons-material';

interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: React.ReactNode;
}

const Breadcrumb: React.FC = React.memo(() => {
  const location = useLocation();
  const params = useParams();

  const breadcrumbItems = useMemo((): BreadcrumbItem[] => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const items: BreadcrumbItem[] = [
      {
        label: 'Dashboard',
        path: '/',
        icon: <HomeIcon sx={{ mr: 0.5, fontSize: 'inherit' }} />,
      },
    ];

    if (pathSegments.length === 0) {
      // We're on the home page, return just the home item without path
      return [{ ...items[0], path: undefined }];
    }

    // Handle different routes
    switch (pathSegments[0]) {
      case 'stock':
        if (params.symbol) {
          items.push({
            label: 'Phân Tích Cổ Phiếu',
            path: undefined, // Current page, no link
          });
          items.push({
            label: params.symbol.toUpperCase(),
            path: undefined, // Current page, no link
          });
        }
        break;

      case 'alerts':
        items.push({
          label: 'Cảnh Báo',
          path: undefined, // Current page, no link
        });
        break;

      case 'historical':
        items.push({
          label: 'Dữ Liệu Lịch Sử',
          path: undefined, // Current page, no link
        });
        break;

      default:
        // For unknown routes, just add the path segment
        items.push({
          label:
            pathSegments[0].charAt(0).toUpperCase() + pathSegments[0].slice(1),
          path: undefined,
        });
    }

    return items;
  }, [location.pathname, params.symbol]);

  // Don't show breadcrumbs on the home page
  if (location.pathname === '/') {
    return null;
  }

  return (
    <Box
      sx={{
        py: 1,
        px: 0,
        borderBottom: '1px solid',
        borderColor: 'divider',
        mb: 2,
      }}
      role="navigation"
      aria-label="breadcrumb"
    >
      <Breadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        aria-label="breadcrumb navigation"
        sx={{
          '& .MuiBreadcrumbs-separator': {
            mx: 1,
          },
        }}
      >
        {breadcrumbItems.map((item, index) => {
          const isLast = index === breadcrumbItems.length - 1;

          if (item.path && !isLast) {
            return (
              <Link
                key={index}
                component={RouterLink}
                to={item.path}
                underline="hover"
                color="inherit"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  fontSize: '0.875rem',
                  '&:hover': {
                    color: 'primary.main',
                  },
                  '&:focus': {
                    outline: '2px solid',
                    outlineColor: 'primary.main',
                    outlineOffset: '2px',
                    borderRadius: '4px',
                  },
                }}
                aria-label={`Navigate to ${item.label}`}
              >
                {item.icon}
                {item.label}
              </Link>
            );
          }

          return (
            <Typography
              key={index}
              color={isLast ? 'text.primary' : 'text.secondary'}
              sx={{
                display: 'flex',
                alignItems: 'center',
                fontSize: '0.875rem',
                fontWeight: isLast ? 500 : 400,
              }}
              aria-current={isLast ? 'page' : undefined}
            >
              {item.icon}
              {item.label}
            </Typography>
          );
        })}
      </Breadcrumbs>
    </Box>
  );
});

export default Breadcrumb;
