/* =========================================================================
   assessment.js - questionnaire rendering, scoring results, simulator
   ========================================================================= */
let QUESTIONNAIRE = null;
let ANSWERS = {};
let RESULT = null;
let CHARTS = {};
const el = (id) => document.getElementById(id);

/* ------------------------- questionnaire ------------------------------ */
async function loadQuestionnaire() {
  const box = el("questions");
  showLoading(box, "Loading questionnaire…");
  try {
    QUESTIONNAIRE = await API.questionnaire();
    el("qMeta").textContent =
      `${QUESTIONNAIRE.total_questions} questions · ${QUESTIONNAIRE.sections.length} categories · ` +
      "answers are scored locally by a deterministic model";
    renderQuestions();
  } catch (error) { showError(box, error.message); }
}

function sectionSlug(name) {
  return "sec-" + name.replace(/^[A-J]\.\s*/, "").toLowerCase().replace(/[^a-z]+/g, "-");
}

function renderQuestions() {
  el("questions").innerHTML = QUESTIONNAIRE.sections.map((section) => `
    <div class="q-section" id="${sectionSlug(section.section)}">
      <h3>${escapeHtml(section.section)} <span style="color:var(--muted);font-weight:500;
        font-size:13px">(${section.questions.length} questions)</span></h3>
      ${section.questions.map((q) => `
        <div class="q" id="q-${q.id}">
          <div class="qtext"><span class="qid">${q.id}</span><span>${escapeHtml(q.text)}</span></div>
          <div class="opts">
            ${q.options.map((o) => `
              <label class="opt"><input type="radio" name="${q.id}" value="${o.value}">
              <span>${escapeHtml(o.label)}</span></label>`).join("")}
          </div>
        </div>`).join("")}
    </div>`).join("");

  el("questions").addEventListener("change", (event) => {
    if (event.target.type !== "radio") return;
    ANSWERS[event.target.name] = event.target.value;
    el("q-" + event.target.name).classList.add("answered");
    updateProgress();
  });
  updateProgress();
}

function updateProgress() {
  const total = QUESTIONNAIRE.total_questions;
  const done = Object.keys(ANSWERS).length;
  const pct = Math.round((done / total) * 100);
  el("progressBar").style.width = pct + "%";
  el("progressText").textContent = `${done} of ${total} answered (${pct}%)`;
  el("submitBtn").disabled = done / total < 0.6;
}

function applyAnswers(answers) {
  ANSWERS = { ...answers };
  Object.entries(ANSWERS).forEach(([qid, value]) => {
    const input = document.querySelector(`input[name="${qid}"][value="${value}"]`);
    if (input) { input.checked = true; el("q-" + qid).classList.add("answered"); }
  });
  updateProgress();
}

/* ------------------------------ results -------------------------------- */
function renderTopCards(result) {
  const controls = `${result.security_controls_enabled}/${result.security_controls_total}`;
  el("topCards").innerHTML = `
    <div class="card stat"><div class="k">Overall Risk Score</div>
      <div class="v" style="color:${colorFor(result.overall_score)}">${result.overall_score.toFixed(2)}</div>
      <div class="s">out of 100 · higher = more exposure</div></div>
    <div class="card stat"><div class="k">Risk Level</div>
      <div class="v"><span class="badge ${result.risk_level}">${result.risk_level}</span></div>
      <div class="s">thresholds 20 / 40 / 70</div></div>
    <div class="card stat"><div class="k">High-Risk Categories</div>
      <div class="v">${result.high_risk_categories.length}</div>
      <div class="s">categories scoring 41 or above</div></div>
    <div class="card stat"><div class="k">Exposure Rubric (Model B)</div>
      <div class="v" style="color:${colorFor(result.exposure_rubric.score)}">${result.exposure_rubric.score.toFixed(1)}</div>
      <div class="s">8-category exposure score</div></div>
    <div class="card stat"><div class="k">Recommendations</div>
      <div class="v">${result.recommendations.length}</div>
      <div class="s">${result.priority_summary.IMMEDIATE} immediate ·
        ${result.priority_summary.IMPORTANT} important</div></div>
    <div class="card stat"><div class="k">Security Controls Enabled</div>
      <div class="v">${controls}</div><div class="s">MFA, alerts, tag review, app review…</div></div>`;
}

function renderCharts(result) {
  const labels = Object.keys(result.category_scores).map((k) => result.category_labels[k]);
  const values = Object.values(result.category_scores);

  if (CHARTS.radar) CHARTS.radar.destroy();
  CHARTS.radar = new Chart(el("radarChart"), {
    type: "radar",
    data: { labels, datasets: [{ label: "Assessed risk (0–100)", data: values,
      backgroundColor: "rgba(59,130,246,.25)", borderColor: "#3b82f6",
      pointBackgroundColor: values.map(colorFor), pointRadius: 4, borderWidth: 2 }] },
    options: { responsive: true, maintainAspectRatio: false,
      scales: { r: { min: 0, max: 100, ticks: { stepSize: 25, backdropColor: "transparent" },
        grid: { color: "rgba(157,176,204,.2)" }, angleLines: { color: "rgba(157,176,204,.2)" },
        pointLabels: { font: { size: 11 } } } },
      plugins: { legend: { position: "bottom" } } },
  });

  if (CHARTS.cat) CHARTS.cat.destroy();
  CHARTS.cat = new Chart(el("catChart"), {
    type: "bar",
    data: { labels, datasets: [{ label: "Category risk score", data: values,
      backgroundColor: values.map(colorFor), borderRadius: 6 }] },
    options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: { min: 0, max: 100, grid: { color: "rgba(157,176,204,.12)" } },
                y: { grid: { display: false } } },
      plugins: { legend: { display: false } } },
  });
}

