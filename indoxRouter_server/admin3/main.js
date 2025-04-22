import { navigateTo } from "./navigation.js";
import { setupUserEventListeners } from "./users.js";
import { setupApiKeyEventListeners } from "./api-keys.js";
import {
  sidebarToggle,
  logoutBtn,
  navItems,
  userName,
  userAvatar,
} from "./dom.js";

function init() {
  if (!localStorage.getItem("admin_api_key")) {
    window.location.href = "/admin/login.html";
    return;
  }

  const storedUserName = localStorage.getItem("admin_user_name");
  const storedAvatar = localStorage.getItem("admin_user_avatar");
  if (storedUserName) userName.textContent = storedUserName;
  if (storedAvatar) userAvatar.src = storedAvatar;

  sidebarToggle.addEventListener("click", () => {
    sidebar.classList.toggle("active");
  });

  logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("admin_api_key");
    localStorage.removeItem("admin_user_name");
    localStorage.removeItem("admin_user_avatar");
    window.location.href = "/admin/login.html";
  });

  navItems.forEach((item) => {
    item.addEventListener("click", () => {
      navigateTo(item.dataset.page);
    });
  });

  setupUserEventListeners();
  setupApiKeyEventListeners();

  navigateTo("dashboard");
}

window.addEventListener("load", init);
