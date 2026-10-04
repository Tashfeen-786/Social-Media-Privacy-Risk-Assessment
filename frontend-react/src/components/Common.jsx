export function StatCard({ label, value, sub, color }) {
  return (
    <div className="card stat">
      <div className="k">{label}</div>
      <div className="v" style={color ? { color } : undefined}>{value}</div>
      {sub && <div className="s">{sub}</div>}
    </div>
  );
}

export function Badge({ level }) {
  return <span className={`badge ${level}`}>{level}</span>;
}

export function Loading({ text = "Loading…" }) {
  return <div className="loading"><div className="spinner" /><span>{text}</span></div>;
}

export function ErrorBox({ message }) {
  return <div className="error"><b>Something went wrong.</b><br />{message}</div>;
}

export function Disclaimer({ text }) {
  return <div className="warn" style={{ marginTop: 16 }}><b>Disclaimer.</b> {text}</div>;
}
