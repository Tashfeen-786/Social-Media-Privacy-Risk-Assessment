"""
privacy_checklist.py
--------------------
The downloadable / printable SOCIAL MEDIA PRIVACY CHECKLIST (21 items).
"""

from typing import Any, Dict, List

CHECKLIST: List[Dict[str, Any]] = [
    {"id": 1, "section": "Profile", "item": "Review profile visibility"},
    {"id": 2, "section": "Profile", "item": "Hide unnecessary contact information"},
    {"id": 3, "section": "Personal Information", "item": "Review birth-date visibility"},
    {"id": 4, "section": "Location", "item": "Review location sharing"},
    {"id": 5, "section": "Location", "item": "Avoid unnecessary real-time location posts"},
    {"id": 6, "section": "Tagging", "item": "Review tagging permissions"},
    {"id": 7, "section": "Connections", "item": "Review followers / friends"},
    {"id": 8, "section": "Connections", "item": "Verify unfamiliar requests"},
    {"id": 9, "section": "Account Security", "item": "Enable MFA"},
    {"id": 10, "section": "Account Security", "item": "Enable login alerts where available"},
    {"id": 11, "section": "Account Security", "item": "Review active sessions"},
    {"id": 12, "section": "Third-Party Apps", "item": "Review connected apps"},
    {"id": 13, "section": "Third-Party Apps", "item": "Remove unused integrations"},
    {"id": 14, "section": "Content", "item": "Review old public posts"},
    {"id": 15, "section": "Content", "item": "Review photo privacy"},
    {"id": 16, "section": "Social Engineering", "item": "Be cautious with unexpected links"},
    {"id": 17, "section": "Social Engineering", "item": "Never share verification codes"},
    {"id": 18, "section": "Digital Footprint", "item": "Review privacy settings periodically"},
    {"id": 19, "section": "Children / Minors",
     "item": "Review child/minor-related media exposure"},
    {"id": 20, "section": "Digital Footprint", "item": "Review username/handle reuse"},
    {"id": 21, "section": "Linked Sites",
     "item": "Review linked-site privacy/tracker information"},
]


def get_checklist() -> Dict[str, Any]:
    return {
        "title": "Social Media Privacy Checklist",
        "total_items": len(CHECKLIST),
        "items": CHECKLIST,
        "note": ("Educational checklist. Setting names differ between platforms; apply "
                 "the equivalent option on each platform you use."),
    }


def checklist_html() -> str:
    rows = "\n".join(
        f'<tr><td class="num">{i["id"]}</td><td class="box">&#9744;</td>'
        f'<td>{i["section"]}</td><td>{i["item"]}</td></tr>' for i in CHECKLIST)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Social Media Privacy Checklist</title>
<style>
 body{{font-family:'Segoe UI',Arial,sans-serif;margin:40px;color:#0f172a;background:#fff}}
 h1{{font-size:26px;margin-bottom:4px}} p.sub{{color:#475569;margin-top:0}}
 table{{width:100%;border-collapse:collapse;margin-top:18px}}
 th,td{{border:1px solid #cbd5e1;padding:9px 12px;text-align:left;font-size:14px}}
 th{{background:#0f172a;color:#fff}} td.num{{width:40px}}
 td.box{{width:40px;font-size:18px;text-align:center}}
 tr:nth-child(even){{background:#f8fafc}}
 .note{{margin-top:18px;font-size:12px;color:#64748b;border-left:3px solid #2563eb;padding-left:10px}}
 @media print{{body{{margin:12mm}}}}
</style></head><body>
<h1>Social Media Privacy Checklist</h1>
<p class="sub">Social Media Privacy Risk Assessment Framework &mdash; printable checklist
 ({len(CHECKLIST)} items)</p>
<table><thead><tr><th>#</th><th>Done</th><th>Area</th><th>Checklist item</th></tr></thead>
<tbody>{rows}</tbody></table>
<p class="note">Educational checklist for defensive privacy awareness. Setting names differ
between platforms; apply the equivalent option on each platform you use.</p>
</body></html>"""
