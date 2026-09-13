document.addEventListener("DOMContentLoaded", () => {
  const mapElement = document.getElementById("map");
  if (!mapElement || typeof L === "undefined") return;

  const imagery = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", { attribution: "Tiles © Esri", maxZoom: 18 });
  const street = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "© OpenStreetMap contributors", maxZoom: 18 });
  const map = L.map("map", { zoomControl: true, attributionControl: true, layers: [imagery] }).setView([-62, 25], 4);
  const routeLayer = L.layerGroup().addTo(map);
  const icebergLayer = L.layerGroup().addTo(map);
  const seaIceLayer = L.layerGroup().addTo(map);
  const vesselLayer = L.layerGroup().addTo(map);
  const riskLayer = L.layerGroup().addTo(map);
  let vesselMarker = null;
  let lastRouteSignature = "";
  let selectedIcebergId = null;
  let seaIceCanvas = null;
  let seaIceBounds = null;
  let seaIceData = null;
  let seaIceAnimationFrame = null;
  let seaIceTime = 0;
  let windVelocityLayer = null;
  let windField = null;
  let windEnabled = true;
  let windLoading = false;
  let windControlStatus = null;

  const colorForRisk = (risk) => ({ low: "#6ee7b7", moderate: "#f5c76a", watch: "#ffb86b", high: "#ff6b6b" }[(risk || "moderate").toLowerCase()] || "#f5c76a");
  const vesselIcon = (heading) => L.divIcon({ className: "marker-vessel", html: `<div class="vessel-glyph" style="transform:rotate(${Number(heading) || 0}deg)"></div>`, iconSize: [24, 24], iconAnchor: [12, 12] });
  const number = (value, digits = 2) => value === undefined || value === null || Number.isNaN(Number(value)) ? "--" : Number(value).toFixed(digits);
  const windMetadata = () => windField && windField.metadata;
  const setWindControlStatus = (message, error = false) => {
    if (!windControlStatus) return;
    windControlStatus.textContent = message;
    windControlStatus.classList.toggle("wind-status-error", error);
  };
  const validWindField = (payload) => {
    const field = payload && payload.field;
    const metadata = payload && payload.metadata;
    if (!Array.isArray(field) || field.length !== 2 || !metadata) return false;
    const header = field[0] && field[0].header;
    const expectedLength = Number(header && header.nx) * Number(header && header.ny);
    return Number.isFinite(expectedLength) && expectedLength > 0
      && Array.isArray(field[0].data) && field[0].data.length === expectedLength
      && Array.isArray(field[1].data) && field[1].data.length === expectedLength;
  };
  const removeWindLayer = () => {
    if (windVelocityLayer) {
      map.removeLayer(windVelocityLayer);
      windVelocityLayer = null;
    }
  };
  const attachWindLayer = () => {
    removeWindLayer();
    if (!windEnabled || !validWindField(windField) || typeof L.velocityLayer !== "function") return;
    windVelocityLayer = L.velocityLayer({
      data: windField.field,
      displayValues: false,
      velocityScale: 0.008,
      particleAge: 90,
      particleMultiplier: 1 / 450,
      lineWidth: 1.2,
      opacity: 0.72,
      colorScale: ["#95d8ff", "#69d2ff", "#6ee7b7", "#f5c76a"],
    }).addTo(map);
  };
  const sampleWind = (latlng) => {
    if (!validWindField(windField)) return null;
    const [uRecord, vRecord] = windField.field;
    const header = uRecord.header;
    const north = Number(header.la1); const south = Number(header.la2);
    const west = Number(header.lo1); const east = Number(header.lo2);
    if (latlng.lat > north || latlng.lat < south || latlng.lng < west || latlng.lng > east) return null;
    const x = Math.max(0, Math.min(Number(header.nx) - 1, Math.round((latlng.lng - west) / (east - west) * (Number(header.nx) - 1))));
    const y = Math.max(0, Math.min(Number(header.ny) - 1, Math.round((north - latlng.lat) / (north - south) * (Number(header.ny) - 1))));
    const index = y * Number(header.nx) + x;
    const u = Number(uRecord.data[index]); const v = Number(vRecord.data[index]);
    if (!Number.isFinite(u) || !Number.isFinite(v)) return null;
    const speed = Math.hypot(u, v);
    const direction = (Math.atan2(-u, -v) * 180 / Math.PI + 360) % 360;
    return { u, v, speed, direction };
  };
  const showWindInspector = (latlng) => {
    const metadata = windMetadata();
    const sample = sampleWind(latlng);
    if (!metadata || !sample) return;
    const status = metadata.stale ? "stale cached field" : "cached forecast field";
    L.popup({ maxWidth: 290 })
      .setLatLng(latlng)
      .setContent(`<div class="wind-inspector"><b>Wind field</b><br>${number(sample.speed, 2)} m/s from ${number(sample.direction, 0)}°<br>U: ${number(sample.u, 3)} m/s · V: ${number(sample.v, 3)} m/s<br><small>${metadata.source} · ${metadata.data_kind}<br>Valid: ${metadata.valid_time}<br>${status} · ${metadata.grid_spacing_deg}° grid</small></div>`)
      .openOn(map);
  };
  const loadWindField = async (refresh = false) => {
    if (windLoading || !window.api || typeof window.api.getWind !== "function") return;
    windLoading = true;
    setWindControlStatus("Loading wind forecast…");
    try {
      const payload = await window.api.getWind(refresh);
      if (!validWindField(payload)) throw new Error("Wind response did not contain a valid U/V grid.");
      windField = payload;
      attachWindLayer();
      const metadata = windMetadata();
      setWindControlStatus(`${metadata.source} · ${metadata.stale ? "stale" : "forecast"} · ${metadata.valid_time}`);
    } catch (error) {
      removeWindLayer();
      setWindControlStatus("Wind forecast unavailable", true);
    } finally {
      windLoading = false;
    }
  };
  const createWindControl = () => {
    const WindControl = L.Control.extend({
      options: { position: "bottomleft" },
      onAdd: () => {
        const container = L.DomUtil.create("div", "leaflet-control wind-control");
        container.innerHTML = `<div class="wind-control-title">Wind forecast</div><div class="wind-control-status">Loading…</div><div class="wind-control-actions"><button type="button" data-wind-toggle>Hide</button><button type="button" data-wind-refresh>Refresh</button></div>`;
        L.DomEvent.disableClickPropagation(container);
        L.DomEvent.disableScrollPropagation(container);
        windControlStatus = container.querySelector(".wind-control-status");
        container.querySelector("[data-wind-toggle]").addEventListener("click", (event) => {
          windEnabled = !windEnabled;
          event.currentTarget.textContent = windEnabled ? "Hide" : "Show";
          if (windEnabled) attachWindLayer(); else removeWindLayer();
        });
        container.querySelector("[data-wind-refresh]").addEventListener("click", () => loadWindField(true));
        return container;
      },
    });
    map.addControl(new WindControl());
  };
  const physicsPopup = (iceberg) => {
    const physics = iceberg.physics_diagnostics || {};
    const routeRisk = iceberg.route_risk || {};
    const status = iceberg.status || "DRIFTING";
    const statusClass = status === "GROUNDED" ? "status-grounded" : status === "COASTAL" ? "status-coastal" : "status-drifting";
    const groundedLine = iceberg.grounded_at_hours !== undefined && iceberg.grounded_at_hours !== null ? `<br>Grounded at: +${number(iceberg.grounded_at_hours, 1)} h` : "";
    return `<div class="iceberg-popup"><b>${iceberg.id}</b> <span class="status-badge ${statusClass}">${status}</span><br><strong>Status</strong><br>${status}${groundedLine}<br><strong>Position</strong><br>${number(iceberg.lat, 4)}° lat, ${number(iceberg.lon, 4)}° lon<br><strong>Motion</strong><br>${number(physics.iceberg_speed, 3)} m/s · heading ${number(iceberg.heading_deg, 1)}°<br>Velocity: ${number(iceberg.velocity_u_m_s, 3)} m/s east, ${number(iceberg.velocity_v_m_s, 3)} m/s north<br><strong>Geometry</strong><br>${number(iceberg.length_m, 1)} m × ${number(iceberg.width_m, 1)} m × ${number(iceberg.height_m, 1)} m<br>Mass: ${number(iceberg.estimated_mass_kg, 0)} kg<br>Effective mass: ${number(physics.effective_mass_kg, 0)} kg<br><strong>Forcing</strong><br>Wind: ${number(physics.wind_speed, 2)} m/s at ${number(physics.wind_direction, 1)}°<br>Current: ${number(physics.current_speed, 3)} m/s at ${number(physics.current_direction, 1)}°<br>Relative wind: ${number(physics.relative_wind_speed, 3)} m/s<br>Relative water: ${number(physics.relative_water_speed, 3)} m/s<br><strong>Forces / acceleration</strong><br>Wind: ${number(physics.wind_force_x, 1)}, ${number(physics.wind_force_y, 1)} N<br>Water: ${number(physics.water_force_x, 1)}, ${number(physics.water_force_y, 1)} N<br>Coriolis: ${number(physics.coriolis_acceleration_x, 5)}, ${number(physics.coriolis_acceleration_y, 5)} m/s²<br>Net acceleration: ${number(physics.net_acceleration_x, 5)}, ${number(physics.net_acceleration_y, 5)} m/s²<br><strong>Route risk</strong><br>${routeRisk.risk_level || iceberg.risk_level || "--"} · ${number(routeRisk.minimum_distance_km, 1)} km from route<br>Risk radius: ${number(routeRisk.risk_radius_km, 1)} km</div>`;
  };

  const renderRoutes = (routes) => {
    const signature = JSON.stringify(routes || {});
    if (signature === lastRouteSignature) return;
    if (lastRouteSignature) {
      mapElement.classList.add("route-changed");
      window.setTimeout(() => mapElement.classList.remove("route-changed"), 1800);
    }
    lastRouteSignature = signature;
    routeLayer.clearLayers();
    const configs = { shortest: { color: "#f8d66d", weight: 3, dashArray: "6 7", label: "Reference / shortest" }, optimized: { color: "#6ee7b7", weight: 5, label: "Recommended" }, conservative: { color: "#7ec8ff", weight: 3, dashArray: "12 8", label: "Conservative" } };
    Object.entries(routes || {}).forEach(([key, route]) => {
      const config = configs[key] || configs.optimized;
      const points = Array.isArray(route.points) ? route.points : [];
      if (points.length < 2) return;
      const line = L.polyline(points, { color: config.color, weight: config.weight, opacity: key === "optimized" ? 0.98 : 0.76, dashArray: config.dashArray || "" }).addTo(routeLayer);
      line.bindPopup(`<b>${config.label}</b><br>${route.distance_km ?? "--"} km`);
      L.marker(points[Math.floor(points.length / 2)], { icon: L.divIcon({ className: "route-label", html: config.label, iconSize: [128, 18] }) }).addTo(routeLayer);
    });
  };

  const renderIcebergs = (icebergs, trajectories) => {
    icebergLayer.clearLayers();
    riskLayer.clearLayers();
    const trajectoryById = Object.fromEntries((trajectories || []).map((feature) => [feature.properties && feature.properties.id, feature]));
    (icebergs || []).forEach((iceberg) => {
      if (iceberg.lat === undefined || iceberg.lon === undefined) return;
      const point = [iceberg.lat, iceberg.lon];
      const feature = trajectoryById[iceberg.id];
      const coordinates = feature && feature.geometry && feature.geometry.coordinates;
      const routeRisk = iceberg.route_risk || {};
      const status = iceberg.status || "DRIFTING";
      let color = colorForRisk(routeRisk.risk_level || iceberg.risk_level);
      let statusClass = "iceberg-drifting";
      if (status === "GROUNDED") {
        color = "#b6c3cc";
        statusClass = "iceberg-grounded";
      } else if (status === "COASTAL") {
        color = "#38bdf8";
        statusClass = "iceberg-coastal";
      }
      const riskRadius = Number(iceberg.risk_radius_m || 0);
      if (riskRadius > 0) L.circle(point, { radius: riskRadius, color, fillColor: color, fillOpacity: routeRisk.route_conflict ? 0.2 : 0.08, weight: routeRisk.route_conflict ? 2 : 1, className: "risk-zone" }).addTo(riskLayer);
      const marker = L.circleMarker(point, { radius: selectedIcebergId === iceberg.id ? 10 : 7, color: selectedIcebergId === iceberg.id ? "#ffffff" : color, fillColor: color, fillOpacity: 1, weight: selectedIcebergId === iceberg.id ? 3 : 2, className: `${statusClass} ${selectedIcebergId === iceberg.id ? "iceberg-selected" : ""}` }).addTo(icebergLayer);
      marker.bindPopup(physicsPopup(iceberg), { maxWidth: 320 });
      marker.on("click", () => {
        selectedIcebergId = iceberg.id;
        document.dispatchEvent(new CustomEvent("iceberg-selected", { detail: { iceberg, trajectory: feature } }));
      });
      if (Array.isArray(coordinates) && coordinates.length > 1) {
        L.polyline(coordinates.map((coordinate) => [coordinate[1], coordinate[0]]), { color, weight: selectedIcebergId === iceberg.id ? 3 : 2, opacity: 0.8, dashArray: "6 8" }).addTo(icebergLayer);
        const horizons = feature.properties && feature.properties.horizons_hours || [];
        horizons.forEach((horizon, index) => {
          const coordinate = coordinates[index + 1];
          if (!coordinate) return;
          L.marker([coordinate[1], coordinate[0]], { icon: L.divIcon({ className: "iceberg-forecast-label", html: `+${horizon}h`, iconSize: [38, 18] }) }).addTo(icebergLayer);
        });
      }
    });
  };

  // Continuous sea-ice color interpolation
