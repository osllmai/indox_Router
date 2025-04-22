import { API_BASE_URL } from "./constants.js";

export function apiFetch(endpoint, method = "GET", data = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", // Include cookies in requests
  };

  // Add bearer token from localStorage if present
  const token = localStorage.getItem("admin_api_key");
  if (token) {
    options.headers["Authorization"] = `Bearer ${token}`;
  }

  if (data) {
    options.body = JSON.stringify(data);
  }

  return fetch(`${API_BASE_URL}${endpoint}`, options)
    .then((response) => {
      if (response.status === 401) {
        // Redirect to login if unauthorized
        window.location.href = "/admin/login.html";
        return Promise.reject("Unauthorized");
      }
      if (!response.ok) {
        throw new Error(response.statusText);
      }
      return response.json();
    })
    .catch((error) => {
      console.error("API Fetch error:", error);
      throw error;
    });
}
