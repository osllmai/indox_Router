// IndoxRouter Admin Panel JavaScript

// Constants
const API_BASE_URL = "/api/v1";
const PAGE_SIZE = 10;

// Data storage
let usersData = [];
let apiKeysData = [];

// DOM Elements
const sidebar = document.querySelector(".sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const contentBody = document.querySelector(".content-body");
const navItems = document.querySelectorAll(".nav-item");
const pageTitle = document.getElementById("page-title");
const logoutBtn = document.getElementById("logout-btn");

// Page containers
const dashboardPage = document.getElementById("dashboard-page");
const usersPage = document.getElementById("users-page");
const apiKeysPage = document.getElementById("api-keys-page");
const usagePage = document.getElementById("usage-page");
const modelsPage = document.getElementById("models-page");
const endpointTesterPage = document.getElementById("endpoint-tester-page");

// User info
const userName = document.getElementById("user-name");
const userAvatar = document.getElementById("user-avatar");

// Dashboard stats
const totalUsers = document.getElementById("total-users");
const activeUsers = document.getElementById("active-users");
const activeKeys = document.getElementById("active-keys");
const totalRequests = document.getElementById("total-requests");
const totalCost = document.getElementById("total-cost");
const totalTokens = document.getElementById("total-tokens");

// Charts
const providerChart = document.querySelector("#provider-chart");
const modelChart = document.querySelector("#model-chart");

// Users page elements
const userSearch = document.getElementById("user-search");
const userSearchBtn = document.getElementById("user-search-btn");
const addUserBtn = document.getElementById("add-user-btn");
const usersTableBody = document.querySelector("#users-table tbody");
const prevPageBtn = document.getElementById("prev-page");
const nextPageBtn = document.getElementById("next-page");
const pageInfo = document.getElementById("page-info");

// User modal elements
const userModal = document.getElementById("user-modal");
const modalTitle = document.getElementById("modal-title");
const userForm = document.getElementById("user-form");
const saveUserBtn = document.getElementById("save-user");
const closeModalBtns = document.querySelectorAll(".close-modal, .cancel-btn");

// API Keys page elements
const apiKeySearch = document.querySelector("#api-key-search");
const apiKeySearchBtn = document.querySelector("#api-key-search-btn");
const addGlobalApiKeyBtn = document.getElementById("add-global-api-key-btn");

// Global variables
let currentPage = 1;
let userSearchTerm = "";
let apiKeySearchTerm = "";

// Utility functions
function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

function showLoading(element) {
  element.innerHTML = '<p class="loading">Loading...</p>';
}

function showError(element, message) {
  element.innerHTML = `<p class="error">Error: ${message}</p>`;
}

// API fetch wrapper
function apiFetch(endpoint, method = "GET", data = null) {
  const options = {
    method: method,
    headers: {
      Authorization: `Bearer ${localStorage.getItem("admin_api_key")}`,
      "Content-Type": "application/json",
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  return fetch(`${API_BASE_URL}${endpoint}`, options).then((response) => {
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    return response.json();
  });
}

// Navigation
function navigateTo(page) {
  // Update active nav item
  navItems.forEach((item) => {
    if (item.dataset.page === page) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  // Update page title
  pageTitle.textContent = page.charAt(0).toUpperCase() + page.slice(1);

  // Hide all pages
  document
    .querySelectorAll(".page")
    .forEach((p) => p.classList.remove("active"));

  // Show selected page
  document.getElementById(`${page}-page`).classList.add("active");

  // Load page-specific data
  switch (page) {
    case "dashboard":
      loadDashboardStats();
      break;
    case "users":
      loadUsers();
      break;
    case "api-keys":
      loadApiKeys();
      break;
    case "usage":
      loadUsageAnalytics();
      break;
    case "models":
      loadModels();
      break;
    case "endpoint-tester":
      setupEndpointTester();
      break;
  }
}

// Dashboard Stats
function loadDashboardStats() {
  apiFetch("/admin/system/stats")
    .then((data) => {
      totalUsers.textContent = data.total_users || 0;
      activeUsers.textContent = data.active_users || 0;
      activeKeys.textContent = data.active_api_keys || 0;
      totalRequests.textContent = data.total_requests?.toLocaleString() || 0;
      totalCost.textContent = `$${(data.total_cost || 0).toFixed(2)}`;
      totalTokens.textContent = `${(data.total_tokens || 0).toLocaleString()}`;

      // Example: Draw charts
      drawProviderChart(data.provider_stats || []);
      drawModelChart(data.model_stats || []);
    })
    .catch((error) => {
      console.error("Error loading dashboard stats:", error);
      alert("Failed to load dashboard stats. Please try again.");
    });
}

// Load Users
function loadUsers() {
  const skip = (currentPage - 1) * PAGE_SIZE;
  const endpoint = `/admin/users?skip=${skip}&limit=${PAGE_SIZE}${
    userSearchTerm ? `&search=${encodeURIComponent(userSearchTerm)}` : ""
  }`;

  apiFetch(endpoint)
    .then((users) => {
      if (users.length === 0 && currentPage > 1) {
        // If no users returned and not on first page, go back a page
        currentPage--;
        loadUsers();
        return;
      }

      usersTableBody.innerHTML = "";

      if (users.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="9" class="loading-row">No users found</td>`;
        usersTableBody.appendChild(tr);
      } else {
        users.forEach((user) => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${user.id}</td>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td>${user.first_name || ""} ${user.last_name || ""}</td>
            <td>${
              user.is_active
                ? '<span class="status active">Active</span>'
                : '<span class="status inactive">Inactive</span>'
            }</td>
            <td>$${user.credits.toFixed(2)}</td>
            <td>${user.account_tier}</td>
            <td>${new Date(user.created_at).toLocaleDateString()}</td>
            <td>
              <button class="action-btn edit" data-id="${
                user.id
              }"><i class="fas fa-edit"></i></button>
              <button class="action-btn delete" data-id="${
                user.id
              }"><i class="fas fa-trash"></i></button>
            </td>
          `;
          usersTableBody.appendChild(tr);
        });

        // Add edit handlers
        document.querySelectorAll(".action-btn.edit").forEach((btn) => {
          btn.addEventListener("click", () => {
            const userId = btn.dataset.id;
            openUserEditModal(userId);
          });
        });

        // Add delete handlers
        document.querySelectorAll(".action-btn.delete").forEach((btn) => {
          btn.addEventListener("click", () => {
            const userId = btn.dataset.id;
            if (confirm("Are you sure you want to delete this user?")) {
              deleteUser(userId);
            }
          });
        });
      }

      // Update pagination
      pageInfo.textContent = `Page ${currentPage}`;
      prevPageBtn.disabled = currentPage === 1;
      nextPageBtn.disabled = users.length < PAGE_SIZE;
    })
    .catch((error) => {
      console.error("Error loading users:", error);
      usersTableBody.innerHTML = `<tr><td colspan="9" class="loading-row">Error loading users. Please try again.</td></tr>`;
    });
}

// User Modal
function openUserEditModal(userId = null) {
  const isNewUser = !userId;
  modalTitle.textContent = isNewUser ? "Add User" : "Edit User";
  userForm.reset();

  // Configure form based on whether we're adding or editing
  document.getElementById("password-group").style.display = isNewUser
    ? "block"
    : "none";
  document.getElementById("initial-credits-group").style.display = isNewUser
    ? "block"
    : "none";
  document.getElementById("existing-credits-group").style.display = isNewUser
    ? "none"
    : "block";
  document.getElementById("add-credits-group").style.display = isNewUser
    ? "none"
    : "block";

  // Set required attribute on password field for new users
  document.getElementById("password").required = isNewUser;

  // Update save button text
  document.getElementById("save-user").textContent = isNewUser
    ? "Add User"
    : "Save Changes";

  if (userId) {
    // Edit existing user
    apiFetch(`/admin/users/${userId}`)
      .then((user) => {
        document.getElementById("user-id").value = user.id;
        document.getElementById("username").value = user.username;
        document.getElementById("email").value = user.email;
        document.getElementById("first-name").value = user.first_name || "";
        document.getElementById("last-name").value = user.last_name || "";
        document.getElementById("account-tier").value =
          user.account_tier || "free";
        document.getElementById("is-active").value = user.is_active
          ? "true"
          : "false";
        document.getElementById("credits").value = user.credits.toFixed(2);

        userModal.classList.add("active");
      })
      .catch((error) => {
        console.error("Error loading user:", error);
        alert("Failed to load user details. Please try again.");
      });
  } else {
    // Add new user - just show the modal with empty form
    userModal.classList.add("active");
  }
}

// Save user changes
function saveUser() {
  console.log("saveUser function called");
  const userId = document.getElementById("user-id").value;
  const isNewUser = !userId;

  if (isNewUser) {
    // Create new user
    const userData = {
      username: document.getElementById("username").value,
      email: document.getElementById("email").value,
      password: document.getElementById("password").value,
      first_name: document.getElementById("first-name").value,
      last_name: document.getElementById("last-name").value,
      account_tier: document.getElementById("account-tier").value,
      is_active: document.getElementById("is-active").value === "true",
      initial_credits:
        parseFloat(document.getElementById("initial-credits").value) || 0,
    };

    console.log(
      "Creating new user with data:",
      JSON.stringify(userData, null, 2)
    );

    // Show loading indicator on the button
    const saveButton = document.getElementById("save-user");
    const originalText = saveButton.textContent;
    saveButton.textContent = "Creating...";
    saveButton.disabled = true;

    apiFetch("/admin/users/create", "POST", userData)
      .then((response) => {
        console.log("User creation response:", response);
        if (response.status === "success" || response.id) {
          console.log("User created successfully");
          userModal.classList.remove("active");
          loadUsers();
          // Show success message
          alert("User created successfully!");
        } else {
          throw new Error(response.message || "Failed to create user");
        }
      })
      .catch((error) => {
        console.error("Error creating user:", error);
        alert(`Failed to create user: ${error.message || "Unknown error"}`);
      })
      .finally(() => {
        // Reset button state
        saveButton.textContent = originalText;
        saveButton.disabled = false;
      });
  } else {
    // Update existing user
    const userData = {
      first_name: document.getElementById("first-name").value,
      last_name: document.getElementById("last-name").value,
      email: document.getElementById("email").value,
      is_active: document.getElementById("is-active").value === "true",
      account_tier: document.getElementById("account-tier").value,
    };

    console.log("Updating user with data:", JSON.stringify(userData, null, 2));

    // Show loading indicator on the button
    const saveButton = document.getElementById("save-user");
    const originalText = saveButton.textContent;
    saveButton.textContent = "Saving...";
    saveButton.disabled = true;

    apiFetch(`/admin/users/${userId}`, "PUT", userData)
      .then((response) => {
        console.log("User update response:", response);
        if (response.status === "success") {
          // Handle credits if needed
          const addCredits = parseFloat(
            document.getElementById("add-credits").value
          );
          if (addCredits > 0) {
            console.log(`Adding ${addCredits} credits to user ${userId}`);
            return apiFetch(`/admin/users/${userId}/credits`, "POST", {
              amount: addCredits,
              payment_method: "admin_grant",
            });
          }
          return response;
        }
        throw new Error(response.message || "Failed to update user");
      })
      .then((response) => {
        console.log("Final response:", response);
        userModal.classList.remove("active");
        loadUsers();
        // Show success message
        alert("User updated successfully!");
      })
      .catch((error) => {
        console.error("Error saving user:", error);
        alert(`Failed to save user: ${error.message || "Unknown error"}`);
      })
      .finally(() => {
        // Reset button state
        saveButton.textContent = originalText;
        saveButton.disabled = false;
      });
  }
}

// Delete user
function deleteUser(userId) {
  apiFetch(`/admin/users/${userId}`, "DELETE")
    .then((response) => {
      if (response.status === "success") {
        loadUsers();
      } else {
        throw new Error("Failed to delete user");
      }
    })
    .catch((error) => {
      console.error("Error deleting user:", error);
      alert("Failed to delete user. Please try again.");
    });
}

// Draw example charts
function drawProviderChart(data) {
  // Placeholder for chart drawing
  // This would use Chart.js to render actual charts
  console.log("Would draw provider chart with:", data);
  document.querySelector("#provider-chart .loading").textContent =
    "Provider chart would render here";
}

function drawModelChart(data) {
  // Placeholder for chart drawing
  // This would use Chart.js to render actual charts
  console.log("Would draw model chart with:", data);
  document.querySelector("#model-chart .loading").textContent =
    "Model chart would render here";
}

// Load Models
function loadModels() {
  // Clear the models grid
  const modelsGrid = document.querySelector(".models-grid");
  if (!modelsGrid) {
    console.error("Models grid not found in DOM. Ensure .models-grid exists.");
    return;
  }
  modelsGrid.innerHTML = '<p class="loading">Loading models...</p>';

  // Fetch models with usage data from our MongoDB-backed endpoint
  apiFetch("/admin/models")
    .then((modelsData) => {
      modelsGrid.innerHTML = "";

      // Create an array of all models from all providers
      const allModels = [
        ...formatModelsWithUsage(modelsData.openai || [], "OpenAI"),
        ...formatModelsWithUsage(modelsData.mistral || [], "Mistral"),
        ...formatModelsWithUsage(modelsData.deepseek || [], "DeepSeek"),
      ];

      if (allModels.length === 0) {
        modelsGrid.innerHTML = '<p class="no-data">No models available</p>';
        return;
      }

      allModels.forEach((model) => {
        const modelCard = document.createElement("div");
        modelCard.className = "model-card";

        // Format costs for display
        const inputCost = formatCurrency(model.inputPricePer1KTokens);
        const outputCost = formatCurrency(model.outputPricePer1KTokens);
        const totalCost = formatCurrency(model.usage?.cost || 0);

        // Format tokens for display
        const inputTokens = (model.usage?.input_tokens || 0).toLocaleString();
        const outputTokens = (model.usage?.output_tokens || 0).toLocaleString();
        const totalTokens = (model.usage?.total_tokens || 0).toLocaleString();

        modelCard.innerHTML = `
          <div class="model-card-header">
            <h3>${model.name}</h3>
            <span class="model-provider">${model.providerName}</span>
          </div>
          <div class="model-description">
            <p>${model.description || "No description available"}</p>
          </div>
          <div class="model-card-stats">
            <div class="model-stat">
              <span class="stat-label">Requests</span>
              <span class="stat-value">${(
                model.usage?.requests || 0
              ).toLocaleString()}</span>
            </div>
            <div class="model-stat">
              <span class="stat-label">Tokens</span>
              <span class="stat-value">${totalTokens}</span>
            </div>
            <div class="model-stat">
              <span class="stat-label">Cost</span>
              <span class="stat-value">${totalCost}</span>
            </div>
          </div>
          <div class="model-details">
            <div class="model-detail"><span>Type:</span> ${model.type}</div>
            <div class="model-detail"><span>Context:</span> ${
              model.contextWindows
            }</div>
            <div class="model-detail"><span>Input Price:</span> ${inputCost} per 1K tokens</div>
            <div class="model-detail"><span>Output Price:</span> ${outputCost} per 1K tokens</div>
          </div>
          <div class="model-card-footer">
            <span class="model-id">${model.modelName}</span>
          </div>
        `;

        modelsGrid.appendChild(modelCard);
      });
    })
    .catch((error) => {
      console.error("Error loading models:", error);
      fetch(`${API_BASE_URL}/admin/models`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("admin_api_key")}`,
          "Content-Type": "application/json",
        },
      })
        .then((resp) => resp.text())
        .then((text) => {
          console.error("Raw error response for models:", text);
          modelsGrid.innerHTML = `<p class="error">Error loading models: ${
            text || error.message || "Unknown error"
          }</p>`;
        })
        .catch((err) => {
          modelsGrid.innerHTML =
            '<p class="error">Error loading models. Please try again.</p>';
        });
    });
}

// Helper function to format models with usage data
function formatModelsWithUsage(models, providerName) {
  if (!Array.isArray(models)) return [];

  return models
    .filter((model) => model.recommended !== false) // Only include recommended models
    .map((model) => ({
      ...model,
      providerName: providerName,
    }));
}

// Function to load API keys
function loadApiKeys(page = 1, searchTerm = apiKeySearchTerm) {
  console.log("Loading API keys...");
  const limit = PAGE_SIZE;
  const offset = (page - 1) * limit;

  let url = `/admin/api-keys?limit=${limit}&offset=${offset}`;
  if (searchTerm) {
    url += `&search=${encodeURIComponent(searchTerm)}`;
  }

  apiFetch(url)
    .then((data) => {
      apiKeysData = data;

      // Get the table body
      const tableBody = document.querySelector(
        "#api-keys-page .table-container"
      );

      // If no table exists yet, create one
      if (!document.getElementById("api-keys-table")) {
        const tableHtml = `
          <table id="api-keys-table" class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Name</th>
                <th>API Key</th>
                <th>Status</th>
                <th>Created</th>
                <th>Last Used</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        `;
        tableBody.innerHTML = tableHtml;
      }

      const tbody = document.querySelector("#api-keys-table tbody");

      // Clear existing rows
      tbody.innerHTML = "";

      if (data.length === 0) {
        const emptyRow = document.createElement("tr");
        emptyRow.innerHTML = `
          <td colspan="8" class="text-center">No API keys found</td>
        `;
        tbody.appendChild(emptyRow);
        return;
      }

      // Add rows for each API key
      data.forEach((key) => {
        const row = document.createElement("tr");

        // Mask the API key, showing only first 4 and last 4 characters
        const maskedKey = key.key
          ? `${key.key.substring(0, 4)}...${key.key.substring(
              key.key.length - 4
            )}`
          : "(hidden)";

        row.innerHTML = `
          <td>${key.id}</td>
          <td>${key.user ? key.user.username : "N/A"}</td>
          <td>${key.name || "Default"}</td>
          <td><code>${maskedKey}</code></td>
          <td><span class="status ${key.active ? "active" : "inactive"}">${
          key.active ? "Active" : "Inactive"
        }</span></td>
          <td>${formatDate(key.created_at)}</td>
          <td>${key.last_used_at ? formatDate(key.last_used_at) : "Never"}</td>
          <td>
            <button class="action-btn copy" data-key="${
              key.id
            }" title="Copy API Key">
              <i class="fas fa-copy"></i>
            </button>
            ${
              key.active
                ? `<button class="action-btn revoke" data-key="${key.id}" title="Revoke API Key">
                <i class="fas fa-ban"></i>
              </button>`
                : ""
            }
          </td>
        `;

        tbody.appendChild(row);
      });

      // Add event listeners for copy and revoke buttons
      document.querySelectorAll(".action-btn.copy").forEach((btn) => {
        btn.addEventListener("click", () => {
          const keyId = btn.getAttribute("data-key");
          copyApiKey(keyId);
        });
      });

      document.querySelectorAll(".action-btn.revoke").forEach((btn) => {
        btn.addEventListener("click", () => {
          const keyId = btn.getAttribute("data-key");
          revokeApiKey(keyId);
        });
      });
    })
    .catch((error) => {
      console.error("Error loading API keys:", error);
      // Display error message
      const tableBody = document.querySelector(
        "#api-keys-page .table-container"
      );
      tableBody.innerHTML = `<div class="error-message">Error loading API keys: ${
        error.message || "Unknown error"
      }</div>`;
    });
}

// Function to copy API key to clipboard
function copyApiKey(keyId) {
  const key = apiKeysData.find((k) => k.id === keyId);
  if (key && key.key) {
    navigator.clipboard
      .writeText(key.key)
      .then(() => {
        alert("API Key copied to clipboard");
      })
      .catch((err) => {
        console.error("Error copying API key:", err);
        alert("Failed to copy API key");
      });
  } else {
    alert("API Key not available for copying");
  }
}

// Function to revoke an API key
function revokeApiKey(keyId) {
  if (
    !confirm(
      "Are you sure you want to revoke this API key? This action cannot be undone."
    )
  ) {
    return;
  }

  const key = apiKeysData.find((k) => k.id === keyId);
  if (!key || !key.user) {
    alert("User information not available for this key");
    return;
  }

  apiFetch(`/admin/users/${key.user.id}/api-keys/${keyId}/revoke`, {
    method: "POST",
  })
    .then(() => {
      alert("API Key revoked successfully");
      loadApiKeys(); // Reload the API keys
    })
    .catch((error) => {
      console.error("Error revoking API key:", error);
      alert("Failed to revoke API key: " + (error.message || "Unknown error"));
    });
}

// Function to create an API key for a user
function createApiKey(userId, keyName) {
  const payload = {
    name: keyName || "Admin Generated Key",
  };
  console.log("Creating API key with payload:", payload);
  apiFetch(`/admin/users/${userId}/api-keys`, "POST", payload)
    .then((response) => {
      // Show the newly created key to the user
      alert(`API Key created successfully: ${response.api_key}`);
      loadApiKeys(); // Reload the API keys
    })
    .catch((error) => {
      console.error("Error creating API key:", error);
      // Attempt to parse error detail from response if available
      fetch(`${API_BASE_URL}/admin/users/${userId}/api-keys`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("admin_api_key")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then((resp) => resp.text())
        .then((text) => {
          console.error("Raw error response:", text);
          alert(
            "Failed to create API key: " +
              (text || error.message || "Unknown error")
          );
        })
        .catch((err) => {
          alert(
            "Failed to create API key: " + (error.message || "Unknown error")
          );
        });
    });
}

// Load Usage Analytics
function loadUsageAnalytics() {
  const usageContainer = document.querySelector("#usage-page .usage-charts");
  if (!usageContainer) {
    console.error(
      "Usage container not found in DOM. Ensure #usage-page .usage-charts exists."
    );
    return;
  }
  showLoading(usageContainer);

  console.log("Fetching usage analytics data...");
  // Fetch analytics data from the backend
  apiFetch("/admin/analytics")
    .then((response) => {
      console.log("Received usage analytics response:", response);
      usageContainer.innerHTML = "";
      if (!response.data || response.data.length === 0) {
        usageContainer.innerHTML =
          '<p class="no-data">No usage data available</p>';
        return;
      }

      // Create a summary section for key statistics
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

      // Create sections for different views of the data
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

      // Process data for different views
      // Display a detailed table with the raw data
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
        console.log("Rendering item:", item);
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

      // Optionally, add filters if provided by the response
      if (response.filters) {
        const filtersDiv = document.createElement("div");
        filtersDiv.className = "filters-info";
        filtersDiv.innerHTML = `
          <p>Filters Applied: Start Date - ${response.filters.start_date}, End Date - ${response.filters.end_date}</p>
        `;
        usageContainer.insertBefore(filtersDiv, overTimeDiv);
      }

      // Render charts using Chart.js
      renderUsageOverTimeChart(response.data);
      renderCostOverTimeChart(response.data);
      renderRequestsByProviderChart(response.data);
      renderTokensByProviderChart(response.data);
      renderLatencyByProviderChart(response.data);
      renderTopModelsChart(response.data);
    })
    .catch((error) => {
      console.error("Error loading usage analytics:", error);
      fetch(`${API_BASE_URL}/admin/analytics`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("admin_api_key")}`,
          "Content-Type": "application/json",
        },
      })
        .then((resp) => resp.text())
        .then((text) => {
          console.error("Raw error response for analytics:", text);
          showError(
            usageContainer,
            "Failed to load usage data: " +
              (text || error.message || "Unknown error")
          );
        })
        .catch((err) => {
          showError(
            usageContainer,
            "Failed to load usage data. Please try again."
          );
        });
    });
}

