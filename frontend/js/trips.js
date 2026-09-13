document.addEventListener("DOMContentLoaded", () => {
  const refs = (ids) => Object.fromEntries(ids.map((id) => [id, document.getElementById(id)]));
  const el = refs(["voyage-form", "system-status", "trip-message", "trip-history", "trip-id", "trip-scenario", "voyage-phase", "vessel-position", "vessel-motion", "fuel-remaining", "vessel-eta", "navigation-risk", "wind-speed", "current-speed", "sea-surface-temp", "wave-height", "current-sic", "predicted-sic", "ice-risk", "forecast-horizon-label", "prediction-confidence", "weather-risk", "tracked-icebergs", "high-risk-icebergs", "nearest-iceberg", "nearest-distance", "trajectory-horizon", "iceberg-details", "optimized-distance", "estimated-time", "fuel-estimate", "safety-score", "route-status", "distance-travelled", "simulation-mode", "simulation-start", "simulation-time", "simulation-end", "simulation-timeline", "event-markers", "event-list", "play-button", "pause-button", "reset-button", "step-back-button", "step-forward-button", "speed-select"]);
  let trip = null;
  let polling = false;
  let pollTimer = null;
  let requestInFlight = false;
  const setText = (node, value) => { if (node) node.textContent = value ?? "--"; };
  const hours = (value) => { const total = Math.max(0, Math.round(Number(value) || 0)); return `${String(total).padStart(2, "0")}:00`; };
  const label = (value) => String(value || "--").replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  const showMessage = (message, error = false) => { setText(el["trip-message"], message); if (el["system-status"]) { el["system-status"].textContent = error ? "Connection issue" : "Backend available"; el["system-status"].style.color = error ? "#ff9e9e" : "#d9f7ff"; } };
  const tripId = () => trip && trip.id;
  const setControls = (enabled) => ["play-button", "pause-button", "reset-button", "step-back-button", "step-forward-button", "speed-select", "simulation-timeline"].forEach((id) => { if (el[id]) el[id].disabled = !enabled; });
  let selectedIcebergId = null;

  const renderIcebergDetails = (iceberg, trajectory) => {
    if (!el["iceberg-details"] || !iceberg) return;
    const physics = iceberg.physics_diagnostics || {};
    const routeRisk = iceberg.route_risk || {};
    const value = (number, digits = 2) => number === undefined || number === null || Number.isNaN(Number(number)) ? "--" : Number(number).toFixed(digits);
    const coordinates = trajectory && trajectory.geometry && trajectory.geometry.coordinates || [];
    const horizons = trajectory && trajectory.properties && trajectory.properties.horizons_hours || [];
    const forecastRows = horizons.map((horizon, index) => { const coordinate = coordinates[index + 1]; return coordinate ? `<tr><td>+${horizon} h</td><td>${value(coordinate[1], 4)}°, ${value(coordinate[0], 4)}°</td></tr>` : ""; }).join("");
    const status = iceberg.status || "DRIFTING";
    const statusClass = status === "GROUNDED" ? "status-grounded" : status === "COASTAL" ? "status-coastal" : "status-drifting";
    const groundedNote = iceberg.grounded_at_hours !== undefined && iceberg.grounded_at_hours !== null ? ` (at +${value(iceberg.grounded_at_hours, 1)} h)` : "";
    el["iceberg-details"].innerHTML = `<div><strong>${iceberg.id}</strong><span class="status-badge ${statusClass}">${status}</span><span class="details-risk">${routeRisk.risk_level || iceberg.risk_level || "--"}</span></div><h4>Position and motion</h4><dl><dt>Status</dt><dd>${status}${groundedNote}</dd><dt>Position</dt><dd>${value(iceberg.lat, 4)}°, ${value(iceberg.lon, 4)}°</dd><dt>Speed</dt><dd>${value(physics.iceberg_speed, 3)} m/s</dd><dt>Heading</dt><dd>${value(iceberg.heading_deg, 1)}°</dd><dt>Velocity</dt><dd>${value(iceberg.velocity_u_m_s, 3)} / ${value(iceberg.velocity_v_m_s, 3)} m/s</dd></dl><h4>Geometry</h4><dl><dt>Dimensions</dt><dd>${value(iceberg.length_m, 1)} × ${value(iceberg.width_m, 1)} × ${value(iceberg.height_m, 1)} m</dd><dt>Mass</dt><dd>${value(iceberg.estimated_mass_kg, 0)} kg</dd><dt>Effective mass</dt><dd>${value(physics.effective_mass_kg, 0)} kg</dd><dt>Air / water area</dt><dd>${value(physics.air_projected_area_m2, 0)} / ${value(physics.underwater_projected_area_m2, 0)} m²</dd></dl><h4>Environmental forcing</h4><dl><dt>Wind</dt><dd>${value(physics.wind_speed, 2)} m/s · ${value(physics.wind_direction, 1)}°</dd><dt>Current</dt><dd>${value(physics.current_speed, 3)} m/s · ${value(physics.current_direction, 1)}°</dd><dt>Relative wind</dt><dd>${value(physics.relative_wind_speed, 3)} m/s</dd><dt>Relative water</dt><dd>${value(physics.relative_water_speed, 3)} m/s</dd></dl><h4>Forces and acceleration</h4><dl><dt>Wind force</dt><dd>${value(physics.wind_force_x, 1)}, ${value(physics.wind_force_y, 1)} N</dd><dt>Water force</dt><dd>${value(physics.water_force_x, 1)}, ${value(physics.water_force_y, 1)} N</dd><dt>Wind acceleration</dt><dd>${value(physics.wind_acceleration_x, 5)}, ${value(physics.wind_acceleration_y, 5)} m/s²</dd><dt>Water acceleration</dt><dd>${value(physics.water_acceleration_x, 5)}, ${value(physics.water_acceleration_y, 5)} m/s²</dd><dt>Coriolis acceleration</dt><dd>${value(physics.coriolis_acceleration_x, 5)}, ${value(physics.coriolis_acceleration_y, 5)} m/s²</dd><dt>Net acceleration</dt><dd>${value(physics.net_acceleration_x, 5)}, ${value(physics.net_acceleration_y, 5)} m/s²</dd></dl><h4>Route risk</h4><dl><dt>Risk</dt><dd>${routeRisk.risk_level || "--"} · ${value(routeRisk.risk_score, 3)}</dd><dt>Route distance</dt><dd>${value(routeRisk.minimum_distance_km, 1)} km</dd><dt>Risk radius</dt><dd>${value(routeRisk.risk_radius_km, 1)} km</dd></dl><h4>Trajectory forecast</h4><table class="trajectory-table"><tbody>${forecastRows || "<tr><td>Unavailable</td><td>--</td></tr>"}</tbody></table>`;
  };

  const renderEvents = (events) => {
    const items = Array.isArray(events) ? events : [];
    if (el["event-list"]) el["event-list"].innerHTML = items.length ? items.slice().reverse().map((event) => `<li class="alert-level-${event.severity || "normal"}"><button type="button" class="event-button" data-event="${items.indexOf(event)}"><strong>${label(event.event_type)}</strong><span>${hours(event.timestamp)} · ${event.title || "Event"}</span></button></li>`).join("") : '<li class="alert-level-normal">No events recorded.</li>';
    if (el["event-markers"] && trip) el["event-markers"].innerHTML = items.map((event, index) => `<button type="button" class="event-marker" title="${event.title || event.event_type}" data-event="${index}" style="left:${Math.min(100, Math.max(0, (Number(event.timestamp) / Number(trip.simulation_end || 72)) * 100))}%"></button>`).join("");
  };

  const renderTripHistory = (trips) => {
    const items = Array.isArray(trips) ? trips : [];
    if (!el["trip-history"]) return;
    el["trip-history"].innerHTML = items.length ? items.slice().reverse().map((item) => `<button type="button" class="history-item" data-trip-id="${item.id}"><strong>${item.id}</strong><span>${label(item.scenario)} · ${item.origin} → ${item.destination}</span><small>${label(item.status)}</small></button>`).join("") : "<span>No trips recorded</span>";
  };

  const renderState = (state) => {
    if (!state) return;
    if (trip) trip.current_simulation_time = state.simulation_time;
    const vessel = state.vessel_state || {};
    const env = state.environment_summary || {};
    const ice = state.sea_ice_state || {};
    const risk = state.risk || {};
    const icebergs = Array.isArray(state.iceberg_states) ? state.iceberg_states : [];
    const selected = icebergs.find((iceberg) => iceberg.id === selectedIcebergId);
    if (selected) {
      const trajectory = (state.iceberg_trajectories || []).find((feature) => feature.properties && feature.properties.id === selected.id);
      renderIcebergDetails(selected, trajectory);
    }
    setText(el["simulation-time"], hours(state.simulation_time));
    if (el["simulation-timeline"]) { el["simulation-timeline"].max = trip.simulation_end || 72; el["simulation-timeline"].value = state.simulation_time || 0; }
    const overallRisk = risk.overall_navigation_risk ?? risk.score;
    setText(el["voyage-phase"], label(state.phase)); setText(el["vessel-position"], vessel.lat !== undefined ? `${Number(vessel.lat).toFixed(3)}°, ${Number(vessel.lon).toFixed(3)}°` : "--"); setText(el["vessel-motion"], vessel.speed_kn !== undefined ? `${vessel.speed_kn} kn · ${vessel.heading_deg}°` : "--"); setText(el["fuel-remaining"], vessel.fuel_remaining_pct !== undefined ? `${vessel.fuel_remaining_pct}%` : "--"); setText(el["vessel-eta"], vessel.eta_hours !== undefined ? `${vessel.eta_hours} hrs` : "--"); setText(el["navigation-risk"], `${label(risk.status)} · ${overallRisk ?? "--"}`);
    setText(el["wind-speed"], env.wind_speed_m_s !== undefined ? `${env.wind_speed_m_s} m/s` : "--"); setText(el["current-speed"], env.surface_current_u_m_s !== undefined ? `${env.surface_current_u_m_s} m/s` : "--"); setText(el["sea-surface-temp"], env.sea_surface_temperature_c !== undefined ? `${env.sea_surface_temperature_c}°C` : "--"); setText(el["wave-height"], env.wave_height_m !== undefined ? `${env.wave_height_m} m` : "--");
    const concentration = Number(ice.concentration || 0); setText(el["current-sic"], `${(concentration * 100).toFixed(0)}%`); setText(el["predicted-sic"], `${(concentration * 100).toFixed(0)}%`); setText(el["ice-risk"], label(ice.risk_level)); setText(el["forecast-horizon-label"], ice.forecast_horizon_days !== undefined ? `${ice.forecast_horizon_days} days` : "--"); setText(el["prediction-confidence"], ice.confidence ?? "--"); setText(el["weather-risk"], env.wind_speed_m_s > 16 ? "HIGH" : "MODERATE");
    const highRisk = icebergs.filter((item) => String(item.risk_level).toLowerCase() === "high").length; setText(el["tracked-icebergs"], icebergs.length); setText(el["high-risk-icebergs"], highRisk); setText(el["nearest-iceberg"], icebergs[0] && icebergs[0].id); setText(el["nearest-distance"], "--"); setText(el["trajectory-horizon"], "48 hrs");
    const routes = state.routes || {}; const optimized = routes.optimized || {}; setText(el["optimized-distance"], optimized.distance_km !== undefined ? `${optimized.distance_km} km` : "--"); setText(el["estimated-time"], state.duration_hours !== undefined ? `${state.duration_hours} hrs` : "--"); setText(el["fuel-estimate"], vessel.fuel_remaining_pct !== undefined ? `${(100 - vessel.fuel_remaining_pct).toFixed(1)}% used` : "--"); setText(el["safety-score"], overallRisk !== undefined ? `${(1 - overallRisk).toFixed(2)}` : "--"); setText(el["route-status"], state.active_route ? `${label(state.active_route)} · ${optimized.name || "Route"}` : optimized.name || "--"); setText(el["distance-travelled"], `${state.distance_km ?? 0} km`);
    ["shortest", "optimized", "conservative"].forEach((key) => { const node = document.getElementById(`route-${key}`); if (node) { const route = routes[key] || {}; node.querySelector("strong").textContent = route.distance_km !== undefined ? `${route.distance_km} km` : "--"; } });
    if (el["simulation-mode"]) { const isReplay = state.status === "REPLAY"; el["simulation-mode"].textContent = isReplay ? "REPLAY" : "LIVE"; el["simulation-mode"].classList.toggle("replay", isReplay); }
    if (window.mapController) window.mapController.updateState(state);
  };

  const loadState = async () => { if (!tripId() || requestInFlight) return; requestInFlight = true; try { const state = await window.api.getTripState(tripId()); renderState(state); } catch (error) { showMessage(error.message, true); } finally { requestInFlight = false; } };
  const stopPolling = () => { polling = false; if (pollTimer) { window.clearTimeout(pollTimer); pollTimer = null; } };
  const poll = async () => { if (!polling || requestInFlight) return; await loadState(); if (polling) pollTimer = window.setTimeout(poll, 1000); };
  const startPolling = () => { stopPolling(); polling = true; poll(); };
  const refreshHistory = async () => { try { const result = await window.api.listTrips(); renderTripHistory(result.trips); } catch (error) { showMessage(error.message, true); } };
  const setTrip = async (nextTrip) => { trip = nextTrip; setControls(true); setText(el["trip-id"], trip.id); setText(el["trip-scenario"], label(trip.scenario)); setText(el["simulation-start"], hours(trip.simulation_start)); setText(el["simulation-end"], hours(trip.simulation_end)); const timeline = await window.api.getTripTimeline(trip.id); const events = await window.api.getTripEvents(trip.id); renderEvents(events.events); renderState((timeline.timeline || [])[timeline.timeline.length - 1] || trip); await loadState(); };
  const action = async (operation, running = false) => { if (!tripId()) return; try { trip = await operation(tripId()); renderState(await window.api.getTripState(tripId())); const events = await window.api.getTripEvents(tripId()); trip.events = events.events; renderEvents(events.events); if (running) startPolling(); else stopPolling(); await refreshHistory(); } catch (error) { showMessage(error.message, true); } };

  el["voyage-form"]?.addEventListener("submit", async (event) => { event.preventDefault(); stopPolling(); try { const created = await window.api.createTrip({ vessel: document.getElementById("vessel-select").value, origin: document.getElementById("origin-select").value, destination: document.getElementById("destination-select").value, scenario: document.getElementById("scenario-select").value, departure_time: document.getElementById("departure-time").value }); await setTrip(created); showMessage(`Trip ${created.id} ready`); await refreshHistory(); } catch (error) { showMessage(error.message, true); } });
  el["play-button"]?.addEventListener("click", () => action(window.api.startTrip, true)); el["pause-button"]?.addEventListener("click", () => action(window.api.pauseTrip)); el["reset-button"]?.addEventListener("click", () => action(window.api.resetTrip)); el["step-forward-button"]?.addEventListener("click", () => action((id) => window.api.stepTrip(id, 1))); el["step-back-button"]?.addEventListener("click", () => action((id) => window.api.seekTrip(id, Math.max(0, Number(trip.current_simulation_time || 0) - 1))));
  el["speed-select"]?.addEventListener("change", () => action((id) => window.api.setTripSpeed(id, Number(el["speed-select"].value)), polling)); el["simulation-timeline"]?.addEventListener("change", () => action((id) => window.api.seekTrip(id, Number(el["simulation-timeline"].value))));
  el["trip-history"]?.addEventListener("click", async (event) => { const button = event.target.closest("[data-trip-id]"); if (!button) return; stopPolling(); try { await setTrip(await window.api.getTrip(button.dataset.tripId)); } catch (error) { showMessage(error.message, true); } });
  el["event-list"]?.addEventListener("click", (event) => { const button = event.target.closest("[data-event]"); if (!button || !trip) return; const eventData = trip.events && trip.events[Number(button.dataset.event)]; if (eventData) showMessage(`${eventData.title}: ${eventData.description} ${eventData.reason || ""}`); });
  document.addEventListener("iceberg-selected", (event) => {
    selectedIcebergId = event.detail.iceberg.id;
    renderIcebergDetails(event.detail.iceberg, event.detail.trajectory);
  });
  setControls(false); refreshHistory();
});
