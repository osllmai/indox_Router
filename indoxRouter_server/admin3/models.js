import { apiFetch } from "./api.js";
import { formatCurrency, showLoading, showError } from "./utils.js";

export function loadUsageAnalytics() {
  const usageContainer = document.querySelector("#usage-page .usage-charts");
  if (!usageContainer) {
    console.error("Usage container not found in DOM.");
    return;
  }
  showLoading(usageContainer);

  apiFetch("/admin/analytics")
    .then((response) => {
      usageContainer.innerHTML = "";
      if (!response.data || response.data.length === 0) {
        usageContainer.innerHTML =
          '<p class="no-data">No usage data available</p>';
        return;
      }

      const summaryDiv = document.createElement("div");
      summaryDiv.className = "usage-summary";
      summaryDiv.innerHTML = `
        <h3>Usage Summary</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <i class="fas fa-exchange-alt stat-icon"></i>
            <div class="stat-content">
              <h3>Total Requests</h3>
              <p>${response.data
                .reduce((sum, item) => sum + (item.count || 0), 0)
                .toLocaleString()}</p>
            </div>
          </div>
          <div class="stat-card">
            <i class="fas fa-coins stat-icon"></i>
            <div class="stat-content">
              <h3>Total Cost</h3>
              <p>${formatCurrency(
                response.data.reduce(
                  (sum, item) => sum + (item.total_cost || 0),
                  0
                )
              )}</p>
            </div>
          </div>
          <div class="stat-card">
            <i class="fas fa-file-alt stat-icon"></i>
            <div class="stat-content">
              <h3>Total Tokens</h3>
              <p>${response.data
                .reduce((sum, item) => sum + (item.total_tokens || 0), 0)
                .toLocaleString()}</p>
            </div>
          </div>
          <div class="stat-card">
            <i class="fas fa-clock stat-icon"></i>
            <div class="stat-content">
              <h3>Avg Latency</h3>
              <p>${(
                response.data.reduce(
                  (sum, item) => sum + (item.avg_latency || 0),
                  0
                ) / response.data.length
              ).toFixed(2)}s</p>
            </div>
          </div>
        </div>
      `;
      usageContainer.appendChild(summaryDiv);

      const overTimeDiv = document.createElement("div");
      overTimeDiv.className = "chart-card full-width";
      overTimeDiv.innerHTML =
        '<h3>Usage Over Time</h3><canvas id="usageOverTimeChart" width="800" height="300"></canvas>';
      usageContainer.appendChild(overTimeDiv);

      const costOverTimeDiv = document.createElement("div");
      costOverTimeDiv.className = "chart-card full-width";
      costOverTimeDiv.innerHTML =
        '<h3>Cost Over Time</h3><canvas id="costOverTimeChart" width="800" height="300"></canvas>';
      usageContainer.appendChild(costOverTimeDiv);

      const byProviderDiv = document.createElement("div");
      byProviderDiv.className = "chart-card";
      byProviderDiv.innerHTML =
        '<h3>Requests by Provider</h3><canvas id="requestsByProviderChart" width="400" height="200"></canvas>';
      usageContainer.appendChild(byProviderDiv);

      const tokensByProviderDiv = document.createElement("div");
      tokensByProviderDiv.className = "chart-card";
      tokensByProviderDiv.innerHTML =
        '<h3>Tokens by Provider</h3><canvas id="tokensByProviderChart" width="400" height="200"></canvas>';
      usageContainer.appendChild(tokensByProviderDiv);

      const latencyByProviderDiv = document.createElement("div");
      latencyByProviderDiv.className = "chart-card";
      latencyByProviderDiv.innerHTML =
        '<h3>Avg Latency by Provider</h3><canvas id="latencyByProviderChart" width="400" height="200"></canvas>';
      usageContainer.appendChild(latencyByProviderDiv);

      const topModelsDiv = document.createElement("div");
      topModelsDiv.className = "chart-card";
      topModelsDiv.innerHTML =
        '<h3>Top Models by Requests</h3><canvas id="topModelsChart" width="400" height="200"></canvas>';
      usageContainer.appendChild(topModelsDiv);

      const table = document.createElement("table");
      table.className = "data-table";
      table.innerHTML = `
        <thead>
          <tr>
            <th>Group Value</th>
            <th>Requests</th>
            <th>Total Cost</th>
            <th>Prompt Tokens</th>
            <th>Completion Tokens</th>
            <th>Total Tokens</th>
            <th>Avg Latency (s)</th>
          </tr>
        </thead>
        <tbody></tbody>
      `;
      usageContainer.appendChild(table);

      const tbody = table.querySelector("tbody");
      response.data.forEach((item) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${item.group_value || "N/A"}</td>
          <td>${item.count || 0}</td>
          <td>${formatCurrency(item.total_cost || 0)}</td>
          <td>${item.total_tokens_prompt || 0}</td>
          <td>${item.total_tokens_completion || 0}</td>
          <td>${item.total_tokens || 0}</td>
          <td>${(item.avg_latency || 0).toFixed(2)}</td>
        `;
        tbody.appendChild(row);
      });

      if (response.filters) {
        const filtersDiv = document.createElement("div");
        filtersDiv.className = "filters-info";
        filtersDiv.innerHTML = `
          <p>Filters Applied: Start Date - ${response.filters.start_date}, End Date - ${response.filters.end_date}</p>
        `;
        usageContainer.insertBefore(filtersDiv, overTimeDiv);
      }

      renderUsageOverTimeChart(response.data);
      renderCostOverTimeChart(response.data);
      renderRequestsByProviderChart(response.data);
      renderTokensByProviderChart(response.data);
      renderLatencyByProviderChart(response.data);
      renderTopModelsChart(response.data);
    })
    .catch((error) => {
      console.error("Error loading usage analytics:", error);
      showError(usageContainer, "Failed to load usage data. Please try again.");
    });
}

function renderUsageOverTimeChart(data) {
  const ctx = document.getElementById("usageOverTimeChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.map((item) => item.group_value || "N/A"),
      datasets: [
        {
          label: "Total Tokens",
          data: data.map((item) => item.total_tokens || 0),
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderWidth: 2,
          fill: true,
        },
        {
          label: "Prompt Tokens",
          data: data.map((item) => item.total_tokens_prompt || 0),
          borderColor: "rgba(255, 99, 132, 1)",
          backgroundColor: "rgba(255, 99, 132, 0.1)",
          borderWidth: 2,
          fill: true,
        },
        {
          label: "Completion Tokens",
          data: data.map((item) => item.total_tokens_completion || 0),
          borderColor: "rgba(54, 162, 235, 1)",
          backgroundColor: "rgba(54, 162, 235, 0.1)",
          borderWidth: 2,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Tokens",
          },
          ticks: {
            maxTicksLimit: 8,
          },
        },
        x: {
          title: {
            display: true,
            text: "Date/Provider/Model",
          },
        },
      },
      plugins: {
        legend: {
          position: "top",
        },
      },
    },
  });
}

function renderCostOverTimeChart(data) {
  const ctx = document.getElementById("costOverTimeChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.map((item) => item.group_value || "N/A"),
      datasets: [
        {
          label: "Total Cost",
          data: data.map((item) => item.total_cost || 0),
          borderColor: "rgba(255, 159, 64, 1)",
          backgroundColor: "rgba(255, 159, 64, 0.2)",
          borderWidth: 2,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Cost (USD)",
          },
          ticks: {
            maxTicksLimit: 8,
            callback: function (value) {
              return "$" + value.toFixed(2);
            },
          },
        },
        x: {
          title: {
            display: true,
            text: "Date/Provider/Model",
          },
        },
      },
      plugins: {
        legend: {
          position: "top",
        },
      },
    },
  });
}

function renderRequestsByProviderChart(data) {
  const ctx = document
    .getElementById("requestsByProviderChart")
    .getContext("2d");
  const providers = Array.from(
    new Set(data.map((item) => item.group_value || "N/A"))
  );
  const counts = providers.map((provider) => {
    const item = data.find((d) => d.group_value === provider);
    return item ? item.count || 0 : 0;
  });

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: providers,
      datasets: [
        {
          label: "Request Count",
          data: counts,
          backgroundColor: "rgba(54, 162, 235, 0.5)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Requests",
          },
        },
        x: {
          title: {
            display: true,
            text: "Provider",
          },
        },
      },
      plugins: {
        legend: {
          position: "top",
        },
      },
    },
  });
}

function renderTokensByProviderChart(data) {
  const ctx = document.getElementById("tokensByProviderChart").getContext("2d");
  const providers = Array.from(
    new Set(data.map((item) => item.group_value || "N/A"))
  );
  const promptTokens = providers.map((provider) => {
    const item = data.find((d) => d.group_value === provider);
    return item ? item.total_tokens_prompt || 0 : 0;
  });
  const completionTokens = providers.map((provider) => {
    const item = data.find((d) => d.group_value === provider);
    return item ? item.total_tokens_completion || 0 : 0;
  });

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: providers,
      datasets: [
        {
          label: "Prompt Tokens",
          data: promptTokens,
          backgroundColor: "rgba(255, 99, 132, 0.5)",
          borderColor: "rgba(255, 99, 132, 1)",
          borderWidth: 1,
        },
        {
          label: "Completion Tokens",
          data: completionTokens,
          backgroundColor: "rgba(75, 192, 192, 0.5)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          stacked: true,
          title: {
            display: true,
            text: "Tokens",
          },
        },
        x: {
          stacked: true,
          title: {
            display: true,
            text: "Provider",
          },
        },
      },
      plugins: {
        legend: {
          position: "top",
        },
      },
    },
  });
}

function renderLatencyByProviderChart(data) {
  const ctx = document
    .getElementById("latencyByProviderChart")
    .getContext("2d");
  const providers = Array.from(
    new Set(data.map((item) => item.group_value || "N/A"))
  );
  const latencies = providers.map((provider) => {
    const item = data.find((d) => d.group_value === provider);
    return item ? item.avg_latency || 0 : 0;
  });

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: providers,
      datasets: [
        {
          label: "Avg Latency (s)",
          data: latencies,
          backgroundColor: "rgba(255, 205, 86, 0.5)",
          borderColor: "rgba(255, 205, 86, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Latency (seconds)",
          },
        },
        x: {
          title: {
            display: true,
            text: "Provider",
          },
        },
      },
      plugins: {
        legend: {
          position: "top",
        },
      },
    },
  });
}

function renderTopModelsChart(data) {
  const ctx = document.getElementById("topModelsChart").getContext("2d");
  const sortedData = data
    .sort((a, b) => (b.count || 0) - (a.count || 0))
    .slice(0, 5);
  const labels = sortedData.map((item) => item.group_value || "N/A");
  const counts = sortedData.map((item) => item.count || 0);

  new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Requests",
          data: counts,
          backgroundColor: [
            "rgba(255, 99, 132, 0.5)",
            "rgba(54, 162, 235, 0.5)",
            "rgba(255, 206, 86, 0.5)",
            "rgba(75, 192, 192, 0.5)",
            "rgba(153, 102, 255, 0.5)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              let label = context.label || "";
              if (label) {
                label += ": ";
              }
              label += context.raw.toLocaleString();
              return label;
            },
          },
        },
      },
    },
  });
}

export function loadModels() {
  apiFetch("/admin/models")
    .then((models) => {
      // Render models in the UI
    })
    .catch((error) => {
      console.error("Error loading models:", error);
      alert("Failed to load models. Please try again.");
    });
}
