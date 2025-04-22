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
import { getAnalytics } from "@/services/api";

interface AnalyticsData {
  data: any[];
  count: number;
  filters: any;
}

export default function Analytics() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [groupBy, setGroupBy] = useState<
    "date" | "model" | "provider" | "endpoint"
  >("date");

  useEffect(() => {
    loadAnalytics();
  }, [groupBy]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const response = await getAnalytics({ groupBy });
      setAnalytics(response);
    } catch (error) {
      console.error("Failed to load analytics:", error);
      toast.error("Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-6">
      <PageHeader
        heading="Analytics"
        text="View system analytics and usage statistics"
      />

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="w-[200px]">
              <Label>Group By</Label>
              <Select
                value={groupBy}
                onValueChange={(
                  value: "date" | "model" | "provider" | "endpoint"
                ) => setGroupBy(value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select grouping" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">Date</SelectItem>
                  <SelectItem value="model">Model</SelectItem>
                  <SelectItem value="provider">Provider</SelectItem>
                  <SelectItem value="endpoint">Endpoint</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {loading ? (
          <p>Loading analytics...</p>
        ) : !analytics ? (
          <p>No analytics data found</p>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Usage Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {analytics.data.map((item, index) => (
                  <Card key={index}>
                    <CardHeader>
                      <CardTitle>
                        {groupBy === "date"
                          ? new Date(item[groupBy]).toLocaleDateString()
                          : item[groupBy]}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div>
                          <Label>Requests</Label>
                          <div>{item.requests.toLocaleString()}</div>
                        </div>
                        <div>
                          <Label>Total Tokens</Label>
                          <div>{item.tokens.toLocaleString()}</div>
                        </div>
                        <div>
                          <Label>Cost</Label>
                          <div>${item.cost.toFixed(2)}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
