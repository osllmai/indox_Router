// Model data for the endpoint tester
// This file contains pre-loaded model data for the endpoint tester

// Model information organized by provider and endpoint type
export interface ModelInfo {
  modelName: string; // The actual model identifier used in API calls
  displayName: string; // User-friendly display name
  type: "chat" | "completion" | "embedding" | "image"; // The endpoint type this model supports
}

// Models organized by provider
export const modelsByProvider: Record<string, ModelInfo[]> = {
  openai: [
    // Chat models
    { modelName: "gpt-4o", displayName: "GPT-4o", type: "chat" },
    { modelName: "gpt-4o-mini", displayName: "GPT-4o Mini", type: "chat" },
    { modelName: "gpt-4-turbo", displayName: "GPT-4 Turbo", type: "chat" },
    {
      modelName: "gpt-4-vision-preview",
      displayName: "GPT-4 Vision",
      type: "chat",
    },
    {
      modelName: "gpt-4-1106-preview",
      displayName: "GPT-4 (1106)",
      type: "chat",
    },
    { modelName: "gpt-4", displayName: "GPT-4", type: "chat" },
    { modelName: "gpt-4-32k", displayName: "GPT-4 32k", type: "chat" },
    { modelName: "gpt-3.5-turbo", displayName: "GPT-3.5 Turbo", type: "chat" },
    {
      modelName: "gpt-3.5-turbo-16k",
      displayName: "GPT-3.5 Turbo 16k",
      type: "chat",
    },

    // Completion models
    {
      modelName: "gpt-3.5-turbo-instruct",
      displayName: "GPT-3.5 Turbo Instruct",
      type: "completion",
    },

    // Embedding models
    {
      modelName: "text-embedding-3-small",
      displayName: "Text Embedding 3 Small",
      type: "embedding",
    },
    {
      modelName: "text-embedding-3-large",
      displayName: "Text Embedding 3 Large",
      type: "embedding",
    },
    {
      modelName: "text-embedding-ada-002",
      displayName: "Text Embedding Ada 002",
      type: "embedding",
    },

    // Image models
    { modelName: "dall-e-3", displayName: "DALL-E 3", type: "image" },
    { modelName: "dall-e-2", displayName: "DALL-E 2", type: "image" },
  ],

  anthropic: [
    {
      modelName: "claude-3-opus-20240229",
      displayName: "Claude 3 Opus",
      type: "chat",
    },
    {
      modelName: "claude-3-sonnet-20240229",
      displayName: "Claude 3 Sonnet",
      type: "chat",
    },
    {
      modelName: "claude-3-haiku-20240307",
      displayName: "Claude 3 Haiku",
      type: "chat",
    },
    { modelName: "claude-2.1", displayName: "Claude 2.1", type: "chat" },
    { modelName: "claude-2.0", displayName: "Claude 2.0", type: "chat" },
    {
      modelName: "claude-instant-1.2",
      displayName: "Claude Instant 1.2",
      type: "chat",
    },
  ],

  mistral: [
    {
      modelName: "mistral-large-latest",
      displayName: "Mistral Large",
      type: "chat",
    },
    {
      modelName: "mistral-large-2402",
      displayName: "Mistral Large 2402",
      type: "chat",
    },
    {
      modelName: "mistral-medium-latest",
      displayName: "Mistral Medium",
      type: "chat",
    },
    {
      modelName: "mistral-medium-2312",
      displayName: "Mistral Medium 2312",
      type: "chat",
    },
    {
      modelName: "mistral-small-latest",
      displayName: "Mistral Small",
      type: "chat",
    },
    {
      modelName: "mistral-small-2402",
      displayName: "Mistral Small 2402",
      type: "chat",
    },
    {
      modelName: "mistral-tiny-2402",
      displayName: "Mistral Tiny",
      type: "chat",
    },
    {
      modelName: "open-mistral-7b",
      displayName: "Open Mistral 7B",
      type: "chat",
    },
    {
      modelName: "open-mixtral-8x7b",
      displayName: "Open Mixtral 8x7B",
      type: "chat",
    },
    {
      modelName: "mistral-embed",
      displayName: "Mistral Embed",
      type: "embedding",
    },
  ],

  deepseek: [
    { modelName: "deepseek-chat", displayName: "DeepSeek Chat", type: "chat" },
    {
      modelName: "deepseek-coder",
      displayName: "DeepSeek Coder",
      type: "chat",
    },
    { modelName: "deepseek-math", displayName: "DeepSeek Math", type: "chat" },
    {
      modelName: "deepseek-llm-67b-chat",
      displayName: "DeepSeek LLM 67B",
      type: "chat",
    },
    {
      modelName: "deepseek-coder-33b-instruct",
      displayName: "DeepSeek Coder 33B",
      type: "chat",
    },
    {
      modelName: "deepseek-coder-6.7b-instruct",
      displayName: "DeepSeek Coder 6.7B",
      type: "chat",
    },
  ],

  cohere: [
    { modelName: "command-r", displayName: "Command R", type: "chat" },
    { modelName: "command-r-plus", displayName: "Command R+", type: "chat" },
    { modelName: "command", displayName: "Command", type: "chat" },
    {
      modelName: "embed-english-v3.0",
      displayName: "Embed English v3.0",
      type: "embedding",
    },
    {
      modelName: "embed-multilingual-v3.0",
      displayName: "Embed Multilingual v3.0",
      type: "embedding",
    },
  ],

  google: [
    {
      modelName: "gemini-1.5-pro",
      displayName: "Gemini 1.5 Pro",
      type: "chat",
    },
    {
      modelName: "gemini-1.5-flash",
      displayName: "Gemini 1.5 Flash",
      type: "chat",
    },
    {
      modelName: "gemini-1.0-pro",
      displayName: "Gemini 1.0 Pro",
      type: "chat",
    },
    {
      modelName: "gemini-1.0-ultra",
      displayName: "Gemini 1.0 Ultra",
      type: "chat",
    },
    {
      modelName: "embedding-001",
      displayName: "PaLM Embedding",
      type: "embedding",
    },
  ],
};

