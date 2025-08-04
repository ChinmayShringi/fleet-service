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

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  created_at?: string;
  last_login?: string;
  is_active?: boolean;
}

export interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
}

export interface VehicleFleetResponse {
  data: VehicleData[];
  columns: string[];
  row_count: number;
}

export interface ScriptResponse {
  message: string;
  output: string;
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

      const result = await response.json();
      
      if (!response.ok) {
        return {
          success: false,
          error: result.message || `HTTP ${response.status}`,
        };
      }

      // Handle API response format - some endpoints return data directly, others wrap it
      if (result.success !== undefined) {
        return {
          success: result.success,
          data: result.data || result.user || result.users || result.stats || result,
          message: result.message,
        };
      }

      // For endpoints that don't wrap in success/data format
      return {
        success: true,
        data: result as T,
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
    return this.request<User>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async register(username: string, password: string, email: string, full_name?: string, role?: string) {
    return this.request<User>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, email, full_name, role }),
    });
  }

  async getAllUsers() {
    return this.request<{ count: number; users: User[] }>('/api/auth/users');
  }

  async getUserStats() {
    return this.request<UserStats>('/api/auth/stats');
  }

  // File Management
  async uploadVehicleFleet(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<{ message: string; file_path: string }>('/api/files/vehicle-fleet/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async getVehicleFleetData() {
    return this.request<VehicleFleetResponse>('/api/files/vehicle-fleet/data');
  }

  async uploadEquipmentLifecycle(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<{ message: string; file_path: string }>('/api/files/equipment-lifecycle/upload', {
      method: 'POST',
      body: formData,
      headers: {},
    });
  }

  // Script Execution
  async runExcelAnalysis() {
    return this.request<ScriptResponse>('/api/scripts/excel-reader/run', {
      method: 'POST',
    });
  }

  async runLOBPivotGenerator() {
    return this.request<ScriptResponse>('/api/scripts/lob-pivot-generator/run', {
      method: 'POST',
    });
  }

  async runOOLReader() {
    return this.request<ScriptResponse>('/api/scripts/ool-reader/run', {
      method: 'POST',
    });
  }

  // Health Check
  async healthCheck() {
    return this.request<{ status: string; database: boolean }>('/health');
  }

  async getApiInfo() {
    return this.request<{ 
      service: string; 
      status: string; 
      endpoints: Record<string, string>;
    }>('/');
  }
}

export const apiService = new ApiService();