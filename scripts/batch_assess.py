"""
batch_assess.py
---------------
Batch CLI: run the file-driven exposure rubric over every sample folder in
data/samples/ and export a CSV summary for workshops / org roll-ups.

Only SYNTHETIC sample folders are processed. Nothing is scraped.

Usage:
    python scripts/batch_assess.py [--samples data/samples] [--out reports/privacy_report.csv]
"""

import argparse
import csv
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from backend.services.exposure_rubric import score_profile  # noqa: E402


def run(samples_dir: str, out_path: str) -> str:
    rows = []
    for folder in sorted(glob.glob(os.path.join(samples_dir, "*"))):
        profile_path = os.path.join(folder, "profile.json")
        posts_path = os.path.join(folder, "posts.json")
        if not (os.path.exists(profile_path) and os.path.exists(posts_path)):
            continue
        with open(profile_path, encoding="utf-8") as handle:
            profile = json.load(handle)
        with open(posts_path, encoding="utf-8") as handle:
            posts = json.load(handle)
        result = score_profile(profile, posts)
        row = {
            "sample": os.path.basename(folder),
            "platform": profile.get("platform", "unknown"),
            "exposure_score": result["score"],
            "risk_level": result["risk_level"],
            "findings_count": len(result["findings"]),
        }
        row.update({f"rubric_{c['key']}": c["points"] for c in result["categories"]})
        rows.append(row)

    if not rows:
        print("[WARN] no sample folders found in", samples_dir)
        return ""

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(f"  {row['sample']:<20} {row['exposure_score']:>6} "
              f"{row['risk_level']:<9} {row['findings_count']} findings")
    print(f"[OK] wrote {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch privacy exposure assessment")
    parser.add_argument("--samples", default=os.path.join(ROOT, "data", "samples"))
    parser.add_argument("--out", default=os.path.join(ROOT, "reports", "privacy_report.csv"))
    args = parser.parse_args()
    run(args.samples, args.out)
