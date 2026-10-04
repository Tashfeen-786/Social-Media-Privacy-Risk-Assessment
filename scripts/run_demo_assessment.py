"""
run_demo_assessment.py
----------------------
Runs the safe fictional DEMONSTRATION PROFILE end to end and prints the real
engine output:

    Overall Risk Score -> Risk Level -> Category Scores -> Top Findings
    -> Recommendations -> Improvement Simulation

It also generates the HTML and PDF privacy reports into reports/.
100% synthetic: no real person, no real account, no real data.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from backend.models.categories import CATEGORIES                      # noqa: E402
from backend.models.database import PrivacyDatabase                   # noqa: E402
from backend.services.assessment_engine import (                      # noqa: E402
    calculate_privacy_risk, demo_profile_answers)
from backend.services.improvement_simulator import simulate_improvement  # noqa: E402
from backend.services.report_generator import (                       # noqa: E402
    generate_html_report, generate_pdf_report)

from backend.services.improvement_simulator import RECOMMENDED_SET  # noqa: E402

# The improvement set named in the project specification
RECOMMENDED_IMPROVEMENTS = RECOMMENDED_SET


def line(char="=", width=78):
    print(char * width)


def main():
    answers = demo_profile_answers()
    result = calculate_privacy_risk(answers)
    PrivacyDatabase().save_assessment(result)

    line()
    print(" SAFE DEMONSTRATION PROFILE (fictional / synthetic - not a real person)")
    line()
    print(" Profile: Public | Phone: Public | Email: Private | Full Birthday: Public")
    print(" Location: Public | Real-Time Check-ins: Yes | Travel Plans: Public")
    print(" Unknown Requests: Often Accepted | Tag Review: Disabled | MFA: Disabled")
    print(" Login Alerts: Disabled | Third-Party Apps: Not Reviewed | Old Posts: Not Reviewed")
    line()
    print(f"\n ASSESSMENT ID      : {result['assessment_id']}")
    print(f" MODEL A  OVERALL RISK SCORE : {result['overall_score']} / 100")
    print(f" MODEL A  RISK LEVEL         : {result['risk_level']}")
    rubric = result["exposure_rubric"]
    print(f" MODEL B  EXPOSURE RUBRIC    : {rubric['score']} / 100  ({rubric['risk_level']})")
    print("          rubric categories  : " + ", ".join(
        f"{c['label'].split(' /')[0]}={c['points']:.0f}/{c['max_points']}"
        for c in rubric["categories"]))
    print(f" SECURITY CONTROLS  : {result['security_controls_enabled']}"
          f"/{result['security_controls_total']} enabled")

    print("\n CATEGORY SCORES (0 = lower assessed risk, 100 = higher)")
    line("-")
    for row in result["score_breakdown"]:
        bar = "#" * int(row["score"] / 4)
        print(f"  {row['label']:<24} {row['score']:>6.2f}  {row['level']:<9} "
              f"w={row['weight_percent']:>4.1f}%  {bar}")

    print("\n TOP FINDINGS")
    line("-")
    for finding in result["findings"][:12]:
        print(f"  [{finding['severity']:<8}] {finding['finding']}")
        print(f"             -> {finding['recommended_action']}")

    print("\n RECOMMENDATIONS (by priority)")
    line("-")
    for priority in ("IMMEDIATE", "IMPORTANT", "GOOD PRACTICE"):
        items = [r for r in result["recommendations"] if r["priority"] == priority]
        print(f"  {priority} ({len(items)}):")
        for rec in items[:6]:
            print(f"     - {rec['recommendation']}")

    print("\n PRIVACY IMPROVEMENT SIMULATION  [FRAMEWORK SIMULATION]")
    line("-")
    simulation = simulate_improvement(answers, RECOMMENDED_IMPROVEMENTS)
    print(f"  CURRENT RISK   : {simulation['current_score']} "
          f"({simulation['current_risk_level']})")
    print(f"  IMPROVEMENTS   : {len(simulation['changes_applied'])} applied")
    for change in simulation["changes_applied"]:
        print(f"     + {change['label']}")
    print(f"  NEW SIMULATED  : {simulation['new_score']} ({simulation['new_risk_level']})")
    print(f"  RISK REDUCTION : -{simulation['risk_reduction']} points "
          f"(-{simulation['risk_reduction_percent']}%)")
    print(f"  EXPOSURE RUBRIC: {simulation['current_exposure_score']} -> "
          f"{simulation['new_exposure_score']} "
          f"(-{simulation['exposure_reduction']} points)")
    print(f"  FINDINGS       : {simulation['findings_before']} -> "
          f"{simulation['findings_after']}")
    print("\n  NOTE: this is a framework simulation of the educational model. It does not "
          "guarantee real-world safety.")

    html_path = generate_html_report(result)
    pdf_path = generate_pdf_report(result)
    print(f"\n  Report (HTML): {html_path}")
    print(f"  Report (PDF) : {pdf_path}")
    line()
    print(" " + result["disclaimer"])
    line()
    return result, simulation


if __name__ == "__main__":
    main()
