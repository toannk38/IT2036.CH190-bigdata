# Design Document: Vietnam Stock Frontend

## Overview

Vietnam Stock Frontend là một ứng dụng web React TypeScript cung cấp giao diện người dùng trực quan để truy cập và hiển thị dữ liệu phân tích cổ phiếu từ Vietnam Stock AI Backend. Ứng dụng được thiết kế với kiến trúc component-based, responsive design và tích hợp đầy đủ với các API endpoints hiện có. Code frontend sẽ được tạo trong thư mục `frontend/` tách biệt với backend.

## Architecture

### Technology Stack

**Frontend Framework:**
- React 18 với TypeScript
- Create React App hoặc Vite cho build tooling
- React Router v6 cho client-side routing

**State Management:**
- React Context API cho global state
- React Query (TanStack Query) cho API data fetching và caching
- Local state với useState/useReducer cho component state

**UI Framework:**
- Material-UI (MUI) hoặc Ant Design cho component library
- Styled-components hoặc CSS Modules cho custom styling
- Responsive design với CSS Grid và Flexbox

**Data Visualization:**
- Chart.js với react-chartjs-2 cho biểu đồ
- Recharts như alternative option
- D3.js cho advanced visualizations nếu cần

**HTTP Client:**
- Axios cho API calls
- React Query cho caching và synchronization

### Application Structure

```
frontend/
├── public/              # Static assets
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── common/      # Common components (Button, Input, etc.)
│   │   ├── charts/      # Chart components
│   │   └── layout/      # Layout components (Header, Footer, etc.)
│   ├── pages/           # Page components
│   │   ├── Dashboard/   # Dashboard page
│   │   ├── StockAnalysis/ # Stock analysis page
│   │   ├── Alerts/      # Alerts page
│   │   └── HistoricalData/ # Historical data page
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API service functions
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   ├── contexts/        # React contexts
│   ├── constants/       # Application constants
│   ├── App.tsx          # Main App component
│   └── index.tsx        # Entry point
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
├── .env                 # Environment variables
└── README.md            # Project documentation
```

## Components and Interfaces

### Core Components

#### 1. App Component
```typescript
interface AppProps {}

const App: React.FC<AppProps> = () => {
  return (
    <BrowserRouter>
      <QueryClient>
        <ThemeProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/stock/:symbol" element={<StockAnalysis />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/historical" element={<HistoricalData />} />
            </Routes>
          </Layout>
        </ThemeProvider>
      </QueryClient>
    </BrowserRouter>
  );
};
```

#### 2. Layout Components

**Header Component:**
```typescript
interface HeaderProps {
  onSearch: (symbol: string) => void;
}

const Header: React.FC<HeaderProps> = ({ onSearch }) => {
  return (
    <AppBar>
      <Toolbar>
        <Logo />
        <Navigation />
        <SearchBox onSearch={onSearch} />
      </Toolbar>
    </AppBar>
  );
};
```

**Navigation Component:**
```typescript
interface NavigationItem {
  path: string;
  label: string;
  icon?: React.ReactNode;
}

const Navigation: React.FC = () => {
  const navigationItems: NavigationItem[] = [
    { path: '/', label: 'Dashboard', icon: <DashboardIcon /> },
    { path: '/alerts', label: 'Alerts', icon: <AlertIcon /> },
    { path: '/historical', label: 'Historical', icon: <HistoryIcon /> }
  ];
  
  return (
    <nav>
      {navigationItems.map(item => (
        <NavLink key={item.path} to={item.path}>
          {item.icon} {item.label}
        </NavLink>
      ))}
    </nav>
  );
};
```

#### 3. Search Component

```typescript
interface SearchBoxProps {
  onSearch: (symbol: string) => void;
  suggestions?: SymbolInfo[];
}

const SearchBox: React.FC<SearchBoxProps> = ({ onSearch, suggestions }) => {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  const filteredSuggestions = useMemo(() => {
    return suggestions?.filter(symbol => 
      symbol.symbol.toLowerCase().includes(query.toLowerCase()) ||
      symbol.organ_name.toLowerCase().includes(query.toLowerCase())
    );
  }, [query, suggestions]);
  
  return (
    <Autocomplete
      options={filteredSuggestions}
      getOptionLabel={(option) => `${option.symbol} - ${option.organ_name}`}
      onInputChange={(_, value) => setQuery(value)}
      onChange={(_, value) => value && onSearch(value.symbol)}
      renderInput={(params) => (
        <TextField {...params} placeholder="Tìm mã cổ phiếu..." />
      )}
    />
  );
};
```

