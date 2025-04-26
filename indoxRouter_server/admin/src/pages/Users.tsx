import React, { useState, useEffect } from "react";
import { getUsers, deleteUser, updateUser, addCredits } from "@/services/api";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
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
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  User,
  Edit,
  Trash,
  MoreHorizontal,
  Plus,
  Search,
  RefreshCw,
} from "lucide-react";
import { toast } from "sonner";
import { Link } from "react-router-dom";

interface User {
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

const Users = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [editUser, setEditUser] = useState<User | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [deleteUserId, setDeleteUserId] = useState<number | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isAddCreditsDialogOpen, setIsAddCreditsDialogOpen] = useState(false);
  const [creditAmount, setCreditAmount] = useState<number>(0);
  const [creditUserId, setCreditUserId] = useState<number | null>(null);
  const [creditPaymentMethod, setCreditPaymentMethod] = useState("admin_grant");

  useEffect(() => {
    fetchUsers(1, 10);
  }, []);

  const fetchUsers = async (page: number = 1, limit: number = 10) => {
    try {
      setLoading(true);
      const skip = (page - 1) * limit;
      const data = await getUsers(skip, limit, searchTerm);
      console.log("API Response:", data);

      // The response should already be an array of users
      setUsers(Array.isArray(data) ? data : []);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching users:", error);
      toast("Failed to load users");
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchUsers(1, 10);
  };

  const handleEditClick = (user: User) => {
    setEditUser(user);
    setIsEditDialogOpen(true);
  };

  const handleDeleteClick = (userId: number) => {
    setDeleteUserId(userId);
    setIsDeleteDialogOpen(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editUser) return;

    try {
      // Prepare update data (excluding credits since we have a separate Add Credits action)
      const userData = {
        first_name: editUser.first_name,
        last_name: editUser.last_name,
        email: editUser.email,
        is_active: editUser.is_active,
        account_tier: editUser.account_tier,
      };

      console.log("Sending update with data:", userData);

      const result = await updateUser(editUser.id, userData);
      console.log("Update result:", result);

      if (result && result.status === "success") {
        // Update the user in the local state to reflect changes
        setUsers(
          users.map((user) =>
            user.id === editUser.id ? { ...user, ...userData } : user
          )
        );

        setIsEditDialogOpen(false);
        toast("User updated successfully", { type: "success" });

        // Refresh the user list to get the most up-to-date data
        fetchUsers(1, 10);
      } else {
        toast("Failed to update user", { type: "error" });
      }
    } catch (error) {
      console.error("Failed to update user:", error);
      toast("Failed to update user", { type: "error" });
    }
  };

  const handleDeleteConfirm = async () => {
    if (deleteUserId === null) return;

    try {
      await deleteUser(deleteUserId);
      setUsers(users.filter((user) => user.id !== deleteUserId));
      toast("User deleted successfully", { type: "success" });
    } catch (error) {
      console.error("Failed to delete user:", error);
      toast("Failed to delete user", { type: "error" });
    } finally {
      setIsDeleteDialogOpen(false);
      setDeleteUserId(null);
    }
  };

  const handleAddCreditsClick = (userId: number) => {
    setCreditUserId(userId);
    setCreditAmount(0);
    setIsAddCreditsDialogOpen(true);
  };

  const handleAddCreditsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (creditUserId === null || creditAmount <= 0) {
      toast("Amount must be greater than 0", { type: "error" });
      return;
    }

    try {
      console.log("Adding credits:", {
        userId: creditUserId,
        amount: creditAmount,
        paymentMethod: creditPaymentMethod,
      });

      const result = await addCredits(
        creditUserId,
        creditAmount,
        creditPaymentMethod
      );

      console.log("Add credits result:", result);

      if (result) {
        // Update the user's credits in the local state
        setUsers(
          users.map((user) =>
            user.id === creditUserId
              ? { ...user, credits: user.credits + creditAmount }
              : user
          )
        );

        setIsAddCreditsDialogOpen(false);
        setCreditUserId(null);
        setCreditAmount(0);
        toast(`Successfully added $${creditAmount} credits`, {
          type: "success",
        });

        // Refresh the users list
        fetchUsers(1, 10);
      }
    } catch (error) {
      console.error("Failed to add credits:", error);
      let errorMessage = "Failed to add credits";

      if (error instanceof Error) {
        errorMessage += ": " + error.message;
      }

      toast(errorMessage, { type: "error" });
    }
  };

  const getAccountTierBadge = (tier: string) => {
    switch (tier) {
      case "admin":
        return <Badge className="bg-purple-500">Admin</Badge>;
      case "premium":
        return <Badge className="bg-amber-500">Premium</Badge>;
      case "standard":
        return <Badge className="bg-blue-500">Standard</Badge>;
      default:
        return <Badge variant="outline">Free</Badge>;
    }
  };

  return (
    <div>
      <PageHeader
        title="User Management"
        description="View and manage user accounts"
        actions={
          <Button asChild className="bg-admin-primary hover:bg-slate-800">
            <Link to="/users/create">
              <Plus className="mr-2 h-4 w-4" /> Add User
            </Link>
          </Button>
        }
      />

      <div className="bg-white rounded-lg shadow mb-8">
        <div className="p-4 border-b">
          <form onSubmit={handleSearch} className="flex space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search users by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button type="submit" variant="outline">
              Search
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => fetchUsers()}
            >
              <RefreshCw className="h-4 w-4 mr-2" /> Refresh
            </Button>
          </form>
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Username</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Account Tier</TableHead>
                <TableHead>Credits</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-4">
                    Loading users...
                  </TableCell>
                </TableRow>
              ) : users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-4">
                    No users found
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.id}</TableCell>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>
                      {user.first_name && user.last_name ? (
                        `${user.first_name} ${user.last_name}`
                      ) : (
                        <span className="text-gray-400">Not set</span>
                      )}
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      {user.is_active ? (
                        <Badge className="bg-green-500">Active</Badge>
                      ) : (
                        <Badge variant="outline" className="text-red-500">
                          Inactive
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {getAccountTierBadge(user.account_tier)}
                    </TableCell>
                    <TableCell>${user.credits.toFixed(2)}</TableCell>
                    <TableCell>
                      {new Date(user.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => handleEditClick(user)}
                          >
                            <Edit className="mr-2 h-4 w-4" /> Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => handleAddCreditsClick(user.id)}
                          >
                            <Plus className="mr-2 h-4 w-4" /> Add Credits
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-red-600"
                            onClick={() => handleDeleteClick(user.id)}
                          >
                            <Trash className="mr-2 h-4 w-4" /> Delete
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

      {/* Edit User Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
            <DialogDescription>
              Make changes to user information below.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleEditSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="firstName" className="text-right">
                  First Name
                </Label>
                <Input
                  id="firstName"
                  value={editUser?.first_name || ""}
                  onChange={(e) =>
                    setEditUser((prev) =>
                      prev ? { ...prev, first_name: e.target.value } : null
                    )
                  }
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="lastName" className="text-right">
                  Last Name
                </Label>
                <Input
                  id="lastName"
                  value={editUser?.last_name || ""}
                  onChange={(e) =>
                    setEditUser((prev) =>
                      prev ? { ...prev, last_name: e.target.value } : null
                    )
                  }
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="email" className="text-right">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={editUser?.email || ""}
                  onChange={(e) =>
                    setEditUser((prev) =>
                      prev ? { ...prev, email: e.target.value } : null
                    )
                  }
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="status" className="text-right">
                  Status
                </Label>
                <div className="col-span-3 flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="status"
                    checked={editUser?.is_active || false}
                    onChange={(e) =>
                      setEditUser((prev) =>
                        prev ? { ...prev, is_active: e.target.checked } : null
                      )
                    }
                    className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
                  />
                  <Label htmlFor="status" className="font-normal">
                    Active
                  </Label>
                </div>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="accountTier" className="text-right">
                  Account Tier
                </Label>
                <select
                  id="accountTier"
                  value={editUser?.account_tier || "free"}
                  onChange={(e) =>
                    setEditUser((prev) =>
                      prev ? { ...prev, account_tier: e.target.value } : null
                    )
                  }
                  className="col-span-3 bg-transparent h-10 rounded-md border border-input px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="free">Free</option>
                  <option value="standard">Standard</option>
                  <option value="premium">Premium</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsEditDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="bg-admin-primary hover:bg-slate-800"
              >
                Save Changes
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete User Dialog */}
      <AlertDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the
              user account and all associated data.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-red-500 hover:bg-red-600"
              onClick={handleDeleteConfirm}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Add Credits Dialog */}
      <Dialog
        open={isAddCreditsDialogOpen}
        onOpenChange={setIsAddCreditsDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Credits</DialogTitle>
            <DialogDescription>
              Add credits to the user's account.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleAddCreditsSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="creditAmount" className="text-right">
                  Amount ($)
                </Label>
                <Input
                  id="creditAmount"
                  type="number"
                  min="0"
                  step="0.01"
                  value={creditAmount}
                  onChange={(e) => setCreditAmount(Number(e.target.value))}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="paymentMethod" className="text-right">
                  Payment Method
                </Label>
                <select
                  id="paymentMethod"
                  value={creditPaymentMethod}
                  onChange={(e) => setCreditPaymentMethod(e.target.value)}
                  className="col-span-3 bg-transparent h-10 rounded-md border border-input px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="admin_grant">Admin Grant</option>
                  <option value="credit_card">Credit Card</option>
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="crypto">Cryptocurrency</option>
                </select>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsAddCreditsDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="bg-admin-primary hover:bg-slate-800"
              >
                Add Credits
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Users;