// Function to render Usage Over Time chart
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

// Function to render Cost Over Time chart
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

// Function to render Requests by Provider chart
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

// Function to render Tokens by Provider chart
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

// Function to render Avg Latency by Provider chart
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

// Function to render Top Models by Requests chart
function renderTopModelsChart(data) {
  const ctx = document.getElementById("topModelsChart").getContext("2d");
  // Sort data by request count and take top 5
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

// Event Listeners
window.addEventListener("load", init);

navItems.forEach((item) => {
  item.addEventListener("click", () => {
    navigateTo(item.dataset.page);
  });
});

sidebarToggle.addEventListener("click", () => {
  sidebar.classList.toggle("active");
});

userSearchBtn.addEventListener("click", () => {
  userSearchTerm = userSearch.value.trim();
  currentPage = 1;
  loadUsers();
});

userSearch.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    userSearchTerm = userSearch.value.trim();
    currentPage = 1;
    loadUsers();
  }
});

prevPageBtn.addEventListener("click", () => {
  if (currentPage > 1) {
    currentPage--;
    loadUsers();
  }
});

nextPageBtn.addEventListener("click", () => {
  currentPage++;
  loadUsers();
});

// Make sure all elements are properly initialized on page load
function init() {
  // Check if logged in
  if (!localStorage.getItem("admin_api_key")) {
    window.location.href = "/admin/login.html";
    return;
  }

  // Set user info if available
  const storedUserName = localStorage.getItem("admin_user_name");
  const storedAvatar = localStorage.getItem("admin_user_avatar");
  if (storedUserName) {
    userName.textContent = storedUserName;
  }
  if (storedAvatar) {
    userAvatar.src = storedAvatar;
  }

  // Make sure all event listeners are properly set
  setupEventListeners();

  // Load initial page
  navigateTo("dashboard");
}

