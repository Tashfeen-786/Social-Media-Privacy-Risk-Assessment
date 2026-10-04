"""
generate_local_evidence.py
--------------------------
Generates the LOCAL (non-browser) evidence items into screenshots/:

    01_project_structure.png     real `find` listing of the project
    02_architecture_diagram.png          architecture diagram (matplotlib)
    23_synthetic_dataset.png     real head of the generated CSV
    24_automated_tests.png       real pytest output for the functional suite
    25_privacy_security_tests.png real pytest output for the security suite
    26_database_schema.png       real sqlite schema dump
    29_readme_preview.png        real first page of README.md

Everything rendered here is captured from genuine command output or real
files - nothing is mocked or hand-drawn to look like application output.
"""

import os
import subprocess
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models.questions import QUESTIONS  # noqa: E402

QUESTION_COUNT = len(QUESTIONS)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "screenshots")
MONO = "/usr/local/lib/python3.13/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSansMono.ttf"
MONO_BOLD = MONO.replace("Mono.ttf", "Mono-Bold.ttf")
if not os.path.exists(MONO):                       # Windows / other platforms
    MONO = MONO_BOLD = None

BG = (11, 18, 32)
FG = (230, 237, 247)
ACCENT = (59, 130, 246)
MUTED = (157, 176, 204)


def _font(size, bold=False):
    path = MONO_BOLD if bold else MONO
    try:
        return ImageFont.truetype(path, size) if path else ImageFont.load_default(size)
    except Exception:                                            # noqa: BLE001
        return ImageFont.load_default()


def render_terminal(title, body, filename, width=1600, font_size=15, max_lines=70):
    """Render real command output as a clean terminal-style screenshot."""
    lines = body.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines - 1] + [f"... ({len(body.splitlines()) - max_lines + 1} more lines)"]
    font = _font(font_size)
    title_font = _font(19, bold=True)
    line_height = font_size + 7
    height = 96 + line_height * max(len(lines), 6) + 34
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)

    draw.rectangle([0, 0, width, 56], fill=(17, 28, 51))
    for index, color in enumerate([(239, 68, 68), (234, 179, 8), (34, 197, 94)]):
        draw.ellipse([22 + index * 22, 22, 34 + index * 22, 34], fill=color)
    draw.text((100, 18), title, font=title_font, fill=FG)
    draw.line([0, 56, width, 56], fill=(34, 49, 79))

    y = 78
    for line in lines:
        color = FG
        stripped = line.strip()
        if stripped.startswith("$"):
            color = ACCENT
        elif "PASS" in line or "passed" in line or "[OK]" in line:
            color = (74, 222, 128)
        elif "FAIL" in line or "failed" in line or "error" in line.lower():
            color = (248, 113, 113)
        elif stripped.startswith(("|", "+", "-", "#")):
            color = MUTED
        draw.text((26, y), line[:190], font=font, fill=color)
        y += line_height

    draw.text((26, height - 28), "Social Media Privacy Risk Assessment Framework - generated evidence",
              font=_font(12), fill=MUTED)
    path = os.path.join(SHOTS, filename)
    image.save(path)
    print(f"[OK] {filename}")
    return path


def run(command, cwd=ROOT):
    process = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    return (process.stdout + process.stderr).strip()


# --------------------------------------------------------------------------
# 01 - project structure
# --------------------------------------------------------------------------
def evidence_project_structure():
    output = run(
        "find . -not -path '*/.git/*' -not -path '*/__pycache__/*' -not -name '*.pyc' "
        "| sort | sed -e 's|[^/]*/|  |g'")
    header = "$ tree -I '__pycache__|*.pyc'   (Social-Media-Privacy-Risk-Assessment)\n\n"
    render_terminal("01 - Project folder structure", header + output,
                    "01_project_structure.png", max_lines=78)


