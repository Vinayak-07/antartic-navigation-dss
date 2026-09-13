document.addEventListener("DOMContentLoaded", () => {
  const panel = document.querySelector(".comparison-panel");
  if (!panel || !window.api) {
    return;
  }

  window.api.optimizeRoutes()
    .then((data) => {
      const routes = data && data.routes ? data.routes : {};
      const items = Object.values(routes);
      panel.innerHTML = `
        <h2>Route Comparison</h2>
        <ol>
          ${items.map((route) => `<li>${route.name || "Unnamed route"}: ${route.distance_km ?? "N/A"} km</li>`).join("")}
        </ol>
      `;
    })
    .catch(() => {
      panel.innerHTML = "<h2>Route Comparison</h2><p>Route comparison unavailable.</p>";
    });
});
