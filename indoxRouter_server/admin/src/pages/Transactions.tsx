import React, { useState, useEffect } from "react";
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
import { toast } from "sonner";
import { getTransactions, Transaction } from "@/services/api";

export default function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const response = await getTransactions();
      setTransactions(response.data || []);
    } catch (error) {
      console.error("Failed to load transactions:", error);
      toast.error("Failed to load transactions");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-6">
      <PageHeader
        heading="Transactions"
        text="View and manage billing transactions"
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <p>Loading transactions...</p>
        ) : transactions.length === 0 ? (
          <p>No transactions found</p>
        ) : (
          transactions.map((transaction) => (
            <Card key={transaction.id}>
              <CardHeader>
                <CardTitle>Transaction {transaction.id}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div>
                    <Label>Amount</Label>
                    <div>${transaction.amount}</div>
                  </div>
                  <div>
                    <Label>Status</Label>
                    <div>{transaction.status}</div>
                  </div>
                  <div>
                    <Label>Date</Label>
                    <div>
                      {new Date(transaction.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <Label>User</Label>
                    <div>{transaction.user_id}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
