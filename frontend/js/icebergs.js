document.addEventListener("DOMContentLoaded", () => {
  const panel = document.querySelector(".iceberg-panel");
  if (!panel || !window.api) {
    return;
  }

  window.api.getIcebergs()
    .then((data) => {
      const summary = data && data.summary ? data.summary : {};
      const items = Array.isArray(data && data.icebergs) ? data.icebergs : [];
      panel.innerHTML = `
        <h2>Iceberg Panel</h2>
        <p>Detected icebergs: ${summary.detected_count ?? items.length}</p>
        <p>High-risk icebergs: ${summary.high_risk_count ?? "N/A"}</p>
        <p>Nearest iceberg: ${summary.nearest_iceberg_id || "N/A"}</p>
        <p>Current placeholder entries: ${items.length}</p>
      `;
    })
    .catch(() => {
      panel.innerHTML = "<h2>Iceberg Panel</h2><p>Data unavailable. No current observation returned.</p>";
    });
});
