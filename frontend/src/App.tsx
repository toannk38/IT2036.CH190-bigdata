import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { Layout } from './components/layout';
import { Dashboard } from './pages/Dashboard';
import { StockAnalysis } from './pages/StockAnalysis';
import { AlertsPage } from './pages/Alerts';
import { HistoricalData } from './pages/HistoricalData';
import { ErrorBoundary } from './components/common';
import './styles/responsive.css';

// Create a theme with responsive breakpoints
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 768,  // Tablet breakpoint
      lg: 1024, // Desktop breakpoint
      xl: 1200,
    },
  },
  typography: {
    // Responsive typography
    h1: {
      fontSize: '2.5rem',
      '@media (max-width:768px)': {
        fontSize: '2rem',
      },
      '@media (max-width:600px)': {
        fontSize: '1.75rem',
      },
    },
    h2: {
      fontSize: '2rem',
      '@media (max-width:768px)': {
        fontSize: '1.75rem',
      },
      '@media (max-width:600px)': {
        fontSize: '1.5rem',
      },
    },
    h3: {
      fontSize: '1.75rem',
      '@media (max-width:768px)': {
        fontSize: '1.5rem',
      },
      '@media (max-width:600px)': {
        fontSize: '1.25rem',
      },
    },
    h4: {
      fontSize: '1.5rem',
      '@media (max-width:768px)': {
        fontSize: '1.25rem',
      },
      '@media (max-width:600px)': {
        fontSize: '1.125rem',
      },
    },
    h5: {
      fontSize: '1.25rem',
      '@media (max-width:768px)': {
        fontSize: '1.125rem',
      },
      '@media (max-width:600px)': {
        fontSize: '1rem',
      },
    },
    h6: {
      fontSize: '1.125rem',
      '@media (max-width:768px)': {
        fontSize: '1rem',
      },
      '@media (max-width:600px)': {
        fontSize: '0.875rem',
      },
    },
  },
  components: {
    // Global responsive component overrides
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingLeft: '16px',
          paddingRight: '16px',
          '@media (max-width:600px)': {
            paddingLeft: '8px',
            paddingRight: '8px',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          minHeight: '44px', // Minimum touch target size
          minWidth: '44px',
          '@media (max-width:768px)': {
            minHeight: '48px', // Larger touch targets on mobile
            minWidth: '48px',
            fontSize: '1rem',
            padding: '12px 16px',
          },
        },
        sizeSmall: {
          minHeight: '40px',
          minWidth: '40px',
          '@media (max-width:768px)': {
            minHeight: '44px',
            minWidth: '44px',
            padding: '10px 12px',
          },
        },
        sizeLarge: {
          minHeight: '48px',
          minWidth: '48px',
          '@media (max-width:768px)': {
            minHeight: '56px',
            minWidth: '56px',
            padding: '16px 24px',
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          minWidth: '44px',
          minHeight: '44px',
          padding: '8px',
          '@media (max-width:768px)': {
            minWidth: '48px',
            minHeight: '48px',
            padding: '12px',
          },
        },
        sizeSmall: {
          minWidth: '40px',
          minHeight: '40px',
          padding: '6px',
          '@media (max-width:768px)': {
            minWidth: '44px',
            minHeight: '44px',
            padding: '10px',
          },
        },
        sizeLarge: {
          minWidth: '48px',
          minHeight: '48px',
          padding: '12px',
          '@media (max-width:768px)': {
            minWidth: '56px',
            minHeight: '56px',
            padding: '16px',
          },
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          minHeight: '44px',
          paddingTop: '12px',
          paddingBottom: '12px',
          '@media (max-width:768px)': {
            minHeight: '48px',
            paddingTop: '16px',
            paddingBottom: '16px',
          },
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          minHeight: '44px',
          paddingTop: '12px',
          paddingBottom: '12px',
          '@media (max-width:768px)': {
            minHeight: '48px',
            paddingTop: '16px',
            paddingBottom: '16px',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          minHeight: '32px',
          '@media (max-width:768px)': {
            minHeight: '40px',
            fontSize: '0.875rem',
          },
        },
        deleteIcon: {
          minWidth: '20px',
          minHeight: '20px',
          '@media (max-width:768px)': {
            minWidth: '24px',
            minHeight: '24px',
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          minHeight: '44px',
          '@media (max-width:768px)': {
            minHeight: '48px',
            fontSize: '1rem',
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          '@media (max-width:768px)': {
            padding: '12px 8px',
          },
        },
      },
    },
    MuiAutocomplete: {
      styleOverrides: {
        option: {
          minHeight: '44px',
          '@media (max-width:768px)': {
            minHeight: '48px',
            padding: '12px 16px',
          },
        },
      },
    },
  },
});

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000, // 30 seconds
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <ErrorBoundary>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/stock/:symbol" element={<StockAnalysis />} />
                  <Route path="/alerts" element={<AlertsPage />} />
                  <Route path="/historical" element={<HistoricalData />} />
                </Routes>
              </Layout>
            </ErrorBoundary>
          </Router>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
