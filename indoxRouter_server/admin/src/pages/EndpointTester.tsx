import React, { useState } from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { apiFetch } from "@/services/api";

interface RequestHistory {
  id: string;
  method: string;
  endpoint: string;
  requestBody: string;
  responseBody: string;
  status: number;
  timestamp: string;
}

const EndpointTester = () => {
  const [method, setMethod] = useState("GET");
  const [endpoint, setEndpoint] = useState("");
  const [requestBody, setRequestBody] = useState("");
  const [responseBody, setResponseBody] = useState("");
  const [status, setStatus] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [requestHistory, setRequestHistory] = useState<RequestHistory[]>([]);
  const [activeTab, setActiveTab] = useState("tester");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!endpoint) {
      toast.error("Please enter an endpoint");
      return;
    }

    try {
      setLoading(true);

      // Ensure endpoint starts with /api/v1
      const fullEndpoint = endpoint.startsWith("/api/v1")
        ? endpoint
        : `/api/v1${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

      let parsedRequestBody = null;
      if (
        requestBody &&
        (method === "POST" || method === "PUT" || method === "PATCH")
      ) {
        try {
          parsedRequestBody = JSON.parse(requestBody);
        } catch (error) {
          toast.error("Invalid JSON in request body");
          return;
        }
      }

      const response = await apiFetch(fullEndpoint, method, parsedRequestBody);

      setResponseBody(JSON.stringify(response, null, 2));
      setStatus(200);

      // Add to history
      const newRequest: RequestHistory = {
        id: Date.now().toString(),
        method,
        endpoint: fullEndpoint,
        requestBody,
        responseBody: JSON.stringify(response, null, 2),
        status: 200,
        timestamp: new Date().toISOString(),
      };

      setRequestHistory([newRequest, ...requestHistory]);
      toast.success("Request successful");
    } catch (error: any) {
      console.error("Request failed:", error);

      let errorMessage = "Request failed";
      let errorStatus = 500;

      if (error.response) {
        errorStatus = error.response.status;
        errorMessage = error.response.data?.detail || error.response.statusText;
      }

      setResponseBody(JSON.stringify({ error: errorMessage }, null, 2));
      setStatus(errorStatus);

      // Add to history
      const newRequest: RequestHistory = {
        id: Date.now().toString(),
        method,
        endpoint: endpoint.startsWith("/api/v1")
          ? endpoint
          : `/api/v1${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`,
        requestBody,
        responseBody: JSON.stringify({ error: errorMessage }, null, 2),
        status: errorStatus,
        timestamp: new Date().toISOString(),
      };

      setRequestHistory([newRequest, ...requestHistory]);
      toast.error(`Request failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setMethod("GET");
    setEndpoint("");
    setRequestBody("");
    setResponseBody("");
    setStatus(null);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const getStatusBadgeClass = (status: number) => {
    if (status >= 200 && status < 300) {
      return "bg-green-100 text-green-800";
    } else if (status >= 300 && status < 400) {
      return "bg-blue-100 text-blue-800";
    } else if (status >= 400 && status < 500) {
      return "bg-yellow-100 text-yellow-800";
    } else {
      return "bg-red-100 text-red-800";
    }
  };

  const loadHistoryItem = (item: RequestHistory) => {
    setMethod(item.method);
    setEndpoint(item.endpoint);
    setRequestBody(item.requestBody);
    setResponseBody(item.responseBody);
    setStatus(item.status);
    setActiveTab("tester");
  };

  return (
    <div>
      <PageHeader
        title="Endpoint Tester"
        description="Test API endpoints and view request history"
      />

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-4"
      >
        <TabsList>
          <TabsTrigger value="tester">API Tester</TabsTrigger>
          <TabsTrigger value="history">Request History</TabsTrigger>
        </TabsList>

        <TabsContent value="tester">
          <Card>
            <CardHeader>
              <CardTitle>API Endpoint Tester</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="method">Method</Label>
                    <Select value={method} onValueChange={setMethod}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select method" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="GET">GET</SelectItem>
                        <SelectItem value="POST">POST</SelectItem>
                        <SelectItem value="PUT">PUT</SelectItem>
                        <SelectItem value="PATCH">PATCH</SelectItem>
                        <SelectItem value="DELETE">DELETE</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2 md:col-span-3">
                    <Label htmlFor="endpoint">Endpoint</Label>
                    <div className="flex space-x-2">
                      <div className="flex-shrink-0 flex items-center px-3 bg-gray-100 rounded-l-md border border-r-0">
                        /api/v1
                      </div>
                      <Input
                        id="endpoint"
                        placeholder="Enter endpoint (e.g., /users or /admin/models)"
                        value={endpoint}
                        onChange={(e) => setEndpoint(e.target.value)}
                        className="rounded-l-none"
                      />
                    </div>
                  </div>
                </div>

                {(method === "POST" ||
                  method === "PUT" ||
                  method === "PATCH") && (
                  <div className="space-y-2">
                    <Label htmlFor="requestBody">Request Body (JSON)</Label>
                    <Textarea
                      id="requestBody"
                      placeholder="Enter JSON request body"
                      value={requestBody}
                      onChange={(e) => setRequestBody(e.target.value)}
                      rows={5}
                    />
                  </div>
                )}

                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={clearForm}>
                    Clear
                  </Button>
                  <Button type="submit" disabled={loading}>
                    {loading ? "Sending..." : "Send Request"}
                  </Button>
                </div>
              </form>

              {status && (
                <div className="mt-6 space-y-4">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-medium">Response</h3>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(
                        status
                      )}`}
                    >
                      {status}
                    </span>
                  </div>
                  <div className="bg-gray-100 p-4 rounded-md overflow-auto max-h-96">
                    <pre className="text-sm">{responseBody}</pre>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Request History</CardTitle>
            </CardHeader>
            <CardContent>
              {requestHistory.length === 0 ? (
                <div className="text-center py-8">No request history</div>
              ) : (
                <div className="space-y-4">
                  {requestHistory.map((item) => (
                    <Card key={item.id} className="overflow-hidden">
                      <div
                        className={`h-1 ${getStatusBadgeClass(item.status)}`}
                      ></div>
                      <CardHeader className="pb-2">
                        <div className="flex justify-between items-center">
                          <CardTitle className="text-base">
                            {item.method} {item.endpoint}
                          </CardTitle>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => loadHistoryItem(item)}
                          >
                            Load
                          </Button>
                        </div>
                        <div className="text-xs text-gray-500">
                          {formatDate(item.timestamp)}
                        </div>
                      </CardHeader>
                      <CardContent>
                        <Tabs defaultValue="response">
                          <TabsList className="mb-2">
                            <TabsTrigger value="request">Request</TabsTrigger>
                            <TabsTrigger value="response">Response</TabsTrigger>
                          </TabsList>
                          <TabsContent value="request">
                            {item.requestBody ? (
                              <div className="bg-gray-100 p-2 rounded-md overflow-auto max-h-40">
                                <pre className="text-xs">
                                  {item.requestBody}
                                </pre>
                              </div>
                            ) : (
                              <div className="text-sm text-gray-500">
                                No request body
                              </div>
                            )}
                          </TabsContent>
                          <TabsContent value="response">
                            <div className="bg-gray-100 p-2 rounded-md overflow-auto max-h-40">
                              <pre className="text-xs">{item.responseBody}</pre>
                            </div>
                          </TabsContent>
                        </Tabs>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EndpointTester;
