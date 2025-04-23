import React, { useState, useRef } from "react";
import { toast } from "sonner";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Copy } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { modelsByEndpoint, modelsByProvider } from "@/services/modelData";
import {
  sendChatRequest,
  sendEmbeddingRequest,
  sendImageGenerationRequest,
  formatResponse,
  generateCurlCommand,
  ChatRequest,
  sendCompletionRequest,
} from "@/services/endpointTester";

// Component for displaying the response
const ResponseDisplay = ({
  response,
  loading,
  imageUrl,
  curlCommand,
}: {
  response: string;
  loading: boolean;
  imageUrl?: string;
  curlCommand?: string;
}) => {
  const copyToClipboard = (text: string, type: "Response" | "Curl") => {
    navigator.clipboard.writeText(text);
    toast(`${type} copied to clipboard`, { type: "success" });
  };

  if (loading) {
    return <div className="p-4 text-center">Loading response...</div>;
  }

  return (
    <div className="mt-6 space-y-4 overflow-hidden">
      {curlCommand && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">Curl Command</h3>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(curlCommand, "Curl")}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Copy curl command to clipboard</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <div className="bg-gray-100 p-4 rounded-md overflow-auto max-h-48">
            <pre className="text-sm whitespace-pre-wrap">{curlCommand}</pre>
          </div>
        </div>
      )}

      {(response || imageUrl) && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">Response</h3>
            {response && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(response, "Response")}
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Copy response to clipboard</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>

          {imageUrl && (
            <div className="mt-4">
              <img
                src={imageUrl}
                alt="Generated image"
                className="max-w-full max-h-96 rounded-md mx-auto"
              />
            </div>
          )}

          {response && (
            <div className="bg-gray-100 p-4 rounded-md overflow-auto max-h-[400px] w-full break-words">
              <pre className="text-sm whitespace-pre-wrap">{response}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// API Key Input Component
const ApiKeyInput = ({
  apiKey,
  setApiKey,
  useApiKey,
  setUseApiKey,
}: {
  apiKey: string;
  setApiKey: (key: string) => void;
  useApiKey: boolean;
  setUseApiKey: (use: boolean) => void;
}) => {
  return (
    <div className="space-y-2 border p-3 rounded-md">
      <div className="flex items-center space-x-2">
        <Switch
          id="useApiKey"
          checked={useApiKey}
          onCheckedChange={setUseApiKey}
        />
        <Label htmlFor="useApiKey">Use Custom API Key</Label>
      </div>

      {useApiKey && (
        <div className="pt-2">
          <Label htmlFor="apiKey">API Key</Label>
          <Input
            id="apiKey"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your API key"
            className="mt-1"
          />
          <p className="text-xs text-gray-500 mt-1">
            Your API key will be used directly with the endpoint and not stored.
          </p>
        </div>
      )}
    </div>
  );
};

// Chat Endpoint Tester Component
const ChatEndpointTester = () => {
  const [model, setModel] = useState("");
  const [messages, setMessages] = useState([
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Hello, please introduce yourself briefly." },
  ]);
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1000);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [useApiKey, setUseApiKey] = useState(false);
  const [curlCommand, setCurlCommand] = useState("");

  const handleUserMessageChange = (content: string) => {
    const newMessages = [...messages];

    // Find and update the last user message, or add a new one if none exists
    const lastUserIndex = newMessages.findIndex((m) => m.role === "user");
    if (lastUserIndex >= 0) {
      newMessages[lastUserIndex].content = content;
    } else {
      newMessages.push({ role: "user", content });
    }

    setMessages(newMessages);
  };

  const handleSystemMessageChange = (content: string) => {
    const newMessages = [...messages];

    // Find and update the system message, or add a new one if none exists
    const systemIndex = newMessages.findIndex((m) => m.role === "system");
    if (systemIndex >= 0) {
      newMessages[systemIndex].content = content;
    } else {
      newMessages.unshift({ role: "system", content });
    }

    setMessages(newMessages);
  };

  const handleSubmit = async () => {
    if (!model) {
      toast("Please select a model", { type: "error" });
      return;
    }

    if (!messages.some((m) => m.role === "user" && m.content.trim())) {
      toast("Please enter a user message", { type: "error" });
      return;
    }

    const requestData = {
      model,
      messages,
      temperature,
      max_tokens: maxTokens,
    };

    // Generate curl command
    setCurlCommand(
      generateCurlCommand(
        "/chat/completions",
        requestData,
        useApiKey ? apiKey : undefined
      )
    );

    try {
      setLoading(true);
      const result = await sendChatRequest(
        requestData as ChatRequest,
        useApiKey ? apiKey : undefined
      );
      setResponse(formatResponse(result));
      toast("Request successful", { type: "success" });
    } catch (error) {
      console.error("Chat request failed:", error);
      toast(
        `Request failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        { type: "error" }
      );
      setResponse(formatResponse({ error: "Request failed" }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Chat Endpoint Tester</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <ApiKeyInput
            apiKey={apiKey}
            setApiKey={setApiKey}
            useApiKey={useApiKey}
            setUseApiKey={setUseApiKey}
          />

          <div className="space-y-2">
            <Label htmlFor="model">Model</Label>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger id="model">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>OpenAI</SelectLabel>
                  {modelsByProvider.openai
                    .filter((m) => m.type === "chat")
                    .map((m) => (
                      <SelectItem key={m.modelName} value={m.modelName}>
                        {m.displayName}
                      </SelectItem>
                    ))}
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>Mistral</SelectLabel>
                  {modelsByProvider.mistral
                    .filter((m) => m.type === "chat")
                    .map((m) => (
                      <SelectItem key={m.modelName} value={m.modelName}>
                        {m.displayName}
                      </SelectItem>
                    ))}
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>DeepSeek</SelectLabel>
                  {modelsByProvider.deepseek
                    .filter((m) => m.type === "chat")
                    .map((m) => (
                      <SelectItem key={m.modelName} value={m.modelName}>
                        {m.displayName}
                      </SelectItem>
                    ))}
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>Anthropic</SelectLabel>
                  {modelsByProvider.anthropic
                    .filter((m) => m.type === "chat")
                    .map((m) => (
                      <SelectItem key={m.modelName} value={m.modelName}>
                        {m.displayName}
                      </SelectItem>
                    ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="systemPrompt">System Message</Label>
            <Textarea
              id="systemPrompt"
              rows={2}
              placeholder="You are a helpful assistant."
              value={messages.find((m) => m.role === "system")?.content || ""}
              onChange={(e) => handleSystemMessageChange(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="userMessage">User Message</Label>
            <Textarea
              id="userMessage"
              rows={4}
              placeholder="Enter your message here..."
              value={messages.find((m) => m.role === "user")?.content || ""}
              onChange={(e) => handleUserMessageChange(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="temperature">
                Temperature: {temperature.toFixed(1)}
              </Label>
              <Slider
                id="temperature"
                min={0}
                max={2}
                step={0.1}
                value={[temperature]}
                onValueChange={(value) => setTemperature(value[0])}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="maxTokens">Max Tokens: {maxTokens}</Label>
              <Slider
                id="maxTokens"
                min={100}
                max={4000}
                step={100}
                value={[maxTokens]}
                onValueChange={(value) => setMaxTokens(value[0])}
              />
            </div>
          </div>

          <div className="flex justify-end">
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? "Sending..." : "Send Request"}
            </Button>
          </div>
        </div>

        <ResponseDisplay
          response={response}
          loading={loading}
          curlCommand={curlCommand}
        />
      </CardContent>
    </Card>
  );
};

// Embedding Endpoint Tester Component
const EmbeddingEndpointTester = () => {
  const [model, setModel] = useState("");
  const [input, setInput] = useState(
    "Embed this text to convert it to a vector representation."
  );
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [useApiKey, setUseApiKey] = useState(false);
  const [curlCommand, setCurlCommand] = useState("");

  const handleSubmit = async () => {
    if (!model) {
      toast("Please select a model", { type: "error" });
      return;
    }

    if (!input.trim()) {
      toast("Please enter input text", { type: "error" });
      return;
    }

    const requestData = {
      model,
      text: input,
    };

    // Generate curl command
    setCurlCommand(
      generateCurlCommand(
        "/embeddings",
        requestData,
        useApiKey ? apiKey : undefined
      )
    );

    try {
      setLoading(true);
      const result = await sendEmbeddingRequest(
        requestData,
        useApiKey ? apiKey : undefined
      );
      setResponse(formatResponse(result));
      toast("Request successful", { type: "success" });
    } catch (error) {
      console.error("Embedding request failed:", error);
      toast(
        `Request failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        { type: "error" }
      );
      setResponse(formatResponse({ error: "Request failed" }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Embedding Endpoint Tester</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <ApiKeyInput
            apiKey={apiKey}
            setApiKey={setApiKey}
            useApiKey={useApiKey}
            setUseApiKey={setUseApiKey}
          />

          <div className="space-y-2">
            <Label htmlFor="embeddingModel">Model</Label>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger id="embeddingModel">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>OpenAI</SelectLabel>
                  {modelsByProvider.openai
                    .filter((m) => m.type === "embedding")
                    .map((m) => (
                      <SelectItem key={m.modelName} value={m.modelName}>
                        {m.displayName}
                      </SelectItem>
                    ))}
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>Mistral</SelectLabel>
                  {modelsByProvider.mistral
                    .filter((m) => m.type === "embedding")
                    .map((m) => (
                      <SelectItem key={m.modelName} value={m.modelName}>
                        {m.displayName}
                      </SelectItem>
                    ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="embeddingInput">Input Text</Label>
            <Textarea
              id="embeddingInput"
              rows={4}
              placeholder="Enter text to embed..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
          </div>

          <div className="flex justify-end">
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? "Embedding..." : "Get Embedding"}
            </Button>
          </div>
        </div>

        <ResponseDisplay
          response={response}
          loading={loading}
          curlCommand={curlCommand}
        />
      </CardContent>
    </Card>
  );
};

// Image Generation Endpoint Tester Component
const ImageEndpointTester = () => {
  const [model, setModel] = useState("");
  const [prompt, setPrompt] = useState(
    "A beautiful sunset over a calm ocean with palm trees silhouetted in the foreground."
  );
  const [size, setSize] = useState<string>("1024x1024");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState<string>("");
  const [apiKey, setApiKey] = useState("");
  const [useApiKey, setUseApiKey] = useState(false);
  const [curlCommand, setCurlCommand] = useState("");

  const handleSubmit = async () => {
    if (!model) {
      toast("Please select a model", { type: "error" });
      return;
    }

    if (!prompt.trim()) {
      toast("Please enter a prompt", { type: "error" });
      return;
    }

    const requestData = {
      model,
      prompt,
      size: size as "256x256" | "512x512" | "1024x1024",
    };

    // Generate curl command
    setCurlCommand(
      generateCurlCommand(
        "/images/generations",
        requestData,
        useApiKey ? apiKey : undefined
      )
    );

    try {
      setLoading(true);
      setImageUrl("");
      const result = await sendImageGenerationRequest(
        requestData,
        useApiKey ? apiKey : undefined
      );

      setResponse(formatResponse(result));

      // Extract image URL from response if available
      if (result?.data?.[0]?.url) {
        setImageUrl(result.data[0].url);
      }

      toast("Image generated successfully", { type: "success" });
    } catch (error) {
      console.error("Image generation request failed:", error);
      toast(
        `Request failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        { type: "error" }
      );
      setResponse(formatResponse({ error: "Request failed" }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Image Generation Endpoint Tester</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <ApiKeyInput
            apiKey={apiKey}
            setApiKey={setApiKey}
            useApiKey={useApiKey}
            setUseApiKey={setUseApiKey}
          />

          <div className="space-y-2">
            <Label htmlFor="imageModel">Model</Label>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger id="imageModel">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>OpenAI</SelectLabel>
                  {modelsByProvider.openai
                    .filter((m) => m.type === "image")
                    .map((m) => (
                      <SelectItem key={m.modelName} value={m.modelName}>
                        {m.displayName}
                      </SelectItem>
                    ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="imagePrompt">Prompt</Label>
            <Textarea
              id="imagePrompt"
              rows={4}
              placeholder="Describe the image you want to generate..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="imageSize">Size</Label>
            <Select value={size} onValueChange={setSize}>
              <SelectTrigger id="imageSize">
                <SelectValue placeholder="Select size" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="256x256">256x256</SelectItem>
                <SelectItem value="512x512">512x512</SelectItem>
                <SelectItem value="1024x1024">1024x1024</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex justify-end">
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? "Generating..." : "Generate Image"}
            </Button>
          </div>
        </div>

        <ResponseDisplay
          response={response}
          loading={loading}
          imageUrl={imageUrl}
          curlCommand={curlCommand}
        />
      </CardContent>
    </Card>
  );
};

// Completion Endpoint Tester Component
const CompletionEndpointTester = () => {
  const [model, setModel] = useState("");
  const [prompt, setPrompt] = useState(
    "Write a short poem about artificial intelligence."
  );
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1000);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [useApiKey, setUseApiKey] = useState(false);
  const [curlCommand, setCurlCommand] = useState("");

  const handleSubmit = async () => {
    if (!model) {
      toast("Please select a model", { type: "error" });
      return;
    }

    if (!prompt.trim()) {
      toast("Please enter a prompt", { type: "error" });
      return;
    }

    const requestData = {
      model,
      prompt,
      temperature,
      max_tokens: maxTokens,
    };

    // Generate curl command
    setCurlCommand(
      generateCurlCommand(
        "/completions",
        requestData,
        useApiKey ? apiKey : undefined
      )
    );

    try {
      setLoading(true);
      const result = await sendCompletionRequest(
        requestData,
        useApiKey ? apiKey : undefined
      );
      setResponse(formatResponse(result));
      toast("Request successful", { type: "success" });
    } catch (error) {
      console.error("Completion request failed:", error);
      toast(
        `Request failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        { type: "error" }
      );
      setResponse(formatResponse({ error: "Request failed" }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Text Completion Endpoint Tester</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <ApiKeyInput
            apiKey={apiKey}
            setApiKey={setApiKey}
            useApiKey={useApiKey}
            setUseApiKey={setUseApiKey}
          />

          <div className="space-y-2">
            <Label htmlFor="completionModel">Model</Label>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger id="completionModel">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>OpenAI</SelectLabel>
                  {modelsByProvider.openai
                    .filter((m) => m.type === "completion")
                    .map((m) => (
                      <SelectItem key={m.modelName} value={m.modelName}>
                        {m.displayName}
                      </SelectItem>
                    ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="completionPrompt">Prompt</Label>
            <Textarea
              id="completionPrompt"
              rows={4}
              placeholder="Enter your prompt here..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="completionTemperature">
                Temperature: {temperature.toFixed(1)}
              </Label>
              <Slider
                id="completionTemperature"
                min={0}
                max={2}
                step={0.1}
                value={[temperature]}
                onValueChange={(value) => setTemperature(value[0])}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="completionMaxTokens">
                Max Tokens: {maxTokens}
              </Label>
              <Slider
                id="completionMaxTokens"
                min={100}
                max={4000}
                step={100}
                value={[maxTokens]}
                onValueChange={(value) => setMaxTokens(value[0])}
              />
            </div>
          </div>

          <div className="flex justify-end">
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? "Sending..." : "Send Request"}
            </Button>
          </div>
        </div>

        <ResponseDisplay
          response={response}
          loading={loading}
          curlCommand={curlCommand}
        />
      </CardContent>
    </Card>
  );
};

// Main EndpointTester Component
const EndpointTester = () => {
  const [activeEndpoint, setActiveEndpoint] = useState("chat");

  return (
    <div className="space-y-6">
      <PageHeader
        title="Endpoint Tester"
        description="Test different model endpoints with various models and parameters"
      />

      <Tabs
        value={activeEndpoint}
        onValueChange={setActiveEndpoint}
        className="space-y-4"
      >
        <TabsList className="grid grid-cols-3 md:grid-cols-4 w-full">
          <TabsTrigger value="chat">Chat</TabsTrigger>
          <TabsTrigger value="completion">Completion</TabsTrigger>
          <TabsTrigger value="embedding">Embedding</TabsTrigger>
          <TabsTrigger value="image">Image</TabsTrigger>
        </TabsList>

        <TabsContent value="chat">
          <ChatEndpointTester />
        </TabsContent>

        <TabsContent value="completion">
          <CompletionEndpointTester />
        </TabsContent>

        <TabsContent value="embedding">
          <EmbeddingEndpointTester />
        </TabsContent>

        <TabsContent value="image">
          <ImageEndpointTester />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EndpointTester;
