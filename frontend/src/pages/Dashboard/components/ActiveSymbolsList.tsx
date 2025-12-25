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
} from '@mui/material';
import { TrendingUp, Business } from '@mui/icons-material';
import { ActiveSymbolsListProps } from '@/types';

export const ActiveSymbolsList: React.FC<ActiveSymbolsListProps> = ({
  symbols,
  loading,
}) => {
  const navigate = useNavigate();

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
              <ListItem key={index} divider>
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
            sx={{ ml: 2 }}
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
              xl: 'repeat(5, 1fr)',
            },
            gap: 2,
          }}
        >
          {symbols.map((symbol) => (
            <Box key={symbol.symbol}>
              <Card
                variant="outlined"
                sx={{
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out',
                  height: '140px',
                  '&:hover': {
                    elevation: 4,
                    transform: 'translateY(-2px)',
                    borderColor: 'primary.main',
                    boxShadow: 3,
                  },
                  '&:active': {
                    transform: 'translateY(0px)',
                  },
                }}
                onClick={() => handleSymbolClick(symbol.symbol)}
              >
                <CardContent
                  sx={{
                    p: 2,
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    '&:last-child': { pb: 2 },
                  }}
                >
                  <Box>
                    <Typography
                      variant="h6"
                      component="div"
                      sx={{
                        fontWeight: 'bold',
                        color: 'primary.main',
                        fontSize: '1.1rem',
                        mb: 1,
                      }}
                    >
                      {symbol.symbol}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        fontSize: '0.8rem',
                        lineHeight: 1.3,
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        mb: 1,
                      }}
                    >
                      {symbol.organ_name}
                    </Typography>
                  </Box>
                  {symbol.icb_name2 && (
                    <Chip
                      label={symbol.icb_name2}
                      size="small"
                      variant="outlined"
                      sx={{
                        fontSize: '0.7rem',
                        height: 24,
                        alignSelf: 'flex-start',
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