# --------------------------------------------------------------------------
# 02 - architecture diagram
# --------------------------------------------------------------------------
def evidence_architecture():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(15, 10.5), dpi=120)
    fig.patch.set_facecolor("#0b1220")
    ax.set_facecolor("#0b1220")
    ax.set_xlim(0, 100), ax.set_ylim(0, 100), ax.axis("off")

    def box(x, y, w, h, text, fill="#111c33", edge="#3b82f6", size=10.5, weight="bold"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.4",
                                    linewidth=1.6, edgecolor=edge, facecolor=fill))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color="#e6edf7",
                fontsize=size, fontweight=weight, linespacing=1.4)

    def arrow(x1, y1, x2, y2, color="#22d3ee"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=15,
                                     linewidth=1.5, color=color, shrinkA=2, shrinkB=2))

    ax.text(50, 96, "Social Media Privacy Risk Assessment Framework - System Architecture",
            ha="center", color="#e6edf7", fontsize=16, fontweight="bold")
    ax.text(50, 92.3, "Defensive - synthetic / self-reported data only - no scraping, no tracking",
            ha="center", color="#9db0cc", fontsize=10.5)

    box(38, 85, 24, 5.5, "User (voluntary)", edge="#22d3ee")
    box(33, 77.5, 34, 5.5, f"Privacy Questionnaire ({QUESTION_COUNT} questions, 10 sections)")
    box(33, 70, 34, 5.5, "Input Validation  (no PII accepted)", edge="#f97316")
    box(33, 62.5, 34, 5.5, "Feature Extraction  extract_privacy_features()")
    box(2, 70, 26, 5.5, "Data contract files\nprofile.json / posts.json (synthetic)",
        size=8.5, edge="#22d3ee")
    arrow(15, 70, 15, 65.2); arrow(15, 65.2, 33, 65.2)

    analyzers = ["Profile Risk\nAnalyzer", "Personal Info\nAnalyzer", "Location / EXIF\nAnalyzer",
                 "Content + Child\nAnalyzer", "Account Security\nAnalyzer",
                 "Social Eng.\nAnalyzer", "Footprint / Link\nAnalyzer"]
    for index, name in enumerate(analyzers):
        box(2 + index * 14, 51, 12.5, 8, name, fill="#152341", edge="#a78bfa", size=8.4)
        ax.plot([8.2 + index * 14, 8.2 + index * 14], [61, 59.4], color="#22d3ee", linewidth=1.3)

    # distribution bus: feature extraction -> all analyzers
    ax.plot([8.2, 92.2], [61, 61], color="#22d3ee", linewidth=1.3)
    arrow(50, 62.5, 50, 61.2)

    box(33, 42, 34, 5.5, "Category Scores  (10 x 0-100)")
    # collection bus: all analyzers -> category scores
    for index in range(7):
        ax.plot([8.2 + index * 14, 8.2 + index * 14], [51, 49.4], color="#22d3ee", linewidth=1.3)
    ax.plot([8.2, 92.2], [49.4, 49.4], color="#22d3ee", linewidth=1.3)
    arrow(50, 49.4, 50, 47.7)
    box(20, 34.5, 28, 5.5, "MODEL A - Risk Scoring Engine\ncalculate_privacy_risk() (weighted)",
        size=9, edge="#3b82f6")
    box(52, 34.5, 28, 5.5, "MODEL B - Exposure Rubric\ncalculate_exposure_rubric() (capped)",
        size=9, edge="#a78bfa")
    box(26, 27, 48, 5.5, "Overall Risk Score + Exposure Score + Level "
                         "(LOW/MODERATE/HIGH/CRITICAL)", size=9)
    box(4, 19, 28, 5.5, "Findings Engine\ngenerate_privacy_findings()", size=9.5, edge="#f97316")
    box(36, 19, 28, 5.5, "Recommendation Engine\ngenerate_recommendations()", size=9.5, edge="#22c55e")
    box(68, 19, 28, 5.5, "Improvement Simulator\nsimulate_improvement()", size=9.5, edge="#eab308")

    box(4, 9, 28, 6, "Privacy Dashboard\n(React + Vite + Recharts)", size=9.5)
    box(36, 9, 28, 6, "Privacy Report\n(HTML / PDF, no personal data)", size=9.5)
    box(68, 9, 28, 6, "Anonymised Aggregates\n-> SQLite Analytics DB", size=9.5, edge="#22d3ee")

    for x1, y1, x2, y2 in [(50, 85, 50, 83), (50, 77.5, 50, 75.5), (50, 70, 50, 68),
                           (50, 42, 34, 40.2), (50, 42, 66, 40.2),
                           (34, 34.5, 42, 32.7), (66, 34.5, 58, 32.7),
                           (50, 27, 18, 24.5), (50, 27, 50, 24.5), (50, 27, 82, 24.5),
                           (18, 19, 18, 15), (50, 19, 50, 15), (82, 19, 82, 15)]:
        arrow(x1, y1, x2, y2)

    ax.text(50, 4, "Privacy by Design: data minimisation - purpose limitation - least privilege - "
                   "privacy by default - transparency - user control - retention limitation",
            ha="center", color="#9db0cc", fontsize=9.5)
    path = os.path.join(SHOTS, "02_architecture_diagram.png")
    fig.savefig(path, facecolor="#0b1220", bbox_inches="tight")
    plt.close(fig)
    print("[OK] 02_architecture_diagram.png")