function renderRubric(result) {
  const rubric = result.exposure_rubric;
  el("rubricBadge").innerHTML =
    `<div style="text-align:right"><div style="font-size:30px;font-weight:800;
      color:${colorFor(rubric.score)}">${rubric.score.toFixed(2)}<span
      style="font-size:15px;color:var(--muted)">/100</span></div>
      <span class="badge ${rubric.risk_level}">${rubric.risk_level}</span></div>`;

  if (CHARTS.rubric) CHARTS.rubric.destroy();
  CHARTS.rubric = new Chart(el("rubricChart"), {
    type: "bar",
    data: { labels: rubric.categories.map((c) => c.label),
      datasets: [
        { label: "Points awarded", data: rubric.categories.map((c) => c.points),
          backgroundColor: "#f97316", borderRadius: 5 },
        { label: "Maximum", data: rubric.categories.map((c) => c.max_points),
          backgroundColor: "rgba(148,163,184,.25)", borderRadius: 5 }] },
    options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: { min: 0, max: 25, grid: { color: "rgba(157,176,204,.12)" } },
                y: { grid: { display: false }, ticks: { font: { size: 10.5 } } } },
      plugins: { legend: { position: "bottom" } } },
  });

  el("rubricTable").innerHTML = `
    <thead><tr><th>Exposure category</th><th>Points</th><th>Max</th>
      <th>Share of cap</th><th>Capped</th></tr></thead>
    <tbody>${rubric.categories.map((c) => `
      <tr><td>${escapeHtml(c.label)}</td><td><b>${c.points.toFixed(2)}</b></td>
        <td>${c.max_points}</td>
        <td><div class="meter"><span style="width:${Math.min(c.percent_of_cap, 100)}%;
          background:${colorFor(c.percent_of_cap)}"></span></div></td>
        <td>${c.capped ? "yes" : "—"}</td></tr>`).join("")}
    </tbody>`;

  el("methodologyNote").innerHTML =
    `<b>Two complementary models.</b> ${escapeHtml(result.methodology.relationship)}
     <br><br><b>Formula (Model B):</b> <code>${escapeHtml(rubric.formula)}</code>`;
}

