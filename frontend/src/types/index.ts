// API Response Types
export interface PriceData {
  timestamp: string;
  open: number;
  close: number;
  high: number;
  low: number;
  volume: number;
}

export interface ComponentScores {
  technical_score: number;
  risk_score: number;
  sentiment_score: number;
}

export interface Alert {
  type: string;
  priority: 'high' | 'medium' | 'low';
  message: string;
}

export interface AIAnalysis {
  trend_prediction?: string;
  technical_score?: number;
}

export interface LLMAnalysis {
  sentiment?: string;
  summary?: string;
}

export interface StockSummary {
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

export interface SymbolInfo {
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

export interface AlertItem {
  symbol: string;
  timestamp: string;
  final_score: number;
  recommendation: string;
  type: string;
  priority: string;
  message: string;
}

export interface AlertResponse {
  alerts: AlertItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface HistoricalDataPoint {
  timestamp: string;
  final_score: number;
  recommendation: string;
  components: ComponentScores;
}

export interface HistoricalData {
  symbol: string;
  start_date: string;
  end_date: string;
  data: HistoricalDataPoint[];
  total_points: number;
}

export interface SymbolsResponse {
  symbols: SymbolInfo[];
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface SearchState {
  query: string;
  suggestions: SymbolInfo[];
  showSuggestions: boolean;
}

export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

// Component Props Types
export interface HeaderProps {
  onSearch: (symbol: string) => void;
}

export interface SearchBoxProps {
  onSearch: (symbol: string) => void;
  suggestions?: SymbolInfo[];
}

export interface NavigationItem {
  path: string;
  label: string;
  icon?: React.ReactNode;
}

export interface DashboardProps {}

export interface StockAnalysisProps {}

export interface AlertsPageProps {}

export interface HistoricalDataProps {}

export interface ActiveSymbolsListProps {
  symbols?: SymbolInfo[];
  loading: boolean;
}

export interface TopAlertsCardProps {
  alerts?: AlertItem[];
  loading: boolean;
}

export interface LastUpdatedInfoProps {
  timestamp?: string;
}

export interface PriceInfoCardProps {
  priceData?: PriceData;
}

export interface RecommendationCardProps {
  finalScore?: number;
  recommendation?: 'BUY' | 'SELL' | 'HOLD';
}

export interface ComponentScoresChartProps {
  scores?: ComponentScores;
}

export interface AnalysisDetailsProps {
  aiAnalysis?: AIAnalysis;
  llmAnalysis?: LLMAnalysis;
}

export interface AlertsListProps {
  alerts: Alert[];
}

export interface AlertsTableProps {
  alerts: AlertItem[];
  loading: boolean;
}

export interface SymbolSelectorProps {
  value: string;
  onChange: (symbol: string) => void;
}

export interface DateRangePickerProps {
  value: { start: string; end: string };
  onChange: (range: { start: string; end: string }) => void;
}

export interface FinalScoreChartProps {
  data: HistoricalDataPoint[];
}

export interface RecommendationTimelineProps {
  data: HistoricalDataPoint[];
}

export interface ErrorBoundaryProps {
  children: React.ReactNode;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export interface ErrorFallbackProps {
  error?: Error;
  onRetry: () => void;
}

// API Service Types
export interface ApiServiceConfig {
  baseURL: string;
  timeout?: number;
}

export interface ApiError {
  status?: number;
  message: string;
  code?: string;
}

export interface RetryConfig {
  maxRetries?: number;
  retryDelay?: number;
}

export interface AlertsQueryParams {
  limit: number;
  offset: number;
}

export interface HistoricalDataQueryParams {
  symbol: string;
  start_date: string;
  end_date: string;
}

// Health Check Response
export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  services?: {
    database?: string;
    api?: string;
  };
}