const SEA_ICE_COLOR_STOPS = [
  { value: 0.0, color: [117, 203, 255, 0.15] },   // Open water - light cyan, very transparent
  { value: 0.1, color: [117, 203, 255, 0.25] },   // Open water
  { value: 0.3, color: [79, 160, 252, 0.35] },    // Low - blue
  { value: 0.6, color: [97, 214, 159, 0.45] },    // Moderate - green
  { value: 0.8, color: [245, 199, 106, 0.55] },   // High - amber
  { value: 1.0, color: [255, 107, 107, 0.65] },   // Very High - red
];

const lerpColor = (t, stops) => {
  if (t <= stops[0].value) return stops[0].color;
  if (t >= stops[stops.length - 1].value) return stops[stops.length - 1].color;
  for (let i = 0; i < stops.length - 1; i++) {
    if (t >= stops[i].value && t <= stops[i + 1].value) {
      const localT = (t - stops[i].value) / (stops[i + 1].value - stops[i].value);
      return [
        Math.round(stops[i].color[0] + (stops[i + 1].color[0] - stops[i].color[0]) * localT),
        Math.round(stops[i].color[1] + (stops[i + 1].color[1] - stops[i].color[1]) * localT),
        Math.round(stops[i].color[2] + (stops[i + 1].color[2] - stops[i].color[2]) * localT),
        Math.round(stops[i].color[3] + (stops[i + 1].color[3] - stops[i].color[3]) * localT),
      ];
    }
  }
  return stops[stops.length - 1].color;
};

