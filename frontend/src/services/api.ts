import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  StockSummary,
  AlertResponse,
  HistoricalData,
  SymbolsResponse,
  HealthCheckResponse,
  ApiServiceConfig,
  ApiError,
  RetryConfig,
  AlertsQueryParams,
} from '@/types';
import { API_BASE_URL } from '@/constants';

class ApiService {
  private httpClient: AxiosInstance;
  private retryConfig: RetryConfig;

  constructor(config: ApiServiceConfig = { baseURL: API_BASE_URL }) {
    this.retryConfig = {
      maxRetries: 3,
      retryDelay: 1000,
    };

    this.httpClient = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for logging
    this.httpClient.interceptors.request.use(
      (config) => {
        console.log(
          `API Request: ${config.method?.toUpperCase()} ${config.url}`
        );
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.httpClient.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError) => {
        const apiError = this.handleApiError(error);
        console.error('API Response Error:', apiError);
        return Promise.reject(apiError);
      }
    );
  }

  private handleApiError(error: AxiosError): ApiError {
    if (error.code === 'ECONNABORTED') {
      return {
        status: 408,
        message: 'Request timeout',
        code: 'TIMEOUT',
      };
    }

    if (!error.response) {
      return {
        message: 'Network error',
        code: 'NETWORK_ERROR',
      };
    }

    const status = error.response.status;
    let message = 'An error occurred';

    switch (status) {
      case 404:
        message = 'Không tìm thấy mã cổ phiếu';
        break;
      case 500:
        message = 'Lỗi hệ thống, vui lòng thử lại sau';
        break;
      case 503:
        message = 'Dịch vụ tạm thời không khả dụng';
        break;
      default:
        message =
          (error.response.data as { message?: string })?.message ||
          'Đã xảy ra lỗi, vui lòng thử lại';
    }

    return {
      status,
      message,
      code: error.code,
    };
  }

  private async retryRequest<T>(
    requestFn: () => Promise<T>,
    retries: number = this.retryConfig.maxRetries || 3
  ): Promise<T> {
    try {
      return await requestFn();
    } catch (error) {
      const apiError = error as ApiError;

      // Don't retry for client errors (4xx) except timeout
      if (
        apiError.status &&
        apiError.status >= 400 &&
        apiError.status < 500 &&
        apiError.status !== 408
      ) {
        throw error;
      }

      // Don't retry if no retries left
      if (retries <= 0) {
        throw error;
      }

      // Wait before retrying
      const delay = this.retryConfig.retryDelay || 1000;
      await new Promise((resolve) =>
        setTimeout(resolve, delay * (4 - retries))
      ); // Exponential backoff

      console.log(`Retrying request... (${4 - retries}/3)`);
      return this.retryRequest(requestFn, retries - 1);
    }
  }

  async getStockSummary(symbol: string): Promise<StockSummary> {
    return this.retryRequest(async () => {
      const response = await this.httpClient.get(`/stock/${symbol}/summary`);
      return response.data;
    });
  }

  async getAlerts(params: AlertsQueryParams): Promise<AlertResponse> {
    return this.retryRequest(async () => {
      const response = await this.httpClient.get('/alerts', { params });
      return response.data;
    });
  }

  async getHistoricalData(
    symbol: string,
    startDate: string,
    endDate: string
  ): Promise<HistoricalData> {
    return this.retryRequest(async () => {
      const response = await this.httpClient.get(`/stock/${symbol}/history`, {
        params: { start_date: startDate, end_date: endDate },
      });
      return response.data;
    });
  }

  async getActiveSymbols(): Promise<SymbolsResponse> {
    return this.retryRequest(async () => {
      const response = await this.httpClient.get('/symbols');
      return response.data;
    });
  }

  async healthCheck(): Promise<HealthCheckResponse> {
    return this.retryRequest(async () => {
      const response = await this.httpClient.get('/health');
      return response.data;
    });
  }

  // Utility method to check if the API is available
  async isApiAvailable(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      return false;
    }
  }

  // Method to update retry configuration
  updateRetryConfig(config: Partial<RetryConfig>): void {
    this.retryConfig = { ...this.retryConfig, ...config };
  }

  // Method to get current configuration
  getConfig(): { baseURL: string; timeout: number; retryConfig: RetryConfig } {
    return {
      baseURL: this.httpClient.defaults.baseURL || '',
      timeout: this.httpClient.defaults.timeout || 10000,
      retryConfig: this.retryConfig,
    };
  }
}

export const apiService = new ApiService();
