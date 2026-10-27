# Automation-Exercise: Testing with Playwright & pytest

## Scope
Test project for the public practice website https://automationexercise.com, covering four features: **Login, Product Search, Cart, Contact Us**.

| Suite | Folder | Tests | What it checks |
|---|---|---|---|
| End-to-end (browser) | `tests/e2e` | 12 (3 per feature) | Positive, negative and boundary user flows |
| API | `tests/api` | 7 test functions (11 test cases) | CRUD operations, negative cases, status codes (200 / 404) |
| Network mocking | `tests/mocking` | 3 | Page behaviour when the server sends empty data or an error |
| Deliberate bug | `tests/bug_demo` | 1 | Proves the suite catches a problem (search results removed) |

Browsers: Chromium, Firefox, WebKit.

## Project structure
```
conftest.py        <- single conftest: helpers, fixtures, screenshot + HTML-report hook
pytest.ini         <- base_url, test path, reruns, markers
requirements.txt
run_all.bat        <- runs everything on 3 browsers + the bug demo (Windows)
tests/
  e2e/             <- test_login.py, test_search.py, test_cart.py, test_contact.py
  api/             <- Login, Search, Cart API tests + status-code tests
  mocking/         <- network mocking tests
  bug_demo/        <- deliberate-bug test
reports/           <- HTML reports (created after a run)
screenshots/       <- screenshots per browser (created after a run)
```

## 1. Create and activate a virtual environment (Windows PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2. Install packages and browsers
```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium firefox webkit
```

## 3. Optional: configure a test account for the valid-login test
Use a test account you are permitted to use. Do not commit credentials to Git or include them in the ZIP.
```powershell
$env:AE_TEST_EMAIL="your-test-account@example.com"
$env:AE_TEST_PASSWORD="your-test-password"
```
If these variables are not set, LOG-001 is skipped; all other tests can still run.

## 4. Run tests
All suites, all three browsers, one HTML report:
```powershell
pytest --browser chromium --browser firefox --browser webkit --html=reports/report-all-browsers.html --self-contained-html
```
One browser at a time:
```powershell
pytest --browser chromium --html=reports/report-chromium.html --self-contained-html
pytest --browser firefox  --html=reports/report-firefox.html  --self-contained-html
pytest --browser webkit   --html=reports/report-webkit.html   --self-contained-html
```
Only one suite (examples):
```powershell
pytest tests/e2e --browser firefox
pytest tests/api
pytest tests/mocking --browser chromium
```
Show the browser while tests run:
```powershell
pytest tests/e2e --browser chromium --headed
```
On Windows you can also run everything (3 browsers + bug demo) with `run_all.bat`.

Notes:
- API tests do not use a browser, so they run once per command, not once per browser.
- Do not run tests in parallel (`-n`): the site rate-limits automated traffic.
- `pytest.ini` retries a failed test once (`--reruns 1`, from `pytest-rerunfailures`). Mention this in your report; remove the option if you want raw results.

## 5. Deliberate bug demo (proves the tests catch problems)
The website is a third-party site, so it is not modified. The bug is injected in the browser with Playwright request interception: when `INJECT_BUG=1`, the search-results response is changed so it contains no products. `test_bug_01_search_shows_results` then fails.

Normal run (passes):
```powershell
pytest tests/bug_demo --browser chromium
```
Run with the bug (fails; keep the report and screenshots as evidence):
```powershell
$env:INJECT_BUG="1"
pytest tests/bug_demo --browser chromium --browser firefox --browser webkit --html=reports/report_with_bug.html --self-contained-html
Remove-Item Env:INJECT_BUG
```
Always remove `INJECT_BUG` afterwards, otherwise later runs will also be "buggy".

## Screenshots and reports
- After every browser test a viewport screenshot is saved to `screenshots/<browser>/<test>_<browser>__PASS|FAIL.png`.
- The same screenshot is embedded in the pytest-html report (expand a test row to see it). Reports are self-contained, so a single HTML file can be shared.

## Important notes
- Replace the result columns in your report with the real output of your own runs; the numbers in any template are placeholders until you run the tests.
- Public websites can change their layout, slow down, or rate-limit automated traffic. If a locator fails, inspect the live page and update the selector based on the real DOM.
- Firefox and WebKit sometimes receive a "Please wait while your request is being verified" page and ad overlays. The project handles this by blocking ads, opening pages by direct URL (`go_to`), and falling back to a JavaScript click (`safe_click`). If tests still hang, try `--headed --slowmo 300`.
- The Cart API tests (`/add_to_cart/<id>`, `/view_cart`, `/delete_cart/<id>`) depend on the site's URLs and HTML ids. Confirm them in browser DevTools (Network tab) if they fail.
- Do not claim a bug exists until you have reproduced it. A failed automation test can also mean a stale selector, network issue, or timing issue.