// Bilinear interpolation for smooth grid rendering
const bilinearInterpolate = (grid, x, y, width, height) => {
  const x1 = Math.floor(x);
  const y1 = Math.floor(y);
  const x2 = Math.min(x1 + 1, width - 1);
  const y2 = Math.min(y1 + 1, height - 1);
  const fx = x - x1;
  const fy = y - y1;

  const v11 = grid[y1]?.[x1] ?? 0;
  const v21 = grid[y1]?.[x2] ?? 0;
  const v12 = grid[y2]?.[x1] ?? 0;
  const v22 = grid[y2]?.[x2] ?? 0;

  return (v11 * (1 - fx) * (1 - fy)) +
         (v21 * fx * (1 - fy)) +
         (v12 * (1 - fx) * fy) +
         (v22 * fx * fy);
};

const renderSeaIce = (seaIce) => {
    seaIceLayer.clearLayers();
    if (!seaIce || !Array.isArray(seaIce.grid)) return;

    // Extract grid data into a 2D array for interpolation
    const cells = seaIce.grid;
    if (cells.length === 0) return;

    // Determine grid bounds and resolution
    const lats = cells.map(c => c.center[0]).sort((a, b) => a - b);
    const lons = cells.map(c => c.center[1]).sort((a, b) => a - b);
    const uniqueLats = [...new Set(lats.map(l => Math.round(l * 100) / 100))].sort((a, b) => a - b);
    const uniqueLons = [...new Set(lons.map(l => Math.round(l * 100) / 100))].sort((a, b) => a - b);

    const latStep = uniqueLats.length > 1 ? uniqueLats[1] - uniqueLats[0] : 4.0;
    const lonStep = uniqueLons.length > 1 ? uniqueLons[1] - uniqueLons[0] : 4.0;

    // Create 2D concentration grid
    const gridWidth = uniqueLons.length;
    const gridHeight = uniqueLats.length;
    const concentrationGrid = Array(gridHeight).fill(null).map(() => Array(gridWidth).fill(0));

    cells.forEach(cell => {
      if (!cell.center) return;
      const latIdx = uniqueLats.findIndex(l => Math.abs(l - cell.center[0]) < latStep / 2);
      const lonIdx = uniqueLons.findIndex(l => Math.abs(l - cell.center[1]) < lonStep / 2);
      if (latIdx >= 0 && lonIdx >= 0) {
        concentrationGrid[latIdx][lonIdx] = cell.concentration ?? 0;
      }
    });

    // Store for canvas rendering
    seaIceData = {
      grid: concentrationGrid,
      bounds: {
        south: uniqueLats[0] - latStep / 2,
        north: uniqueLats[uniqueLats.length - 1] + latStep / 2,
        west: uniqueLons[0] - lonStep / 2,
        east: uniqueLons[uniqueLons.length - 1] + lonStep / 2,
      },
      latStep,
      lonStep,
      uniqueLats,
      uniqueLons,
    };

    seaIceBounds = [
      [seaIceData.bounds.south, seaIceData.bounds.west],
      [seaIceData.bounds.north, seaIceData.bounds.east],
    ];

    // Create or update canvas overlay
    createSeaIceCanvas();
  };

