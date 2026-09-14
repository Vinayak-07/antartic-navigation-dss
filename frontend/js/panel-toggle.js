// Panel show/hide toggles (see .panel-toggle styles in /css/style.css).
// Collapses a fixed side panel off-canvas by toggling the .collapsed class
// the stylesheet already defines; the docked button itself just flips its
// chevron via .is-collapsed and keeps aria-expanded in sync.
document.addEventListener("DOMContentLoaded", () => {
  const wire = (buttonId, panelId) => {
    const button = document.getElementById(buttonId);
    const panel = document.getElementById(panelId);
    if (!button || !panel) return;
    const apply = (collapsed) => {
      panel.classList.toggle("collapsed", collapsed);
      button.classList.toggle("is-collapsed", collapsed);
      button.setAttribute("aria-expanded", String(!collapsed));
    };
    button.addEventListener("click", () => apply(!panel.classList.contains("collapsed")));
  };
  wire("toggle-left-panel", "left-panel");
  wire("toggle-right-panel", "right-panel");
});
