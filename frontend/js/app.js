/* =========================================================================
   app.js - shared helpers (API client, formatting, UI states)
   ========================================================================= */
const API = (function () {
  const base = "";                     // same origin: backend serves the frontend
  async function request(path, options = {}) {
    const response = await fetch(base + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!response.ok) {
      let detail = response.statusText;
      try { detail = (await response.json()).detail || detail; } catch (e) { /* noop */ }
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    return response.json();
  }
  return {
    questionnaire: () => request("/api/questionnaire"),
    demoProfile: () => request("/api/demo-profile"),
    improvements: () => request("/api/improvements"),
    checklist: () => request("/api/privacy-checklist"),
    stats: () => request("/api/dashboard/stats"),
    methodology: () => request("/api/methodology"),
    privacyAreas: () => request("/api/privacy-areas"),
    sampleProfile: (name) => request("/api/sample-profile?name=" + encodeURIComponent(name)),
    analyze: (profile, posts) => request("/api/analyze", {
      method: "POST", body: JSON.stringify({ profile, posts }) }),
    schema: () => request("/api/database/schema"),
    assess: (answers) => request("/api/assessment", {
      method: "POST", body: JSON.stringify({ answers, save: true }) }),
    simulate: (answers, improvements) => request("/api/assessment/simulate-improvement", {
      method: "POST", body: JSON.stringify({ answers, improvements }) }),
  };
})();

const LEVEL_COLORS = { LOW: "#22c55e", MODERATE: "#eab308", HIGH: "#f97316", CRITICAL: "#ef4444" };
const CHART_PALETTE = ["#3b82f6", "#22d3ee", "#a78bfa", "#f472b6", "#fb923c",
                       "#facc15", "#4ade80", "#38bdf8", "#f87171", "#c084fc"];

function levelOf(score) {
  if (score <= 20) return "LOW";
  if (score <= 40) return "MODERATE";
  if (score <= 70) return "HIGH";
  return "CRITICAL";
}
function colorFor(score) { return LEVEL_COLORS[levelOf(score)]; }
function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function showLoading(el, message = "Loading…") {
  el.innerHTML = `<div class="loading"><div class="spinner"></div><span>${escapeHtml(message)}</span></div>`;
}
function showError(el, message) {
  el.innerHTML = `<div class="error"><b>Something went wrong.</b><br>${escapeHtml(message)}</div>`;
}
function chartDefaults() {
  if (window.Chart) {
    Chart.defaults.color = "#9db0cc";
    Chart.defaults.font.family = "'Segoe UI',system-ui,Arial,sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
  }
}
document.addEventListener("DOMContentLoaded", chartDefaults);