const createSeaIceCanvas = () => {
    if (!seaIceData) return;

    // Remove existing canvas if any
    if (seaIceCanvas) {
      map.removeLayer(seaIceCanvas);
      seaIceCanvas = null;
    }

    // Create canvas element
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Calculate canvas size based on map view - use higher resolution for smoother rendering
    const bounds = seaIceData.bounds;
    const mapSize = map.getSize();
    const swPoint = map.latLngToContainerPoint([bounds.south, bounds.west]);
    const nePoint = map.latLngToContainerPoint([bounds.north, bounds.east]);
    const canvasWidth = Math.abs(nePoint.x - swPoint.x);
    const canvasHeight = Math.abs(swPoint.y - nePoint.y);

    // Use a reasonable resolution (max 512px on longest side for performance)
    const maxDim = Math.max(canvasWidth, canvasHeight);
    const scale = maxDim > 512 ? 512 / maxDim : 1;
    canvas.width = Math.round(canvasWidth * scale);
    canvas.height = Math.round(canvasHeight * scale);

    const grid = seaIceData.grid;
    const gridHeight = grid.length;
    const gridWidth = grid[0]?.length ?? 0;

    // Render interpolated sea-ice field
    const imageData = ctx.createImageData(canvas.width, canvas.height);
    const data = imageData.data;

    for (let py = 0; py < canvas.height; py++) {
      for (let px = 0; px < canvas.width; px++) {
        // Map canvas pixel to grid coordinates
        const gx = (px / canvas.width) * (gridWidth - 1);
        const gy = (py / canvas.height) * (gridHeight - 1);

        const concentration = bilinearInterpolate(grid, gx, gy, gridWidth, gridHeight);
        const color = lerpColor(concentration, SEA_ICE_COLOR_STOPS);

        const idx = (py * canvas.width + px) * 4;
        data[idx] = color[0];     // R
        data[idx + 1] = color[1]; // G
        data[idx + 2] = color[2]; // B
        data[idx + 3] = Math.round(color[3] * 255); // A
      }
    }

    ctx.putImageData(imageData, 0, 0);

    // Create Leaflet ImageOverlay
    seaIceCanvas = L.imageOverlay(canvas.toDataURL(), seaIceBounds, {
      opacity: 0.85,
      interactive: false,
      attribution: '',
    }).addTo(seaIceLayer);
  };

