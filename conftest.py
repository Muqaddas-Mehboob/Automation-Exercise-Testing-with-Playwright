"""Single conftest for the whole project: helpers + fixtures + report hook.
Used by: tests/api, tests/mocking, tests/bug_demo, tests/e2e"""
import base64
import json
import os
import re
import time
import uuid
from pathlib import Path

import pytest
import pytest_html
from bs4 import BeautifulSoup
from playwright.sync_api import Error as PlaywrightError

# =============================================================== settings
BASE_URL = "https://automationexercise.com"

# Better: set these as environment variables instead of keeping them in code.
TEST_EMAIL = os.getenv("AE_TEST_EMAIL", "zeenu123@gmail.com")
TEST_PASSWORD = os.getenv("AE_TEST_PASSWORD", "12345678")

SEARCH_URL = re.compile(r"/products\?search=")
SCREENSHOT_DIR = Path("screenshots")

# Ad / tracking requests that make Firefox & WebKit hang or overlay the page.
AD_RE = re.compile(
    r"(googlesyndication|doubleclick|googleadservices|adservice\.google|"
    r"pagead|google-analytics|googletagmanager|amazon-adsystem|adsbygoogle|"
    r"taboola|outbrain|criteo)"
)

HIDE_ADS_JS = """
document.addEventListener('DOMContentLoaded', () => {
  const s = document.createElement('style');
  s.textContent = `ins.adsbygoogle, iframe[id^="aswift"], iframe[src*="googlesyndication"],
    .google-auto-placed, #ad_position_box, #dismiss-button, div[id^="google_ads"],
    div[id^="aswift"] { display:none !important; pointer-events:none !important; }`;
  document.head.appendChild(s);
});
"""


# =============================================================== API / mocking helpers
def body(resp):
    """The site returns JSON as text/html, so parse manually."""
    return json.loads(resp.text())


def soup(resp_or_html):
    html = resp_or_html if isinstance(resp_or_html, str) else resp_or_html.text()
    return BeautifulSoup(html, "html.parser")


def strip_products(html: str) -> str:
    """Remove every product card from a products/search page."""
    s = BeautifulSoup(html, "html.parser")
    for el in s.select(".features_items .product-image-wrapper"):
        el.decompose()
    return str(s)


def make_user() -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        "name": f"QA {uid}", "email": f"qa_{uid}@example.com", "password": "Test@1234",
        "title": "Mr", "birth_date": "10", "birth_month": "May", "birth_year": "1999",
        "firstname": "QA", "lastname": "Tester", "company": "NED",
        "address1": "NED University", "address2": "Gulshan", "country": "Pakistan",
        "zipcode": "75270", "state": "Sindh", "city": "Karachi", "mobile_number": "03001234567",
    }


# =============================================================== E2E helpers
def wait_for_site_ready(page, timeout=60):
    """Wait until the real site is shown (not the 'request is being verified' page)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            text = page.locator("body").inner_text(timeout=2000)
        except PlaywrightError:
            text = ""
        if "request is being verified" not in text and page.locator("a[href='/products']").count() > 0:
            return
        page.wait_for_timeout(1000)
    raise AssertionError("Site did not finish loading (stuck on verification page?)")


def go_to(page, path="/"):
    """Open a page directly (more reliable than clicking menu links in Firefox)."""
    url = BASE_URL + path
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    wait_for_site_ready(page)
    if "google_vignette" in page.url:          # full-screen Google ad -> reload clean
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        wait_for_site_ready(page)


def safe_click(locator, timeout=8000):
    """Normal click; if Firefox/WebKit hangs (ad overlay, 'not stable') use a JavaScript click."""
    try:
        locator.scroll_into_view_if_needed(timeout=timeout)
        locator.click(timeout=timeout, no_wait_after=True)
    except PlaywrightError:
        locator.evaluate("el => el.click()")


# =============================================================== API fixtures
@pytest.fixture(scope="session")
def api(playwright):
    ctx = playwright.request.new_context(base_url=BASE_URL)
    yield ctx
    ctx.dispose()


@pytest.fixture
def cart_api(playwright):
    """Fresh request context = fresh cookie jar = its own empty cart (cart is session based)."""
    ctx = playwright.request.new_context(base_url=BASE_URL)
    yield ctx
    ctx.dispose()


# =============================================================== browser fixtures
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1366, "height": 768}, "locale": "en-US"}


@pytest.fixture(autouse=True)
def browser_setup(request):
    """Runs for every test, but only touches the browser if the test uses one
    (API tests stay browser-free): blocks ads, hides ad overlays, sets timeouts."""
    if "page" in request.fixturenames:
        page = request.getfixturevalue("page")
        context = request.getfixturevalue("context")
        context.route(AD_RE, lambda route: route.abort())
        page.add_init_script(HIDE_ADS_JS)
        page.set_default_timeout(30000)
        page.set_default_navigation_timeout(60000)
    yield


@pytest.fixture
def site_page(page):
    """For mocking / bug-demo tests: page + JS error collector + optional deliberate bug."""
    # DELIBERATE BUG (only when INJECT_BUG=1): search returns ZERO products
    if os.getenv("INJECT_BUG") == "1":
        def buggy(route):
            resp = route.fetch()
            route.fulfill(response=resp, body=strip_products(resp.text()))
        page.route(SEARCH_URL, buggy)

    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.js_errors = errors
    return page


# =============================================================== report hook
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """After every browser test: save a screenshot AND embed it in the HTML report."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    page = item.funcargs.get("page")
    if page is None:                       # API tests have no browser page
        return

    browser_name = item.funcargs.get("browser_name", "browser")
    name = re.sub(r"[^A-Za-z0-9_-]+", "_", item.originalname or item.name)
    status = "PASS" if report.passed else ("SKIP" if report.skipped else "FAIL")
    try:
        png = page.screenshot(timeout=15000)       # viewport only (fast, small)
        folder = SCREENSHOT_DIR / browser_name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}_{browser_name}__{status}.png").write_bytes(png)

        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.png(base64.b64encode(png).decode(), name=f"{browser_name} screenshot"))
        report.extras = extras
    except Exception as exc:
        print(f"\nCould not save screenshot for {name}: {exc}")
