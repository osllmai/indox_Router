import { toast } from "sonner";

// Use relative path for API base URL to work with nginx proxy
const API_BASE_URL = "/api/v1";

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
  key?: string; // For backward compatibility
  created_at: string;
  last_used_at?: string;
  is_active: boolean;
  active?: boolean; // For backward compatibility
  request_count?: number;
  user?: {
    id: number;
    username: string;
    email: string;
  };
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
  by_endpoint: {
    endpoint: string;
    requests: number;
    tokens: number;
    cost: number;
  }[];
}

export interface SystemStats {
  users: {
    total: number;
    active: number;
    new_last_30_days: number;
  };
  api_keys: {
    total: number;
    active: number;
  };
  usage: {
    total_requests: number;
    total_tokens: number;
    total_cost: number;
    requests_today: number;
    tokens_today: number;
    cost_today: number;
  };
  providers: Record<
    string,
    {
      requests: number;
      tokens: number;
      cost: number;
    }
  >;
  models: Record<
    string,
    {
      provider: string;
      model: string;
      requests: number;
      tokens: number;
      cost: number;
    }
  >;
}

export interface LoginResponse {
  success: boolean;
  token: string;
  user: {
    name: string;
    avatar: string;
  };
}

interface PaginatedResponse<T> {
  data: T[];
  count: number;
}

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const errorMessage =
      errorData?.detail || `Error: ${response.status} ${response.statusText}`;
    toast(errorMessage, { type: "error" });
    throw new Error(errorMessage);
  }
  return response.json();
};

// Authentication
export const login = async (username: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/admin/admin/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  const data = await handleResponse(response);
  if (data.token) {
    localStorage.setItem("admin_token", data.token);
  }
  return data;
};

// Helper function to add auth token to requests
const authFetch = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem("admin_token");

  if (!token) {
    toast("Authentication token missing. Please login again.", {
      type: "error",
    });
    throw new Error("Authentication token missing");
  }

  const headers = {
    ...options.headers,
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: "include",
    });
    return handleResponse(response);
  } catch (error) {
    console.error("API request error:", error);
    throw error;
  }
};

// Export apiFetch for components to use
export const apiFetch = async (
  endpoint: string,
  method: string = "GET",
  data: Record<string, unknown> | null = null
) => {
  // If the endpoint already has the correct admin/admin prefix, just use it directly
  let processedEndpoint = endpoint;

  // If the endpoint doesn't already have the double admin prefix
  if (
    !endpoint.startsWith("/admin/admin/") &&
    !endpoint.startsWith("admin/admin/")
  ) {
    // If it starts with admin/ or /admin/, we need to make sure it has the double prefix
    if (endpoint.startsWith("/admin/") || endpoint.startsWith("admin/")) {
      // Convert to /admin/admin/...
      processedEndpoint = "/admin/" + endpoint.replace(/^\/?(admin\/)/i, "");
    } else {
      // For other endpoints like /users/, prepend /admin/
      processedEndpoint =
        "/admin/" +
        (endpoint.startsWith("/") ? endpoint.substring(1) : endpoint);
    }
  }

  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE_URL}${
        processedEndpoint.startsWith("/") ? "" : "/"
      }${processedEndpoint}`;

  const options: RequestInit = {
    method,
    ...(data && { body: JSON.stringify(data) }),
  };
  return authFetch(url, options);
};

// User Management
export const getUsers = async (
  skip: number,
  limit: number
): Promise<User[]> => {
  return apiFetch(`admin/admin/users?skip=${skip}&limit=${limit}`);
};

// Alias for backward compatibility
export const getAllUsers = getUsers;

export const getUser = async (userId: number): Promise<User> => {
  return apiFetch(`admin/admin/users/${userId}`);
};

export const updateUser = async (
  userId: number,
  data: Partial<User>
): Promise<{ status: string; user: User }> => {
  return apiFetch(`admin/admin/users/${userId}`, "PUT", data);
};

export const deleteUser = async (
  userId: number
): Promise<{ status: string; message: string }> => {
  return apiFetch(`admin/admin/users/${userId}`, "DELETE");
};

export const addCredits = async (
  userId: number,
  amount: number,
  paymentMethod = "admin_grant",
  referenceId?: string
): Promise<Transaction> => {
  return apiFetch(`admin/admin/users/${userId}/credits`, "POST", {
    amount,
    payment_method: paymentMethod,
    reference_id: referenceId,
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
  return apiFetch("admin/admin/users/create", "POST", userData);
};

// API Key Management
export const getAllApiKeys = async (
  limit = 100,
  offset = 0,
  search?: string
): Promise<ApiKey[]> => {
  const searchParam = search ? `&search=${encodeURIComponent(search)}` : "";
  return apiFetch(
    `admin/admin/api-keys?limit=${limit}&offset=${offset}${searchParam}`
  );
};

export const getUserApiKeys = async (userId: number): Promise<ApiKey[]> => {
  return apiFetch(`admin/admin/users/${userId}/api-keys`);
};

export const revokeApiKey = async (
  userId: number,
  keyId: number
): Promise<{ status: string; message: string }> => {
  return apiFetch(
    `admin/admin/users/${userId}/api-keys/${keyId}/revoke`,
    "POST"
  );
};

export const enableApiKey = async (
  userId: number,
  keyId: number
): Promise<{ status: string; message: string }> => {
  return apiFetch(
    `admin/admin/users/${userId}/api-keys/${keyId}/enable`,
    "POST"
  );
};

export const deleteApiKey = async (
  userId: number,
  keyId: number
): Promise<{ status: string; message: string }> => {
  return apiFetch(
    `admin/admin/users/${userId}/api-keys/${keyId}`,
    "DELETE"
  ).catch((error) => {
    console.error(`Error deleting API key: ${error.message}`);
    throw error;
  });
};

export const createApiKey = async (
  userId: number,
  name: string
): Promise<ApiKey> => {
  return apiFetch(`admin/admin/users/${userId}/api-keys`, "POST", { name });
};

// Transactions
export const getUserTransactions = async (
  userId: number,
  limit = 20,
  offset = 0
): Promise<{ transactions: Transaction[]; count: number }> => {
  return apiFetch(
    `admin/admin/users/${userId}/transactions?limit=${limit}&offset=${offset}`
  );
};

// Transaction Management
export const getTransactions = async (
  limit = 100,
  offset = 0,
  search?: string
): Promise<{ transactions: Transaction[]; count: number }> => {
  const searchParam = search ? `&search=${encodeURIComponent(search)}` : "";
  try {
    const result = await apiFetch(
      `admin/admin/transactions?limit=${limit}&offset=${offset}${searchParam}`
    );
    return result;
  } catch (error) {
    console.error("Error fetching transactions:", error);
    // Return empty data to prevent UI from breaking
    return { transactions: [], count: 0 };
  }
};

// Usage Statistics
export const getUserUsage = async (
  userId: number,
  startDate?: string,
  endDate?: string
): Promise<UsageStats> => {
  let url = `admin/admin/users/${userId}/usage`;
  if (startDate && endDate) {
    url += `?start_date=${startDate}&end_date=${endDate}`;
  }
  return apiFetch(url);
};

export const getSystemStats = async (): Promise<SystemStats> => {
  return apiFetch("admin/admin/system/stats");
};
