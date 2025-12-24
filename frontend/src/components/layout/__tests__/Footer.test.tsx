import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import Footer from '../Footer';

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('Footer Component', () => {
  it('should render app title and description', () => {
    renderWithTheme(<Footer />);
    expect(screen.getByText('Vietnam Stock AI')).toBeInTheDocument();
    expect(screen.getByText('Hệ thống phân tích cổ phiếu thông minh')).toBeInTheDocument();
  });

  it('should render last updated section', () => {
    renderWithTheme(<Footer />);
    expect(screen.getByText('Cập nhật lần cuối:')).toBeInTheDocument();
  });

  it('should format last updated time correctly', () => {
    const testDate = '2024-01-01T12:00:00Z';
    renderWithTheme(<Footer lastUpdated={testDate} />);
    // Should show formatted date instead of default message
    expect(screen.queryByText('Chưa có dữ liệu')).not.toBeInTheDocument();
  });

  it('should show default message when no last updated time provided', () => {
    renderWithTheme(<Footer />);
    expect(screen.getByText('Chưa có dữ liệu')).toBeInTheDocument();
  });

  it('should render copyright', () => {
    renderWithTheme(<Footer />);
    const currentYear = new Date().getFullYear();
    expect(screen.getByText(`© ${currentYear} Vietnam Stock AI. All rights reserved.`)).toBeInTheDocument();
  });
});