document.addEventListener("DOMContentLoaded", () => {
  const panel = document.querySelector(".sea-ice-panel");
  if (!panel || !window.api) {
    return;
  }

  window.api.getSeaIce()
    .then((data) => {
      if (!data || !data.forecast) {
        panel.innerHTML = "<h2>Sea-Ice Panel</h2><p>Data unavailable. No current observation returned.</p>";
        return;
      }

      panel.innerHTML = `
        <h2>Sea-Ice Panel</h2>
        <p>Predicted concentration: ${data.forecast.concentration_mean ?? "N/A"}</p>
        <p>Sea-ice risk: ${data.forecast.risk_level ?? "N/A"}</p>
        <p>Forecast horizon: ${data.forecast.forecast_horizon_days ?? "N/A"} days</p>
        <p>Prediction confidence: ${data.forecast.confidence ?? "N/A"}</p>
        <p>Uncertainty: ${data.forecast.uncertainty ?? "N/A"}</p>
      `;
    })
    .catch(() => {
      panel.innerHTML = "<h2>Sea-Ice Panel</h2><p>API unavailable. Sea-ice data unavailable.</p>";
    });
});
