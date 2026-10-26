@echo off
REM 1) Normal run
pytest tests --browser chromium --browser firefox --browser webkit --screenshot on --output=test-results --html=reports\report_normal.html --self-contained-html

REM 2) Run with deliberate bug (BUG-01 fail hona chahiye)
set INJECT_BUG=1
pytest tests --browser chromium --browser firefox --browser webkit --screenshot on --output=test-results-bug --html=reports\report_with_bug.html --self-contained-html
set INJECT_BUG=