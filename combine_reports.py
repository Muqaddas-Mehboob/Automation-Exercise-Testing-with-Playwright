
import json
import glob
import os
from datetime import datetime
from html import escape

REPORTS_DIR = "reports"
OUTPUT_FILE = os.path.join(REPORTS_DIR, "combined_report.html")

json_files = glob.glob(os.path.join(REPORTS_DIR, "*.json"))

all_tests = []
total_passed = 0
total_failed = 0
total_skipped = 0

for file_path in json_files:
    if os.path.basename(file_path) == "combined_report.json":
        continue

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            report = json.load(file)

        for test in report.get("tests", []):
            outcome = test.get("outcome", "unknown")

            if outcome == "passed":
                total_passed += 1
            elif outcome == "failed":
                total_failed += 1
            elif outcome == "skipped":
                total_skipped += 1

            all_tests.append({
                "name": test.get("nodeid", "Unknown test"),
                "outcome": outcome,
                "message": test.get("call", {}).get(
                    "longrepr", ""
                ),
                "source": os.path.basename(file_path)
            })

    except (json.JSONDecodeError, OSError) as error:
        print(f"Could not read {file_path}: {error}")

if not json_files:
    print("No JSON reports found in the reports folder.")
    raise SystemExit(1)

rows = ""

for test in all_tests:
    outcome = test["outcome"].upper()
    message = escape(str(test["message"]))
    rows += f"""
    <tr>
        <td>{escape(test['name'])}</td>
        <td>{escape(outcome)}</td>
        <td>{escape(test['source'])}</td>
        <td><pre>{message}</pre></td>
    </tr>
    """

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Combined Playwright Test Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 30px; }}
h1 {{ color: #333; }}
.summary {{ display: flex; gap: 20px; margin: 20px 0; }}
.card {{ padding: 15px; background: #f2f2f2; border-radius: 8px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
th {{ background: #333; color: white; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
</style>
</head>
<body>
<h1>Combined Playwright Test Report</h1>
<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<div class="summary">
<div class="card">Total tests: {len(all_tests)}</div>
<div class="card">Passed: {total_passed}</div>
<div class="card">Failed: {total_failed}</div>
<div class="card">Skipped: {total_skipped}</div>
</div>
<table>
<thead>
<tr>
<th>Test Name</th>
<th>Status</th>
<th>Source Report</th>
<th>Failure Details</th>
</tr>
</thead>
<tbody>{rows}</tbody>
</table>
</body>
</html>
"""

os.makedirs(REPORTS_DIR, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"Combined report created: {OUTPUT_FILE}")
print(f"Total tests: {len(all_tests)}")
print(f"Passed: {total_passed}")
print(f"Failed: {total_failed}")
print(f"Skipped: {total_skipped}")
