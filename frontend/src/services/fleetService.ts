/**
 * Fleet Service
 * Dedicated service for fleet management API calls with backend pagination and filtering
 */

const API_BASE_URL = 'http://localhost:3300';

export interface FleetVehicle {
  Equipment: string;
  Make: string;
  Model: string;
  Year: number;
  Cost: number;
  Location: string;
  Status: string;
  Department?: string;
  FuelType?: string;
  Mileage?: number;
  LastMaintenance?: string;
}

export interface FleetDataResponse {
  success: boolean;
  data: FleetVehicle[];
  total_count: number;
  page: number;
  limit: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
  columns: string[];
  message?: string;
}

export interface FleetSummary {
  total_vehicles: number;
  total_cost: number;
  average_cost: number;
  average_year: number;
  make_distribution: Record<string, number>;
  year_distribution: Record<string, number>;
  cost_distribution: Record<string, number>;
  location_distribution: Record<string, number>;
  status_distribution: Record<string, number>;
  department_distribution?: Record<string, number>;
  fuel_type_distribution?: Record<string, number>;
}

export interface FleetSummaryResponse {
  success: boolean;
  summary: FleetSummary;
  message?: string;
}

export interface FleetFilterOptions {
  makes: string[];
  years: number[];
  locations: string[];
  statuses: string[];
  departments?: string[];
  fuel_types?: string[];
}

export interface FleetFilterOptionsResponse {
  success: boolean;
  options: FleetFilterOptions;
  message?: string;
}

export interface FleetExportResponse {
  success: boolean;
  message: string;
  filename?: string;
  filepath?: string;
  record_count?: number;
}

export interface FleetDataRequest {
  page?: number;
  limit?: number;
  search?: string;
  make?: string;
  year?: number;
  location?: string;
  status?: string;
  department?: string;
  fuel_type?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

class FleetService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const config = { ...defaultOptions, ...options };

    try {
      console.log(`Fleet API Request: ${config.method || 'GET'} ${url}`);
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(`Fleet API Response:`, data);
      return data;
    } catch (error) {
      console.error(`Fleet API Error:`, error);
      throw error;
    }
  }

  // Fleet data with backend pagination and filtering
  async getFleetData(params: FleetDataRequest = {}): Promise<FleetDataResponse> {
    const queryParams = new URLSearchParams();
    
    // Add all parameters to query string
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    const endpoint = `/api/fleet/data${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request<FleetDataResponse>(endpoint);
  }

  // Fleet summary for charts and dashboard
  async getFleetSummary(): Promise<FleetSummaryResponse> {
    return this.request<FleetSummaryResponse>('/api/fleet/summary');
  }

  // Filter options for dropdowns
  async getFilterOptions(): Promise<FleetFilterOptionsResponse> {
    return this.request<FleetFilterOptionsResponse>('/api/fleet/filters');
  }

  // Export fleet data
  async exportFleetData(format: 'excel' | 'csv' = 'excel', params: FleetDataRequest = {}): Promise<FleetExportResponse> {
    const queryParams = new URLSearchParams();
    queryParams.append('format', format);
    
    // Add filter parameters
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '' && key !== 'page' && key !== 'limit') {
        queryParams.append(key, value.toString());
      }
    });

    const endpoint = `/api/fleet/export?${queryParams.toString()}`;
    return this.request<FleetExportResponse>(endpoint);
  }

  // Add new vehicle
  async addVehicle(vehicle: Partial<FleetVehicle>): Promise<{ success: boolean; message: string; vehicle?: FleetVehicle }> {
    return this.request('/api/fleet/vehicles', {
      method: 'POST',
      body: JSON.stringify(vehicle),
    });
  }

  // Update existing vehicle
  async updateVehicle(vehicleId: string, updates: Partial<FleetVehicle>): Promise<{ success: boolean; message: string }> {
    return this.request(`/api/fleet/vehicles/${vehicleId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  // Delete vehicle
  async deleteVehicle(vehicleId: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/api/fleet/vehicles/${vehicleId}`, {
      method: 'DELETE',
    });
  }

  // Refresh cache
  async refreshCache(): Promise<{ success: boolean; message: string; total_vehicles?: number }> {
    return this.request('/api/fleet/cache/refresh', {
      method: 'POST',
    });
  }
}

// Export singleton instance
export const fleetService = new FleetService();