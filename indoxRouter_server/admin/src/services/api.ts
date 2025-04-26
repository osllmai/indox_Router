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
  user_id?: number; // Make it optional as it might not always be present directly
  key?: string; // For backwards compatibility
  api_key?: string; // Primary field for the key
  name: string;
  is_active?: boolean; // Database field name
  active?: boolean; // For backward compatibility
  created_at: string;
  last_used_at?: string;
  expires_at?: string;
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
    let errorMessage = `Error: ${response.status} ${response.statusText}`;

    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = errorData.detail;
      } else if (typeof errorData === "object") {
        errorMessage = JSON.stringify(errorData);
      }
    } catch (e) {
      // If we can't parse the JSON, just use the status text
      console.error("Failed to parse error response:", e);
    }

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
    credentials: "include", // Important for receiving cookies
  });

  const data = await handleResponse(response);
  if (data.token) {
    localStorage.setItem("admin_token", data.token);
    // Also store login timestamp to check token freshness
    localStorage.setItem("admin_login_time", Date.now().toString());
  }
  return data;
};

// Refresh token if it's older than 12 hours
const refreshTokenIfNeeded = async () => {
  const loginTime = localStorage.getItem("admin_login_time");
  const token = localStorage.getItem("admin_token");

  if (!loginTime || !token) {
    return false;
  }

  const hoursElapsed = (Date.now() - Number(loginTime)) / (1000 * 60 * 60);

  // If token is older than 12 hours, get a new one
  if (hoursElapsed > 12) {
    try {
      // Try to refresh by accessing a lightweight endpoint
      // We won't actually handle the data, just use it to refresh the cookie
      await fetch(`${API_BASE_URL}/admin/admin/system/stats`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        credentials: "include",
      });

      // Update the timestamp
      localStorage.setItem("admin_login_time", Date.now().toString());
      return true;
    } catch (error) {
      console.error("Failed to refresh token", error);
      return false;
    }
  }

  return true;
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

  // Check if token needs refreshing
  await refreshTokenIfNeeded();

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

    // If we get unauthorized, the token might be expired
    if (response.status === 401) {
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_login_time");

      // Force reload to the login page
      window.location.href = "/login";
      throw new Error("Your session has expired. Please login again.");
    }

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
  limit: number,
  search?: string
): Promise<User[]> => {
  const searchParam = search ? `&search=${encodeURIComponent(search)}` : "";
  return apiFetch(
    `admin/admin/users?skip=${skip}&limit=${limit}${searchParam}`
  );
};

// Alias for backward compatibility
export const getAllUsers = getUsers;

export const getUser = async (userId: number): Promise<User> => {
  return apiFetch(`admin/admin/users/${userId}`);
};

export const updateUser = async (
  userId: number,
  data: Partial<User>
): Promise<{ status: string; user: User; message?: string }> => {
  // Convert data object to URL query parameters
  const params = new URLSearchParams();
  Object.entries(data).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      params.append(key, value.toString());
    }
  });

  // Use encoded URL with query parameters instead of JSON body
  return apiFetch(`admin/admin/users/${userId}?${params.toString()}`, "PUT");
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
  // Ensure we're sending the exact property names the backend expects
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

export const extendApiKeyExpiration = async (
  userId: number,
  keyId: number,
  daysToAdd: number = 30
): Promise<{ status: string; message: string; expires_at: string }> => {
  return apiFetch(
    `admin/admin/users/${userId}/api-keys/${keyId}/extend`,
    "POST",
    { days: daysToAdd }
  );
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
