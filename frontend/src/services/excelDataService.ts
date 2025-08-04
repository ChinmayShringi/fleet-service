const API_BASE_URL = 'http://localhost:3300/api/excel';

export interface ExcelColumnStats {
  column_name: string;
  total_values: number;
  non_null_values: number;
  null_values: number;
  unique_values: number;
  data_type: string;
  min_value?: number;
  max_value?: number;
  mean_value?: number;
  median_value?: number;
  std_deviation?: number;
  top_values: Array<{value: string; count: number}>;
}

export interface ExcelFileInfo {
  file_key: string;
  filename: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  sheets: string[];
  file_exists: boolean;
  error?: string;
}

export interface ExcelPagination {
  current_page: number;
  page_size: number;
  total_rows: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
  start_row: number;
  end_row: number;
}

export interface ExcelDataFilters {
  search_query?: string;
  column_filters?: Record<string, any>;
  value_filters?: Record<string, {min?: number; max?: number}>;
  sort_column?: string;
  sort_direction?: 'asc' | 'desc';
}

export interface ExcelDataResponse {
  success: boolean;
  data: Record<string, any>[];
  columns: string[];
  pagination: ExcelPagination;
  filters_applied: ExcelDataFilters;
  file_info: {
    file_key: string;
    sheet_name?: string;
    total_rows_before_filter: number;
    total_rows_after_filter: number;
  };
  error?: string;
}

export interface ExcelDataRequest {
  page?: number;
  page_size?: number;
  search?: string;
  column_filters?: Record<string, any>;
  value_filters?: Record<string, {min?: number; max?: number}>;
  sort_column?: string;
  sort_direction?: 'asc' | 'desc';
  sheet?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

class ExcelDataService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      console.log('Excel API Request:', `${API_BASE_URL}${endpoint}`);
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      console.log('Excel API Response Status:', response.status);
      
      const result = await response.json();
      console.log('Excel API Response Data:', result);
      
      if (!response.ok) {
        console.error('Excel API Error:', result);
        return {
          success: false,
          error: result.error || result.message || `HTTP ${response.status}`,
        };
      }

      // Excel API returns the full structure: {success, data, columns, pagination, file_info, filters_applied}
      // We need to return just the structured part (without the outer success wrapper)
      if (result.success !== undefined) {
        // Extract everything except the success field for the data
        const { success, ...dataStructure } = result;
        return {
          success: result.success,
          data: dataStructure as T,
          error: result.error
        };
      } else {
        // Fallback for other formats
        return {
          success: true,
          data: result as T,
        };
      }
    } catch (error) {
      console.error('Excel API Network Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  // Get available Excel files
  async getAvailableFiles() {
    return this.request<{
      available_files: Record<string, string>;
      file_details: Record<string, ExcelFileInfo>;
    }>('/files');
  }

  // Get file information
  async getFileInfo(fileKey: string) {
    return this.request<{ file_info: ExcelFileInfo }>(`/files/${fileKey}/info`);
  }

  // Get file data (GET method with query params)
  async getFileData(fileKey: string, params: ExcelDataRequest = {}): Promise<ApiResponse<ExcelDataResponse>> {
    const searchParams = new URLSearchParams();
    
    if (params.page) searchParams.set('page', params.page.toString());
    if (params.page_size) searchParams.set('page_size', params.page_size.toString());
    if (params.search) searchParams.set('search', params.search);
    if (params.sort_column) searchParams.set('sort_column', params.sort_column);
    if (params.sort_direction) searchParams.set('sort_direction', params.sort_direction);
    if (params.sheet) searchParams.set('sheet', params.sheet);
    
    // Add column filters
    if (params.column_filters) {
      Object.entries(params.column_filters).forEach(([key, value]) => {
        if (value && value !== 'all') {
          searchParams.set(`filter_${key}`, Array.isArray(value) ? value.join(',') : value);
        }
      });
    }
    
    // Add value filters as JSON
    if (params.value_filters) {
      searchParams.set('value_filters', JSON.stringify(params.value_filters));
    }

    const queryString = searchParams.toString();
    const endpoint = `/files/${fileKey}/data${queryString ? `?${queryString}` : ''}`;
    
    return this.request<ExcelDataResponse>(endpoint);
  }

  // Get file data (POST method for complex filters)
  async getFileDataPost(fileKey: string, data: ExcelDataRequest): Promise<ApiResponse<ExcelDataResponse>> {
    return this.request<ExcelDataResponse>(`/files/${fileKey}/data`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Get column statistics
  async getColumnStats(fileKey: string, column: string, sheet?: string) {
    const searchParams = new URLSearchParams();
    if (sheet) searchParams.set('sheet', sheet);
    
    const endpoint = `/files/${fileKey}/columns/${encodeURIComponent(column)}/stats${
      searchParams.toString() ? `?${searchParams.toString()}` : ''
    }`;
    
    return this.request<{ column_stats: ExcelColumnStats }>(endpoint);
  }

  // Global search across all files
  async globalSearch(query: string, maxResults: number = 10) {
    const searchParams = new URLSearchParams({
      search: query,
      max_results: maxResults.toString(),
    });
    
    return this.request<{
      search_query: string;
      results: Record<string, {
        matches_found: number;
        total_matches: number;
        sample_data: Record<string, any>[];
        columns: string[];
      }>;
      files_searched: string[];
    }>(`/search?${searchParams.toString()}`);
  }

  // Shortcut methods for commonly used files
  async getVehicleFleetData(params: ExcelDataRequest = {}): Promise<ApiResponse<ExcelDataResponse>> {
    console.log('Getting vehicle fleet data with params:', params);
    return this.getFileData('vehicle_fleet_master_data', params);
  }

  async getEquipmentLifecycleData(params: ExcelDataRequest = {}): Promise<ApiResponse<ExcelDataResponse>> {
    return this.getFileData('equipment_lifecycle_reference', params);
  }

  async getElectricVehicleBudgetData(params: ExcelDataRequest = {}): Promise<ApiResponse<ExcelDataResponse>> {
    return this.getFileData('electric_vehicle_budget_analysis', params);
  }

  async getRadioEquipmentCostData(params: ExcelDataRequest = {}): Promise<ApiResponse<ExcelDataResponse>> {
    return this.getFileData('radio_equipment_cost_analysis', params);
  }

  async getVehicleReplacementForecastData(params: ExcelDataRequest = {}): Promise<ApiResponse<ExcelDataResponse>> {
    return this.getFileData('vehicle_replacement_detailed_forecast', params);
  }

  async getVehicleReplacementCategoryData(params: ExcelDataRequest = {}): Promise<ApiResponse<ExcelDataResponse>> {
    return this.getFileData('vehicle_replacement_by_category', params);
  }

  async getEquipmentLifecycleBusinessData(params: ExcelDataRequest = {}): Promise<ApiResponse<ExcelDataResponse>> {
    return this.getFileData('equipment_lifecycle_by_business_unit', params);
  }
}

export const excelDataService = new ExcelDataService();