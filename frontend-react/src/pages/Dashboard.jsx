import { useEffect, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from "recharts";
import { API, LEVEL_COLORS, colorFor, levelOf } from "../api.js";
import { Badge, ErrorBox, Loading, StatCard } from "../components/Common.jsx";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    API.stats().then(setStats).catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorBox message={error} />;
  if (!stats) return <Loading text="Loading dashboard…" />;

  const categoryData = Object.entries(stats.category_averages)
    .map(([key, value]) => ({ name: stats.category_labels[key] || key, score: value }))
    .sort((a, b) => b.score - a.score);
  const distributionData = ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    .map((level) => ({ name: level, value: stats.risk_distribution[level] || 0 }));
  const weaknessData = stats.top_weaknesses.map((w) => ({
    name: w.finding_type.replace(/_/g, " "), count: w.c,
  }));
  const rubricData = Object.entries(stats.rubric_averages || {})
    .map(([key, value]) => ({ name: stats.rubric_labels[key] || key, points: value }));
  const modelData = [{
    name: "Average score", modelA: stats.average_score, modelB: stats.average_exposure_score,
  }];

  return (
    <>
      <div className="section" style={{ marginTop: 28 }}>
        <div className="section-head">
          <div><h2>Privacy Risk Dashboard</h2>
            <p>Anonymised aggregate analytics — no personal data.</p>
            <p style={{ marginTop: 6 }}>
              <span className="chip" style={{ background: "rgba(234,179,8,.15)",
                color: "#facc15", borderColor: "rgba(234,179,8,.4)" }}>
                {stats.data_notice}</span></p>
          </div>
        </div>
      </div>

      <div className="grid g5">
        <StatCard label="Average Model A score" value={stats.average_score.toFixed(2)}
          sub={`across ${stats.total_assessments} assessments`} color={colorFor(stats.average_score)} />
        <StatCard label="Average Model B exposure" value={stats.average_exposure_score.toFixed(2)}
          sub="8-category rubric" color={colorFor(stats.average_exposure_score)} />
        <StatCard label="Dominant risk level" value={<Badge level={levelOf(stats.average_score)} />}
          sub="based on the average score" />
        <StatCard label="High / Critical" value={(stats.risk_distribution.HIGH || 0) +
          (stats.risk_distribution.CRITICAL || 0)} sub="need priority remediation" />
        <StatCard label="Top weakness"
          value={<span style={{ fontSize: 17 }}>
            {stats.top_weaknesses[0]?.finding_type || "–"}</span>}
          sub={stats.top_weaknesses[0] ? `${stats.top_weaknesses[0].c} occurrences` : "no data"} />
      </div>

      <div className="section grid g2">
        <div className="card"><h3>1. Category Risk Scores (average)</h3>
          <div className="chart-box tall">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} layout="vertical" margin={{ left: 110 }}>
                <CartesianGrid stroke="rgba(157,176,204,.12)" />
                <XAxis type="number" domain={[0, 100]} tick={{ fill: "#9db0cc", fontSize: 11 }} />
                <YAxis type="category" dataKey="name" width={110}
                       tick={{ fill: "#9db0cc", fontSize: 10 }} />
                <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
                <Bar dataKey="score" name="Average risk">
                  {categoryData.map((d) => <Cell key={d.name} fill={colorFor(d.score)} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card"><h3>2. Privacy Risk Distribution</h3>
          <div className="chart-box tall">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={distributionData} dataKey="value" nameKey="name" innerRadius="55%"
                     outerRadius="80%" stroke="#111c33" strokeWidth={3}>
                  {distributionData.map((d) => <Cell key={d.name} fill={LEVEL_COLORS[d.name]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="section grid g2">
        <div className="card"><h3>3. Top Privacy Weaknesses</h3>
          <div className="chart-box tall">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weaknessData} layout="vertical" margin={{ left: 150 }}>
                <CartesianGrid stroke="rgba(157,176,204,.12)" />
                <XAxis type="number" tick={{ fill: "#9db0cc", fontSize: 11 }} />
                <YAxis type="category" dataKey="name" width={150}
                       tick={{ fill: "#9db0cc", fontSize: 10 }} />
                <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
                <Bar dataKey="count" name="Occurrences" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card"><h3>4. Exposure Rubric averages (Model B)</h3>
          <div className="chart-box tall">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rubricData} layout="vertical" margin={{ left: 150 }}>
                <CartesianGrid stroke="rgba(157,176,204,.12)" />
                <XAxis type="number" domain={[0, 25]} tick={{ fill: "#9db0cc", fontSize: 11 }} />
                <YAxis type="category" dataKey="name" width={150}
                       tick={{ fill: "#9db0cc", fontSize: 10 }} />
                <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
                <Bar dataKey="points" name="Average points" fill="#a78bfa" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="section card">
        <h3>5. Model A vs Model B (complementary, not equivalent)</h3>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={modelData}>
              <CartesianGrid stroke="rgba(157,176,204,.12)" />
              <XAxis dataKey="name" tick={{ fill: "#9db0cc", fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: "#9db0cc", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
              <Legend />
              <Bar dataKey="modelA" name="Model A · Privacy Assessment Score" fill="#3b82f6" />
              <Bar dataKey="modelB" name="Model B · Privacy Exposure Rubric" fill="#a78bfa" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="section card">
        <h3>Recent assessments (privacy-minimised records)</h3>
        <div style={{ overflowX: "auto" }}>
          <table>
            <thead><tr><th>Assessment ID</th><th>Model A</th><th>Level</th>
              <th>Model B</th><th>Created</th></tr></thead>
            <tbody>
              {stats.recent_assessments.map((r) => (
                <tr key={r.assessment_id}>
                  <td><code>{r.assessment_id}</code></td>
                  <td><b>{r.overall_score.toFixed(2)}</b></td>
                  <td><Badge level={r.risk_level} /></td>
                  <td>{(r.exposure_score ?? 0).toFixed(2)}</td>
                  <td>{r.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="warn" style={{ marginTop: 18 }}><b>Disclaimer.</b> {stats.disclaimer}</div>
    </>
  );
}
