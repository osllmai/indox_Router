
import { toast } from 'sonner';

const API_BASE_URL = 'http://localhost:8000'; // Change this to your FastAPI server URL

// Types based on FastAPI models
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  account_tier: string;
  created_at: string;
  credits: number;
}

export interface ApiKey {
  id: number;
  user_id: number;
  name: string;
  api_key: string;
  created_at: string;
  last_used?: string;
  is_active: boolean;
}

export interface Transaction {
  id: number;
  user_id: number;
  amount: number;
  payment_method: string;
  reference_id: string;
  created_at: string;
  description: string;
}

export interface UsageStats {
  total_requests: number;
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  cost: number;
  by_date: { date: string; requests: number; tokens: number; cost: number }[];
  by_model: { model: string; requests: number; tokens: number; cost: number }[];
  by_endpoint: { endpoint: string; requests: number; tokens: number; cost: number }[];
}

export interface SystemStats {
  total_users: number;
  active_users: number;
  total_requests: number;
  total_tokens: number;
  total_cost: number;
  user_growth: { date: string; count: number }[];
  request_growth: { date: string; count: number }[];
  model_usage: { model: string; requests: number; tokens: number }[];
}

export interface LoginResponse {
  success: boolean;
  token: string;
  user: {
    name: string;
    avatar: string;
  };
}

export interface ModelData {
  modelName: string;
  provider: string;
  contextLength: number;
  usage: {
    requests: number;
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
    cost: number;
  };
}

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const errorMessage = errorData?.detail || `Error: ${response.status} ${response.statusText}`;
    toast.error(errorMessage);
    throw new Error(errorMessage);
  }
  return response.json();
};

// Authentication
export const login = async (username: string, password: string): Promise<LoginResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
      credentials: 'include',
    });
    return handleResponse(response);
  } catch (error) {
    console.error('Login error:', error);
    toast.error('Failed to login. Please check your credentials.');
    throw error;
  }
};

// Helper function to add auth token to requests
const authFetch = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('admin_token');
  
  if (!token) {
    toast.error('Authentication token missing. Please login again.');
    throw new Error('Authentication token missing');
  }
  
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
  
  try {
    const response = await fetch(url, { ...options, headers, credentials: 'include' });
    return handleResponse(response);
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

// User Management
export const getUsers = async (skip = 0, limit = 100, search?: string): Promise<User[]> => {
  const searchParam = search ? `&search=${encodeURIComponent(search)}` : '';
  return authFetch(`${API_BASE_URL}/admin/users?skip=${skip}&limit=${limit}${searchParam}`);
};

export const getUser = async (userId: number): Promise<User> => {
  return authFetch(`${API_BASE_URL}/admin/users/${userId}`);
};

export const updateUser = async (userId: number, data: Partial<User>): Promise<{ status: string; user: User }> => {
  return authFetch(`${API_BASE_URL}/admin/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
};

export const deleteUser = async (userId: number): Promise<{ status: string; message: string }> => {
  return authFetch(`${API_BASE_URL}/admin/users/${userId}`, {
    method: 'DELETE',
  });
};

export const addCredits = async (userId: number, amount: number, paymentMethod = 'admin_grant', referenceId?: string): Promise<Transaction> => {
  return authFetch(`${API_BASE_URL}/admin/users/${userId}/credits`, {
    method: 'POST',
    body: JSON.stringify({ amount, payment_method: paymentMethod, reference_id: referenceId }),
  });
};

export const createUser = async (userData: {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  account_tier?: string;
  is_active?: boolean;
  initial_credits?: number;
}): Promise<{ status: string; message: string; id: number }> => {
  return authFetch(`${API_BASE_URL}/admin/users/create`, {
    method: 'POST',
    body: JSON.stringify(userData),
  });
};

// API Key Management
export const getAllApiKeys = async (limit = 100, offset = 0, search?: string): Promise<ApiKey[]> => {
  const searchParam = search ? `&search=${encodeURIComponent(search)}` : '';
  return authFetch(`${API_BASE_URL}/admin/api-keys?limit=${limit}&offset=${offset}${searchParam}`);
};

export const getUserApiKeys = async (userId: number): Promise<ApiKey[]> => {
  return authFetch(`${API_BASE_URL}/admin/users/${userId}/api-keys`);
};

export const revokeApiKey = async (userId: number, keyId: number): Promise<{ status: string; message: string }> => {
  return authFetch(`${API_BASE_URL}/admin/users/${userId}/api-keys/${keyId}/revoke`, {
    method: 'POST',
  });
};

export const createApiKey = async (userId: number, name: string): Promise<ApiKey> => {
  return authFetch(`${API_BASE_URL}/admin/users/${userId}/api-keys`, {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
};

// Transactions
export const getUserTransactions = async (userId: number, limit = 20, offset = 0): Promise<{ transactions: Transaction[]; count: number }> => {
  return authFetch(`${API_BASE_URL}/admin/users/${userId}/transactions?limit=${limit}&offset=${offset}`);
};

// Usage Statistics
export const getUserUsage = async (userId: number, startDate?: string, endDate?: string): Promise<UsageStats> => {
  let url = `${API_BASE_URL}/admin/users/${userId}/usage`;
  if (startDate && endDate) {
    url += `?start_date=${startDate}&end_date=${endDate}`;
  }
  return authFetch(url);
};

export const getSystemStats = async (): Promise<SystemStats> => {
  return authFetch(`${API_BASE_URL}/admin/system/stats`);
};

export const getAnalytics = async (params: {
  startDate?: string;
  endDate?: string;
  groupBy?: 'date' | 'model' | 'provider' | 'endpoint';
  provider?: string;
  model?: string;
  endpoint?: string;
  includeContent?: boolean;
}): Promise<{ data: any[]; count: number; filters: any }> => {
  const queryParams = new URLSearchParams();
  if (params.startDate) queryParams.append('start_date', params.startDate);
  if (params.endDate) queryParams.append('end_date', params.endDate);
  if (params.groupBy) queryParams.append('group_by', params.groupBy);
  if (params.provider) queryParams.append('provider', params.provider);
  if (params.model) queryParams.append('model', params.model);
  if (params.endpoint) queryParams.append('endpoint', params.endpoint);
  if (params.includeContent !== undefined) queryParams.append('include_content', params.includeContent.toString());
  
  return authFetch(`${API_BASE_URL}/admin/analytics?${queryParams.toString()}`);
};

export const getModels = async (): Promise<Record<string, ModelData[]>> => {
  return authFetch(`${API_BASE_URL}/admin/models`);
};
