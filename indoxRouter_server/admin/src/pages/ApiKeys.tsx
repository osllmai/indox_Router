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
  extendApiKeyExpiration,
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
      const keys = await getAllApiKeys(100, 0, searchTerm);
      console.log("API Keys:", keys);

      // Log the first key to inspect its structure
      if (keys && keys.length > 0) {
        console.log(
          "First API key structure:",
          JSON.stringify(keys[0], null, 2)
        );
      }

      // Normalize the API keys structure to ensure both formats work
      const normalizedKeys = keys.map((key) => {
        // Ensure both access patterns work by storing user_id at top level too
        return {
          ...key,
          // If user_id is not directly available, get it from user.id
          user_id: key.user_id || (key.user ? key.user.id : undefined),
          // Ensure is_active and active are both available
          is_active: key.is_active || key.active,
          active: key.active || key.is_active,
          // Ensure both api_key and key are available
          api_key: key.api_key || key.key,
          key: key.key || key.api_key,
        };
      });

      setApiKeys(Array.isArray(normalizedKeys) ? normalizedKeys : []);
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

  // Extend API key expiration mutation
  const extendExpirationMutation = useMutation({
    mutationFn: ({ userId, keyId }: { userId: number; keyId: number }) =>
      extendApiKeyExpiration(userId, keyId, 30),
    onSuccess: (data) => {
      loadApiKeys();
      toast(`API key expiration extended to ${formatDate(data.expires_at)}`, {
        type: "success",
      });
    },
    onError: (error: Error) => {
      toast(
        `Failed to extend API key expiration: ${
          error.message || "Unknown error"
        }`
      );
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
    // Get the API key details
    const apiKey = apiKeys.find(
      (key) => key.id === keyId && key.user_id === userId
    );

    // Add special handling for admin panel keys
    if (apiKey && apiKey.name === "Admin Panel Access") {
      toast(
        "Warning: This is an Admin Panel Access key. Revoking it will prevent admin login. Create a new admin key first before revoking this one.",
        {
          type: "warning",
          duration: 6000,
        }
      );
      return;
    }

    revokeApiKeyMutation.mutate({ userId, keyId });
  };

  const handleEnableApiKey = (userId: number, keyId: number) => {
    enableApiKeyMutation.mutate({ userId, keyId });
  };

  const handleExtendExpiration = (userId: number, keyId: number) => {
    extendExpirationMutation.mutate({ userId, keyId });
  };

  const handleDeleteKey = (userId: number, keyId: number) => {
    // Get the API key details
    const apiKey = apiKeys.find(
      (key) => key.id === keyId && key.user_id === userId
    );

    // Add special handling for admin panel keys
    if (apiKey && apiKey.name === "Admin Panel Access") {
      toast(
        "Warning: This is an Admin Panel Access key. Deleting it will prevent admin login. Create a new admin key first before deleting this one.",
        {
          type: "warning",
          duration: 6000,
        }
      );
      return;
    }

    setDeleteApiKeyId({ userId, keyId });
    setIsDeleteDialogOpen(true);
  };

  const copyApiKey = (apiKey: string) => {
    if (!apiKey || apiKey === "(hidden)") {
      toast("API key not available for copying", { type: "error" });
      return;
    }

    try {
      // Use modern Clipboard API with fallback
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard
          .writeText(apiKey)
          .then(() => {
            toast("API key copied to clipboard", { type: "success" });
          })
          .catch((err) => {
            console.error("Error copying API key:", err);
            fallbackCopyToClipboard(apiKey);
          });
      } else {
        fallbackCopyToClipboard(apiKey);
      }
    } catch (err) {
      console.error("Copy failed:", err);
      toast("Failed to copy API key", { type: "error" });
    }
  };

  // Fallback method for older browsers
  const fallbackCopyToClipboard = (text: string) => {
    try {
      const textArea = document.createElement("textarea");
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const successful = document.execCommand("copy");
      document.body.removeChild(textArea);

      if (successful) {
        toast("API key copied to clipboard", { type: "success" });
      } else {
        toast("Failed to copy API key", { type: "error" });
      }
    } catch (err) {
      console.error("Fallback copy failed:", err);
      toast("Failed to copy API key", { type: "error" });
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    return format(new Date(dateString), "MMM d, yyyy HH:mm");
  };

  const maskApiKey = (apiKey: string) => {
    if (!apiKey) return "(hidden)";
    return `${apiKey.substring(0, 8)}...${apiKey.substring(apiKey.length - 4)}`;
  };

  const isExpiringSoon = (
    expiryDateStr: string | null | undefined
  ): boolean => {
    if (!expiryDateStr) return false;

    const expiryDate = new Date(expiryDateStr);
    const now = new Date();

    // Calculate days remaining
    const daysRemaining = Math.floor(
      (expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    );

    // Return true if less than 7 days remaining
    return daysRemaining >= 0 && daysRemaining < 7;
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

      {/* Admin Keys Warning Banner */}
      <div className="bg-amber-50 border-l-4 border-amber-500 p-4 mb-4 rounded-md">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-amber-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-amber-700">
              <strong>Warning:</strong> Do not revoke or delete any API key
              named "Admin Panel Access" that belongs to your account. These
              keys are used for admin panel authentication. If you need to
              replace one, create a new admin key first.
            </p>
          </div>
        </div>
      </div>

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
                <TableHead>Expires</TableHead>
                <TableHead>Last Used</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={10} className="text-center py-4">
                    Loading API keys...
                  </TableCell>
                </TableRow>
              ) : apiKeys.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} className="text-center py-4">
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
                            copyApiKey(
                              (apiKey.api_key || apiKey.key || "").toString()
                            )
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
                      <div className="flex items-center">
                        {formatDate(apiKey.expires_at || null)}
                        {isExpiringSoon(apiKey.expires_at) && (
                          <Badge
                            className="ml-2 bg-yellow-500"
                            title="Expires soon"
                          >
                            Expiring Soon
                          </Badge>
                        )}
                      </div>
                    </TableCell>
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
                                handleRevokeApiKey(apiKey.user_id, apiKey.id);
                              }}
                            >
                              <XCircle className="mr-2 h-4 w-4" /> Revoke
                            </DropdownMenuItem>
                          ) : (
                            <DropdownMenuItem
                              className="text-green-600"
                              onClick={() => {
                                handleEnableApiKey(apiKey.user_id, apiKey.id);
                              }}
                            >
                              <CheckCircle className="mr-2 h-4 w-4" /> Enable
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem
                            className="text-blue-600"
                            onClick={() => {
                              handleExtendExpiration(apiKey.user_id, apiKey.id);
                            }}
                          >
                            <RefreshCw className="mr-2 h-4 w-4" /> Extend
                            Expiration
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-red-600"
                            onClick={() => {
                              handleDeleteKey(apiKey.user_id, apiKey.id);
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

      {/* Delete API Key Confirmation Dialog */}
      <AlertDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action will permanently delete the API key and cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-red-500 text-white hover:bg-red-600"
              onClick={() => {
                if (deleteApiKeyId) {
                  deleteApiKeyMutation.mutate({
                    userId: deleteApiKeyId.userId,
                    keyId: deleteApiKeyId.keyId,
                  });
                }
                setIsDeleteDialogOpen(false);
                setDeleteApiKeyId(null);
              }}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default ApiKeysPage;
