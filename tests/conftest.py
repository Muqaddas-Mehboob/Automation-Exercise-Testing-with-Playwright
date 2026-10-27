
import re
from pathlib import Path
import pytest

BASE_URL = "https://automationexercise.com"

TEST_EMAIL = "zeenu123@gmail.com"
TEST_PASSWORD = "12345678"

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


@pytest.fixture
def open_home(page):
    """Open the website home page before a test."""
    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )
    page.wait_for_load_state("networkidle", timeout=15000)
    return page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make the test result available to fixtures and report hooks."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)


@pytest.fixture(autouse=True)
def save_screenshot_after_test(request, page):
    """Save a screenshot after each test, whether it passes or fails."""
    yield

    if hasattr(request.node, "rep_call"):
        safe_name = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            request.node.name
        )
        status = "PASS" if request.node.rep_call.passed else "FAIL"
        path = SCREENSHOT_DIR / f"{safe_name}_{status}.png"

        try:
            page.screenshot(
                path=str(path),
                full_page=True,
                timeout=15000
            )
            print(f"\nScreenshot saved: {path}")
        except Exception as exc:
            print(
                f"\nCould not save screenshot for "
                f"{request.node.name}: {exc}"
            )
