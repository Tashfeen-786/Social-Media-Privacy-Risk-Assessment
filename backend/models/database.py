"""
database.py
-----------
Privacy-first SQLite storage layer.

DATA MINIMISATION - only this is stored:
    assessment_id, overall_score, risk_level, created_at,
    category scores (model A), exposure rubric scores (model B),
    finding types, recommendation texts.

NEVER STORED:
    phone numbers, e-mail addresses, home addresses, birth dates, passwords,
    exact locations, private messages, raw questionnaire answers, IP addresses,
    names, children's details or any other direct identifier.

Schema
    ASSESSMENTS            (assessment_id, overall_score, risk_level,
                            exposure_score, exposure_level, created_at)
    CATEGORY_SCORES        (category_score_id, assessment_id, category, score)
    EXPOSURE_RUBRIC_SCORES (rubric_score_id, assessment_id, rubric_category,
                            points, max_points)
    FINDINGS               (finding_id, assessment_id, category, finding_type,
                            severity, description)
    RECOMMENDATIONS        (recommendation_id, finding_type, recommendation, priority)
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                 "data", "privacy_assessment.db"),
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id  TEXT PRIMARY KEY,
    overall_score  REAL NOT NULL,
    risk_level     TEXT NOT NULL,
    exposure_score REAL NOT NULL DEFAULT 0,
    exposure_level TEXT NOT NULL DEFAULT 'LOW',
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS category_scores (
    category_score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id     TEXT NOT NULL,
    category          TEXT NOT NULL,
    score             REAL NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exposure_rubric_scores (
    rubric_score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id   TEXT NOT NULL,
    rubric_category TEXT NOT NULL,
    points          REAL NOT NULL,
    max_points      REAL NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS findings (
    finding_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT NOT NULL,
    category      TEXT NOT NULL,
    finding_type  TEXT NOT NULL,
    severity      TEXT NOT NULL,
    description   TEXT NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_type      TEXT NOT NULL UNIQUE,
    recommendation    TEXT NOT NULL,
    priority          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cat_assessment ON category_scores(assessment_id);
CREATE INDEX IF NOT EXISTS idx_rub_assessment ON exposure_rubric_scores(assessment_id);
CREATE INDEX IF NOT EXISTS idx_find_assessment ON findings(assessment_id);
"""

# Column name fragments that must never exist anywhere in the schema.
FORBIDDEN_COLUMNS = [
    "phone", "email", "address", "birth", "dob", "password", "passwd",
    "latitude", "longitude", "message", "ip_address", "full_name", "username",
    "child_name", "school",
]


class PrivacyDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self.init_db()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    # Lightweight forward migrations: columns added after v1.0 are applied to
    # existing database files so an older DB never breaks a fresh checkout.
    MIGRATIONS = [
        ("assessments", "exposure_score", "REAL NOT NULL DEFAULT 0"),
        ("assessments", "exposure_level", "TEXT NOT NULL DEFAULT 'LOW'"),
    ]

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            for table, column, definition in self.MIGRATIONS:
                existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
                if existing and column not in existing:
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    # ------------------------------------------------------------------
    # Writes (privacy-minimised)
    # ------------------------------------------------------------------
    def save_assessment(self, result: Dict[str, Any]) -> str:
        aid = result["assessment_id"]
        rubric = result.get("exposure_rubric", {}) or {}
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO assessments (assessment_id, overall_score, "
                "risk_level, exposure_score, exposure_level, created_at) VALUES (?,?,?,?,?,?)",
                (aid, result["overall_score"], result["risk_level"],
                 rubric.get("score", 0.0), rubric.get("risk_level", "LOW"),
                 result["created_at"]))

            conn.execute("DELETE FROM category_scores WHERE assessment_id=?", (aid,))
            conn.executemany(
                "INSERT INTO category_scores (assessment_id, category, score) VALUES (?,?,?)",
                [(aid, cat, score) for cat, score in result["category_scores"].items()])

            conn.execute("DELETE FROM exposure_rubric_scores WHERE assessment_id=?", (aid,))
            conn.executemany(
                "INSERT INTO exposure_rubric_scores (assessment_id, rubric_category, "
                "points, max_points) VALUES (?,?,?,?)",
                [(aid, c["key"], c["points"], c["max_points"])
                 for c in rubric.get("categories", [])])

            conn.execute("DELETE FROM findings WHERE assessment_id=?", (aid,))
            conn.executemany(
                "INSERT INTO findings (assessment_id, category, finding_type, severity, "
                "description) VALUES (?,?,?,?,?)",
                [(aid, f["category"], f["finding_type"], f["severity"], f["finding"])
                 for f in result["findings"]])

            conn.executemany(
                "INSERT OR IGNORE INTO recommendations (finding_type, recommendation, "
                "priority) VALUES (?,?,?)",
                [(r["finding_type"], r["recommendation"], r["priority"])
                 for r in result["recommendations"]])
        return aid

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM assessments WHERE assessment_id=?",
                               (assessment_id,)).fetchone()
            if not row:
                return None
            categories = conn.execute(
                "SELECT category, score FROM category_scores WHERE assessment_id=?",
                (assessment_id,)).fetchall()
            rubric = conn.execute(
                "SELECT rubric_category, points, max_points FROM exposure_rubric_scores "
                "WHERE assessment_id=?", (assessment_id,)).fetchall()
            findings = conn.execute(
                "SELECT category, finding_type, severity, description FROM findings "
                "WHERE assessment_id=?", (assessment_id,)).fetchall()
            return {
                "assessment_id": row["assessment_id"],
                "overall_score": row["overall_score"],
                "risk_level": row["risk_level"],
                "exposure_score": row["exposure_score"],
                "exposure_level": row["exposure_level"],
                "created_at": row["created_at"],
                "category_scores": {r["category"]: r["score"] for r in categories},
                "exposure_rubric_scores": {r["rubric_category"]: r["points"] for r in rubric},
                "findings": [dict(r) for r in findings],
            }

    def get_recommendations(self, assessment_id: str) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT f.finding_type, f.category, f.severity, r.recommendation, r.priority "
                "FROM findings f JOIN recommendations r ON r.finding_type = f.finding_type "
                "WHERE f.assessment_id=?", (assessment_id,)).fetchall()]

    def delete_assessment(self, assessment_id: str) -> bool:
        with self.connect() as conn:
            cur = conn.execute("DELETE FROM assessments WHERE assessment_id=?", (assessment_id,))
            for table in ("category_scores", "exposure_rubric_scores", "findings"):
                conn.execute(f"DELETE FROM {table} WHERE assessment_id=?", (assessment_id,))
            return cur.rowcount > 0

    # ------------------------------------------------------------------
    # Aggregates (anonymised analytics only)
    # ------------------------------------------------------------------
    def dashboard_stats(self) -> Dict[str, Any]:
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) c FROM assessments").fetchone()["c"]
            avg = conn.execute("SELECT AVG(overall_score) a FROM assessments").fetchone()["a"]
            avg_exp = conn.execute("SELECT AVG(exposure_score) a FROM assessments").fetchone()["a"]
            distribution = {r["risk_level"]: r["c"] for r in conn.execute(
                "SELECT risk_level, COUNT(*) c FROM assessments GROUP BY risk_level")}
            category_avg = {r["category"]: round(r["a"], 2) for r in conn.execute(
                "SELECT category, AVG(score) a FROM category_scores GROUP BY category")}
            rubric_avg = {r["rubric_category"]: round(r["a"], 2) for r in conn.execute(
                "SELECT rubric_category, AVG(points) a FROM exposure_rubric_scores "
                "GROUP BY rubric_category")}
            weaknesses = [dict(r) for r in conn.execute(
                "SELECT finding_type, severity, COUNT(*) c FROM findings "
                "GROUP BY finding_type ORDER BY c DESC LIMIT 10")]
            recent = [dict(r) for r in conn.execute(
                "SELECT assessment_id, overall_score, risk_level, exposure_score, created_at "
                "FROM assessments ORDER BY created_at DESC LIMIT 10")]
        for level in ("LOW", "MODERATE", "HIGH", "CRITICAL"):
            distribution.setdefault(level, 0)
        return {
            "data_notice": "SYNTHETIC / DEMONSTRATION DATA",
            "total_assessments": total,
            "average_score": round(avg, 2) if avg else 0.0,
            "average_exposure_score": round(avg_exp, 2) if avg_exp else 0.0,
            "risk_distribution": distribution,
            "category_averages": category_avg,
            "rubric_averages": rubric_avg,
            "top_weaknesses": weaknesses,
            "recent_assessments": recent,
        }

    def schema_info(self) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            tables = [r["name"] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            return [{
                "table": table,
                "columns": [{"name": c["name"], "type": c["type"], "pk": bool(c["pk"])}
                            for c in conn.execute(f"PRAGMA table_info({table})")],
            } for table in tables]


__all__ = ["PrivacyDatabase", "FORBIDDEN_COLUMNS", "DEFAULT_DB_PATH", "SCHEMA"]
