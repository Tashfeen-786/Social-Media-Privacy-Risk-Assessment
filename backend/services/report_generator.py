"""
report_generator.py
-------------------
Professional privacy assessment report generation (HTML and PDF).

PRIVACY RULE:
    The report contains only assessment metadata, scores, finding types and
    recommendations. It never contains phone numbers, e-mail addresses,
    addresses, birth dates, passwords or raw answers - the application never
    collects them in the first place.
"""

import html
import os
import re
from datetime import datetime
from typing import Any, Dict

from backend.models.categories import CATEGORIES, DISCLAIMER, METHODOLOGY, RUBRIC_CATEGORIES
from backend.services.privacy_checklist import CHECKLIST
from backend.utils.privacy_scan import scan

REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")

SEVERITY_COLOR = {"CRITICAL": "#b91c1c", "HIGH": "#ea580c",
                  "MEDIUM": "#ca8a04", "LOW": "#0369a1"}
LEVEL_COLOR = {"LOW": "#15803d", "MODERATE": "#ca8a04",
               "HIGH": "#ea580c", "CRITICAL": "#b91c1c"}

# Defensive guard: the report must never contain sensitive personal data.
def assert_no_sensitive_data(content: str) -> None:
    """Raise if the rendered report accidentally contains sensitive patterns."""
    for name, match in scan(content).items():
        if match:
            raise ValueError(f"Report blocked: possible sensitive data ({name}): '{match}'")


def build_report_html(result: Dict[str, Any]) -> str:
    esc = html.escape
    level = result["risk_level"]
    date = datetime.fromisoformat(result["created_at"].replace("Z", "+00:00")).strftime(
        "%d %B %Y, %H:%M UTC") if "created_at" in result else ""

    cat_rows = "".join(
        f'<tr><td>{esc(CATEGORIES[k])}</td><td class="score">{v:.2f}</td>'
        f'<td><div class="bar"><span style="width:{min(v,100):.0f}%"></span></div></td></tr>'
        for k, v in sorted(result["category_scores"].items(),
                           key=lambda kv: kv[1], reverse=True))

    finding_rows = "".join(
        f'<tr><td><span class="sev" style="background:{SEVERITY_COLOR[f["severity"]]}">'
        f'{f["severity"]}</span></td><td>{esc(CATEGORIES[f["category"]])}</td>'
        f'<td><b>{esc(f["finding"])}</b><div class="exp">{esc(f["explanation"])}</div></td>'
        f'<td>{esc(f["recommended_action"])}</td></tr>'
        for f in result["findings"][:20]) or \
        '<tr><td colspan="4">No significant findings detected.</td></tr>'

    rec_rows = "".join(
        f'<tr><td><span class="pri p{r["priority"].split()[0].lower()}">{r["priority"]}</span></td>'
        f'<td>{esc(r["category_label"])}</td><td>{esc(r["recommendation"])}</td></tr>'
        for r in result["recommendations"])

    priority_actions = "".join(
        f"<li>{esc(r['recommendation'])}</li>"
        for r in result["recommendations"] if r["priority"] == "IMMEDIATE") or \
        "<li>No immediate actions identified by the framework.</li>"

    checklist_items = "".join(
        f'<li>&#9744; {esc(c["item"])}</li>' for c in CHECKLIST)

    rubric = result.get("exposure_rubric", {}) or {}
    rubric_rows = "".join(
        f'<tr><td>{esc(c["label"])}</td><td class="score">{c["points"]:.2f}</td>'
        f'<td>{c["max_points"]}</td>'
        f'<td><div class="bar"><span style="width:{min(c["percent_of_cap"],100):.0f}%"></span></div></td>'
        f'<td>{"capped" if c["capped"] else ""}</td></tr>'
        for c in rubric.get("categories", []))

    rubric_score_txt = f"{rubric.get('score', 0):.1f}/100"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Privacy Assessment Report {esc(result['assessment_id'])}</title>
