// Glacier reference layer (see .glacier-marker styles in /css/map.css).
// Positions are approximate real-world reference points for major East
// Antarctic ice shelves / outlet glaciers within the operational map window,
// following the SCAR / Australian Antarctic Data Centre gazetteer entries
// referenced in the dashboard's data-provenance list. This layer is static
// reference geography: no simulation state, no forecasts.
//
// Markers stay collision-safe per the phase 76 label rules: the glacier name
// is revealed as a hover tooltip (.glacier-label) instead of a permanently
// drawn label, and selection opens the "Nearby Glaciers" inspector panel.
document.addEventListener("DOMContentLoaded", () => {
  if (!window.mapController || typeof L === "undefined") return;
  const map = window.mapController.map;
  const detailsPanel = document.getElementById("glacier-details");
  if (!detailsPanel) return;

  const GLACIERS = [
    { id: "AMERY-IS", name: "Amery Ice Shelf", type: "Ice shelf", lat: -70.0, lon: 72.0 },
    { id: "LAMBERT-GL", name: "Lambert Glacier", type: "Outlet glacier", lat: -70.5, lon: 68.0 },
    { id: "PUBLICATIONS-IS", name: "Publications Ice Shelf", type: "Ice shelf", lat: -67.5, lon: 62.0 },
    { id: "WEST-IS", name: "West Ice Shelf", type: "Ice shelf", lat: -67.0, lon: 84.5 },
    { id: "RIISER-LARSEN-IS", name: "Riiser-Larsen Ice Shelf", type: "Ice shelf", lat: -70.8, lon: 17.5 },
    { id: "LAZAREV-IS", name: "Lazarev Ice Shelf", type: "Ice shelf", lat: -69.8, lon: 14.5 },
  ];

  const glacierLayer = L.layerGroup().addTo(map);
  window.mapController.registerOverlay("Glaciers (reference)", glacierLayer);

  // The operational view is permanently zoomed out (locked view), so glyph
  // scale only needs a coarse step per zoom level rather than continuous
  // rescaling (see scaleForZoom note in /css/map.css).
  const scaleForZoom = (zoom) => (zoom >= 5 ? 1.5 : zoom >= 4 ? 1.25 : zoom >= 3 ? 1 : 0.8);
  const scale = scaleForZoom(map.getZoom());

  const coordinates = (glacier) => `${Math.abs(glacier.lat).toFixed(1)}°S, ${Math.abs(glacier.lon).toFixed(1)}°E`;
  const number = (value, digits = 1) => value === undefined || value === null || Number.isNaN(Number(value)) ? "--" : Number(value).toFixed(digits);
  // Display-only great-circle distance between two reference points; voyage
  // risk screening itself stays in the backend simulation.
  const haversineKm = (first, second) => {
    const toRad = (deg) => (deg * Math.PI) / 180;
    const dLat = toRad(second.lat - first.lat);
    const dLon = toRad(second.lon - first.lon);
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(first.lat)) * Math.cos(toRad(second.lat)) * Math.sin(dLon / 2) ** 2;
    return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  };

  const renderDetails = (glacier) => {
    const vessel = window.mapController.getVesselPosition();
    const distanceLine = vessel
      ? `<h4>Proximity screening</h4><dl><dt>Distance from vessel</dt><dd>${number(haversineKm(glacier, { lat: vessel.lat, lon: vessel.lng }), 0)} km</dd></dl>`
      : "";
    detailsPanel.innerHTML = `
      <div><strong>${glacier.name}</strong><span class="details-risk">${glacier.type}</span></div>
      <h4>Reference position</h4>
      <dl>
        <dt>Coordinates</dt><dd>${coordinates(glacier)}</dd>
        <dt>Gazetteer ID</dt><dd>${glacier.id}</dd>
        <dt>Position accuracy</dt><dd>Approximate</dd>
      </dl>
      ${distanceLine}
      <p style="margin-top:0.45rem">Source: SCAR / AAD gazetteer reference entry. Static geography — not part of the simulation state.</p>`;
  };

  let selectedMarker = null;
  GLACIERS.forEach((glacier) => {
    const size = Math.round(24 * scale);
    const marker = L.marker([glacier.lat, glacier.lon], {
      icon: L.divIcon({
        className: "glacier-marker",
        html: `<span class="glacier-glyph" style="--glacier-scale:${scale}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 20 L5.5 9.5 L8.5 13.5 L11.5 5.5 L14.5 11.5 L17 7.5 L19.5 14 L21.5 20 Z"></path></svg></span>`,
        iconSize: [size, size],
        iconAnchor: [Math.round(size / 2), Math.round(size / 2)],
      }),
      title: `${glacier.name} · ${glacier.type}`,
    }).addTo(glacierLayer);
    marker.bindTooltip(glacier.name, { className: "glacier-label", direction: "top", offset: [0, -Math.round(12 * scale)] });
    marker.on("click", () => {
      if (selectedMarker) selectedMarker.getElement()?.classList.remove("glacier-selected");
      selectedMarker = marker;
      marker.getElement()?.classList.add("glacier-selected");
      renderDetails(glacier);
      document.dispatchEvent(new CustomEvent("glacier-selected", { detail: { glacier } }));
    });
  });
});
