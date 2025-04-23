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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Search, RefreshCw, Download, PlusCircle } from "lucide-react";
import { getTransactions, getAllUsers, addCredits } from "@/services/api";
import { Transaction, User } from "@/services/api";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/card";

const TransactionsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [limit, setLimit] = useState(20);
  const [offset, setOffset] = useState(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [paymentMethodFilter, setPaymentMethodFilter] = useState<string>("all");
  const queryClient = useQueryClient();

  // Add credits dialog state
  const [isAddCreditsDialogOpen, setIsAddCreditsDialogOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [creditAmount, setCreditAmount] = useState<string>("10");
  const [paymentMethod, setPaymentMethod] = useState<string>("admin_grant");
  const [referenceId, setReferenceId] = useState<string>("");

  // Load transactions
  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await getTransactions(limit, offset, searchTerm);

      // Handle case where data doesn't have the expected structure
      if (!data || !data.transactions) {
        console.error(
          "Unexpected response format from transactions API:",
          data
        );
        setTransactions([]);
        setTotalCount(0);
        return;
      }

      let filteredTransactions = data.transactions;

      // Apply payment method filter if selected
      if (paymentMethodFilter && paymentMethodFilter !== "all") {
        filteredTransactions = filteredTransactions.filter(
          (t) => t.payment_method === paymentMethodFilter
        );
      }

      setTransactions(filteredTransactions);
      setTotalCount(data.count || 0);
    } catch (error) {
      console.error("Failed to load transactions:", error);
      toast("Failed to load transactions");
      setTransactions([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  // Fetch users for the add credits dialog
  const { data: users, isLoading: loadingUsers } = useQuery({
    queryKey: ["users"],
    queryFn: () => getAllUsers(0, 100),
  });

  // Add credits mutation
  const addCreditsMutation = useMutation({
    mutationFn: ({
      userId,
      amount,
      paymentMethod,
      referenceId,
    }: {
      userId: number;
      amount: number;
      paymentMethod: string;
      referenceId?: string;
    }) => addCredits(userId, amount, paymentMethod, referenceId),
    onSuccess: () => {
      loadTransactions();
      toast("Credits added successfully", { type: "success" });
      setIsAddCreditsDialogOpen(false);
      resetAddCreditsForm();
    },
    onError: (error: Error) => {
      toast(`Failed to add credits: ${error.message || "Unknown error"}`);
    },
  });

  const resetAddCreditsForm = () => {
    setSelectedUserId("");
    setCreditAmount("10");
    setPaymentMethod("admin_grant");
    setReferenceId("");
  };

  // Fetch transactions using React Query
  const { isLoading, refetch } = useQuery({
    queryKey: ["transactions", limit, offset, searchTerm, paymentMethodFilter],
    queryFn: loadTransactions,
    enabled: true,
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    loadTransactions();
  }, [limit, offset, paymentMethodFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setOffset(0); // Reset to first page when searching
    loadTransactions();
  };

  const handleAddCredits = () => {
    if (!selectedUserId) {
      toast("Please select a user", { type: "error" });
      return;
    }

    const amountNum = parseFloat(creditAmount);
    if (isNaN(amountNum) || amountNum <= 0) {
      toast("Please enter a valid amount", { type: "error" });
      return;
    }

    addCreditsMutation.mutate({
      userId: parseInt(selectedUserId),
      amount: amountNum,
      paymentMethod,
      referenceId: referenceId || undefined,
    });
  };

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), "MMM d, yyyy HH:mm");
  };

  // Format currency
  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(amount);
  };

  // Get payment method badge color
  const getPaymentMethodBadge = (method: string) => {
    // If method is empty or undefined, use 'unknown'
    const paymentMethod = method ? method.trim().toLowerCase() : "unknown";

    switch (paymentMethod) {
      case "admin_grant":
        return <Badge className="bg-blue-500">Admin Grant</Badge>;
      case "credit_card":
        return <Badge className="bg-green-500">Credit Card</Badge>;
      case "paypal":
        return <Badge className="bg-indigo-500">PayPal</Badge>;
      case "stripe":
        return <Badge className="bg-purple-500">Stripe</Badge>;
      case "unknown":
        return <Badge variant="outline">Unknown</Badge>;
      default:
        return <Badge variant="outline">{method || "Unknown"}</Badge>;
    }
  };

  // Get unique payment methods for filtering
  const getUniquePaymentMethods = () => {
    const methods = new Set<string>();
    transactions.forEach((transaction) => {
      // Make sure we don't include empty strings, null, or undefined values
      if (
        transaction.payment_method &&
        transaction.payment_method.trim() !== ""
      ) {
        methods.add(transaction.payment_method.trim());
      } else {
        // Add a placeholder for unknown/empty payment methods
        methods.add("unknown");
      }
    });
    return Array.from(methods);
  };

  // Export transactions as CSV
  const exportTransactions = () => {
    if (transactions.length === 0) {
      toast("No transactions to export");
      return;
    }

    // Create CSV content
    const headers = [
      "ID",
      "User ID",
      "Amount",
      "Payment Method",
      "Reference ID",
      "Description",
      "Date",
    ].join(",");

    const rows = transactions.map((t) =>
      [
        t.id,
        t.user_id,
        t.amount,
        t.payment_method,
        t.reference_id,
        t.description ? `"${t.description.replace(/"/g, '""')}"` : "",
        t.created_at,
      ].join(",")
    );

    const csvContent = [headers, ...rows].join("\n");

    // Create and download the file
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `transactions_${new Date().toISOString().slice(0, 10)}.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      <PageHeader
        title="Transactions"
        description="View and manage financial transactions"
        actions={
          <div className="flex space-x-2">
            <Button
              onClick={() => setIsAddCreditsDialogOpen(true)}
              className="bg-green-600 hover:bg-green-700"
            >
              <PlusCircle className="mr-2 h-4 w-4" /> Add Credits
            </Button>
            <Button
              onClick={exportTransactions}
              className="bg-admin-primary hover:bg-slate-800"
            >
              <Download className="mr-2 h-4 w-4" /> Export CSV
            </Button>
          </div>
        }
      />

      <Card className="mb-8">
        <div className="p-4 border-b">
          <div className="flex flex-col gap-4 md:flex-row">
            <form onSubmit={handleSearch} className="flex space-x-2 flex-1">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search transactions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button type="submit" variant="outline">
                Search
              </Button>
              <Button type="button" variant="outline" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4 mr-2" /> Refresh
              </Button>
            </form>

            <div className="flex space-x-2">
              <Select
                value={paymentMethodFilter}
                onValueChange={setPaymentMethodFilter}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Payment Method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Methods</SelectItem>
                  {getUniquePaymentMethods().map((method) => (
                    <SelectItem key={method} value={method}>
                      {method === "unknown" ? "Unknown" : method}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>User ID</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Payment Method</TableHead>
                <TableHead>Reference ID</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-4">
                    Loading transactions...
                  </TableCell>
                </TableRow>
              ) : transactions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-4">
                    No transactions found
                  </TableCell>
                </TableRow>
              ) : (
                transactions.map((transaction) => (
                  <TableRow key={transaction.id}>
                    <TableCell className="font-medium">
                      {transaction.id}
                    </TableCell>
                    <TableCell>{transaction.user_id}</TableCell>
                    <TableCell
                      className={
                        transaction.amount > 0
                          ? "text-green-600 font-semibold"
                          : "text-red-600 font-semibold"
                      }
                    >
                      {formatAmount(transaction.amount)}
                    </TableCell>
                    <TableCell>
                      {getPaymentMethodBadge(transaction.payment_method)}
                    </TableCell>
                    <TableCell className="font-mono text-xs truncate max-w-[150px]">
                      {transaction.reference_id}
                    </TableCell>
                    <TableCell className="truncate max-w-[200px]">
                      {transaction.description}
                    </TableCell>
                    <TableCell>{formatDate(transaction.created_at)}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination controls */}
        <div className="p-4 border-t flex justify-between items-center">
          <div className="text-sm text-gray-500">
            Showing {offset + 1}-
            {Math.min(offset + transactions.length, totalCount)} of {totalCount}{" "}
            transactions
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setOffset(offset + limit)}
              disabled={offset + transactions.length >= totalCount}
            >
              Next
            </Button>
          </div>
        </div>
      </Card>

      {/* Add Credits Dialog */}
      <Dialog
        open={isAddCreditsDialogOpen}
        onOpenChange={setIsAddCreditsDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Credits to User</DialogTitle>
            <DialogDescription>
              Add credits to a user's account. Credits will be immediately
              available.
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
              <Label htmlFor="amount" className="text-right">
                Amount
              </Label>
              <Input
                id="amount"
                type="number"
                min="1"
                step="1"
                value={creditAmount}
                onChange={(e) => setCreditAmount(e.target.value)}
                className="col-span-3"
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="paymentMethod" className="text-right">
                Payment Method
              </Label>
              <Select value={paymentMethod} onValueChange={setPaymentMethod}>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select payment method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin_grant">Admin Grant</SelectItem>
                  <SelectItem value="credit_card">Credit Card</SelectItem>
                  <SelectItem value="paypal">PayPal</SelectItem>
                  <SelectItem value="stripe">Stripe</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="referenceId" className="text-right">
                Reference ID
              </Label>
              <Input
                id="referenceId"
                value={referenceId}
                onChange={(e) => setReferenceId(e.target.value)}
                placeholder="Optional"
                className="col-span-3"
              />
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
              onClick={handleAddCredits}
              className="bg-green-600 hover:bg-green-700"
            >
              Add Credits
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TransactionsPage;
