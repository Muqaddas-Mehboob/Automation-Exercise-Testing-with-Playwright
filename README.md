# Automation-Exercise — Testing with Playwright & pytest

## Scope
This project contains 12 planned end-to-end tests across Login, Product Search, Cart, and Contact Us. It uses the public practice website https://automationexercise.com.

## 1. Create and activate a virtual environment (Windows PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2. Install packages and browsers
```powershell
python -m pip install -r requirements.txt
python -m playwright install
```

## 3. Optional: configure a test account for the valid-login test
Use a test account you are permitted to use. Do not commit credentials to Git or include them in the ZIP.
```powershell
$env:AE_TEST_EMAIL="your-test-account@example.com"
$env:AE_TEST_PASSWORD="your-test-password"
```
If these variables are not set, LOG-001 is skipped; the other login tests can still run.

## 4. Run tests
Chromium:
```powershell
pytest --browser chromium --html=reports/report-chromium.html --self-contained-html
```
Firefox:
```powershell
pytest --browser firefox --html=reports/report-firefox.html --self-contained-html
```
WebKit:
```powershell
pytest --browser webkit --html=reports/report-webkit.html --self-contained-html
```
All three browser engines in one run:
```powershell
pytest --browser chromium --browser firefox --browser webkit --html=reports/report-all-browsers.html --self-contained-html
```

Show the browser while tests run:
```powershell
pytest --browser chromium --headed
```

## Screenshots
The `screenshots` folder is populated after tests run. The fixture attempts to save a full-page screenshot for each test, naming it with the test name and PASS/FAIL status. The HTML reports are created by pytest-html.

## Important notes
- The tests have not been executed as part of preparing this starter project. Run them and update your report using the actual output.
- Public websites can change their layout, slow down, or rate-limit automated traffic. If a locator fails, inspect the live page and update the selector based on the real DOM.
- Do not claim a bug exists until you have reproduced it. A failed automation test can also mean a stale selector, network issue, or timing issue.
- Do not deliberately alter a third-party website. If your instructor requires a deliberately introduced bug, use a local copy or a website your team owns, with permission.