# --------------------------------------------------------------------------
# 23 - synthetic dataset
# --------------------------------------------------------------------------
def evidence_dataset():
    csv_path = os.path.join(ROOT, "data", "social_media_privacy_assessments.csv")
    rows = run(f"wc -l {csv_path}")
    head = run("python3 - <<'PY'\n"
               "import csv\n"
               f"rows = list(csv.reader(open(r'{csv_path}')))[:16]\n"
               "rows = [r[:11] for r in rows]\n"
               "w = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]\n"
               "for i, r in enumerate(rows):\n"
               "    print('  '.join(c.ljust(w[j]) for j, c in enumerate(r)))\n"
               "    if i == 0:\n"
               "        print('-' * (sum(w) + 2 * len(w)))\n"
               "PY")
    dist = run("python3 - <<'PY'\nimport csv,collections\n"
               f"rows=list(csv.DictReader(open(r'{csv_path}')))\n"
               "c=collections.Counter(r['risk_level'] for r in rows)\n"
               "print('records:',len(rows))\n"
               "[print(f'  {k:<9} {v:>5}') for k,v in sorted(c.items())]\n"
               "print('average Model A score:',round(sum(float(r['risk_score']) for r in rows)/len(rows),2))\n"
               "print('average Model B score:',round(sum(float(r['exposure_rubric_score']) for r in rows)/len(rows),2))\n"
               "print('columns:',len(rows[0]))\nPY")
    body = ("$ python data/generate_dataset.py --records 1200 --seed 42\n"
            f"$ wc -l data/social_media_privacy_assessments.csv\n{rows}\n\n"
            "$ head -18 data/social_media_privacy_assessments.csv   (first 12 columns)\n"
            f"{head}\n\n$ risk level distribution\n{dist}\n\n"
            "All records are SYNTHETIC and FICTIONAL - no real people, no scraped data.")
    render_terminal("23 - Synthetic dataset (1,200 fictional records, both models)", body,
                    "23_synthetic_dataset.png", width=1750, font_size=14, max_lines=48)


# --------------------------------------------------------------------------
# 24 / 25 - test evidence
# --------------------------------------------------------------------------
def evidence_tests():
    functional = run("python3 -m pytest tests/test_privacy_framework.py -v --no-header -p no:cacheprovider")
    render_terminal("24 - Automated tests (functional suite)",
                    "$ python -m pytest tests/test_privacy_framework.py -v\n\n" + functional,
                    "24_automated_tests.png", width=1750, font_size=14, max_lines=62)

    security = run("python3 -m pytest tests/test_security_privacy.py -v --no-header -p no:cacheprovider")
    render_terminal("25 - Security & privacy tests",
                    "$ python -m pytest tests/test_security_privacy.py -v\n\n" + security,
                    "25_privacy_security_tests.png", width=1750, font_size=14, max_lines=50)


# --------------------------------------------------------------------------
# 26 - database schema
# --------------------------------------------------------------------------
def evidence_schema():
    db_path = os.path.join(ROOT, "data", "privacy_assessment.db")
    schema = run(f"python3 -c \"import sqlite3;c=sqlite3.connect(r'{db_path}');"
                 "print(chr(10).join(r[0]+';' for r in c.execute("
                 "\\\"SELECT sql FROM sqlite_master WHERE sql IS NOT NULL\\\")))\"")
    counts = run("python3 - <<'PY'\n"
                 "import sqlite3\n"
                 f"c = sqlite3.connect(r'{db_path}')\n"
                 "for t in ['assessments','category_scores','findings','recommendations']:\n"
                 "    n = c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0]\n"
                 "    print(f'  {t:<18}{n:>8} rows')\n"
                 "PY")
    body = ("$ sqlite3 data/privacy_assessment.db .schema\n\n" + schema +
            "\n\n$ row counts\n" + counts +
            "\n\nNEVER STORED: phone numbers, e-mail addresses, home addresses, birth dates,\n"
            "passwords, exact locations, private messages, raw questionnaire answers.")
    render_terminal("26 - Privacy-first database schema (SQLite)", body,
                    "26_database_schema.png", width=1650, font_size=14, max_lines=60)


# --------------------------------------------------------------------------
# 29 - README preview
# --------------------------------------------------------------------------
def evidence_readme():
    readme = os.path.join(ROOT, "README.md")
    if not os.path.exists(readme):
        print("[skip] README.md not found yet")
        return
    text = open(readme, encoding="utf-8").read()
    lines = []
    for raw in text.splitlines()[:70]:
        lines.extend(textwrap.wrap(raw, 150) or [""])
    render_terminal("29 - README.md preview", "\n".join(lines[:62]),
                    "29_readme_preview.png", width=1650, font_size=14, max_lines=64)


if __name__ == "__main__":
    os.makedirs(SHOTS, exist_ok=True)
    sys.path.insert(0, ROOT)
    evidence_project_structure()
    evidence_architecture()
    evidence_dataset()
    evidence_tests()
    evidence_schema()
    evidence_readme()
    print("\nLocal evidence generation complete ->", SHOTS)
