// API functions for model endpoints

import { apiFetch } from "./api";

// Chat completion endpoint
export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  stop?: string | string[];
  stream?: boolean;
  [key: string]: unknown;
}

export const sendChatRequest = async (requestData: ChatCompletionRequest) => {
  return apiFetch("chat/completions", "POST", requestData);
};

// Text completion endpoint
export interface CompletionRequest {
  model: string;
  prompt: string;
  temperature?: number;
  max_tokens?: number;
  stop?: string | string[];
  stream?: boolean;
  [key: string]: unknown;
}

export const sendCompletionRequest = async (requestData: CompletionRequest) => {
  return apiFetch("completions", "POST", requestData);
};

// Embedding endpoint
export interface EmbeddingRequest {
  model: string;
  input: string | string[];
  [key: string]: unknown;
}

export const sendEmbeddingRequest = async (requestData: EmbeddingRequest) => {
  return apiFetch("embeddings", "POST", requestData);
};

// Image generation endpoint
export interface ImageGenerationRequest {
  model: string;
  prompt: string;
  n?: number;
  size?: "256x256" | "512x512" | "1024x1024";
  [key: string]: unknown;
}

export const sendImageGenerationRequest = async (
  requestData: ImageGenerationRequest
) => {
  return apiFetch("images/generations", "POST", requestData);
};

// Function to format responses for display
export const formatResponse = (data: unknown): string => {
  try {
    return JSON.stringify(data, null, 2);
  } catch (err) {
    return String(data);
  }
};
