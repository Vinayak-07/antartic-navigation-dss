document.addEventListener("DOMContentLoaded", () => {
  const systemStatus = document.getElementById("system-status");
  const updateTime = document.getElementById("last-update");

  const setStatus = (message, isError = false) => {
    if (!systemStatus) {
      return;
    }
    systemStatus.textContent = message;
    systemStatus.style.color = isError ? "#ff9e9e" : "#d9f7ff";
  };

  const setLastUpdate = () => {
    if (!updateTime) {
      return;
    }
    const now = new Date();
    updateTime.textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const updateText = (id, value) => {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = value ?? "--";
    }
  };

  const populateDashboard = async () => {
    try {
      const health = await window.api.health();
      setStatus(health && health.status ? `${health.status.toUpperCase()}` : "ONLINE");
      setLastUpdate();
      document.getElementById("data-status").textContent = "Synthetic scientific simulation prototype";
    } catch (error) {
      setStatus("API unavailable", true);
      document.getElementById("data-status").textContent = "No feed";
      return;
    }

    setLastUpdate();
  };

  populateDashboard();
});