// Models organized by endpoint type
export const modelsByEndpoint = {
  chat: [
    ...modelsByProvider.openai.filter((m) => m.type === "chat"),
    ...modelsByProvider.anthropic.filter((m) => m.type === "chat"),
    ...modelsByProvider.mistral.filter((m) => m.type === "chat"),
    ...modelsByProvider.deepseek.filter((m) => m.type === "chat"),
    ...modelsByProvider.cohere.filter((m) => m.type === "chat"),
    ...modelsByProvider.google.filter((m) => m.type === "chat"),
  ],

  completion: [
    ...modelsByProvider.openai.filter((m) => m.type === "completion"),
  ],

  embedding: [
    ...modelsByProvider.openai.filter((m) => m.type === "embedding"),
    ...modelsByProvider.mistral.filter((m) => m.type === "embedding"),
    ...modelsByProvider.cohere.filter((m) => m.type === "embedding"),
    ...modelsByProvider.google.filter((m) => m.type === "embedding"),
  ],

  image: [...modelsByProvider.openai.filter((m) => m.type === "image")],
};

// Get display name from model name
export const getModelDisplayName = (modelName: string): string => {
  // Check all providers for a matching model
  for (const provider in modelsByProvider) {
    const model = modelsByProvider[
      provider as keyof typeof modelsByProvider
    ].find((m) => m.modelName === modelName);
    if (model) return model.displayName;
  }
  return modelName;
};

// Get provider from model name
export const getModelProvider = (modelName: string): string => {
  // Check each provider's models for a match
  for (const provider in modelsByProvider) {
    const found = modelsByProvider[
      provider as keyof typeof modelsByProvider
    ].some((m) => m.modelName === modelName);
    if (found) return provider;
  }

  // Fallback logic for model names that don't match exactly
  if (modelName.startsWith("claude")) return "anthropic";
  if (modelName.startsWith("mistral") || modelName.includes("mixtral"))
    return "mistral";
  if (modelName.startsWith("gemini")) return "google";
  if (modelName.startsWith("command")) return "cohere";
  if (modelName.startsWith("deepseek")) return "deepseek";
  if (modelName.startsWith("gpt") || modelName.includes("dall-e"))
    return "openai";

  return "";
};
