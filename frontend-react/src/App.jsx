import { useState } from "react";
import Home from "./pages/Home.jsx";
import Assessment from "./pages/Assessment.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Analyzer from "./pages/Analyzer.jsx";

const TABS = [
  { key: "home", label: "Home" },
  { key: "assessment", label: "Assessment" },
  { key: "dashboard", label: "Dashboard" },
  { key: "analyzer", label: "File Analyzer" },
];

export default function App() {
  const [tab, setTab] = useState("home");

  return (
    <>
      <nav className="nav">
        <div className="nav-inner">
          <div className="brand">
            <div className="logo">&#128737;</div>
            <div>
              Privacy Risk Assessment
              <small>Defensive Cybersecurity Framework · React + Vite</small>
            </div>
          </div>
          <div className="nav-links">
            {TABS.map((t) => (
              <a key={t.key} href="#" className={tab === t.key ? "active" : ""}
                 onClick={(e) => { e.preventDefault(); setTab(t.key); }}>
                {t.label}
              </a>
            ))}
            <a href="/api/privacy-checklist?fmt=html" target="_blank" rel="noreferrer">Checklist</a>
            <a href="/docs" target="_blank" rel="noreferrer">API Docs</a>
          </div>
        </div>
      </nav>

      <div className="container">
        {tab === "home" && <Home onStart={() => setTab("assessment")} />}
        {tab === "assessment" && <Assessment />}
        {tab === "dashboard" && <Dashboard />}
        {tab === "analyzer" && <Analyzer />}

        <footer className="site">
          Social Media Privacy Risk Assessment Framework · v2.0 · Defensive cybersecurity &amp;
          privacy education · Synthetic / self-reported data only
        </footer>
      </div>
    </>
  );
}
