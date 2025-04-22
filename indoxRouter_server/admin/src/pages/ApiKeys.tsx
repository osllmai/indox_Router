import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { toast } from "sonner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Copy, Ban, Trash2, Plus, Search, RefreshCw } from "lucide-react";
import {
  getAllApiKeys,
  getUserApiKeys,
  revokeApiKey,
  enableApiKey,
  createApiKey,
  getAllUsers,
  getApiKeys,
} from "@/services/api";
import { ApiKey, User } from "@/services/api";
import { PageHeader } from "@/components/ui/PageHeader";
import { Label } from "@/components/ui/label";

const ApiKeysPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [apiKeyName, setApiKeyName] = useState("API Key");
  const queryClient = useQueryClient();
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch API keys
  const {
    data: apiKeysData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["apiKeys", searchTerm],
    queryFn: () => getAllApiKeys(100, 0, searchTerm),
  });

  // Fetch users for the create API key dialog
  const { data: users } = useQuery({
    queryKey: ["users"],
    queryFn: () => getAllUsers(100, 0, ""),
  });

  // Create API key mutation
  const createApiKeyMutation = useMutation({
    mutationFn: ({ userId, name }: { userId: number; name: string }) =>
      createApiKey(userId, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] });
      toast.success("API key created successfully");
      setIsCreateDialogOpen(false);
      setSelectedUserId("");
      setApiKeyName("API Key");
    },
    onError: (error: any) => {
      toast.error(
        `Failed to create API key: ${error.message || "Unknown error"}`
      );
    },
  });

  // Revoke API key mutation
  const revokeApiKeyMutation = useMutation({
    mutationFn: ({ userId, keyId }: { userId: number; keyId: number }) =>
      revokeApiKey(userId, keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] });
      toast.success("API key revoked successfully");
    },
    onError: (error: any) => {
      toast.error(
        `Failed to revoke API key: ${error.message || "Unknown error"}`
      );
    },
  });

  // Enable API key mutation
  const enableApiKeyMutation = useMutation({
    mutationFn: ({ userId, keyId }: { userId: number; keyId: number }) =>
      enableApiKey(userId, keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] });
      toast.success("API key enabled successfully");
    },
    onError: (error: any) => {
      toast.error(
        `Failed to enable API key: ${error.message || "Unknown error"}`
      );
    },
  });

  const handleCreateApiKey = () => {
    if (!selectedUserId) {
      toast.error("Please select a user");
      return;
    }
    createApiKeyMutation.mutate({
      userId: parseInt(selectedUserId),
      name: apiKeyName,
    });
  };

  const handleRevokeApiKey = (userId: number, keyId: number) => {
    if (
      window.confirm(
        "Are you sure you want to revoke this API key? This action cannot be undone."
      )
    ) {
      revokeApiKeyMutation.mutate({ userId, keyId });
    }
  };

  const handleEnableApiKey = (userId: number, keyId: number) => {
    if (window.confirm("Are you sure you want to enable this API key?")) {
      enableApiKeyMutation.mutate({ userId, keyId });
    }
  };

  const copyApiKey = (apiKey: string) => {
    navigator.clipboard
      .writeText(apiKey)
      .then(() => {
        toast.success("API key copied to clipboard");
      })
      .catch((err) => {
        console.error("Error copying API key:", err);
        toast.error("Failed to copy API key");
      });
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    return format(new Date(dateString), "MMM d, yyyy HH:mm");
  };

  const maskApiKey = (apiKey: string) => {
    if (!apiKey) return "(hidden)";
    return `${apiKey.substring(0, 4)}...${apiKey.substring(apiKey.length - 4)}`;
  };

  const loadApiKeys = async () => {
    try {
      setLoading(true);
      const response = await getAllApiKeys();
      setApiKeys(response || []);
    } catch (error) {
      console.error("Failed to load API keys:", error);
      toast.error("Failed to load API keys");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApiKeys();
  }, []);

  return (
    <div className="container mx-auto py-6">
      <PageHeader heading="API Keys" text="View and manage API keys" />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <p>Loading API keys...</p>
        ) : apiKeys.length === 0 ? (
          <p>No API keys found</p>
        ) : (
          apiKeys.map((apiKey) => (
            <Card key={apiKey.id}>
              <CardHeader>
                <CardTitle>API Key {apiKey.id}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div>
                    <Label>Name</Label>
                    <div>{apiKey.name}</div>
                  </div>
                  <div>
                    <Label>Status</Label>
                    <div>{apiKey.is_active ? "Active" : "Inactive"}</div>
                  </div>
                  <div>
                    <Label>Created</Label>
                    <div>{new Date(apiKey.created_at).toLocaleString()}</div>
                  </div>
                  <div>
                    <Label>Last Used</Label>
                    <div>
                      {apiKey.last_used_at
                        ? new Date(apiKey.last_used_at).toLocaleString()
                        : "Never"}
                    </div>
                  </div>
                  <div>
                    <Label>User</Label>
                    <div>{apiKey.user?.username || "N/A"}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default ApiKeysPage;