### Page Components

#### 1. Dashboard Page

```typescript
interface DashboardProps {}

const Dashboard: React.FC<DashboardProps> = () => {
  const { data: symbols, isLoading: symbolsLoading } = useActiveSymbols();
  const { data: topAlerts, isLoading: alertsLoading } = useTopAlerts(5);
  
  return (
    <Container>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h4">Vietnam Stock AI Dashboard</Typography>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <ActiveSymbolsList symbols={symbols} loading={symbolsLoading} />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <TopAlertsCard alerts={topAlerts} loading={alertsLoading} />
        </Grid>
        
        <Grid item xs={12}>
          <LastUpdatedInfo />
        </Grid>
      </Grid>
    </Container>
  );
};
```

#### 2. Stock Analysis Page

```typescript
interface StockAnalysisProps {}

const StockAnalysis: React.FC<StockAnalysisProps> = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const { data: stockSummary, isLoading, error } = useStockSummary(symbol!);
  
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!stockSummary) return <NotFoundMessage symbol={symbol} />;
  
  return (
    <Container>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <StockHeader symbol={symbol} companyName={stockSummary.symbol} />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <PriceInfoCard priceData={stockSummary.current_price} />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <RecommendationCard 
            finalScore={stockSummary.final_score}
            recommendation={stockSummary.recommendation}
          />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <ComponentScoresChart scores={stockSummary.component_scores} />
        </Grid>
        
        <Grid item xs={12} md={8}>
          <AnalysisDetails 
            aiAnalysis={stockSummary.ai_ml_analysis}
            llmAnalysis={stockSummary.llm_analysis}
          />
        </Grid>
        
        {stockSummary.alerts.length > 0 && (
          <Grid item xs={12}>
            <AlertsList alerts={stockSummary.alerts} />
          </Grid>
        )}
      </Grid>
    </Container>
  );
};
```

#### 3. Alerts Page

```typescript
interface AlertsPageProps {}

const AlertsPage: React.FC<AlertsPageProps> = () => {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  
  const { data: alertsResponse, isLoading } = useAlerts({
    limit: pageSize,
    offset: (page - 1) * pageSize
  });
  
  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Cảnh Báo Thị Trường
      </Typography>
      
      <AlertsTable 
        alerts={alertsResponse?.alerts || []}
        loading={isLoading}
      />
      
      <Pagination
        count={Math.ceil((alertsResponse?.total || 0) / pageSize)}
        page={page}
        onChange={(_, newPage) => setPage(newPage)}
      />
    </Container>
  );
};
```

#### 4. Historical Data Page

```typescript
interface HistoricalDataProps {}

const HistoricalData: React.FC<HistoricalDataProps> = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  const [dateRange, setDateRange] = useState<{start: string, end: string}>({
    start: '',
    end: ''
  });
  
  const { data: historicalData, isLoading } = useHistoricalData(
    selectedSymbol,
    dateRange.start,
    dateRange.end,
    { enabled: !!selectedSymbol && !!dateRange.start && !!dateRange.end }
  );
  
  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Dữ Liệu Lịch Sử
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <SymbolSelector 
            value={selectedSymbol}
            onChange={setSelectedSymbol}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <DateRangePicker 
            value={dateRange}
            onChange={setDateRange}
          />
        </Grid>
        
        {historicalData && (
          <>
            <Grid item xs={12}>
              <FinalScoreChart data={historicalData.data} />
            </Grid>
            
            <Grid item xs={12}>
              <ComponentScoresChart data={historicalData.data} />
            </Grid>
            
            <Grid item xs={12}>
              <RecommendationTimeline data={historicalData.data} />
            </Grid>
          </>
        )}
      </Grid>
    </Container>
  );
};
```

## Data Models

### TypeScript Interfaces