function renderTables(result) {
  el("catTable").innerHTML = `
    <thead><tr><th>Category</th><th>Score</th><th>Level</th><th>Weight</th>
      <th>Contribution</th><th>Exposure</th></tr></thead><tbody>
    ${result.score_breakdown.map((row) => `
      <tr><td>${escapeHtml(row.label)}</td>
        <td><b>${row.score.toFixed(2)}</b></td>
        <td><span class="badge ${row.level}">${row.level}</span></td>
        <td>${row.weight_percent.toFixed(0)}%</td>
        <td>${row.contribution.toFixed(2)}</td>
        <td><div class="meter"><span style="width:${Math.min(row.score,100)}%;
          background:${colorFor(row.score)}"></span></div></td></tr>`).join("")}
    </tbody>`;

  el("findTable").innerHTML = `
    <thead><tr><th>Severity</th><th>Category</th><th>Finding</th><th>Recommended action</th></tr></thead>
    <tbody>${result.findings.length ? result.findings.slice(0, 20).map((f) => `
      <tr><td><span class="sev ${f.severity}">${f.severity}</span></td>
        <td>${escapeHtml(f.category_label)}</td>
        <td><b>${escapeHtml(f.finding)}</b><div style="color:var(--muted);font-size:12.5px;
          margin-top:4px">${escapeHtml(f.explanation)}</div></td>
        <td>${escapeHtml(f.recommended_action)}</td></tr>`).join("")
      : '<tr><td colspan="4">No significant findings detected — strong privacy posture.</td></tr>'}
    </tbody>`;

  el("recTable").innerHTML = `
    <thead><tr><th>Priority</th><th>Category</th><th>Trigger</th><th>Recommendation</th></tr></thead>
    <tbody>${result.recommendations.map((r) => `
      <tr><td><span class="pri ${r.priority.split(" ")[0]}">${r.priority}</span></td>
        <td>${escapeHtml(r.category_label)}</td>
        <td>${escapeHtml(r.trigger)}</td>
        <td>${escapeHtml(r.recommendation)}</td></tr>`).join("")}</tbody>`;
}

async function renderSimulator(result) {
  el("simCurrent").textContent = result.overall_score.toFixed(2);
  el("simCurrent").style.color = colorFor(result.overall_score);
  el("simCurrentLevel").innerHTML = `<span class="badge ${result.risk_level}">${result.risk_level}</span>`;
  el("simCurrentFindings").textContent = `${result.findings.length} findings detected`;
  const data = await API.improvements();
  el("impList").innerHTML = data.improvements.map((i) => `
    <label class="imp"><input type="checkbox" value="${i.key}">
      <span style="font-size:13.5px">${escapeHtml(i.label)}</span></label>`).join("");
}

async function runSimulation() {
  const keys = [...document.querySelectorAll("#impList input:checked")].map((i) => i.value);
  if (!keys.length) { el("simChanges").innerHTML =
    '<span style="color:#fca5a5">Select at least one improvement.</span>'; return; }
  el("simNew").textContent = "…";
  try {
    const sim = await API.simulate(ANSWERS, keys);
    el("simNew").textContent = sim.new_score.toFixed(2);
    el("simNew").style.color = colorFor(sim.new_score);
    el("simNewLevel").innerHTML = `<span class="badge ${sim.new_risk_level}">${sim.new_risk_level}</span>`;
    el("simReduction").innerHTML =
      `<b style="color:#4ade80">Risk reduction: −${sim.risk_reduction.toFixed(2)} points
       (−${sim.risk_reduction_percent.toFixed(1)}%)</b><br>
       <span style="color:var(--muted);font-size:12.5px">Findings ${sim.findings_before}
       → ${sim.findings_after}</span>`;
    el("simChanges").innerHTML = "<b>Changes applied:</b><br>" +
      sim.changes_applied.map((c) => "• " + escapeHtml(c.label)).join("<br>");

    const labels = Object.keys(sim.current_category_scores).map((k) => RESULT.category_labels[k]);
    if (CHARTS.sim) CHARTS.sim.destroy();
    CHARTS.sim = new Chart(el("simChart"), {
      type: "bar",
      data: { labels, datasets: [
        { label: "Current", data: Object.values(sim.current_category_scores),
          backgroundColor: "#f97316", borderRadius: 5 },
        { label: "Simulated after improvements", data: Object.values(sim.new_category_scores),
          backgroundColor: "#22c55e", borderRadius: 5 }] },
      options: { responsive: true, maintainAspectRatio: false,
        scales: { y: { min: 0, max: 100, grid: { color: "rgba(157,176,204,.12)" } },
                  x: { grid: { display: false }, ticks: { maxRotation: 45, minRotation: 30 } } },
        plugins: { legend: { position: "bottom" } } },
    });
  } catch (error) { el("simChanges").innerHTML =
    `<span style="color:#fca5a5">${escapeHtml(error.message)}</span>`; }
}

async function submitAssessment() {
  const button = el("submitBtn");
  button.disabled = true; button.textContent = "Calculating…";
  el("submitError").classList.add("hidden");
  try {
    RESULT = await API.assess(ANSWERS);
    el("quizView").classList.add("hidden");
    el("resultView").classList.remove("hidden");
    el("resMeta").textContent =
      `Assessment ID ${RESULT.assessment_id} · ${RESULT.created_at} · ` +
      `${RESULT.answered_questions}/${RESULT.total_questions} questions answered`;
    el("resDisclaimer").innerHTML = "<b>Disclaimer.</b> " + escapeHtml(RESULT.disclaimer);
    renderTopCards(RESULT); renderCharts(RESULT); renderRubric(RESULT); renderTables(RESULT);
    await renderSimulator(RESULT);
    window.scrollTo({ top: 0, behavior: "instant" });
  } catch (error) {
    const box = el("submitError");
    box.textContent = "Assessment failed: " + error.message;
    box.classList.remove("hidden");
  } finally { button.disabled = false; button.textContent = "▶  Calculate Privacy Risk"; }
}

function downloadReport(format) {
  const form = document.createElement("form");
  form.method = "POST";
  form.action = "/api/assessment/report?fmt=" + format;
  form.target = "_blank";
  // POST as JSON is not possible with a plain form, so use fetch + blob instead.
  fetch(form.action, { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers: ANSWERS, save: true }) })
    .then((r) => r.blob())
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `privacy_report_${RESULT.assessment_id}.${format}`;
      link.click(); URL.revokeObjectURL(url);
    });
}

/* ------------------------------- wiring -------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  loadQuestionnaire();
  el("submitBtn").addEventListener("click", submitAssessment);
  el("simRun").addEventListener("click", runSimulation);
  el("backBtn").addEventListener("click", () => {
    el("resultView").classList.add("hidden");
    el("quizView").classList.remove("hidden");
    window.scrollTo({ top: 0 });
  });
  el("clearAll").addEventListener("click", () => {
    ANSWERS = {};
    document.querySelectorAll('#questions input[type="radio"]').forEach((i) => (i.checked = false));
    document.querySelectorAll(".q").forEach((q) => q.classList.remove("answered"));
    updateProgress();
  });
  el("loadDemo").addEventListener("click", async () => {
    const demo = await API.demoProfile();
    applyAnswers(demo.answers);
  });
  el("reportHtml").addEventListener("click", () => downloadReport("html"));
  el("reportPdf").addEventListener("click", () => downloadReport("pdf"));
});
