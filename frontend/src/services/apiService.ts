const API_BASE_URL = 'http://localhost:3300';

export interface VehicleData {
  Equipment: string;
  Make: string;
  Model: string;
  Year: number;
  Cost: number;
  Location: string;
  Status?: string;
  LastMaintenance?: string;
}

export interface UserStats {
  total_users: number;
  active_sessions: number;
  recent_logins: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();
      
      if (!response.ok) {
        return {
          success: false,
          error: data.message || `HTTP ${response.status}`,
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  // Authentication
  async login(username: string, password: string) {
    return this.request<{ user_id: string; username: string; email: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async register(username: string, password: string, email: string) {
    return this.request<{ user_id: string }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, email }),
    });
  }

  async getUserStats() {
    return this.request<UserStats>('/api/auth/stats');
  }

  // File Management
  async uploadVehicleFleet(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<{ message: string; records_count: number }>('/api/files/vehicle-fleet/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async getVehicleFleetData() {
    return this.request<VehicleData[]>('/api/files/vehicle-fleet/data');
  }

  async uploadEquipmentLifecycle(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<{ message: string }>('/api/files/equipment-lifecycle/upload', {
      method: 'POST',
      body: formData,
      headers: {},
    });
  }

  // Script Execution
  async runExcelAnalysis() {
    return this.request<{ 
      message: string; 
      reports_generated: string[];
      execution_time: number;
    }>('/api/scripts/excel-reader/run', {
      method: 'POST',
    });
  }

  async runLOBPivotGenerator() {
    return this.request<{ 
      message: string; 
      files_generated: string[];
    }>('/api/scripts/lob-pivot-generator/run', {
      method: 'POST',
    });
  }

  async runOOLReader() {
    return this.request<{ 
      message: string; 
      processed_records: number;
    }>('/api/scripts/ool-reader/run', {
      method: 'POST',
    });
  }

  // Health Check
  async healthCheck() {
    return this.request<{ status: string; timestamp: string }>('/health');
  }

  async getApiInfo() {
    return this.request<{ 
      name: string; 
      version: string; 
      endpoints: string[];
    }>('/');
  }
}

export const apiService = new ApiService();