// Re-render sea ice on zoom/pan for crisp interpolation
map.on('zoomend moveend', () => {
    if (seaIceData) {
      createSeaIceCanvas();
    }
  });

  map.on("click", (event) => {
    if (windEnabled && windField) showWindInspector(event.latlng);
  });

  const updateState = (state) => {
    const vessel = state && state.vessel_state;
    if (vessel && vessel.lat !== undefined && vessel.lon !== undefined) {
      if (!vesselMarker) vesselMarker = L.marker([vessel.lat, vessel.lon], { icon: vesselIcon(vessel.heading_deg) }).addTo(vesselLayer);
      else { vesselMarker.setLatLng([vessel.lat, vessel.lon]); vesselMarker.setIcon(vesselIcon(vessel.heading_deg)); }
      vesselMarker.bindPopup(`<b>${vessel.name || "Vessel"}</b><br>Speed: ${vessel.speed_kn ?? "--"} kn<br>Heading: ${vessel.heading_deg ?? "--"}°<br>Fuel: ${vessel.fuel_remaining_pct ?? "--"}%<br>Risk: ${vessel.risk_state || "--"}`);
    }
    renderRoutes(state && state.routes);
    renderIcebergs(state && state.iceberg_states, state && state.iceberg_trajectories);
    renderSeaIce(state && state.sea_ice_state);
  };

  const baseLayers = { "Satellite Imagery": imagery, "Base Map": street };
  const overlays = { "Recommended / routes": routeLayer, "Icebergs": icebergLayer, "Sea-Ice": seaIceLayer, "Vessel": vesselLayer, "Risk zones": riskLayer };
  L.control.layers(baseLayers, overlays, { collapsed: false }).addTo(map);
  createWindControl();
  window.mapController = { map, updateState };
  loadWindField();
  window.setTimeout(() => map.invalidateSize(), 200);
});
