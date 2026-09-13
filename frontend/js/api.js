const API_BASE_URL = "/api";

async function fetchJson(url, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const requestOptions = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${url}`, requestOptions);
    const text = await response.text();

    if (!response.ok) {
      let message = `Request failed for ${url}: ${response.status}`;
      try {
        const payload = JSON.parse(text);
        if (payload && payload.detail) {
          message = payload.detail;
        }
      } catch (error) {
        // Ignore JSON parsing errors for failed responses and surface the status code instead.
      }
      throw new Error(message);
    }

    if (!text) {
      return null;
    }

    try {
      return JSON.parse(text);
    } catch (error) {
      throw new Error(`Invalid JSON returned for ${url}`);
    }
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error(`Unexpected error while calling ${url}`);
  }
}

window.api = {
  loading: {},
  setLoading(name, isLoading) {
    this.loading[name] = isLoading;
    const statusElement = document.getElementById("system-status");
    if (statusElement) {
      statusElement.textContent = isLoading
        ? `Loading ${name}…`
        : "Backend available";
    }
  },
  async request(endpoint, options = {}) {
    const key = endpoint;
    this.setLoading(key, true);
    try {
      return await fetchJson(endpoint, options);
    } finally {
      this.setLoading(key, false);
    }
  },
  health: () => window.api.request("/health"),
  analyzeVoyage: (payload) => window.api.request("/voyage/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  getSeaIce: () => window.api.request("/sea-ice"),
  getIcebergs: () => window.api.request("/icebergs"),
  predictIcebergs: () => window.api.request("/icebergs/predict", { method: "POST", body: JSON.stringify({}) }),
  optimizeRoutes: () => window.api.request("/routes/optimize", { method: "POST", body: JSON.stringify({}) }),
  getEnvironment: () => window.api.request("/environment"),
  getWind: (refresh = false, bounds = null) => {
    const params = new URLSearchParams();
    if (refresh) params.set("refresh", "true");
    if (bounds) {
      Object.entries(bounds).forEach(([key, value]) => params.set(key, Number(value).toFixed(6)));
    }
    const query = params.toString();
    return window.api.request(`/wind${query ? `?${query}` : ""}`);
  },
  createTrip: (payload) => window.api.request("/trips", { method: "POST", body: JSON.stringify(payload) }),
  listTrips: () => window.api.request("/trips"),
  getTrip: (tripId) => window.api.request(`/trips/${encodeURIComponent(tripId)}`),
  startTrip: (tripId) => window.api.request(`/trips/${encodeURIComponent(tripId)}/start`, { method: "POST" }),
  pauseTrip: (tripId) => window.api.request(`/trips/${encodeURIComponent(tripId)}/pause`, { method: "POST" }),
  resetTrip: (tripId) => window.api.request(`/trips/${encodeURIComponent(tripId)}/reset`, { method: "POST" }),
  stepTrip: (tripId, steps) => window.api.request(`/trips/${encodeURIComponent(tripId)}/step`, { method: "POST", body: JSON.stringify({ steps }) }),
  seekTrip: (tripId, targetTime) => window.api.request(`/trips/${encodeURIComponent(tripId)}/seek`, { method: "POST", body: JSON.stringify({ target_time: targetTime }) }),
  setTripSpeed: (tripId, speed) => window.api.request(`/trips/${encodeURIComponent(tripId)}/speed`, { method: "POST", body: JSON.stringify({ speed }) }),
  getTripState: (tripId) => window.api.request(`/trips/${encodeURIComponent(tripId)}/state`),
  getTripTimeline: (tripId) => window.api.request(`/trips/${encodeURIComponent(tripId)}/timeline`),
  getTripEvents: (tripId) => window.api.request(`/trips/${encodeURIComponent(tripId)}/events`),
};
