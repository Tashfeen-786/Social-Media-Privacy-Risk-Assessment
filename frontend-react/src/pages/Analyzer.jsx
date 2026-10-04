import { useState } from "react";
import { API, colorFor } from "../api.js";
import { Badge, ErrorBox, Loading } from "../components/Common.jsx";

/**
 * File Analyzer - runs the 8-category PRIVACY EXPOSURE RUBRIC over the
 * project's profile.json / posts.json data contract.
 *
 * Only SYNTHETIC or self-owned exported files should be analysed. Nothing is
 * scraped and no network lookup of any account is performed.
 */
export default function Analyzer() {
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [sampleName, setSampleName] = useState("demo_oversharer");

  async function runSample(name) {
    setBusy(true); setError("");
    try {
      const sample = await API.sample(name);
      setResult(await API.analyze(sample.profile, sample.posts));
      setSampleName(name);
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  async function onUpload(event) {
    event.preventDefault();
    setBusy(true); setError("");
    try {
      const form = new FormData(event.target);
      const response = await fetch("/api/upload", { method: "POST", body: form });
      if (!response.ok) throw new Error((await response.json()).detail || response.statusText);
      setResult(await response.json());
      setSampleName("uploaded files");
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  return (
    <>
      <div className="section" style={{ marginTop: 28 }}>
        <div className="section-head">
          <div><h2>Profile / Posts File Analyzer</h2>
            <p>Rule-based 8-category exposure rubric over the project data contract.</p></div>
        </div>
        <div className="notice">
          <b>Safe use.</b> Analyse only <b>synthetic</b> or your own exported files. The analyser
          runs locally on the server you started, performs no scraping, contacts no website and
          stores no uploaded content. The tracker check is a basic educational check based only
          on information declared in the file — not a browser-level tracker audit.
        </div>
      </div>

      <div className="grid g2">
        <div className="card"><h3>Use a bundled synthetic sample</h3>
          <p>Two fictional demo profiles ship with the project.</p>
          <div style={{ marginTop: 12, display: "flex", gap: 10, flexWrap: "wrap" }}>
            <button className="btn btn-primary btn-sm" disabled={busy}
                    onClick={() => runSample("demo_oversharer")}>Analyse demo_oversharer</button>
            <button className="btn btn-ghost btn-sm" disabled={busy}
                    onClick={() => runSample("demo_hardened")}>Analyse demo_hardened</button>
          </div>
        </div>

        <div className="card"><h3>Upload profile.json + posts.json</h3>
          <form onSubmit={onUpload}>
            <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 8 }}>
              <label style={{ fontSize: 13.5 }}>profile.json{" "}
                <input type="file" name="profile" accept=".json" required /></label>
              <label style={{ fontSize: 13.5 }}>posts.json{" "}
                <input type="file" name="posts" accept=".json" required /></label>
              <button className="btn btn-primary btn-sm" style={{ alignSelf: "flex-start" }}
                      disabled={busy}>Analyze</button>
            </div>
          </form>
        </div>
      </div>

      {busy && <Loading text="Analysing…" />}
      {error && <ErrorBox message={error} />}

      {result && !busy && (
        <>
          <div className="section grid g3">
            <div className="card stat"><div className="k">Exposure score</div>
              <div className="v" style={{ color: colorFor(result.score) }}>
                {result.score.toFixed(2)}</div>
              <div className="s">min(100, sum of capped points)</div></div>
            <div className="card stat"><div className="k">Risk level</div>
              <div className="v"><Badge level={result.risk_level} /></div>
              <div className="s">source: {sampleName}</div></div>
            <div className="card stat"><div className="k">Findings</div>
              <div className="v">{result.findings.length}</div>
              <div className="s">each with a specific fix</div></div>
          </div>

          <div className="section card"><h3>Rubric categories</h3>
            <div style={{ overflowX: "auto" }}>
              <table>
                <thead><tr><th>Category</th><th>Points</th><th>Max</th><th>Capped</th></tr></thead>
                <tbody>
                  {result.categories.map((c) => (
                    <tr key={c.key}><td>{c.label}</td><td><b>{c.points.toFixed(2)}</b></td>
                      <td>{c.max_points}</td><td>{c.capped ? "yes" : "—"}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="section card"><h3>Findings &amp; fixes</h3>
            <div style={{ overflowX: "auto" }}>
              <table>
                <thead><tr><th>Category</th><th>Finding</th><th>Fix</th><th>Points</th></tr></thead>
                <tbody>
                  {result.findings.map((f, index) => (
                    <tr key={index}><td>{f.cat}</td><td>{f.item}</td>
                      <td>{f.fix || "—"}</td><td>{f.points}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="warn" style={{ marginTop: 16 }}>
            <b>Note.</b> {result.note} {result.tracker_disclaimer || ""}
          </div>
        </>
      )}
    </>
  );
}
