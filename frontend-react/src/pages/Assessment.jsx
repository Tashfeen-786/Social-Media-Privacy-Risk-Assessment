import { useEffect, useMemo, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, PolarAngleAxis, PolarGrid,
  PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { API, colorFor } from "../api.js";
import { Badge, ErrorBox, Loading, StatCard } from "../components/Common.jsx";

function sectionSlug(name) {
  return "sec-" + name.replace(/^CATEGORY [A-J]:\s*/, "").toLowerCase().replace(/[^a-z]+/g, "-");
}

export default function Assessment() {
  const [questionnaire, setQuestionnaire] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [improvements, setImprovements] = useState([]);
  const [selected, setSelected] = useState([]);
  const [simulation, setSimulation] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    API.questionnaire().then(setQuestionnaire).catch((e) => setError(e.message));
    API.improvements().then((d) => setImprovements(d.improvements)).catch(() => {});
  }, []);

  const total = questionnaire?.total_questions ?? 0;
  const answered = Object.keys(answers).length;
  const progress = total ? Math.round((answered / total) * 100) : 0;

  const radarData = useMemo(() => {
    if (!result) return [];
    return Object.entries(result.category_scores).map(([key, value]) => ({
      category: result.category_labels[key], score: value,
    }));
  }, [result]);

  async function loadDemo() {
    const demo = await API.demoProfile();
    setAnswers(demo.answers);
  }

  async function submit() {
    setBusy(true); setError("");
    try {
      const data = await API.assess(answers);
      setResult(data); setSimulation(null);
      window.scrollTo({ top: 0 });
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  async function runSimulation() {
    if (!selected.length) { setError("Select at least one improvement."); return; }
    setError("");
    try {
      setSimulation(await API.simulate(answers, selected));
    } catch (e) { setError(e.message); }
  }

  if (error && !questionnaire) return <ErrorBox message={error} />;
  if (!questionnaire) return <Loading text="Loading questionnaire…" />;

  // ------------------------------- results view -------------------------
  if (result) {
    const rubric = result.exposure_rubric;
    const rubricData = rubric.categories.map((c) => ({
      name: c.label, points: c.points, max: c.max_points,
    }));
    const simData = simulation
      ? Object.keys(simulation.current_category_scores).map((key) => ({
          name: result.category_labels[key],
          before: simulation.current_category_scores[key],
          after: simulation.new_category_scores[key],
        }))
      : [];

    return (
      <>
        <div className="section" style={{ marginTop: 28 }}>
          <div className="section-head">
            <div><h2>Assessment Results</h2>
              <p>{result.assessment_id} · {result.created_at} · {result.answered_questions}/
                {result.total_questions} answered</p></div>
            <button className="btn btn-ghost btn-sm" onClick={() => setResult(null)}>
              Edit answers</button>
          </div>
        </div>

        <div className="grid g3" id="topCards">
          <StatCard label="Model A · Overall Risk Score"
            value={result.overall_score.toFixed(2)} sub="0–100, higher = more exposure"
            color={colorFor(result.overall_score)} />
          <StatCard label="Risk Level" value={<Badge level={result.risk_level} />}
            sub="thresholds 20 / 40 / 70" />
          <StatCard label="Model B · Exposure Rubric"
            value={rubric.score.toFixed(2)} sub={`8 categories · ${rubric.risk_level}`}
            color={colorFor(rubric.score)} />
          <StatCard label="High-Risk Categories" value={result.high_risk_categories.length}
            sub="scoring 41 or above" />
          <StatCard label="Recommendations" value={result.recommendations.length}
            sub={`${result.priority_summary.IMMEDIATE} immediate`} />
          <StatCard label="Security Controls Enabled"
            value={`${result.security_controls_enabled}/${result.security_controls_total}`}
            sub="MFA, alerts, tag review, app review…" />
        </div>

        <div className="section grid g2" id="chartsRow">
          <div className="card"><h3>Privacy Risk Radar (Model A)</h3>
            <p>Higher value = higher assessed risk.</p>
            <div className="chart-box tall">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(157,176,204,.25)" />
                  <PolarAngleAxis dataKey="category" tick={{ fill: "#9db0cc", fontSize: 10 }} />
                  <PolarRadiusAxis domain={[0, 100]} tick={{ fill: "#9db0cc", fontSize: 10 }} />
                  <Radar dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.35} />
                  <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card"><h3>Exposure Rubric contributions (Model B)</h3>
            <p>Points awarded against each category cap · min(100, sum).</p>
            <div className="chart-box tall">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={rubricData} layout="vertical"
                          margin={{ left: 120, right: 10, top: 5, bottom: 5 }}>
                  <CartesianGrid stroke="rgba(157,176,204,.12)" />
                  <XAxis type="number" domain={[0, 25]} tick={{ fill: "#9db0cc", fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" width={120}
                         tick={{ fill: "#9db0cc", fontSize: 10 }} />
                  <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
                  <Legend />
                  <Bar dataKey="max" name="Maximum" fill="rgba(148,163,184,.3)" />
                  <Bar dataKey="points" name="Points" fill="#f97316" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="section card" id="catTableCard">
          <h3>Category score breakdown &amp; weighting (Model A)</h3>
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead><tr><th>Category</th><th>Score</th><th>Level</th><th>Weight</th>
                <th>Contribution</th></tr></thead>
              <tbody>
                {result.score_breakdown.map((row) => (
                  <tr key={row.category}>
                    <td>{row.label}</td><td><b>{row.score.toFixed(2)}</b></td>
                    <td><Badge level={row.level} /></td>
                    <td>{row.weight_percent.toFixed(0)}%</td>
                    <td>{row.contribution.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="notice" style={{ marginTop: 14 }}>
            <b>Two complementary models.</b> {result.methodology.relationship}
          </div>
        </div>

        <div className="section card" id="findingsCard">
          <h3>Top Privacy Findings</h3>
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead><tr><th>Severity</th><th>Category</th><th>Finding</th>
                <th>Recommended action</th></tr></thead>
              <tbody>
                {result.findings.slice(0, 20).map((f) => (
                  <tr key={f.finding_type}>
                    <td><span className={`sev ${f.severity}`}>{f.severity}</span></td>
                    <td>{f.category_label}</td>
                    <td><b>{f.finding}</b>
                      <div style={{ color: "var(--muted)", fontSize: 12.5 }}>{f.explanation}</div>
                    </td>
                    <td>{f.recommended_action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="section card" id="recCard">
          <h3>Personalised Recommendations</h3>
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead><tr><th>Priority</th><th>Category</th><th>Recommendation</th></tr></thead>
              <tbody>
                {result.recommendations.map((r) => (
                  <tr key={r.finding_type}>
                    <td><span className={`pri ${r.priority.split(" ")[0]}`}>{r.priority}</span></td>
                    <td>{r.category_label}</td><td>{r.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ------------------------- simulator ------------------------- */}
        <div className="section" id="simCard">
          <div className="section-head">
            <div><h2>Privacy Improvement Simulator</h2>
              <p>“What happens if I improve my settings?” — <b>FRAMEWORK SIMULATION</b></p></div>
            <button className="btn btn-primary btn-sm" onClick={runSimulation}>Run simulation</button>
          </div>
          <div className="warn" style={{ marginBottom: 14 }}>
            <b>FRAMEWORK SIMULATION.</b> The simulated reduction shows how this educational
            model re-scores the same questionnaire. It does not guarantee real-world safety.
          </div>
          <div className="sim-grid">
            <div className="sim-col">
              <div style={{ color: "var(--muted)", fontSize: 11.5, letterSpacing: ".09em",
                            textTransform: "uppercase", fontWeight: 700 }}>Current risk</div>
              <div className="sim-score" style={{ color: colorFor(result.overall_score) }}>
                {result.overall_score.toFixed(2)}</div>
              <div style={{ marginTop: 10 }}><Badge level={result.risk_level} /></div>
              <div style={{ marginTop: 14, color: "var(--muted)", fontSize: 13 }}>
                Exposure rubric {rubric.score.toFixed(2)} · {result.findings.length} findings
              </div>
            </div>

            <div className="sim-col">
              <div style={{ color: "var(--muted)", fontSize: 11.5, letterSpacing: ".09em",
                            textTransform: "uppercase", fontWeight: 700, marginBottom: 8 }}>
                Select improvements</div>
              <div style={{ maxHeight: 330, overflow: "auto" }}>
                {improvements.map((imp) => (
                  <label className="imp" key={imp.key}>
                    <input type="checkbox" checked={selected.includes(imp.key)}
                      onChange={(e) => setSelected(e.target.checked
                        ? [...selected, imp.key]
                        : selected.filter((k) => k !== imp.key))} />
                    <span style={{ fontSize: 13.5 }}>{imp.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="sim-col">
              <div style={{ color: "var(--muted)", fontSize: 11.5, letterSpacing: ".09em",
                            textTransform: "uppercase", fontWeight: 700 }}>Simulated new risk</div>
              <div className="sim-score"
                   style={{ color: simulation ? colorFor(simulation.new_score) : "var(--muted)" }}>
                {simulation ? simulation.new_score.toFixed(2) : "–"}</div>
              {simulation && (
                <>
                  <div style={{ marginTop: 10 }}><Badge level={simulation.new_risk_level} /></div>
                  <div style={{ marginTop: 14, fontSize: 14 }}>
                    <b style={{ color: "#4ade80" }}>
                      Risk reduction: −{simulation.risk_reduction.toFixed(2)} points
                      (−{simulation.risk_reduction_percent.toFixed(1)}%)
                    </b>
                    <div style={{ color: "var(--muted)", fontSize: 12.5 }}>
                      Exposure rubric {simulation.current_exposure_score.toFixed(2)} →{" "}
                      {simulation.new_exposure_score.toFixed(2)} · findings{" "}
                      {simulation.findings_before} → {simulation.findings_after}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {simulation && (
            <div className="card" style={{ marginTop: 18 }}>
              <h3>Privacy Improvement Comparison</h3>
              <div className="chart-box">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={simData} margin={{ bottom: 60 }}>
                    <CartesianGrid stroke="rgba(157,176,204,.12)" />
                    <XAxis dataKey="name" angle={-35} textAnchor="end" interval={0}
                           tick={{ fill: "#9db0cc", fontSize: 10 }} height={80} />
                    <YAxis domain={[0, 100]} tick={{ fill: "#9db0cc", fontSize: 11 }} />
                    <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
                    <Legend />
                    <Bar dataKey="before" name="Current" fill="#f97316" />
                    <Bar dataKey="after" name="Simulated" fill="#22c55e" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>

        {error && <ErrorBox message={error} />}
        <div className="warn" style={{ marginTop: 20 }}>
          <b>Disclaimer.</b> {result.disclaimer}
        </div>
      </>
    );
  }

  // ---------------------------- questionnaire view ----------------------
  return (
    <>
      <div className="section" style={{ marginTop: 28 }}>
        <div className="section-head">
          <div><h2>Privacy Assessment Questionnaire</h2>
            <p>{total} questions · {questionnaire.sections.length} categories · deterministic scoring</p></div>
          <div>
            <button className="btn btn-ghost btn-sm" onClick={loadDemo}>Load demo profile</button>
            <button className="btn btn-ghost btn-sm" onClick={() => setAnswers({})}>Clear</button>
          </div>
        </div>
        <div className="notice"><b>Privacy notice.</b> {questionnaire.privacy_notice}</div>
      </div>

      <div className="progress-wrap">
        <div className="progress"><span style={{ width: `${progress}%` }} /></div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8,
                      fontSize: 12.5, color: "var(--muted)" }}>
          <span>{answered} of {total} answered ({progress}%)</span>
          <span>Minimum 60% required to submit</span>
        </div>
      </div>

      <div style={{ marginTop: 20 }}>
        {questionnaire.sections.map((section) => (
          <div className="q-section" key={section.section} id={sectionSlug(section.section)}>
            <h3>{section.section}{" "}
              <span style={{ color: "var(--muted)", fontWeight: 500, fontSize: 13 }}>
                ({section.questions.length} questions)</span></h3>
            {section.questions.map((q) => (
              <div className={`q ${answers[q.id] ? "answered" : ""}`} key={q.id}>
                <div className="qtext"><span className="qid">{q.id}</span><span>{q.text}</span></div>
                <div className="opts">
                  {q.options.map((o) => (
                    <label className="opt" key={o.value}>
                      <input type="radio" name={q.id} value={o.value}
                             checked={answers[q.id] === o.value}
                             onChange={() => setAnswers({ ...answers, [q.id]: o.value })} />
                      <span>{o.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>

      {error && <ErrorBox message={error} />}
      <div style={{ margin: "22px 0 40px", display: "flex", gap: 12, flexWrap: "wrap" }}>
        <button className="btn btn-primary" disabled={progress < 60 || busy} onClick={submit}>
          {busy ? "Calculating…" : "▶  Calculate Privacy Risk"}
        </button>
        <span style={{ color: "var(--muted)", fontSize: 13, alignSelf: "center" }}>
          Deterministic scoring · no black box · nothing personal is transmitted
        </span>
      </div>
    </>
  );
}
