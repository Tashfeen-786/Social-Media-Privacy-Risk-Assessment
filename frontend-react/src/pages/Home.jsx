import { useEffect, useState } from "react";
import { API } from "../api.js";

export default function Home({ onStart }) {
  const [areas, setAreas] = useState([]);
  const [count, setCount] = useState(58);

  useEffect(() => {
    API.privacyAreas().then((d) => setAreas(d.areas)).catch(() => {});
    API.questionnaire().then((d) => setCount(d.total_questions)).catch(() => {});
  }, []);

  return (
    <>
      <section className="hero">
        <span className="chip">Defensive &amp; Educational</span>
        <span className="chip">Synthetic / self-reported data only</span>
        <span className="chip">Privacy by Design</span>
        <h1>Assess your <span>social-media privacy exposure</span><br />before someone else does.</h1>
        <p className="lead">
          A privacy-focused cybersecurity framework that scores profile exposure, personal
          information, location, content, connections, tagging, account security, third-party
          apps, social-engineering risk and digital footprint — plus a dedicated 8-category
          exposure rubric covering PII, geolocation/EXIF, children in media, workplace
          disclosures, weak settings, linkage, handle reuse and trackers.
        </p>
        <button className="btn btn-primary" onClick={onStart}>▶&nbsp; Start Privacy Assessment</button>
      </section>

      <section className="grid g4">
        <div className="card stat"><div className="k">Questionnaire</div>
          <div className="v">{count}</div><div className="s">questions · 10 sections</div></div>
        <div className="card stat"><div className="k">Scoring models</div>
          <div className="v">2</div><div className="s">10-category score + 8-category rubric</div></div>
        <div className="card stat"><div className="k">Privacy areas</div>
          <div className="v">{areas.length || 20}</div><div className="s">all covered by questions</div></div>
        <div className="card stat"><div className="k">Personal data stored</div>
          <div className="v">0</div><div className="s">no phone, e-mail, DOB or passwords</div></div>
      </section>

      <section className="section grid g2">
        <div className="card"><h3>A · PRIVACY ASSESSMENT SCORE (10 categories)</h3>
          <p>Weighted behaviour/configuration model: 0–100, higher = more assessed risk.
             Levels: LOW 0–20 · MODERATE 21–40 · HIGH 41–70 · CRITICAL 71–100.</p></div>
        <div className="card"><h3>B · PRIVACY EXPOSURE RUBRIC (8 categories)</h3>
          <p>PII 25 · Geo/EXIF 20 · Children 15 · Workplace/School 10 · Weak settings 10 ·
             Linkage 10 · Handle reuse 5 · Trackers 5 → final = min(100, sum).</p></div>
      </section>

      <section className="section">
        <div className="section-head"><div><h2>The 20 privacy areas assessed</h2>
          <p>Loaded live from the API.</p></div></div>
        <div className="card">
          {(areas.length ? areas : ["loading…"]).map((a) => (
            <span className="chip" key={a}>{a}</span>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="card"><h3>Ethical scope</h3>
          <p>This project is designed for defensive cybersecurity and privacy education. It uses
             synthetic or voluntarily provided assessment responses and does <b>not</b> scrape,
             track or profile real social-media users. It never asks for your actual phone
             number, e-mail address, postal address, birth date, password or any child's
             personal details — only whether such information is publicly visible.</p></div>
      </section>
    </>
  );
}
