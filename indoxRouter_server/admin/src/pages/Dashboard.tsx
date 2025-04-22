
import React, { useState, useEffect } from 'react';
import { getSystemStats } from '@/services/api';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatCard } from '@/components/ui/StatCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, BarChart2, Database, FileText } from 'lucide-react';
import { Area, AreaChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getSystemStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch system stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  // Placeholder data until the API call returns
  const placeholderStats = {
    total_users: 124,
    active_users: 87,
    total_requests: 15420,
    total_tokens: 2345678,
    total_cost: 128.45,
    user_growth: Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 86400000).toISOString().split('T')[0],
      count: 85 + Math.floor(Math.random() * 15)
    })),
    request_growth: Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 86400000).toISOString().split('T')[0],
      count: 400 + Math.floor(Math.random() * 200)
    })),
    model_usage: [
      { model: 'gpt-4', requests: 5842, tokens: 876543 },
      { model: 'gpt-3.5-turbo', requests: 7821, tokens: 1234567 },
      { model: 'claude-v2', requests: 1245, tokens: 198765 },
      { model: 'mistral-large', requests: 512, tokens: 87654 }
    ]
  };

  const displayStats = stats || placeholderStats;
  
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const pieData = displayStats.model_usage.map((item: any) => ({
    name: item.model,
    value: item.requests
  }));

  return (
    <div>
      <PageHeader 
        title="Dashboard" 
        description="Overview of your platform metrics and usage statistics" 
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          title="Total Users" 
          value={displayStats.total_users} 
          icon={<Users size={24} />} 
          change={{ value: '12%', isPositive: true }}
          color="blue"
        />
        <StatCard 
          title="Active Users" 
          value={displayStats.active_users} 
          icon={<Users size={24} />} 
          change={{ value: '8%', isPositive: true }}
          color="green"
        />
        <StatCard 
          title="Total Requests" 
          value={new Intl.NumberFormat().format(displayStats.total_requests)} 
          icon={<Database size={24} />} 
          change={{ value: '23%', isPositive: true }}
          color="purple"
        />
        <StatCard 
          title="Total Cost" 
          value={`$${displayStats.total_cost.toFixed(2)}`} 
          icon={<BarChart2 size={24} />} 
          change={{ value: '5%', isPositive: false }}
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
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={displayStats.user_growth}
                  margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="count" stroke="#3b82f6" fill="#93c5fd" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Request Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={displayStats.request_growth}
                  margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#8884d8" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Model Usage Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80 flex items-center justify-center">
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
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {pieData.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Top Models by Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {displayStats.model_usage.map((model: any, index: number) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-3 h-3 rounded-full mr-3" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                    <span className="font-medium">{model.model}</span>
                  </div>
                  <div className="text-gray-500">
                    {new Intl.NumberFormat().format(model.requests)} requests
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
