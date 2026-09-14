document.addEventListener("DOMContentLoaded", () => {
  const mapElement = document.getElementById("map");
  if (!mapElement || typeof L === "undefined") return;

  const imagery = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", { attribution: "Tiles © Esri", maxZoom: 18 });
  const street = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "© OpenStreetMap contributors", maxZoom: 18 });
  const operationalBounds = L.latLngBounds([[-75, 10], [-28, 90]]);
  const map = L.map("map", {
    zoomControl: false,
    attributionControl: true,
    layers: [imagery],
    maxBounds: operationalBounds,
    maxBoundsViscosity: 1.0,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false,
    touchZoom: false,
  }).fitBounds(operationalBounds, { padding: [8, 8], maxZoom: 4 });
  map.dragging.disable();
  map.boxZoom.disable();
  map.doubleClickZoom.disable();
  map.keyboard.disable();
  map.scrollWheelZoom.disable();
  map.touchZoom.disable();
  const fixedCenter = map.getCenter();
  const fixedZoom = map.getZoom();
  // Guard flag: Leaflet fires "moveend" synchronously inside setView, and
  // pixel-snapped centers can wobble by ~1e-7 deg between corrections —
  // above the default .equals() tolerance — so an unguarded re-centre can
  // recurse until the call stack blows (intermittent RangeError).
  let correctingView = false;
  map.on("moveend zoomend", () => {
    if (correctingView) return;
    if (map.getZoom() !== fixedZoom || !map.getCenter().equals(fixedCenter)) {
      correctingView = true;
      map.setView(fixedCenter, fixedZoom, { animate: false });
      correctingView = false;
    }
  });
  mapElement.addEventListener("wheel", (event) => event.preventDefault(), { passive: false });
  mapElement.addEventListener("touchmove", (event) => event.preventDefault(), { passive: false });
  // Explicit pane ordering (phase 76.2): the sea-ice concentration canvas
  // must sit below every iceberg feature so glyphs and trajectory lines are
  // never painted underneath the heatmap.
  map.createPane("sea-ice-pane");
  map.getPane("sea-ice-pane").style.zIndex = 350;
  const routeLayer = L.layerGroup().addTo(map);
  const icebergLayer = L.layerGroup().addTo(map);
  const seaIceLayer = L.layerGroup().addTo(map);
  const vesselLayer = L.layerGroup().addTo(map);
  const riskLayer = L.layerGroup().addTo(map);
  const labelLayer = L.layerGroup().addTo(map);
  let vesselMarker = null;
  let lastRouteSignature = "";
  let pendingLabels = [];
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
      .setContent(`<div class="wind-inspector"><b>Wind field</b><br>${number(sample.speed, 2)} m/s from ${number(sample.direction, 0)}°<br>U: ${number(sample.u, 3)} m/s · V: ${number(sample.v, 3)} m/s<br><small>${metadata.source} · ${metadata.data_kind}<br>Valid: ${metadata.valid_time}<br>${status} · ${number(metadata.grid_spacing_deg.lat, 2)}° lat / ${number(metadata.grid_spacing_deg.lon, 2)}° lon grid</small></div>`)
      .openOn(map);
  };
  // The wind field must cover the map's actual visible extent, not just the
  // operational rectangle: fitBounds leaves margins at the locked view, so
  // particles would otherwise die inside the visible map.  The clamp keeps the
  // request inside the documented Antarctic window the backend accepts.
  const windRequestBounds = () => {
    const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
    const visible = map.getBounds().pad(0.02);
    return {
      south: clamp(visible.getSouth(), -89, -20),
      north: clamp(visible.getNorth(), -89, -20),
      west: clamp(visible.getWest(), -180, 180),
      east: clamp(visible.getEast(), -180, 180),
      spacing: 2,
    };
  };
  const windRequestSignature = (bounds) => Object.values(bounds).map((value) => Number(value).toFixed(2)).join(",");
  let lastWindRequestSignature = null;
  const loadWindField = async (refresh = false) => {
    if (windLoading || !window.api || typeof window.api.getWind !== "function") return;
    const bounds = windRequestBounds();
    const signature = windRequestSignature(bounds);
    if (!refresh && windField && signature === lastWindRequestSignature) return;
    lastWindRequestSignature = signature;
    windLoading = true;
    setWindControlStatus("Loading wind forecast…");
    try {
      const payload = await window.api.getWind(refresh, bounds);
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
  // Always-visible legend (phase 76.2): vessel, iceberg statuses, route
  // types, and the sea-ice ramp were previously decodable only by opening
  // popups. Docked bottom-right, away from the wind control (bottom-left).
  const createLegendControl = () => {
    const LegendControl = L.Control.extend({
      options: { position: "bottomright" },
      onAdd: () => {
        const container = L.DomUtil.create("div", "leaflet-control map-legend");
        container.innerHTML = `
          <div class="map-legend-title">Legend</div>
          <div class="map-legend-row"><span class="legend-swatch legend-vessel"></span>Vessel</div>
          <div class="map-legend-row"><span class="legend-swatch legend-iceberg"></span>Iceberg — drifting</div>
          <div class="map-legend-row"><span class="legend-swatch legend-iceberg legend-iceberg-coastal"></span>Iceberg — coastal</div>
          <div class="map-legend-row"><span class="legend-swatch legend-iceberg legend-iceberg-grounded"></span>Iceberg — grounded</div>
          <div class="map-legend-row"><span class="legend-swatch legend-route-recommended"></span>Recommended route</div>
          <div class="map-legend-row"><span class="legend-swatch legend-route-shortest"></span>Reference / shortest</div>
          <div class="map-legend-row"><span class="legend-swatch legend-route-conservative"></span>Conservative route</div>
          <div class="map-legend-row"><span class="legend-swatch legend-glacier"></span>Glacier (reference)</div>
          <div class="map-legend-ramp">
            <div class="legend-sea-ice-ramp"></div>
            <div class="map-legend-row"><span>Sea-ice: open water → consolidated</span></div>
          </div>`;
        L.DomEvent.disableClickPropagation(container);
        L.DomEvent.disableScrollPropagation(container);
        return container;
      },
    });
    map.addControl(new LegendControl());
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
      pendingLabels.push({ latlng: points[Math.floor(points.length / 2)], className: "route-label", html: config.label, iconSize: [128, 18], summary: `<b>${config.label}</b>${route.distance_km != null ? ` · ${route.distance_km} km` : ""}` });
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
      const marker = L.marker(point, {
        icon: L.divIcon({
          className: `iceberg-marker ${statusClass} ${selectedIcebergId === iceberg.id ? "iceberg-selected" : ""}`,
          // Two-tone silhouette (phase 76.2): a bright above-water tip in the
          // status/risk colour over a fainter submerged base, split by a
          // waterline — unmistakably "iceberg", never mistakable for the
          // blue-to-white sea-ice concentration ramp.
          html: `<span class="iceberg-glyph" style="--iceberg-color:${color}"><svg viewBox="0 0 26 32" aria-hidden="true"><polygon class="iceberg-base" points="5,14 21,14 17,29 9,29"></polygon><polygon class="iceberg-tip" points="13,2 21,14 5,14"></polygon><line class="iceberg-waterline" x1="2" y1="14" x2="24" y2="14"></line></svg></span>`,
          iconSize: selectedIcebergId === iceberg.id ? [30, 36] : [26, 32],
          iconAnchor: selectedIcebergId === iceberg.id ? [15, 18] : [13, 16],
        }),
        title: `${iceberg.id} · ${status}`,
      }).addTo(icebergLayer);
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
          pendingLabels.push({ latlng: [coordinate[1], coordinate[0]], className: "iceberg-forecast-label", html: `+${horizon}h`, iconSize: [38, 18], summary: `<b>${iceberg.id}</b> · +${horizon}h forecast position` });
        });
      }
    });
  };

  // Label collision avoidance (phase 76.1): route pills and iceberg
  // forecast tags all converge on the same pixels because the three route
  // alternatives and several trajectories share origin/destination
  // endpoints. Bucket every queued label by its rounded screen position
  // (~32px cells — slightly larger than the badge glyph itself so two
  // buckets never overlap; the map view is locked, so container points are
  // stable between renders) and draw one label per bucket. Crowded buckets
  // collapse into a single "×N" badge whose popup lists everything that
  // was suppressed underneath it, instead of stacking text on text.
  const LABEL_BUCKET_PX = 32;
  const flushLabels = () => {
    labelLayer.clearLayers();
    const buckets = new Map();
    pendingLabels.forEach((label) => {
      const point = map.latLngToContainerPoint(L.latLng(label.latlng));
      const key = `${Math.round(point.x / LABEL_BUCKET_PX)}:${Math.round(point.y / LABEL_BUCKET_PX)}`;
      if (!buckets.has(key)) buckets.set(key, []);
      buckets.get(key).push(label);
    });
    buckets.forEach((labels) => {
      if (labels.length === 1) {
        const label = labels[0];
        L.marker(label.latlng, { icon: L.divIcon({ className: label.className, html: label.html, iconSize: label.iconSize }), interactive: false }).addTo(labelLayer);
        return;
      }
      const badge = L.marker(labels[0].latlng, {
        icon: L.divIcon({ className: "label-cluster", html: `×${labels.length}`, iconSize: [30, 18] }),
        title: `${labels.length} labels overlap here`,
      }).addTo(labelLayer);
      badge.bindPopup(`<div class="label-cluster-popup"><b>${labels.length} labels overlap here</b><ul>${labels.map((label) => `<li>${label.summary}</li>`).join("")}</ul></div>`, { maxWidth: 300 });
    });
    pendingLabels = [];
  };

  // Sea-ice concentration ramp (phase 76.2): ice/water reads as
  // blue-to-white — open water is the deep ocean background, consolidated
  // ice approaches white. Amber and red stay reserved for risk coding
  // elsewhere on the map, so the heatmap no longer competes with hazards.
