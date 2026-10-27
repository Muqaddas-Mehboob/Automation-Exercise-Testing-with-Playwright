@echo off
REM Run from the project folder with the venv activated. Output = HTML reports.
if not exist reports mkdir reports
if not exist screenshots mkdir screenshots

REM 1) Everything, all 3 browsers -> one HTML report
pytest --browser chromium --browser firefox --browser webkit --html=reports\report-all-browsers.html --self-contained-html

REM 2) Deliberate bug demo (BUG-01 must FAIL)
set INJECT_BUG=1
pytest tests\bug_demo --browser chromium --browser firefox --browser webkit --html=reports\report_with_bug.html --self-contained-html
set INJECT_BUG=

echo.
echo Done. Open the HTML files inside the reports folder.
