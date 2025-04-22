import React, { useState, useEffect } from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { getModels } from "@/services/api";

interface Model {
  id: string;
  name: string;
  provider: string;
  context_length: number;
  max_tokens: number;
  cost_per_1k_tokens: number;
  is_active: boolean;
}

interface UsageData {
  model_id: string;
  model_name: string;
  request_count: number;
  token_count: number;
  total_cost: number;
}

const Models = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [usageData, setUsageData] = useState<UsageData[]>([]);
  const [loading, setLoading] = useState(true);
  const [newModel, setNewModel] = useState({
    name: "",
    provider: "",
    context_length: 0,
    max_tokens: 0,
    cost_per_1k_tokens: 0,
    is_active: true,
  });
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    loadModels();
    loadUsageData();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await getModels();
      setModels(response.data || []);
    } catch (error) {
      console.error("Failed to load models:", error);
      toast.error("Failed to load models");
    } finally {
      setLoading(false);
    }
  };

  const loadUsageData = async () => {
    try {
      const response = await getAnalytics({
        groupBy: "model",
      });
      // Transform the response to match the expected format
      const usageList = response.data.map((item: any) => ({
        model_id: item.model || "unknown",
        model_name: item.model || "Unknown Model",
        request_count: item.requests || 0,
        token_count: item.tokens || 0,
        total_cost: item.cost || 0,
      }));
      setUsageData(usageList);
    } catch (error) {
      console.error("Failed to load usage data:", error);
      toast.error("Failed to load usage data");
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setNewModel({
      ...newModel,
      [name]: type === "number" ? parseFloat(value) : value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiFetch("/admin/models", "POST", newModel);
      toast.success("Model added successfully");
      setShowAddForm(false);
      setNewModel({
        name: "",
        provider: "",
        context_length: 0,
        max_tokens: 0,
        cost_per_1k_tokens: 0,
        is_active: true,
      });
      loadModels();
    } catch (error) {
      console.error("Failed to add model:", error);
      toast.error("Failed to add model");
    }
  };

  const toggleModelStatus = async (modelId: string, currentStatus: boolean) => {
    try {
      await apiFetch(`/admin/models/${modelId}`, "PATCH", {
        is_active: !currentStatus,
      });
      toast.success(
        `Model ${currentStatus ? "deactivated" : "activated"} successfully`
      );
      loadModels();
    } catch (error) {
      console.error("Failed to update model status:", error);
      toast.error("Failed to update model status");
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  return (
    <div>
      <PageHeader
        title="Models"
        description="Manage AI models and view usage statistics"
      />

      <Tabs defaultValue="models" className="space-y-4">
        <TabsList>
          <TabsTrigger value="models">Models</TabsTrigger>
          <TabsTrigger value="usage">Usage Statistics</TabsTrigger>
        </TabsList>

        <TabsContent value="models" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Available Models</h2>
            <Button onClick={() => setShowAddForm(!showAddForm)}>
              {showAddForm ? "Cancel" : "Add New Model"}
            </Button>
          </div>

          {showAddForm && (
            <Card>
              <CardHeader>
                <CardTitle>Add New Model</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Model Name</Label>
                      <Input
                        id="name"
                        name="name"
                        value={newModel.name}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="provider">Provider</Label>
                      <Input
                        id="provider"
                        name="provider"
                        value={newModel.provider}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="context_length">Context Length</Label>
                      <Input
                        id="context_length"
                        name="context_length"
                        type="number"
                        value={newModel.context_length}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="max_tokens">Max Tokens</Label>
                      <Input
                        id="max_tokens"
                        name="max_tokens"
                        type="number"
                        value={newModel.max_tokens}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="cost_per_1k_tokens">
                        Cost per 1K Tokens
                      </Label>
                      <Input
                        id="cost_per_1k_tokens"
                        name="cost_per_1k_tokens"
                        type="number"
                        step="0.0001"
                        value={newModel.cost_per_1k_tokens}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit">Add Model</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {loading ? (
            <div className="text-center py-8">Loading models...</div>
          ) : models.length === 0 ? (
            <div className="text-center py-8">No models found</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {models.map((model) => (
                <Card key={model.id}>
                  <CardHeader>
                    <CardTitle className="flex justify-between items-center">
                      <span>{model.name}</span>
                      <Button
                        variant={model.is_active ? "destructive" : "default"}
                        size="sm"
                        onClick={() =>
                          toggleModelStatus(model.id, model.is_active)
                        }
                      >
                        {model.is_active ? "Deactivate" : "Activate"}
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="font-medium">Provider:</span>
                        <span>{model.provider}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Context Length:</span>
                        <span>{model.context_length.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Max Tokens:</span>
                        <span>{model.max_tokens.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Cost per 1K Tokens:</span>
                        <span>{formatCurrency(model.cost_per_1k_tokens)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="usage" className="space-y-4">
          <h2 className="text-2xl font-bold">Model Usage Statistics</h2>

          {usageData.length === 0 ? (
            <div className="text-center py-8">No usage data available</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {usageData.map((data) => (
                <Card key={data.model_id}>
                  <CardHeader>
                    <CardTitle>{data.model_name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="font-medium">Request Count:</span>
                        <span>{data.request_count.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Token Count:</span>
                        <span>{data.token_count.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Total Cost:</span>
                        <span>{formatCurrency(data.total_cost)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Models;
