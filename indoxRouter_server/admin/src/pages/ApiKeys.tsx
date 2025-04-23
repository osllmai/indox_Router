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
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Copy,
  CheckCircle,
  XCircle,
  MoreHorizontal,
  Plus,
  Search,
  RefreshCw,
  Trash2,
} from "lucide-react";
import {
  getAllApiKeys,
  revokeApiKey,
  enableApiKey,
  createApiKey,
  deleteApiKey,
  getAllUsers,
} from "@/services/api";
import { ApiKey, User } from "@/services/api";
import { PageHeader } from "@/components/ui/PageHeader";
import { Label } from "@/components/ui/label";

const ApiKeysPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [apiKeyName, setApiKeyName] = useState("API Key");
  const [deleteApiKeyId, setDeleteApiKeyId] = useState<{
    userId: number;
    keyId: number;
  } | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState(true);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);

  // Fetch API keys
  const loadApiKeys = async () => {
    try {
      setLoading(true);
      const keys = await getAllApiKeys();
      console.log("API Keys:", keys);

      // Log the first key to inspect its structure
      if (keys && keys.length > 0) {
        console.log(
          "First API key structure:",
          JSON.stringify(keys[0], null, 2)
        );
      }

      setApiKeys(Array.isArray(keys) ? keys : []);
    } catch (error) {
      console.error("Failed to load API keys:", error);
      toast("Failed to load API keys");
    } finally {
      setLoading(false);
    }
  };

  // Fetch users for the create API key dialog
  const { data: users, isLoading: loadingUsers } = useQuery({
    queryKey: ["users"],
    queryFn: () => getAllUsers(0, 100),
  });

  // Create API key mutation
  const createApiKeyMutation = useMutation({
    mutationFn: ({ userId, name }: { userId: number; name: string }) =>
      createApiKey(userId, name),
    onSuccess: () => {
      loadApiKeys();
      toast("API key created successfully", { type: "success" });
      setIsCreateDialogOpen(false);
      setSelectedUserId("");
      setApiKeyName("API Key");
    },
    onError: (error: Error) => {
      toast(`Failed to create API key: ${error.message || "Unknown error"}`);
    },
  });

  // Revoke API key mutation
  const revokeApiKeyMutation = useMutation({
    mutationFn: ({ userId, keyId }: { userId: number; keyId: number }) =>
      revokeApiKey(userId, keyId),
    onSuccess: () => {
      loadApiKeys();
      toast("API key revoked successfully", { type: "success" });
    },
    onError: (error: Error) => {
      toast(`Failed to revoke API key: ${error.message || "Unknown error"}`);
    },
  });

  // Enable API key mutation
  const enableApiKeyMutation = useMutation({
    mutationFn: ({ userId, keyId }: { userId: number; keyId: number }) =>
      enableApiKey(userId, keyId),
    onSuccess: () => {
      loadApiKeys();
      toast("API key enabled successfully", { type: "success" });
    },
    onError: (error: Error) => {
      toast(`Failed to enable API key: ${error.message || "Unknown error"}`);
    },
  });

  // Delete API key mutation
  const deleteApiKeyMutation = useMutation({
    mutationFn: ({ userId, keyId }: { userId: number; keyId: number }) =>
      deleteApiKey(userId, keyId),
    onSuccess: () => {
      loadApiKeys();
      toast("API key deleted successfully", { type: "success" });
    },
    onError: (error: Error) => {
      toast(`Failed to delete API key: ${error.message || "Unknown error"}`);
    },
  });

  const handleCreateApiKey = () => {
    if (!selectedUserId) {
      toast("Please select a user");
      return;
    }
    createApiKeyMutation.mutate({
      userId: parseInt(selectedUserId),
      name: apiKeyName,
    });
  };

  const handleRevokeApiKey = (userId: number, keyId: number) => {
    // Check if userId is undefined, and use the user.id property if available
    const effectiveUserId =
      userId || apiKeys.find((k) => k.id === keyId)?.user?.id;

    if (!effectiveUserId) {
      toast("Cannot revoke key: User ID is missing", { type: "error" });
      return;
    }

    console.log(`Revoking key: userId=${effectiveUserId}, keyId=${keyId}`);
    revokeApiKeyMutation.mutate({ userId: effectiveUserId, keyId });
  };

  const handleEnableApiKey = (userId: number, keyId: number) => {
    // Check if userId is undefined, and use the user.id property if available
    const effectiveUserId =
      userId || apiKeys.find((k) => k.id === keyId)?.user?.id;

    if (!effectiveUserId) {
      toast("Cannot enable key: User ID is missing", { type: "error" });
      return;
    }

    console.log(`Enabling key: userId=${effectiveUserId}, keyId=${keyId}`);
    enableApiKeyMutation.mutate({ userId: effectiveUserId, keyId });
  };

  const handleDeleteKey = (userId: number, keyId: number) => {
    // Check if userId is undefined, and use the user.id property if available
    const effectiveUserId =
      userId || apiKeys.find((k) => k.id === keyId)?.user?.id;

    if (!effectiveUserId) {
      toast("Cannot delete key: User ID is missing", { type: "error" });
      return;
    }

    if (
      window.confirm(
        "Are you sure you want to delete this API key? This action cannot be undone."
      )
    ) {
      console.log(`Deleting key: userId=${effectiveUserId}, keyId=${keyId}`);

      deleteApiKeyMutation.mutate(
        { userId: effectiveUserId, keyId },
        {
          onSuccess: () => {
            toast("API key deleted successfully", { type: "success" });
            loadApiKeys(); // Refresh the list
          },
          onError: (error: Error) => {
            console.error("Delete API key failed:", error);
            toast(
              `Failed to delete API key: ${error.message || "Unknown error"}`,
              { type: "error" }
            );
          },
        }
      );
    }
  };

  const copyApiKey = (apiKey: string) => {
    navigator.clipboard
      .writeText(apiKey)
      .then(() => {
        toast("API key copied to clipboard", { type: "success" });
      })
      .catch((err) => {
        console.error("Error copying API key:", err);
        toast("Failed to copy API key");
      });
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    return format(new Date(dateString), "MMM d, yyyy HH:mm");
  };

  const maskApiKey = (apiKey: string) => {
    if (!apiKey) return "(hidden)";
    return `${apiKey.substring(0, 8)}...${apiKey.substring(apiKey.length - 4)}`;
  };

  useEffect(() => {
    loadApiKeys();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadApiKeys();
  };

  return (
    <div>
      <PageHeader
        title="API Keys Management"
        description="View and manage API keys across the platform"
        actions={
          <Button
            onClick={() => setIsCreateDialogOpen(true)}
            className="bg-admin-primary hover:bg-slate-800"
          >
            <Plus className="mr-2 h-4 w-4" /> Create API Key
          </Button>
        }
      />

      <div className="bg-white rounded-lg shadow mb-8">
        <div className="p-4 border-b">
          <form onSubmit={handleSearch} className="flex space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search API keys..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button type="submit" variant="outline">
              Search
            </Button>
            <Button type="button" variant="outline" onClick={loadApiKeys}>
              <RefreshCw className="h-4 w-4 mr-2" /> Refresh
            </Button>
          </form>
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>API Key</TableHead>
                <TableHead>Owner</TableHead>
                <TableHead>Requests</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Last Used</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-4">
                    Loading API keys...
                  </TableCell>
                </TableRow>
              ) : apiKeys.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-4">
                    No API keys found
                  </TableCell>
                </TableRow>
              ) : (
                apiKeys.map((apiKey) => (
                  <TableRow key={apiKey.id}>
                    <TableCell className="font-medium">{apiKey.id}</TableCell>
                    <TableCell>{apiKey.name}</TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs">
                          {maskApiKey(apiKey.api_key || apiKey.key || "")}
                        </span>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() =>
                            copyApiKey(apiKey.api_key || apiKey.key || "")
                          }
                          title="Copy API key"
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell>
                      {apiKey.user ? apiKey.user.username : "N/A"}
                    </TableCell>
                    <TableCell>
                      {apiKey.request_count !== undefined
                        ? apiKey.request_count.toLocaleString()
                        : "N/A"}
                    </TableCell>
                    <TableCell>
                      {apiKey.is_active || apiKey.active ? (
                        <Badge className="bg-green-500">Active</Badge>
                      ) : (
                        <Badge variant="outline" className="text-red-500">
                          Revoked
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{formatDate(apiKey.created_at)}</TableCell>
                    <TableCell>
                      {formatDate(apiKey.last_used_at || null)}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {apiKey.is_active || apiKey.active ? (
                            <DropdownMenuItem
                              className="text-orange-600"
                              onClick={() => {
                                // Check for user ID in different locations
                                const userId =
                                  apiKey.user_id || apiKey.user?.id;
                                handleRevokeApiKey(userId, apiKey.id);
                              }}
                            >
                              <XCircle className="mr-2 h-4 w-4" /> Revoke
                            </DropdownMenuItem>
                          ) : (
                            <DropdownMenuItem
                              className="text-green-600"
                              onClick={() => {
                                // Check for user ID in different locations
                                const userId =
                                  apiKey.user_id || apiKey.user?.id;
                                handleEnableApiKey(userId, apiKey.id);
                              }}
                            >
                              <CheckCircle className="mr-2 h-4 w-4" /> Enable
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem
                            className="text-red-600"
                            onClick={() => {
                              // Check for user ID in different locations
                              const userId = apiKey.user_id || apiKey.user?.id;
                              handleDeleteKey(userId, apiKey.id);
                            }}
                          >
                            <Trash2 className="mr-2 h-4 w-4" /> Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Create API Key Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New API Key</DialogTitle>
            <DialogDescription>
              Create an API key for a user to access the API.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="user" className="text-right">
                User
              </Label>
              <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select a user" />
                </SelectTrigger>
                <SelectContent>
                  {loadingUsers ? (
                    <SelectItem value="loading" disabled>
                      Loading users...
                    </SelectItem>
                  ) : !users || users.length === 0 ? (
                    <SelectItem value="none" disabled>
                      No users found
                    </SelectItem>
                  ) : (
                    users.map((user: User) => (
                      <SelectItem key={user.id} value={user.id.toString()}>
                        {user.username} ({user.email})
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Key Name
              </Label>
              <Input
                id="name"
                value={apiKeyName}
                onChange={(e) => setApiKeyName(e.target.value)}
                className="col-span-3"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsCreateDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateApiKey}
              className="bg-admin-primary hover:bg-slate-800"
            >
              Create API Key
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ApiKeysPage;
