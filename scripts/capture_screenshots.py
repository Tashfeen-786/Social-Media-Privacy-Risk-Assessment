"""
capture_screenshots.py
----------------------
Captures REAL browser screenshots of the running application (evidence 03-22)
with Playwright + Chromium at 1600x1000 (device scale 1.5 -> 2400x1500).

Nothing is drawn or mocked: every image is a screenshot of the actual executed
React UI, driven by real clicks and real API responses, using synthetic demo
data only.

Prerequisites:
    pip install playwright && python -m playwright install chromium
    backend :8000   ->  python -m uvicorn backend.app:app --port 8000
    frontend :5173  ->  npm run dev   (inside frontend-react)

Usage:
    python scripts/capture_screenshots.py [react_url] [api_url]
"""

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "screenshots")
UI = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"
API = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"

from playwright.sync_api import sync_playwright  # noqa: E402

IMPROVEMENTS = [
    "make_phone_private", "make_birthday_private", "make_location_private",
    "make_travel_private", "verify_unknown_requests", "enable_tag_review",
    "enable_mfa", "enable_login_alerts", "review_third_party_apps",
    "protect_child_media", "reduce_linkage_risk", "strip_photo_metadata",
]


def shot(target, name):
    path = os.path.join(SHOTS, name)
    target.screenshot(path=path)
    print(f"[OK] {name}")


def main():
    os.makedirs(SHOTS, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 1000},
                                device_scale_factor=1.5)

        # ---------------- 03 homepage ----------------
        page.goto(UI, wait_until="networkidle")
        page.wait_for_timeout(1200)
        shot(page, "03_privacy_assessment_homepage.png")

        # Make the sticky navigation static so element screenshots are never
        # overlapped by the floating header (purely a capture-time style).
        unstick = ".nav{position:static !important} .progress-wrap{position:static !important}"

        # ---------------- questionnaire ----------------
        page.click("text=Start Privacy Assessment")
        page.wait_for_selector(".q", timeout=20000)
        page.add_style_tag(content=unstick)
        page.click("text=Load demo profile")
        page.wait_for_timeout(900)
        shot(page, "04_questionnaire.png")

        sections = {
            "#sec-profile-visibility": "05_profile_privacy_section.png",
            "#sec-personal-information": "06_personal_information_section.png",
            "#sec-location-privacy": "07_location_section.png",
            "#sec-authentication-account-security": "08_account_security_section.png",
            "#sec-messaging-social-engineering": "09_social_engineering_section.png",
        }
        for selector, filename in sections.items():
            page.locator(selector).scroll_into_view_if_needed()
            page.wait_for_timeout(350)
            shot(page.locator(selector), filename)

        # ---------------- submit & results ----------------
        page.click("text=Calculate Privacy Risk")
        page.wait_for_selector("#topCards", timeout=25000)
        page.add_style_tag(content=unstick)
        page.wait_for_timeout(2200)

        shot(page.locator("#topCards"), "10_overall_risk_score.png")
        shot(page.locator("#catTableCard"), "11_category_scores.png")
        page.locator("#chartsRow").scroll_into_view_if_needed()
        page.wait_for_timeout(900)
        shot(page.locator("#chartsRow"), "12_privacy_risk_chart.png")
        shot(page.locator("#findingsCard"), "13_top_findings.png")
        shot(page.locator("#recCard"), "14_recommendations.png")

        # ---------------- improvement simulator ----------------
        page.locator("#simCard").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        shot(page.locator("#simCard"), "15_improvement_simulator_before.png")

        for key in IMPROVEMENTS:
            checkbox = page.locator(f'.imp:has-text("{key}")')  # fallback below
        labels = page.locator(".imp")
        count = labels.count()
        for index in range(count):
            label = labels.nth(index)
            text = (label.inner_text() or "").lower()
            if any(word in text for word in [
                    "phone", "birth date", "location", "travel", "unknown connection",
                    "tag review", "multi-factor", "login alerts", "third-party",
                    "children", "link-in-bio", "metadata"]):
                label.locator("input").check()
        page.click("text=Run simulation")
        page.wait_for_timeout(2500)
        shot(page.locator("#simCard"), "16_improvement_simulator_after.png")
        shot(page.locator(".sim-grid"), "17_risk_reduction.png")

        # ---------------- dashboard ----------------
        page.click(".nav-links >> text=Dashboard")
        page.wait_for_selector(".stat", timeout=25000)
        page.wait_for_timeout(2800)
        shot(page, "18_privacy_dashboard.png")
        page.add_style_tag(content=unstick)
        charts = page.locator(".card:has(h3:text('Privacy Risk Distribution'))")
        shot(charts.first, "19_risk_distribution.png")
        weakness = page.locator(".card:has(h3:text('Top Privacy Weaknesses'))")
        weakness.first.scroll_into_view_if_needed()
        page.wait_for_timeout(800)
        shot(weakness.first, "20_top_weakness_chart.png")

        # ---------------- 30 file analyzer (extra evidence) ----------------
        page.click(".nav-links >> text=File Analyzer")
        page.wait_for_timeout(700)
        page.click("text=Analyse demo_oversharer")
        page.wait_for_timeout(2200)
        shot(page, "30_file_analyzer_exposure_rubric.png")

        # ---------------- checklist ----------------
        page.goto(f"{API}/api/privacy-checklist?fmt=html", wait_until="networkidle")
        page.wait_for_timeout(600)
        shot(page, "21_privacy_checklist.png")

        # ---------------- privacy report ----------------
        reports = sorted(
            [f for f in os.listdir(os.path.join(ROOT, "reports")) if f.endswith(".html")],
            key=lambda f: os.path.getmtime(os.path.join(ROOT, "reports", f)), reverse=True)
        if reports:
            page.goto("file://" + os.path.join(ROOT, "reports", reports[0]), wait_until="load")
            page.wait_for_timeout(800)
            shot(page, "22_privacy_report.png")
        else:
            print("[skip] no HTML report found - run scripts/run_demo_assessment.py first")

        browser.close()
    print("\nBrowser screenshot capture complete ->", SHOTS)


if __name__ == "__main__":
    main()
