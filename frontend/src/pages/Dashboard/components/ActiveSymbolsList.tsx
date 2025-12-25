import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  Skeleton,
  Box,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { TrendingUp, Business } from '@mui/icons-material';
import { ActiveSymbolsListProps } from '@/types';
import { touchTargetStyles } from '../../../utils/responsive';

export const ActiveSymbolsList: React.FC<ActiveSymbolsListProps> = ({
  symbols,
  loading,
}) => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleSymbolClick = (symbol: string) => {
    navigate(`/stock/${symbol}`);
  };

  if (loading) {
    return (
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TrendingUp sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h2">
              Mã Cổ Phiếu Đang Hoạt Động
            </Typography>
          </Box>
          <List>
            {Array.from({ length: 8 }).map((_, index) => (
              <ListItem key={index} divider sx={touchTargetStyles.listItem}>
                <ListItemText
                  primary={<Skeleton variant="text" width="60%" />}
                  secondary={<Skeleton variant="text" width="80%" />}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    );
  }

  if (!symbols || symbols.length === 0) {
    return (
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TrendingUp sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h2">
              Mã Cổ Phiếu Đang Hoạt Động
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Business sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              Không có dữ liệu mã cổ phiếu
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TrendingUp sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            Mã Cổ Phiếu Đang Hoạt Động
          </Typography>
          <Chip
            label={symbols.length}
            size="small"
            color="primary"
            sx={{ 
              ml: 2,
              ...touchTargetStyles.chip,
            }}
          />
        </Box>

        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              sm: 'repeat(2, 1fr)',
              md: 'repeat(3, 1fr)',
              lg: 'repeat(4, 1fr)',
            },
            gap: { xs: 1, sm: 1.5 },
          }}
        >
          {symbols.map((symbol) => (
            <Box key={symbol.symbol}>
              <Card
                variant="outlined"
                sx={{
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out',
                  minHeight: { xs: '120px', sm: '100px' }, // Ensure adequate touch area
                  '&:hover': {
                    elevation: 4,
                    transform: 'translateY(-2px)',
                    borderColor: 'primary.main',
                  },
                  '&:active': {
                    transform: 'translateY(0px)',
                  },
                }}
                onClick={() => handleSymbolClick(symbol.symbol)}
              >
                <CardContent 
                  sx={{ 
                    p: { xs: 2, sm: 1.5 }, 
                    '&:last-child': { pb: { xs: 2, sm: 1.5 } },
                    minHeight: { xs: '88px', sm: '68px' }, // Ensure content area is touchable
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                  }}
                >
                  <Typography
                    variant="h6"
                    component="div"
                    sx={{
                      fontWeight: 'bold',
                      color: 'primary.main',
                      fontSize: { xs: '1.1rem', sm: '1rem' },
                      mb: 0.5,
                    }}
                  >
                    {symbol.symbol}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      fontSize: { xs: '0.875rem', sm: '0.75rem' },
                      lineHeight: 1.3,
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      mb: symbol.icb_name2 ? 1 : 0,
                    }}
                  >
                    {symbol.organ_name}
                  </Typography>
                  {symbol.icb_name2 && !isMobile && (
                    <Chip
                      label={symbol.icb_name2}
                      size="small"
                      variant="outlined"
                      sx={{
                        fontSize: '0.7rem',
                        height: { xs: 24, sm: 20 },
                        ...touchTargetStyles.chip,
                      }}
                    />
                  )}
                </CardContent>
              </Card>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};
