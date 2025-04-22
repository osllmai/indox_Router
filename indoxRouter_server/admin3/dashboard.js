import { apiFetch } from "./api.js";
import {
  totalUsers,
  activeUsers,
  activeKeys,
  totalRequests,
  totalCost,
  totalTokens,
  providerChart,
  modelChart,
} from "./dom.js";

export function loadDashboardStats() {
  apiFetch("/admin/system/stats")
    .then((data) => {
      totalUsers.textContent = data.total_users || 0;
      activeUsers.textContent = data.active_users || 0;
      activeKeys.textContent = data.active_api_keys || 0;
      totalRequests.textContent = data.total_requests?.toLocaleString() || 0;
      totalCost.textContent = `$${(data.total_cost || 0).toFixed(2)}`;
      totalTokens.textContent = `${(data.total_tokens || 0).toLocaleString()}`;

      drawProviderChart(data.provider_stats || []);
      drawModelChart(data.model_stats || []);
    })
    .catch((error) => {
      console.error("Error loading dashboard stats:", error);
      alert("Failed to load dashboard stats. Please try again.");
    });
}

function drawProviderChart(data) {
  // Implement chart drawing logic here
}

function drawModelChart(data) {
  // Implement chart drawing logic here
}
