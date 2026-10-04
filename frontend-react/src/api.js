/* Thin API client. All requests are same-origin and proxied to FastAPI. */
async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = response.statusText;
    try { detail = (await response.json()).detail || detail; } catch { /* ignore */ }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return response.json();
}

export const API = {
  questionnaire: () => request("/api/questionnaire"),
  demoProfile: () => request("/api/demo-profile"),
  improvements: () => request("/api/improvements"),
  methodology: () => request("/api/methodology"),
  privacyAreas: () => request("/api/privacy-areas"),
  stats: () => request("/api/dashboard/stats"),
  sample: (name) => request(`/api/sample-profile?name=${encodeURIComponent(name)}`),
  assess: (answers) =>
    request("/api/assessment", { method: "POST", body: JSON.stringify({ answers, save: true }) }),
  simulate: (answers, improvements) =>
    request("/api/assessment/simulate-improvement", {
      method: "POST", body: JSON.stringify({ answers, improvements }),
    }),
  analyze: (profile, posts) =>
    request("/api/analyze", { method: "POST", body: JSON.stringify({ profile, posts }) }),
};

export const LEVEL_COLORS = {
  LOW: "#22c55e", MODERATE: "#eab308", HIGH: "#f97316", CRITICAL: "#ef4444",
};

export function levelOf(score) {
  if (score <= 20) return "LOW";
  if (score <= 40) return "MODERATE";
  if (score <= 70) return "HIGH";
  return "CRITICAL";
}

export const colorFor = (score) => LEVEL_COLORS[levelOf(score)];