```typescript
// API Response Types
interface PriceData {
  timestamp: string;
  open: number;
  close: number;
  high: number;
  low: number;
  volume: number;
}

interface ComponentScores {
  technical_score: number;
  risk_score: number;
  sentiment_score: number;
}

interface Alert {
  type: string;
  priority: 'high' | 'medium' | 'low';
  message: string;
}

interface StockSummary {
  symbol: string;
  current_price?: PriceData;
  ai_ml_analysis?: AIAnalysis;
  llm_analysis?: LLMAnalysis;
  final_score?: number;
  recommendation?: 'BUY' | 'SELL' | 'HOLD';
  component_scores?: ComponentScores;
  alerts: Alert[];
  last_updated?: string;
}

interface SymbolInfo {
  symbol: string;
  organ_name: string;
  icb_name2?: string;
  icb_name3?: string;
  icb_name4?: string;
  com_type_code?: string;
  active: boolean;
  created_at?: string;
  updated_at?: string;
}

interface AlertResponse {
  alerts: AlertItem[];
  total: number;
  page: number;
  page_size: number;
}

interface AlertItem {
  symbol: string;
  timestamp: string;
  final_score: number;
  recommendation: string;
  type: string;
  priority: string;
  message: string;
}

interface HistoricalData {
  symbol: string;
  start_date: string;
  end_date: string;
  data: HistoricalDataPoint[];
  total_points: number;
}

interface HistoricalDataPoint {
  timestamp: string;
  final_score: number;
  recommendation: string;
  components: ComponentScores;
}

// UI State Types
interface LoadingState {
  isLoading: boolean;
  error?: string;
}

interface SearchState {
  query: string;
  suggestions: SymbolInfo[];
  showSuggestions: boolean;
}

interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}
```

### API Service Layer

```typescript
class ApiService {
  private baseURL: string;
  private httpClient: AxiosInstance;
  
  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.httpClient = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    this.setupInterceptors();
  }
  
  private setupInterceptors() {
    this.httpClient.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.code === 'ECONNABORTED') {
          throw new Error('Request timeout');
        }
        if (!error.response) {
          throw new Error('Network error');
        }
        throw error;
      }
    );
  }
  
  async getStockSummary(symbol: string): Promise<StockSummary> {
    const response = await this.httpClient.get(`/stock/${symbol}/summary`);
    return response.data;
  }
  
  async getAlerts(params: { limit: number; offset: number }): Promise<AlertResponse> {
    const response = await this.httpClient.get('/alerts', { params });
    return response.data;
  }
  
  async getHistoricalData(
    symbol: string, 
    startDate: string, 
    endDate: string
  ): Promise<HistoricalData> {
    const response = await this.httpClient.get(`/stock/${symbol}/history`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  }
  
  async getActiveSymbols(): Promise<SymbolInfo[]> {
    const response = await this.httpClient.get('/symbols');
    return response.data.symbols;
  }
  
  async healthCheck(): Promise<any> {
    const response = await this.httpClient.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService(process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000');
```

### Custom React Hooks

