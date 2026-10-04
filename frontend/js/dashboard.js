/* =========================================================================
   dashboard.js - aggregate privacy analytics dashboard
   ========================================================================= */
const $ = (id) => document.getElementById(id);

async function loadDashboard() {
  try {
    const stats = await API.stats();
    const demo = await API.demoProfile();
    renderCards(stats);
    renderCategoryChart(stats);
    renderDistribution(stats);
    renderWeaknesses(stats);
    renderControls(stats);
    renderFootprint(stats);
    renderRecent(stats);
    renderRubricAverages(stats);
    renderModelComparison(stats);
    $("dashDisclaimer").innerHTML = "<b>Disclaimer.</b> " + escapeHtml(stats.disclaimer);
    renderImprovement(demo.answers);
  } catch (error) {
    $("dashError").classList.remove("hidden");
    $("dashError").textContent = "Dashboard failed to load: " + error.message;
    $("cards").innerHTML = "";
  }
}

function renderCards(stats) {
  const avg = stats.average_score || 0;
  const highRisk = (stats.risk_distribution.HIGH || 0) + (stats.risk_distribution.CRITICAL || 0);
  const topWeak = stats.top_weaknesses[0];
  const highCats = Object.values(stats.category_averages).filter((v) => v >= 41).length;
  $("cards").innerHTML = `
    <div class="card stat"><div class="k">Average Risk Score</div>
      <div class="v" style="color:${colorFor(avg)}">${avg.toFixed(2)}</div>
      <div class="s">across ${stats.total_assessments} stored assessments</div></div>
    <div class="card stat"><div class="k">Dominant Risk Level</div>
      <div class="v"><span class="badge ${levelOf(avg)}">${levelOf(avg)}</span></div>
      <div class="s">based on the average score</div></div>
    <div class="card stat"><div class="k">High-Risk Categories</div>
      <div class="v">${highCats}</div><div class="s">category averages of 41 or above</div></div>
    <div class="card stat"><div class="k">High / Critical Assessments</div>
      <div class="v">${highRisk}</div><div class="s">need priority remediation</div></div>
    <div class="card stat"><div class="k">Top Weakness</div>
      <div class="v" style="font-size:17px">${topWeak ? escapeHtml(topWeak.finding_type) : "–"}</div>
      <div class="s">${topWeak ? topWeak.c + " occurrences" : "no data yet"}</div></div>`;
}

function renderCategoryChart(stats) {
  const entries = Object.entries(stats.category_averages)
    .sort((a, b) => b[1] - a[1]);
  new Chart($("catChart"), {
    type: "bar",
    data: { labels: entries.map(([k]) => stats.category_labels[k] || k),
      datasets: [{ label: "Average risk", data: entries.map(([, v]) => v),
        backgroundColor: entries.map(([, v]) => colorFor(v)), borderRadius: 6 }] },
    options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: { min: 0, max: 100, grid: { color: "rgba(157,176,204,.12)" } },
                y: { grid: { display: false } } },
      plugins: { legend: { display: false } } },
  });
}

function renderDistribution(stats) {
  const order = ["LOW", "MODERATE", "HIGH", "CRITICAL"];
  new Chart($("distChart"), {
    type: "doughnut",
    data: { labels: order,
      datasets: [{ data: order.map((l) => stats.risk_distribution[l] || 0),
        backgroundColor: order.map((l) => LEVEL_COLORS[l]), borderColor: "#111c33", borderWidth: 3 }] },
    options: { responsive: true, maintainAspectRatio: false, cutout: "58%",
      plugins: { legend: { position: "bottom" } } },
  });
}

function renderWeaknesses(stats) {
  const top = stats.top_weaknesses.slice(0, 10);
  new Chart($("weakChart"), {
    type: "bar",
    data: { labels: top.map((w) => w.finding_type.replace(/_/g, " ")),
      datasets: [{ label: "Occurrences", data: top.map((w) => w.c),
        backgroundColor: CHART_PALETTE, borderRadius: 6 }] },
    options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: { grid: { color: "rgba(157,176,204,.12)" } }, y: { grid: { display: false } } },
      plugins: { legend: { display: false } } },
  });
}

function renderControls(stats) {
  // Derived from the account-security and third-party category averages:
  // control adoption = 100 - average category risk.
  const security = stats.category_averages.account_security || 0;
  const apps = stats.category_averages.third_party_risk || 0;
  const tagging = stats.category_averages.tagging_risk || 0;
  new Chart($("ctrlChart"), {
    type: "bar",
    data: { labels: ["Account security controls", "Third-party app hygiene", "Tagging controls"],
      datasets: [
        { label: "Adopted (%)", data: [100 - security, 100 - apps, 100 - tagging],
          backgroundColor: "#22c55e", borderRadius: 6 },
        { label: "Missing / risk (%)", data: [security, apps, tagging],
          backgroundColor: "#ef4444", borderRadius: 6 }] },
    options: { responsive: true, maintainAspectRatio: false,
      scales: { x: { stacked: true, grid: { display: false } },
                y: { stacked: true, min: 0, max: 100, grid: { color: "rgba(157,176,204,.12)" } } },
      plugins: { legend: { position: "bottom" } } },
  });
}

