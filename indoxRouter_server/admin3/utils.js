export function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

export function showLoading(element) {
  element.innerHTML = '<p class="loading">Loading...</p>';
}

export function showError(element, message) {
  element.innerHTML = `<p class="error">Error: ${message}</p>`;
}