```typescript
// useStockSummary hook
export const useStockSummary = (symbol: string) => {
  return useQuery({
    queryKey: ['stockSummary', symbol],
    queryFn: () => apiService.getStockSummary(symbol),
    enabled: !!symbol,
    staleTime: 30000, // 30 seconds
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  });
};

// useAlerts hook
export const useAlerts = (params: { limit: number; offset: number }) => {
  return useQuery({
    queryKey: ['alerts', params],
    queryFn: () => apiService.getAlerts(params),
    staleTime: 60000, // 1 minute
    keepPreviousData: true
  });
};

// useActiveSymbols hook
export const useActiveSymbols = () => {
  return useQuery({
    queryKey: ['activeSymbols'],
    queryFn: () => apiService.getActiveSymbols(),
    staleTime: 300000, // 5 minutes
    cacheTime: 600000 // 10 minutes
  });
};

// useHistoricalData hook
export const useHistoricalData = (
  symbol: string,
  startDate: string,
  endDate: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: ['historicalData', symbol, startDate, endDate],
    queryFn: () => apiService.getHistoricalData(symbol, startDate, endDate),
    enabled: options?.enabled,
    staleTime: 300000 // 5 minutes
  });
};
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Dựa trên prework analysis, tôi sẽ tạo các correctness properties từ các acceptance criteria có thể test được:

### Property 1: Symbol List Display
*For any* API response containing active symbols, the Dashboard component should render all symbols in the symbols list
**Validates: Requirements 1.2**

### Property 2: Top Alerts Limit
*For any* alerts API response, the Dashboard should display exactly 5 alerts or fewer (if less than 5 available)
**Validates: Requirements 1.3**

### Property 3: Navigation Behavior
*For any* valid stock symbol, clicking on it should navigate to the correct stock analysis URL path
**Validates: Requirements 1.5**

### Property 4: API Call Triggering
*For any* stock symbol parameter, accessing the stock analysis page should trigger the correct API endpoint call
**Validates: Requirements 2.1**

### Property 5: Price Data Rendering
*For any* valid price data object, the UI should display all required price fields (open, close, high, low, volume)
**Validates: Requirements 2.2**

### Property 6: Recommendation Color Coding
*For any* recommendation value (BUY/SELL/HOLD), the UI should apply the correct color styling
**Validates: Requirements 2.5**

### Property 7: Search Filtering
*For any* search query and symbol list, the search results should only include symbols matching the query in symbol code or company name
**Validates: Requirements 3.2, 3.4**

### Property 8: Search Navigation
*For any* selected symbol from search suggestions, the application should navigate to the stock analysis page for that symbol
**Validates: Requirements 3.3**

### Property 9: Invalid Search Handling
*For any* search query that matches no symbols, the UI should display the "Không tìm thấy mã cổ phiếu" message
**Validates: Requirements 3.5**

### Property 10: Alert Sorting
*For any* unsorted alerts list, the displayed alerts should be sorted by priority (high > medium > low) then by timestamp (newest first)
**Validates: Requirements 4.3**

### Property 11: Alert Priority Styling
*For any* alert with a priority level, the UI should apply the correct color coding (red for high, yellow for medium, green for low)
**Validates: Requirements 4.5**

### Property 12: Historical Data API Call
*For any* valid symbol and date range, submitting the historical data form should trigger the correct API call with proper parameters
**Validates: Requirements 5.2**

### Property 13: Responsive Layout
*For any* screen width in the tablet range (768px-1023px), the application should display the responsive tablet layout
**Validates: Requirements 6.2**

### Property 14: Mobile Layout
*For any* screen width below 768px, the application should display the mobile layout with hamburger menu
**Validates: Requirements 6.3, 6.4**

### Property 15: Touch Target Sizing
*For any* interactive element (button, link), the element should meet minimum touch target size requirements (44px minimum)
**Validates: Requirements 6.6**

### Property 16: Loading State Display
*For any* pending API request, the UI should display an appropriate loading indicator
**Validates: Requirements 7.1**

### Property 17: Error Message Display
*For any* API error response (404, 500, network), the UI should display the appropriate error message
**Validates: Requirements 7.2, 7.3, 7.4**

### Property 18: Retry Functionality
*For any* error state, the UI should provide a retry button that re-attempts the failed operation
**Validates: Requirements 7.5**

### Property 19: Automatic Retry
*For any* transient network error, the system should automatically retry the API call according to the retry policy
**Validates: Requirements 7.6**

### Property 20: Success State Transition
*For any* successful API response after loading, the UI should hide loading indicators and display the data
**Validates: Requirements 7.7**

### Property 21: Active Menu Highlighting
*For any* current route, the corresponding navigation menu item should be highlighted as active
**Validates: Requirements 8.4**

### Property 22: Menu Navigation
*For any* menu item click, the application should navigate to the corresponding page route
**Validates: Requirements 8.5**

### Property 23: Breadcrumb Display
*For any* page that requires breadcrumb navigation, the breadcrumb should display the correct navigation path
**Validates: Requirements 8.7**

## Error Handling

### Error Boundaries
```typescript
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box textAlign="center" p={4}>
          <Typography variant="h5" color="error" gutterBottom>
            Đã xảy ra lỗi
          </Typography>
          <Typography variant="body1" gutterBottom>
            Vui lòng tải lại trang hoặc thử lại sau.
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => window.location.reload()}
          >
            Tải lại trang
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
```

### API Error Handling
```typescript
const handleApiError = (error: any): string => {
  if (error.response) {
    switch (error.response.status) {
      case 404:
        return 'Không tìm thấy mã cổ phiếu';
      case 500:
        return 'Lỗi hệ thống, vui lòng thử lại sau';
      default:
        return 'Đã xảy ra lỗi, vui lòng thử lại';
    }
  } else if (error.request) {
    return 'Không có kết nối mạng';
  } else {
    return 'Đã xảy ra lỗi không xác định';
  }
};
```

## Testing Strategy

### Unit Testing
- Test individual components in isolation
- Mock API calls and external dependencies
- Test component props and state changes
- Test user interactions (clicks, form submissions)
- Use React Testing Library for DOM testing

### Property-Based Testing
- Test universal properties across many generated inputs
- Use fast-check library for property-based testing in JavaScript/TypeScript
- Generate random data for API responses, user inputs, and component props
- Verify properties hold for all valid inputs
- Each property test should run minimum 100 iterations

### Integration Testing
- Test component interactions and data flow
- Test API integration with mock servers
- Test routing and navigation flows
- Test error handling scenarios

### End-to-End Testing
- Test complete user workflows
- Use Cypress or Playwright for E2E testing
- Test responsive design on different screen sizes
- Test accessibility compliance

### Testing Configuration
```typescript
// Property test example with fast-check
import fc from 'fast-check';

