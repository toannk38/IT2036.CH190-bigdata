import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme } from '@mui/material';
import Header from '../Header';

const theme = createTheme();
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>{component}</BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('Header Component', () => {
  it('should render app title', () => {
    renderWithProviders(<Header />);
    expect(
      screen.getByRole('button', { name: /về trang chủ vietnam stock ai/i })
    ).toBeInTheDocument();
  });

  it('should render navigation items', () => {
    renderWithProviders(<Header />);
    expect(
      screen.getByRole('button', { name: /điều hướng đến trang dashboard/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /điều hướng đến trang cảnh báo/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', {
        name: /điều hướng đến trang dữ liệu lịch sử/i,
      })
    ).toBeInTheDocument();
  });

  it('should render search box', () => {
    renderWithProviders(<Header />);
    expect(
      screen.getByPlaceholderText('Tìm mã cổ phiếu...')
    ).toBeInTheDocument();
  });
});
