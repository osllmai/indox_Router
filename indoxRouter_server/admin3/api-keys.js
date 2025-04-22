import { apiFetch } from "./api.js";
import {
  apiKeysPage,
  apiKeySearch,
  apiKeySearchBtn,
  addGlobalApiKeyBtn,
} from "./dom.js";
import { formatDate, showError } from "./utils.js";
import { PAGE_SIZE } from "./constants.js";

let apiKeysData = [];
let apiKeySearchTerm = "";

export function loadApiKeys(page = 1, searchTerm = apiKeySearchTerm) {
  const limit = PAGE_SIZE;
  const offset = (page - 1) * limit;

  let url = `/admin/api-keys?limit=${limit}&offset=${offset}`;
  if (searchTerm) {
    url += `&search=${encodeURIComponent(searchTerm)}`;
  }

  const tableBody = document.querySelector("#api-keys-page .table-container");
  tableBody.innerHTML = '<div class="loading">Loading...</div>';

  apiFetch(url)
    .then((data) => {
      apiKeysData = data;

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
      tbody.innerHTML = "";

      if (data.length === 0) {
        const emptyRow = document.createElement("tr");
        emptyRow.innerHTML = `<td colspan="8" class="text-center">No API keys found</td>`;
        tbody.appendChild(emptyRow);
        return;
      }

      data.forEach((key) => {
        const row = document.createElement("tr");
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

      document.querySelectorAll(".action-btn.copy").forEach((btn) => {
        btn.addEventListener("click", () => {
          const keyId = btn.getAttribute("data-key");
          copyApiKey(keyId);
        });
      });

      document.querySelectorAll(". suivreaction-btn.revoke").forEach((btn) => {
        btn.addEventListener("click", () => {
          const keyId = btn.getAttribute("data-key");
          revokeApiKey(keyId);
        });
      });
    })
    .catch((error) => {
      console.error("Error loading API keys:", error);
      showError(
        tableBody,
        `Error loading API keys: ${error.message || "Unknown error"}`
      );
    });
}

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
      loadApiKeys();
    })
    .catch((error) => {
      console.error("Error revoking API key:", error);
      alert("Failed to revoke API key: " + (error.message || "Unknown error"));
    });
}

export function createApiKey(userId, keyName) {
  const payload = {
    name: keyName || "Admin Generated Key",
  };
  apiFetch(`/admin/users/${userId}/api-keys`, "POST", payload)
    .then((response) => {
      alert(`API Key created successfully: ${response.api_key}`);
      loadApiKeys();
    })
    .catch((error) => {
      console.error("Error creating API key:", error);
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
        .catch(() => {
          alert(
            "Failed to create API key: " + (error.message || "Unknown error")
          );
        });
    });
}

function openGlobalCreateApiKeyModal() {
  apiFetch("/admin/users?limit=100")
    .then((users) => {
      if (!users.length) {
        alert("No users found. Please create a user first.");
        return;
      }

      let filteredUsers = users;

      const updateUserOptions = (userList) => {
        return userList
          .map(
            (user) =>
              `<option value="${user.id}">${user.username} (${user.email})</option>`
          )
          .join("");
      };

      const modalHtml = `
        <div class="modal api-key-modal active">
          <div class="modal-content">
            <div class="modal-header">
              <h2>Create New API Key</h2>
              <button class="close-modal" id="close-api-key-modal">×</button>
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

      const modalContainer = document.createElement("div");
      modalContainer.innerHTML = modalHtml;
      document.body.appendChild(modalContainer);

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

export function setupApiKeyEventListeners() {
  apiKeySearchBtn.addEventListener("click", () => {
    const searchTerm = apiKeySearch.value.trim();
    loadApiKeys(1, searchTerm);
  });

  addGlobalApiKeyBtn.addEventListener("click", openGlobalCreateApiKeyModal);
}
