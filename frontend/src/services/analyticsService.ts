/**
 * Analytics Service for consuming analytics and summary APIs
 */

export interface QuickStats {
  total_files: number;
  total_records: number;
  total_vehicles: number;
  total_equipment: number;
  total_value: number;
  total_value_formatted: string;
  total_value_millions: string;
  avg_cost: number;
  avg_cost_formatted: string;
  avg_year: number;
  unique_makes: number;
  unique_locations: number;
}

export interface QuickStatsResponse {
  quick_stats: QuickStats;
  page_type: string;
  analysis_type: string;
  analysis_success: boolean;
  analysis_data: any; // Full analysis data from the script
}

export interface VehicleAnalytics {
  total_vehicles: number;
  total_value: number;
  total_value_formatted: string;
  total_value_millions: string;
  unique_makes: number;
  unique_locations: number;
  unique_types: number;
  avg_cost: number;
  avg_cost_formatted: string;
  avg_year: number;
  cost_breakdown: Record<string, any>;
  year_distribution: Record<string, any>;
  files_analyzed: Array<{ file_key: string; filename: string }>;
}

export interface EquipmentAnalytics {
  total_equipment: number;
  unique_types: number;
  unique_locations: number;
  unique_manufacturers: number;
  avg_lifecycle: number;
  lifecycle_distribution: Record<string, any>;
  files_analyzed: Array<{ file_key: string; filename: string }>;
}

export interface FileSummary {
  basic_stats: {
    total_rows: number;
    total_columns: number;
    file_size_mb: number;
    sheets: string[];
  };
  vehicle_stats?: {
    total_vehicles: number;
    unique_makes: number;
    unique_models: number;
    unique_locations: number;
    unique_types: number;
  };
  equipment_stats?: {
    total_equipment: number;
    unique_types: number;
    unique_locations: number;
    unique_manufacturers: number;
  };
  financial_stats?: Record<string, {
    total: number;
    average: number;
    median: number;
    min: number;
    max: number;
  }>;
  year_stats?: Record<string, {
    avg_year: number;
    oldest: number;
    newest: number;
    total_count: number;
  }>;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

const API_BASE_URL = 'http://localhost:3300/api/analytics';

class AnalyticsService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      console.log('Analytics API Request:', `${API_BASE_URL}${endpoint}`);
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      console.log('Analytics API Response Status:', response.status);
      
      const result = await response.json();
      console.log('Analytics API Response Data:', result);
      
      if (!response.ok) {
        console.error('Analytics API Error:', result);
        return {
          success: false,
          error: result.error || result.message || `HTTP ${response.status}`,
        };
      }

      return {
        success: result.success !== undefined ? result.success : true,
        data: result.success !== undefined ? result : result as T,
        error: result.error
      };
    } catch (error) {
      console.error('Analytics API Network Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  async getQuickStats(pageType?: string): Promise<ApiResponse<QuickStatsResponse>> {
    const endpoint = pageType ? `/quick-stats?page=${pageType}` : '/quick-stats';
    const response = await this.request<QuickStatsResponse>(endpoint);
    return response;
  }

  async getVehicleAnalytics(): Promise<ApiResponse<VehicleAnalytics>> {
    const response = await this.request<{ analytics: VehicleAnalytics }>('/vehicles');
    if (response.success && response.data) {
      return {
        success: true,
        data: response.data.analytics
      };
    }
    return response as ApiResponse<VehicleAnalytics>;
  }

  async getEquipmentAnalytics(): Promise<ApiResponse<EquipmentAnalytics>> {
    const response = await this.request<{ analytics: EquipmentAnalytics }>('/equipment');
    if (response.success && response.data) {
      return {
        success: true,
        data: response.data.analytics
      };
    }
    return response as ApiResponse<EquipmentAnalytics>;
  }

  async getFileSummary(fileKey: string): Promise<ApiResponse<FileSummary>> {
    const response = await this.request<{ summary: FileSummary }>(`/summaries/${fileKey}`);
    if (response.success && response.data) {
      return {
        success: true,
        data: response.data.summary
      };
    }
    return response as ApiResponse<FileSummary>;
  }

  async getAllSummaries(): Promise<ApiResponse<Record<string, any>>> {
    return this.request<Record<string, any>>('/summaries');
  }

  async getDashboardSummary(): Promise<ApiResponse<any>> {
    return this.request<any>('/dashboard');
  }

  async getChartData(chartType: string, fileKey?: string): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    params.set('type', chartType);
    if (fileKey) {
      params.set('file_key', fileKey);
    }
    
    return this.request<any>(`/charts?${params.toString()}`);
  }
}

export const analyticsService = new AnalyticsService();
export default analyticsService;