describe('Search functionality properties', () => {
  it('Property 7: Search filtering should only return matching symbols', () => {
    fc.assert(fc.property(
      fc.string(),
      fc.array(fc.record({
        symbol: fc.string(),
        organ_name: fc.string()
      })),
      (query, symbols) => {
        const filtered = filterSymbols(query, symbols);
        return filtered.every(symbol => 
          symbol.symbol.toLowerCase().includes(query.toLowerCase()) ||
          symbol.organ_name.toLowerCase().includes(query.toLowerCase())
        );
      }
    ), { numRuns: 100 });
  });
});
```

Each property-based test must be tagged with:
**Feature: vietnam-stock-frontend, Property {number}: {property_text}**

### Property Reflection

Sau khi phân tích prework, tôi xác định các properties có thể được gộp lại để tránh redundancy:

- Properties về API calls và data rendering có thể được gộp thành properties tổng quát hơn
- Properties về responsive design có thể được gộp theo device categories
- Properties về error handling có thể được gộp theo error types
- Properties về navigation có thể được gộp thành navigation behavior properties

### Correctness Properties

Dựa trên prework analysis, đây là các correctness properties chính:

**Property 1: API Integration and Data Display**
*For any* valid API response data, when the Frontend_App receives the data, it should render all required fields correctly in the UI without missing or corrupted information
**Validates: Requirements 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 5.2**

**Property 2: Search Functionality**
*For any* search query input, the Frontend_App should filter and display suggestions that match either the stock symbol or company name, and navigation should work correctly when a suggestion is selected
**Validates: Requirements 3.2, 3.3, 3.4, 3.5**

**Property 3: Navigation Behavior**
*For any* navigation action (menu clicks, symbol clicks, route changes), the Frontend_App should update the URL correctly and render the appropriate page component
**Validates: Requirements 1.5, 4.7, 8.4, 8.5**

**Property 4: Conditional Styling and Visual Feedback**
*For any* data with priority, recommendation, or status values, the Frontend_App should apply the correct color coding and visual styling consistently across all components
**Validates: Requirements 2.5, 2.7, 4.5**

**Property 5: Responsive Design Adaptation**
*For any* screen size within supported ranges (mobile: <768px, tablet: 768-1023px, desktop: ≥1024px), the Frontend_App should adapt its layout and show appropriate UI elements (hamburger menu on mobile, proper touch targets)
**Validates: Requirements 6.2, 6.3, 6.4, 6.6**

**Property 6: Error Handling and Recovery**
*For any* API error response (404, 500, network errors), the Frontend_App should display the appropriate error message and provide recovery options (retry button, navigation alternatives)
**Validates: Requirements 7.2, 7.3, 7.4, 7.5, 7.6**

**Property 7: Loading State Management**
*For any* asynchronous operation, the Frontend_App should show loading indicators during the operation and hide them when the operation completes (success or error)
**Validates: Requirements 7.1, 7.7**

**Property 8: Data Visualization Accuracy**
*For any* numerical data (scores, prices, historical data), the Frontend_App should render charts and visualizations that accurately represent the data values and maintain proper scaling
**Validates: Requirements 2.6, 5.3, 5.4, 5.5**

**Property 9: Pagination and Data Sorting**
*For any* paginated data set, the Frontend_App should maintain correct sorting order (priority then timestamp for alerts) and provide functional pagination controls
**Validates: Requirements 4.3, 4.6**

**Property 10: Interactive Chart Features**
*For any* chart component, the Frontend_App should support user interactions (zoom, pan) and handle empty data states with appropriate messaging
**Validates: Requirements 5.6, 5.7**

## Error Handling

### Error Types and Handling Strategy

**API Errors:**
- 404 Not Found: Display "Không tìm thấy mã cổ phiếu" with suggestion to check symbol
- 500 Server Error: Display "Lỗi hệ thống, vui lòng thử lại sau" with retry button
- Network Timeout: Display "Kết nối chậm, đang thử lại..." with automatic retry
- Network Offline: Display "Không có kết nối mạng" with manual retry option

**Data Validation Errors:**
- Invalid date ranges: Display inline validation messages
- Empty search results: Display "Không tìm thấy kết quả" with search suggestions
- Missing required fields: Display field-specific error messages

**UI State Errors:**
- Component render errors: Use React Error Boundaries to catch and display fallback UI
- Route not found: Display 404 page with navigation back to dashboard
- Invalid URL parameters: Redirect to appropriate default page

### Error Recovery Mechanisms

```typescript
// Error Boundary Component
class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback 
          error={this.state.error}
          onRetry={() => this.setState({ hasError: false, error: null })}
        />
      );
    }
    
    return this.props.children;
  }
}