const SEA_ICE_COLOR_STOPS = [
  { value: 0.0, color: [10, 29, 46, 0.10] },      // Open water - deep ocean blue, near transparent
  { value: 0.2, color: [42, 84, 118, 0.22] },     // Trace ice
  { value: 0.4, color: [96, 148, 186, 0.35] },    // Low concentration
  { value: 0.6, color: [150, 196, 228, 0.48] },   // Moderate concentration
  { value: 0.8, color: [207, 233, 255, 0.62] },   // High concentration (#cfe9ff)
  { value: 1.0, color: [255, 255, 255, 0.80] },   // Consolidated pack ice - white
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

    // Create Leaflet ImageOverlay on the dedicated low z-index pane so it
    // renders beneath iceberg trajectories, risk zones, and glyph markers
    seaIceCanvas = L.imageOverlay(canvas.toDataURL(), seaIceBounds, {
      opacity: 0.85,
      interactive: false,
      attribution: '',
      pane: "sea-ice-pane",
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
    flushLabels();
  };

  const baseLayers = { "Satellite Imagery": imagery, "Base Map": street };
  const overlays = { "Recommended / routes": routeLayer, "Icebergs": icebergLayer, "Sea-Ice": seaIceLayer, "Vessel": vesselLayer, "Risk zones": riskLayer, "Labels": labelLayer };
  const layersControl = L.control.layers(baseLayers, overlays, { collapsed: false }).addTo(map);
  createWindControl();
  createLegendControl();
  // Other modules (glaciers.js) may register their own overlay groups and
  // query the vessel position for proximity readouts.
  window.mapController = {
    map,
    updateState,
    registerOverlay: (name, layer) => layersControl.addOverlay(layer, name),
    getVesselPosition: () => vesselMarker && vesselMarker.getLatLng(),
  };
  loadWindField();
  window.addEventListener("resize", () => {
    map.invalidateSize();
    loadWindField();
  });
  window.setTimeout(() => {
    map.invalidateSize();
    loadWindField();
  }, 200);
});
