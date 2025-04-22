import { apiFetch } from "./api.js";
import {
  usersTableBody,
  userModal,
  modalTitle,
  userForm,
  saveUserBtn,
  closeModalBtns,
  userSearch,
  userSearchBtn,
  addUserBtn,
  prevPageBtn,
  nextPageBtn,
  pageInfo,
} from "./dom.js";
import { formatDate, showLoading, showError } from "./utils.js";
import { PAGE_SIZE } from "./constants.js";

let usersData = [];
let currentPage = 1;
let userSearchTerm = "";

export function loadUsers() {
  const skip = (currentPage - 1) * PAGE_SIZE;
  const endpoint = `/admin/users?skip=${skip}&limit=${PAGE_SIZE}${
    userSearchTerm ? `&search=${encodeURIComponent(userSearchTerm)}` : ""
  }`;

  showLoading(usersTableBody);

  apiFetch(endpoint)
    .then((users) => {
      if (users.length === 0 && currentPage > 1) {
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

        document.querySelectorAll(".action-btn.edit").forEach((btn) => {
          btn.addEventListener("click", () => {
            const userId = btn.dataset.id;
            openUserEditModal(userId);
          });
        });

        document.querySelectorAll(".action-btn.delete").forEach((btn) => {
          btn.addEventListener("click", () => {
            const userId = btn.dataset.id;
            if (confirm("Are you sure you want to delete this user?")) {
              deleteUser(userId);
            }
          });
        });
      }

      pageInfo.textContent = `Page ${currentPage}`;
      prevPageBtn.disabled = currentPage === 1;
      nextPageBtn.disabled = users.length < PAGE_SIZE;
    })
    .catch((error) => {
      console.error("Error loading users:", error);
      showError(usersTableBody, "Error loading users. Please try again.");
    });
}

export function openUserEditModal(userId = null) {
  const isNewUser = !userId;
  modalTitle.textContent = isNewUser ? "Add User" : "Edit User";
  userForm.reset();

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

  document.getElementById("password").required = isNewUser;
  saveUserBtn.textContent = isNewUser ? "Add User" : "Save Changes";

  if (userId) {
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
    userModal.classList.add("active");
  }
}

function saveUser() {
  const userId = document.getElementById("user-id").value;
  const isNewUser = !userId;

  if (isNewUser) {
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

    const originalText = saveUserBtn.textContent;
    saveUserBtn.textContent = "Creating...";
    saveUserBtn.disabled = true;

    apiFetch("/admin/users/create", "POST", userData)
      .then((response) => {
        if (response.status === "success" || response.id) {
          userModal.classList.remove("active");
          loadUsers();
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
        saveUserBtn.textContent = originalText;
        saveUserBtn.disabled = false;
      });
  } else {
    const userData = {
      first_name: document.getElementById("first-name").value,
      last_name: document.getElementById("last-name").value,
      email: document.getElementById("email").value,
      is_active: document.getElementById("is-active").value === "true",
      account_tier: document.getElementById("account-tier").value,
    };

    const originalText = saveUserBtn.textContent;
    saveUserBtn.textContent = "Saving...";
    saveUserBtn.disabled = true;

    apiFetch(`/admin/users/${userId}`, "PUT", userData)
      .then((response) => {
        if (response.status === "success") {
          const addCredits = parseFloat(
            document.getElementById("add-credits").value
          );
          if (addCredits > 0) {
            return apiFetch(`/admin/users/${userId}/credits`, "POST", {
              amount: addCredits,
              payment_method: "admin_grant",
            });
          }
          return response;
        }
        throw new Error(response.message || "Failed to update user");
      })
      .then(() => {
        userModal.classList.remove("active");
        loadUsers();
        alert("User updated successfully!");
      })
      .catch((error) => {
        console.error("Error saving user:", error);
        alert(`Failed to save user: ${error.message || "Unknown error"}`);
      })
      .finally(() => {
        saveUserBtn.textContent = originalText;
        saveUserBtn.disabled = false;
      });
  }
}

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

export function setupUserEventListeners() {
  addUserBtn.addEventListener("click", () => openUserEditModal(null));
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
  if (saveUserBtn) {
    saveUserBtn.addEventListener("click", saveUser);
  }
  closeModalBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      userModal.classList.remove("active");
    });
  });
}