// Retry Logic for API Calls
const useRetryableQuery = <T>(
  queryKey: string[],
  queryFn: () => Promise<T>,
  options?: { maxRetries?: number; retryDelay?: number }
) => {
  return useQuery({
    queryKey,
    queryFn,
    retry: options?.maxRetries || 3,
    retryDelay: (attemptIndex) => 
      Math.min(1000 * 2 ** attemptIndex, options?.retryDelay || 30000),
    onError: (error) => {
      // Log error for monitoring
      console.error('Query failed:', error);
    }
  });
};
```

## Testing Strategy

### Dual Testing Approach

**Unit Tests:**
- Component rendering with various props
- Hook behavior with different inputs
- Utility function correctness
- Error boundary functionality
- API service methods

**Property-Based Tests:**
- UI rendering with random valid data
- Search functionality with random queries
- Navigation with random routes
- Responsive behavior with random screen sizes
- Error handling with random error scenarios

### Testing Framework Configuration

**Testing Stack:**
- Jest for test runner and assertions
- React Testing Library for component testing
- MSW (Mock Service Worker) for API mocking
- fast-check for property-based testing
- Cypress for end-to-end testing

**Property Test Configuration:**
- Minimum 100 iterations per property test
- Custom generators for domain-specific data (stock symbols, prices, dates)
- Shrinking enabled to find minimal failing cases
- Timeout configuration for async operations

### Test Data Generators

```typescript
// Property-based test generators
const stockSymbolGen = fc.stringOf(fc.char().filter(c => /[A-Z]/.test(c)), { minLength: 3, maxLength: 4 });

const priceDataGen = fc.record({
  timestamp: fc.date().map(d => d.toISOString()),
  open: fc.float({ min: 1, max: 1000 }),
  close: fc.float({ min: 1, max: 1000 }),
  high: fc.float({ min: 1, max: 1000 }),
  low: fc.float({ min: 1, max: 1000 }),
  volume: fc.integer({ min: 1000, max: 10000000 })
});

const alertGen = fc.record({
  type: fc.constantFrom('price_movement', 'volume_spike', 'news_sentiment'),
  priority: fc.constantFrom('high', 'medium', 'low'),
  message: fc.string({ minLength: 10, maxLength: 100 })
});