function renderFootprint(stats) {
  const keys = ["digital_footprint", "profile_exposure", "content_exposure", "location_exposure"];
  new Chart($("footChart"), {
    type: "radar",
    data: { labels: keys.map((k) => stats.category_labels[k]),
      datasets: [{ label: "Average assessed risk", data: keys.map((k) => stats.category_averages[k] || 0),
        backgroundColor: "rgba(34,211,238,.22)", borderColor: "#22d3ee", pointRadius: 4 }] },
    options: { responsive: true, maintainAspectRatio: false,
      scales: { r: { min: 0, max: 100, grid: { color: "rgba(157,176,204,.2)" },
        angleLines: { color: "rgba(157,176,204,.2)" }, ticks: { backdropColor: "transparent" } } },
      plugins: { legend: { position: "bottom" } } },
  });
}

async function renderImprovement(demoAnswers) {
  const keys = ["enable_mfa", "make_phone_private", "disable_realtime_location",
    "enable_tag_review", "review_third_party_apps", "review_old_posts",
    "verify_unknown_requests", "enable_login_alerts", "make_birthday_private",
    "make_location_private", "make_travel_private", "review_privacy_settings"];
  const sim = await API.simulate(demoAnswers, keys);
  new Chart($("impChart"), {
    type: "bar",
    data: { labels: ["Overall risk score"],
      datasets: [
        { label: `Before (${sim.current_risk_level})`, data: [sim.current_score],
          backgroundColor: "#f97316", borderRadius: 6 },
        { label: `After simulation (${sim.new_risk_level})`, data: [sim.new_score],
          backgroundColor: "#22c55e", borderRadius: 6 }] },
    options: { responsive: true, maintainAspectRatio: false,
      scales: { y: { min: 0, max: 100, grid: { color: "rgba(157,176,204,.12)" } } },
      plugins: { legend: { position: "bottom" },
        title: { display: true, text: `Framework simulation · risk reduction −${sim.risk_reduction.toFixed(2)} points` } } },
  });
}

function renderRubricAverages(stats) {
  const caps = { pii: 25, geo: 20, child: 15, work: 10, privacy: 10, link: 10, handle: 5, tracker: 5 };
  const keys = Object.keys(caps).filter((k) => k in (stats.rubric_averages || {}));
  if (!keys.length) return;
  new Chart($("rubricChart"), {
    type: "bar",
    data: { labels: keys.map((k) => stats.rubric_labels[k] || k),
      datasets: [
        { label: "Average points", data: keys.map((k) => stats.rubric_averages[k]),
          backgroundColor: "#f97316", borderRadius: 5 },
        { label: "Maximum", data: keys.map((k) => caps[k]),
          backgroundColor: "rgba(148,163,184,.25)", borderRadius: 5 }] },
    options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: { min: 0, max: 25, grid: { color: "rgba(157,176,204,.12)" } },
                y: { grid: { display: false }, ticks: { font: { size: 10.5 } } } },
      plugins: { legend: { position: "bottom" } } },
  });
}

function renderModelComparison(stats) {
  new Chart($("modelChart"), {
    type: "bar",
    data: { labels: ["Average score across stored assessments"],
      datasets: [
        { label: "Model A — Privacy Assessment Score", data: [stats.average_score],
          backgroundColor: "#3b82f6", borderRadius: 6 },
        { label: "Model B — Privacy Exposure Rubric", data: [stats.average_exposure_score],
          backgroundColor: "#a78bfa", borderRadius: 6 }] },
    options: { responsive: true, maintainAspectRatio: false,
      scales: { y: { min: 0, max: 100, grid: { color: "rgba(157,176,204,.12)" } } },
      plugins: { legend: { position: "bottom" },
        title: { display: true, text: "Complementary models — not mathematically equivalent" } } },
  });
}

function renderRecent(stats) {
  $("recentTable").innerHTML = `
    <thead><tr><th>Assessment ID</th><th>Model A score</th><th>Risk level</th>
      <th>Model B exposure</th><th>Created</th></tr></thead>
    <tbody>${stats.recent_assessments.map((r) => `
      <tr><td><code>${escapeHtml(r.assessment_id)}</code></td>
        <td><b>${r.overall_score.toFixed(2)}</b></td>
        <td><span class="badge ${r.risk_level}">${r.risk_level}</span></td>
        <td>${(r.exposure_score ?? 0).toFixed(2)}</td>
        <td>${escapeHtml(r.created_at)}</td></tr>`).join("") ||
      '<tr><td colspan="5">No assessments stored yet.</td></tr>'}</tbody>`;
}

document.addEventListener("DOMContentLoaded", loadDashboard);