// Setup all event listeners in one place to ensure they are all attached
function setupEventListeners() {
  console.log("Setting up event listeners");

  // Add User button - make sure this gets attached
  if (addUserBtn) {
    console.log("Add User button found, attaching click listener");
    // Remove any existing event listeners first
    addUserBtn.removeEventListener("click", openAddUserModal);
    // Then add the new one
    addUserBtn.addEventListener("click", openAddUserModal);
  } else {
    console.error("Add User button not found!");
  }

  // Function to open the global create API key modal
  function openGlobalCreateApiKeyModal() {
    console.log("Opening global API key modal");
    // First get the list of users to populate a select dropdown
    apiFetch("/admin/users?limit=100")
      .then((users) => {
        if (!users.length) {
          alert("No users found. Please create a user first.");
          return;
        }

        // Store users for filtering
        let filteredUsers = users;

        // Create options for select dropdown
        const updateUserOptions = (userList) => {
          return userList
            .map(
              (user) =>
                `<option value="${user.id}">${user.username} (${user.email})</option>`
            )
            .join("");
        };

        // Show a modal dialog with user selection and search
        const modalHtml = `
        <div class="modal api-key-modal active">
          <div class="modal-content">
            <div class="modal-header">
              <h2>Create New API Key</h2>
              <button class="close-modal" id="close-api-key-modal">&times;</button>
            </div>
            <div class="modal-body">
              <form id="api-key-form">
                <div class="form-group">
                  <label for="user-search-modal">Search User:</label>
                  <input type="text" id="user-search-modal" placeholder="Search by username or email..." />
                </div>
                <div class="form-group">
                  <label for="key-user-id">User:</label>
                  <select id="key-user-id" required>
                    <option value="">-- Select User --</option>
                    ${updateUserOptions(filteredUsers)}
                  </select>
                </div>
                <div class="form-group">
                  <label for="key-name">API Key Name:</label>
                  <input type="text" id="key-name" value="API Key" required />
                </div>
              </form>
            </div>
            <div class="modal-footer">
              <button id="create-api-key-btn" class="primary-btn">Create API Key</button>
              <button id="cancel-api-key-btn" class="cancel-btn">Cancel</button>
            </div>
          </div>
        </div>
      `;

        // Add the modal to the document
        const modalContainer = document.createElement("div");
        modalContainer.innerHTML = modalHtml;
        document.body.appendChild(modalContainer);

        // Add event listeners
        document
          .getElementById("close-api-key-modal")
          .addEventListener("click", () => {
            document.body.removeChild(modalContainer);
          });

        document
          .getElementById("cancel-api-key-btn")
          .addEventListener("click", () => {
            document.body.removeChild(modalContainer);
          });

        // Add search functionality for users in modal
        document
          .getElementById("user-search-modal")
          .addEventListener("input", (e) => {
            const searchTerm = e.target.value.toLowerCase();
            filteredUsers = users.filter(
              (user) =>
                user.username.toLowerCase().includes(searchTerm) ||
                user.email.toLowerCase().includes(searchTerm)
            );
            const select = document.getElementById("key-user-id");
            select.innerHTML = `<option value="">-- Select User --</option>${updateUserOptions(
              filteredUsers
            )}`;
          });

        document
          .getElementById("create-api-key-btn")
          .addEventListener("click", () => {
            const userId = document.getElementById("key-user-id").value;
            const keyName = document.getElementById("key-name").value;

            if (!userId) {
              alert("Please select a user");
              return;
            }

            createApiKey(userId, keyName);
            document.body.removeChild(modalContainer);
          });
      })
      .catch((error) => {
        console.error("Error fetching users:", error);
        alert("Error fetching users. Please try again.");
      });
  }

  // Add Global API Key button
  const addGlobalApiKeyBtn = document.getElementById("add-global-api-key-btn");
  if (addGlobalApiKeyBtn) {
    addGlobalApiKeyBtn.removeEventListener(
      "click",
      openGlobalCreateApiKeyModal
    );
    addGlobalApiKeyBtn.addEventListener("click", openGlobalCreateApiKeyModal);
  }

  // Save User button
  if (saveUserBtn) {
    console.log("Save User button found, attaching click listener");
    // Remove any existing event listeners first
    saveUserBtn.removeEventListener("click", saveUser);
    // Then add the new one
    saveUserBtn.addEventListener("click", saveUser);
  } else {
    console.error("Save User button not found!");
  }

  // Close modal buttons
  closeModalBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      userModal.classList.remove("active");
    });
  });

  // API Key Search button
  if (apiKeySearchBtn) {
    apiKeySearchBtn.addEventListener("click", () => {
      apiKeySearchTerm = apiKeySearch.value.trim();
      loadApiKeys(1, apiKeySearchTerm);
    });
  }

  // API Key Search input (Enter key)
  if (apiKeySearch) {
    apiKeySearch.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        apiKeySearchTerm = apiKeySearch.value.trim();
        loadApiKeys(1, apiKeySearchTerm);
      }
    });
  }
}

// Function specifically for opening the Add User modal
function openAddUserModal() {
  console.log("openAddUserModal called");
  openUserEditModal(null);
}

// Logout
logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("admin_api_key");
  localStorage.removeItem("admin_user_name");
  localStorage.removeItem("admin_user_avatar");
  window.location.href = "/admin/login.html";
});