const componentScoresGen = fc.record({
  technical_score: fc.float({ min: 0, max: 1 }),
  risk_score: fc.float({ min: 0, max: 1 }),
  sentiment_score: fc.float({ min: 0, max: 1 })
});
```

### Example Property Tests

```typescript
// Property Test Example 1: API Integration
describe('Property 1: API Integration and Data Display', () => {
  it('should render all required fields for any valid stock summary data', () => {
    fc.assert(fc.property(
      fc.record({
        symbol: stockSymbolGen,
        current_price: priceDataGen,
        final_score: fc.float({ min: 0, max: 1 }),
        recommendation: fc.constantFrom('BUY', 'SELL', 'HOLD'),
        component_scores: componentScoresGen,
        alerts: fc.array(alertGen, { maxLength: 5 })
      }),
      (stockSummary) => {
        render(<StockAnalysis />, {
          wrapper: ({ children }) => (
            <QueryClient>
              <MemoryRouter initialEntries={[`/stock/${stockSummary.symbol}`]}>
                {children}
              </MemoryRouter>
            </QueryClient>
          )
        });
        
        // Mock API response
        server.use(
          rest.get(`/stock/${stockSummary.symbol}/summary`, (req, res, ctx) => {
            return res(ctx.json(stockSummary));
          })
        );
        
        // Verify all required fields are displayed
        expect(screen.getByText(stockSummary.symbol)).toBeInTheDocument();
        expect(screen.getByText(stockSummary.recommendation)).toBeInTheDocument();
        expect(screen.getByText(stockSummary.final_score.toString())).toBeInTheDocument();
        
        // Verify price data is displayed
        if (stockSummary.current_price) {
          expect(screen.getByText(stockSummary.current_price.close.toString())).toBeInTheDocument();
        }
        
        // Verify alerts are displayed
        stockSummary.alerts.forEach(alert => {
          expect(screen.getByText(alert.message)).toBeInTheDocument();
        });
      }
    ), { numRuns: 100 });
  });
});

// Property Test Example 2: Search Functionality
describe('Property 2: Search Functionality', () => {
  it('should filter suggestions correctly for any search query', () => {
    fc.assert(fc.property(
      fc.record({
        query: fc.string({ minLength: 1, maxLength: 10 }),
        symbols: fc.array(fc.record({
          symbol: stockSymbolGen,
          organ_name: fc.string({ minLength: 5, maxLength: 50 })
        }), { minLength: 5, maxLength: 20 })
      }),
      ({ query, symbols }) => {
        const { result } = renderHook(() => useSearchSuggestions(query, symbols));
        
        const suggestions = result.current;
        
        // All suggestions should match the query
        suggestions.forEach(suggestion => {
          const matchesSymbol = suggestion.symbol.toLowerCase().includes(query.toLowerCase());
          const matchesName = suggestion.organ_name.toLowerCase().includes(query.toLowerCase());
          expect(matchesSymbol || matchesName).toBe(true);
        });
        
        // Should not include symbols that don't match
        const nonMatchingSymbols = symbols.filter(symbol => 
          !symbol.symbol.toLowerCase().includes(query.toLowerCase()) &&
          !symbol.organ_name.toLowerCase().includes(query.toLowerCase())
        );
        
        nonMatchingSymbols.forEach(symbol => {
          expect(suggestions).not.toContain(symbol);
        });
      }
    ), { numRuns: 100 });
  });
});
```

### Unit Test Examples

```typescript
// Unit Test Example: Component Rendering
describe('StockSummaryCard', () => {
  it('should display BUY recommendation with green color', () => {
    const mockData = {
      symbol: 'VIC',
      final_score: 0.8,
      recommendation: 'BUY' as const
    };
    
    render(<StockSummaryCard data={mockData} />);
    
    const recommendation = screen.getByText('BUY');
    expect(recommendation).toBeInTheDocument();
    expect(recommendation).toHaveStyle({ color: 'green' });
  });
  
  it('should display SELL recommendation with red color', () => {
    const mockData = {
      symbol: 'ABC',
      final_score: 0.2,
      recommendation: 'SELL' as const
    };
    
    render(<StockSummaryCard data={mockData} />);
    
    const recommendation = screen.getByText('SELL');
    expect(recommendation).toBeInTheDocument();
    expect(recommendation).toHaveStyle({ color: 'red' });
  });
});

// Unit Test Example: Error Handling
describe('ErrorBoundary', () => {
  it('should display error fallback when child component throws', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };
    
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    
    expect(screen.getByText(/Something went wrong/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });
});
```

### Test Configuration

**Jest Configuration (jest.config.js):**
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/reportWebVitals.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

**Property Test Tags:**
Each property test must include a comment tag referencing the design document property:
```typescript
// Feature: vietnam-stock-frontend, Property 1: API Integration and Data Display
// Feature: vietnam-stock-frontend, Property 2: Search Functionality
// Feature: vietnam-stock-frontend, Property 3: Navigation Behavior
```

This dual testing approach ensures both specific functionality (unit tests) and general correctness across all inputs (property tests), providing comprehensive coverage for the frontend application.