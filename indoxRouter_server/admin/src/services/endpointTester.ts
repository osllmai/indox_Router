import { apiFetch } from "./api";

// Interfaces for request and response types
export interface ChatRequest {
  model?: string;
  messages?: Array<{ role: string; content: string }>;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stream?: boolean;
  role?: string;
  content?: string;
  provider?: string;
  [key: string]: unknown;
}

export interface CompletionRequest {
  model?: string;
  prompt: string;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stream?: boolean;
  provider?: string;
  [key: string]: unknown;
}

export interface EmbeddingRequest {
  model?: string;
  text: string | string[];
  provider?: string;
  [key: string]: unknown;
}

export interface ImageRequest {
  model?: string;
  prompt: string;
  size?: string;
  n?: number;
  provider?: string;
  [key: string]: unknown;
}

// Response interfaces
export interface ChatResponse {
  request_id: string;
  created_at: string;
  duration_ms: number;
  provider: string;
  model: string;
  success: boolean;
  message: string;
  data: string;
  finish_reason?: string;
  usage?: {
    tokens_prompt: number;
    tokens_completion: number;
    tokens_total: number;
    cost: number;
    latency: number;
  };
  raw_response?: Record<string, unknown>;
}

export interface CompletionResponse {
  request_id: string;
  created_at: string;
  duration_ms: number;
  provider: string;
  model: string;
  success: boolean;
  message: string;
  data: string;
  finish_reason?: string;
  usage?: {
    tokens_prompt: number;
    tokens_completion: number;
    tokens_total: number;
    cost: number;
    latency: number;
  };
  raw_response?: Record<string, unknown>;
}

export interface EmbeddingResponse {
  request_id: string;
  created_at: string;
  duration_ms: number;
  provider: string;
  model: string;
  success: boolean;
  message: string;
  data: number[][];
  dimensions: number;
  usage?: {
    tokens_prompt: number;
    tokens_completion: number;
    tokens_total: number;
    cost: number;
    latency: number;
  };
  raw_response?: Record<string, unknown>;
}

export interface ImageResponse {
  request_id: string;
  created_at: string;
  duration_ms: number;
  provider: string;
  model: string;
  success: boolean;
  message: string;
  data: Array<{
    url?: string;
    b64_json?: string;
  }>;
  usage?: {
    tokens_prompt: number;
    tokens_completion: number;
    tokens_total: number;
    cost: number;
    latency: number;
  };
  raw_response?: Record<string, unknown>;
}

export interface ResponseItem {
  embedding?: number[];
  [key: string]: unknown;
}

// Direct API call function for using custom API keys
export const callEndpointWithKey = async (
  endpoint: string,
  method: string,
  data: Record<string, unknown>,
  apiKey?: string
): Promise<unknown> => {
  const url = `/api/v1${endpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (apiKey) {
    headers["Authorization"] = `Bearer ${apiKey}`;
  }

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.detail || `Error ${response.status}: ${response.statusText}`
      );
    }

    return response.json();
  } catch (error) {
    console.error(`Error calling ${endpoint}:`, error);
    throw error;
  }
};

// API Functions for different endpoints
export const sendChatRequest = async (
  request: ChatRequest,
  apiKey?: string
): Promise<ChatResponse> => {
  try {
    if (apiKey) {
      const response = await callEndpointWithKey(
        "/chat/completions",
        "POST",
        request,
        apiKey
      );
      return response as ChatResponse;
    } else {
      const response = await fetch("/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail ||
            `Error ${response.status}: ${response.statusText}`
        );
      }

      return response.json();
    }
  } catch (error) {
    console.error("Error in chat request:", error);
    throw error;
  }
};

export const sendCompletionRequest = async (
  request: CompletionRequest,
  apiKey?: string
): Promise<CompletionResponse> => {
  try {
    if (apiKey) {
      const response = await callEndpointWithKey(
        "/completions",
        "POST",
        request,
        apiKey
      );
      return response as CompletionResponse;
    } else {
      const response = await fetch("/api/v1/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail ||
            `Error ${response.status}: ${response.statusText}`
        );
      }

      return response.json();
    }
  } catch (error) {
    console.error("Error in completion request:", error);
    throw error;
  }
};

export const sendEmbeddingRequest = async (
  request: EmbeddingRequest,
  apiKey?: string
): Promise<EmbeddingResponse> => {
  try {
    if (apiKey) {
      const response = await callEndpointWithKey(
        "/embeddings",
        "POST",
        request,
        apiKey
      );
      return response as EmbeddingResponse;
    } else {
      const response = await fetch("/api/v1/embeddings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail ||
            `Error ${response.status}: ${response.statusText}`
        );
      }

      return response.json();
    }
  } catch (error) {
    console.error("Error in embedding request:", error);
    throw error;
  }
};

export const sendImageGenerationRequest = async (
  request: ImageRequest,
  apiKey?: string
): Promise<ImageResponse> => {
  try {
    if (apiKey) {
      const response = await callEndpointWithKey(
        "/images/generations",
        "POST",
        request,
        apiKey
      );
      return response as ImageResponse;
    } else {
      const response = await fetch("/api/v1/images/generations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail ||
            `Error ${response.status}: ${response.statusText}`
        );
      }

      return response.json();
    }
  } catch (error) {
    console.error("Error in image generation request:", error);
    throw error;
  }
};

// Generate curl command for the request
export const generateCurlCommand = (
  endpoint: string,
  requestData: Record<string, unknown>,
  apiKey?: string
): string => {
  const url = `${window.location.origin}/api/v1${endpoint}`;
  const authHeader = apiKey ? `-H "Authorization: Bearer ${apiKey}" ` : "";

  return `curl -X POST "${url}" \\
${authHeader}-H "Content-Type: application/json" \\
-d '${JSON.stringify(requestData, null, 2)}'`;
};

// Helper function to format the response for display
export const formatResponse = (response: unknown): string => {
  if (!response) return "";

  // Remove potentially large embedding arrays for cleaner display
  const responseCopy = JSON.parse(JSON.stringify(response));

  if (responseCopy.data && Array.isArray(responseCopy.data)) {
    responseCopy.data = responseCopy.data.map((item: ResponseItem) => {
      if (item.embedding && Array.isArray(item.embedding)) {
        const embeddingLength = item.embedding.length;
        // Show just the first few values of the embedding
        item.embedding = [
          ...item.embedding.slice(0, 3),
          `... (${embeddingLength - 6} more values) ...`,
          ...item.embedding.slice(embeddingLength - 3),
        ] as number[];
      }
      return item;
    });
  }

  return JSON.stringify(responseCopy, null, 2);
};
