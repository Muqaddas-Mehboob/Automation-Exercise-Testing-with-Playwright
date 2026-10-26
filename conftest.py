import json
import os
import re
import uuid

import pytest
from bs4 import BeautifulSoup

BASE_URL = "https://automationexercise.com"
SEARCH_URL = re.compile(r"/products\?search=")
AD_URLS = re.compile(r"(googlesyndication|doubleclick|googleads|adservice|googletagmanager)")


# ---------- helpers ----------
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


# ---------- API fixtures ----------
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


# ---------- Browser fixture (ad-blocking + optional deliberate bug) ----------
@pytest.fixture
def site_page(page):
    page.route(AD_URLS, lambda route: route.abort())   # ads make tests flaky

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