<style>
 *{{box-sizing:border-box}}
 body{{font-family:'Segoe UI',Arial,sans-serif;margin:0;background:#f1f5f9;color:#0f172a}}
 .page{{max-width:1000px;margin:0 auto;background:#fff;padding:40px 48px}}
 header{{border-bottom:3px solid #2563eb;padding-bottom:16px;margin-bottom:24px}}
 h1{{margin:0;font-size:26px}} .sub{{color:#475569;font-size:14px;margin-top:6px}}
 h2{{font-size:18px;margin:32px 0 10px;padding-bottom:6px;border-bottom:1px solid #e2e8f0}}
 .meta{{display:flex;gap:16px;flex-wrap:wrap;margin-top:18px}}
 .card{{flex:1;min-width:180px;border:1px solid #e2e8f0;border-radius:10px;padding:16px;background:#f8fafc}}
 .card .k{{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#64748b}}
 .card .v{{font-size:24px;font-weight:700;margin-top:6px}}
 table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:13.5px}}
 th,td{{border:1px solid #e2e8f0;padding:9px 11px;text-align:left;vertical-align:top}}
 th{{background:#0f172a;color:#fff;font-weight:600}}
 td.score{{width:80px;font-weight:700}}
 .bar{{background:#e2e8f0;height:10px;border-radius:5px;overflow:hidden;min-width:120px}}
 .bar span{{display:block;height:100%;background:linear-gradient(90deg,#22c55e,#eab308,#ef4444)}}
 .sev,.pri{{color:#fff;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700}}
 .pri.immediate{{background:#b91c1c}} .pri.important{{background:#ea580c}} .pri.good{{background:#0369a1}}
 .exp{{color:#475569;font-size:12.5px;margin-top:4px}}
 .level{{display:inline-block;padding:4px 14px;border-radius:999px;color:#fff;font-weight:700;
   background:{LEVEL_COLOR[level]}}}
 ul{{margin:8px 0 0 18px}} li{{margin:4px 0;font-size:13.5px}}
 .disclaimer{{margin-top:32px;background:#fff7ed;border-left:4px solid #ea580c;padding:14px 16px;
   font-size:12.5px;color:#7c2d12;border-radius:0 8px 8px 0}}
 .cols{{column-count:2;column-gap:28px}}
 footer{{margin-top:28px;border-top:1px solid #e2e8f0;padding-top:12px;font-size:11.5px;color:#64748b}}
</style></head><body><div class="page">
<header>
  <h1>Social Media Privacy Risk Assessment Report</h1>
  <div class="sub">Assessment ID: <b>{esc(result['assessment_id'])}</b> &nbsp;|&nbsp;
     Assessment Date: <b>{esc(date)}</b> &nbsp;|&nbsp; Framework v1.0 (educational)</div>
</header>

<div class="meta">
  <div class="card"><div class="k">Overall Risk Score</div><div class="v">{result['overall_score']:.2f}/100</div></div>
  <div class="card"><div class="k">Risk Level</div><div class="v"><span class="level">{level}</span></div></div>
  <div class="card"><div class="k">Exposure Rubric (Model B)</div>
     <div class="v">{rubric_score_txt}</div></div>
  <div class="card"><div class="k">Findings</div><div class="v">{len(result['findings'])}</div></div>
  <div class="card"><div class="k">Recommendations</div><div class="v">{len(result['recommendations'])}</div></div>
  <div class="card"><div class="k">Security Controls</div>
     <div class="v">{result['security_controls_enabled']}/{result['security_controls_total']}</div></div>
</div>

<h2>1. Category Scores (0 = lower assessed risk, 100 = higher assessed risk)</h2>
<table><thead><tr><th>Category</th><th>Score</th><th>Exposure</th></tr></thead>
<tbody>{cat_rows}</tbody></table>

<h2>2. Privacy Exposure Rubric (Model B, 8 categories)</h2>
<p style="font-size:13px;color:#475569;margin:4px 0 8px">
 Exposure score <b>{rubric.get('score', 0):.2f} / 100</b> &mdash;
 level <b>{esc(rubric.get('risk_level', 'LOW'))}</b>.
 Formula: {esc(rubric.get('formula', ''))}</p>
<table><thead><tr><th>Exposure category</th><th>Points</th><th>Max</th>
 <th>Share of cap</th><th>Note</th></tr></thead>
<tbody>{rubric_rows}</tbody></table>
<p style="font-size:12px;color:#64748b;margin-top:6px">{esc(METHODOLOGY['relationship'])}</p>

<h2>3. Top Findings</h2>
<table><thead><tr><th>Severity</th><th>Category</th><th>Finding</th><th>Recommended action</th></tr></thead>
<tbody>{finding_rows}</tbody></table>

<h2>4. Security Recommendations</h2>
<table><thead><tr><th>Priority</th><th>Category</th><th>Recommendation</th></tr></thead>
<tbody>{rec_rows}</tbody></table>

<h2>5. Priority Actions (IMMEDIATE)</h2>
<ul>{priority_actions}</ul>

<h2>6. Privacy Checklist</h2>
<div class="cols"><ul>{checklist_items}</ul></div>

<div class="disclaimer"><b>Disclaimer.</b> {esc(DISCLAIMER)}
 This report contains no personal data: the framework only records
 answer categories, scores and finding types (Privacy by Design / Data Minimisation).</div>

<footer>Generated by the Social Media Privacy Risk Assessment Framework &mdash;
defensive cybersecurity &amp; privacy education. Synthetic / self-reported data only.</footer>
</div></body></html>"""


def generate_html_report(result: Dict[str, Any], output_dir: str = None) -> str:
    output_dir = output_dir or REPORTS_DIR
    os.makedirs(output_dir, exist_ok=True)
    content = build_report_html(result)
    assert_no_sensitive_data(content)
    path = os.path.join(output_dir, f"privacy_report_{result['assessment_id']}.html")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return path


def generate_pdf_report(result: Dict[str, Any], output_dir: str = None) -> str:
    """PDF version using ReportLab (pure Python, Windows friendly)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

    output_dir = output_dir or REPORTS_DIR
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"privacy_report_{result['assessment_id']}.pdf")

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1x", parent=styles["Title"], fontSize=17, spaceAfter=6)
    h2 = ParagraphStyle("h2x", parent=styles["Heading2"], fontSize=12.5,
                        textColor=colors.HexColor("#0f172a"), spaceBefore=12)
    body = ParagraphStyle("bodyx", parent=styles["BodyText"], fontSize=9, leading=12)

    story = [Paragraph("Social Media Privacy Risk Assessment Report", h1)]
    story.append(Paragraph(
        f"Assessment ID: <b>{result['assessment_id']}</b> &nbsp;|&nbsp; "
        f"Date: {result['created_at']} &nbsp;|&nbsp; Framework v1.0 (educational)", body))
    story.append(Spacer(1, 8))

    summary = [["Overall Risk Score", f"{result['overall_score']:.2f} / 100"],
               ["Risk Level", result["risk_level"]],
               ["Findings", str(len(result["findings"]))],
               ["Recommendations", str(len(result["recommendations"]))],
               ["Security Controls Enabled",
                f"{result['security_controls_enabled']}/{result['security_controls_total']}"]]
    table = Table(summary, colWidths=[70 * mm, 90 * mm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("FONTSIZE", (0, 0), (-1, -1), 9), ("PADDING", (0, 0), (-1, -1), 5)]))
    story += [table, Paragraph("1. Category Scores", h2)]

    cat_data = [["Category", "Score", "Level"]]
    for key, value in sorted(result["category_scores"].items(), key=lambda kv: kv[1], reverse=True):
        lvl = "CRITICAL" if value > 70 else "HIGH" if value > 40 else "MODERATE" if value > 20 else "LOW"
        cat_data.append([CATEGORIES[key], f"{value:.2f}", lvl])
    cat_table = Table(cat_data, colWidths=[90 * mm, 30 * mm, 40 * mm])
    cat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5)]))
    story += [cat_table, Paragraph("2. Privacy Exposure Rubric (Model B)", h2)]
    rubric = result.get("exposure_rubric", {}) or {}
    story.append(Paragraph(
        f"Exposure score <b>{rubric.get('score', 0):.2f} / 100</b> "
        f"({rubric.get('risk_level', 'LOW')}). "
        f"{rubric.get('formula', '')}", body))
    rub_data = [["Exposure category", "Points", "Max"]]
    for cat in rubric.get("categories", []):
        rub_data.append([cat["label"], f"{cat['points']:.2f}", str(cat["max_points"])])
    rub_table = Table(rub_data, colWidths=[100 * mm, 30 * mm, 30 * mm])
    rub_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5)]))
    story += [rub_table, Paragraph("3. Top Findings", h2)]

    find_data = [["Severity", "Finding", "Recommended action"]]
    for finding in result["findings"][:14]:
        find_data.append([finding["severity"],
                          Paragraph(finding["finding"], body),
                          Paragraph(finding["recommended_action"], body)])
    find_table = Table(find_data, colWidths=[22 * mm, 62 * mm, 76 * mm])
    find_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [find_table, Paragraph("4. Priority Actions", h2)]

    for rec in [r for r in result["recommendations"] if r["priority"] == "IMMEDIATE"][:12]:
        story.append(Paragraph(f"&bull; <b>[IMMEDIATE]</b> {rec['recommendation']}", body))

    story.append(Paragraph("5. Privacy Checklist", h2))
    for item in CHECKLIST:
        story.append(Paragraph(f"[ ] {item['item']}", body))

    story.append(Paragraph("Disclaimer", h2))
    story.append(Paragraph(
        DISCLAIMER + " This report contains no personal data; only scores, "
        "finding types and recommendations are recorded.", body))

    SimpleDocTemplate(path, pagesize=A4, topMargin=18 * mm, bottomMargin=16 * mm,
                      leftMargin=16 * mm, rightMargin=16 * mm,
                      title=f"Privacy Report {result['assessment_id']}").build(story)
    return path


__all__ = ["generate_html_report", "generate_pdf_report", "build_report_html",
           "assert_no_sensitive_data", "REPORTS_DIR"]
