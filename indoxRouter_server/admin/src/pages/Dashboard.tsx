import React, { useState, useEffect } from "react";
import { getSystemStats } from "@/services/api";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatCard } from "@/components/ui/StatCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, BarChart2, Database, FileText } from "lucide-react";
import {
  Area,
  AreaChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { toast } from "sonner";

const Dashboard = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getSystemStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch system stats:", error);
        setError("Failed to load dashboard data. Please try again later.");
        toast.error("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  // Empty state when no data is available
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold mb-2">
            Unable to load dashboard data
          </h3>
          <p className="text-gray-500 mb-4">
            {error || "An unknown error occurred"}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

  const pieData =
    stats.model_usage?.map((item: any) => ({
      name: item.model,
      value: item.requests,
    })) || [];

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Overview of your platform metrics and usage statistics"
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Users"
          value={stats.total_users || 0}
          icon={<Users size={24} />}
          change={{ value: "12%", isPositive: true }}
          color="blue"
        />
        <StatCard
          title="Active Users"
          value={stats.active_users || 0}
          icon={<Users size={24} />}
          change={{ value: "8%", isPositive: true }}
          color="green"
        />
        <StatCard
          title="Total Requests"
          value={new Intl.NumberFormat().format(stats.total_requests || 0)}
          icon={<Database size={24} />}
          change={{ value: "23%", isPositive: true }}
          color="purple"
        />
        <StatCard
          title="Total Cost"
          value={`$${(stats.total_cost || 0).toFixed(2)}`}
          icon={<BarChart2 size={24} />}
          change={{ value: "5%", isPositive: false }}
          color="amber"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">User Growth</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              {stats.user_growth && stats.user_growth.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={stats.user_growth}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="count"
                      stroke="#3b82f6"
                      fill="#93c5fd"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-gray-500">No user growth data available</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">
              Request Volume
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              {stats.request_growth && stats.request_growth.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={stats.request_growth}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="count" stroke="#8884d8" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-gray-500">
                    No request volume data available
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">
              Model Usage Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80 flex items-center justify-center">
              {pieData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) =>
                        `${name}: ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {pieData.map((entry: any, index: number) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-gray-500">No model usage data available</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">
              Top Models by Usage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.model_usage && stats.model_usage.length > 0 ? (
                stats.model_usage.map((model: any, index: number) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <div
                        className="w-3 h-3 rounded-full mr-3"
                        style={{
                          backgroundColor: COLORS[index % COLORS.length],
                        }}
                      ></div>
                      <span className="font-medium">{model.model}</span>
                    </div>
                    <div className="text-gray-500">
                      {new Intl.NumberFormat().format(model.requests)} requests
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500">No model usage data available</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
