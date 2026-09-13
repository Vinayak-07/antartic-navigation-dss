document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("voyage-form");

  if (!form || !window.api) {
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      vessel: document.getElementById("vessel-select")?.value || "RV Aurora",
      origin: document.getElementById("origin-select")?.value || "Cape Town",
      destination: document.getElementById("destination-select")?.value || "Bharati Station",
      departure_time: document.getElementById("departure-time")?.value || "2026-01-15T06:00",
      forecast_horizon_days: Number(document.getElementById("forecast-horizon")?.value || 10),
    };

    const statusElement = document.getElementById("system-status");
    if (statusElement) {
      statusElement.textContent = "Submitting voyage analysis…";
    }

    try {
      const result = await window.api.analyzeVoyage(payload);
      const panel = document.querySelector(".route-panel");
      if (panel && result && result.voyage) {
        panel.innerHTML = `
          <h2>Route Panel</h2>
          <p>Voyage: ${result.voyage.voyage_id || "N/A"}</p>
          <p>Origin: ${result.voyage.origin || "N/A"}</p>
          <p>Destination: ${result.voyage.destination || "N/A"}</p>
          <p>Status: ${result.voyage.status || "N/A"}</p>
          <p>Recommended route: ${result.routes?.recommended?.name || "N/A"}</p>
        `;
      }
      if (statusElement) {
        statusElement.textContent = "Voyage analysis completed";
      }
    } catch (error) {
      if (statusElement) {
        statusElement.textContent = "Voyage analysis failed";
      }
      const panel = document.querySelector(".route-panel");
      if (panel) {
        panel.innerHTML = "<h2>Route Panel</h2><p>API unavailable. Voyage analysis failed.</p>";
      }
    }
  });
});
