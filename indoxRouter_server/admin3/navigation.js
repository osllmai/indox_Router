import {
  navItems,
  pageTitle,
  dashboardPage,
  usersPage,
  apiKeysPage,
  usagePage,
  modelsPage,
  endpointTesterPage,
} from "./dom.js";
import { loadDashboardStats } from "./dashboard.js";
import { loadUsers } from "./users.js";
import { loadApiKeys } from "./api-keys.js";
import { loadUsageAnalytics } from "./usage.js";
import { loadModels } from "./models.js";
import { setupEndpointTester } from "./endpoint-tester.js";

export function navigateTo(page) {
  navItems.forEach((item) => {
    if (item.dataset.page === page) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  pageTitle.textContent = page.charAt(0).toUpperCase() + page.slice(1);

  document
    .querySelectorAll(".page")
    .forEach((p) => p.classList.remove("active"));

  document.getElementById(`${page}-page`).classList.add("active");

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
