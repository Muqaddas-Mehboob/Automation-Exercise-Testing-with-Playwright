"""Network mocking. Site is server-rendered, so we mock the HTML response (search) and AJAX/POST calls (cart, contact).
Goal: page must not break (no JS errors, layout alive)."""
import re
import pytest
from playwright.sync_api import expect
from conftest import SEARCH_URL, strip_products


@pytest.mark.mock
def test_mock_01_search_returns_empty_results(site_page, browser_name):
    """PRODUCT SEARCH: server returns an EMPTY result list"""
    page = site_page

    def empty(route):
        resp = route.fetch()
        route.fulfill(response=resp, body=strip_products(resp.text()))

    page.route(SEARCH_URL, empty)   # registered later => has priority
    page.goto("/products")
    page.fill("#search_product", "top")
    page.click("#submit_search")
    page.wait_for_url(re.compile(r"search=top"))

    expect(page.locator("h2.title").first).to_contain_text("Searched Products")
    assert page.locator(".features_items .product-image-wrapper").count() == 0
    expect(page.locator("header")).to_be_visible()
    assert page.js_errors == [], f"JS errors: {page.js_errors}"
    page.screenshot(path=f"screenshots/mock01_empty_search_{browser_name}.png")


@pytest.mark.mock
def test_mock_02_cart_add_returns_server_error(site_page, browser_name):
    """CART: add-to-cart AJAX call fails with HTTP 500"""
    page = site_page
    page.route(re.compile(r"/add_to_cart/\d+"),
               lambda route: route.fulfill(status=500, content_type="text/plain", body="Internal Server Error"))
    page.goto("/products")
    page.locator(".productinfo .add-to-cart").first.click()

    expect(page).to_have_url(re.compile(r"/products"))
    assert page.locator(".features_items .product-image-wrapper").count() > 0   # page still intact
    expect(page.get_by_role("link", name=re.compile("Cart")).first).to_be_visible()
    assert page.js_errors == [], f"JS errors: {page.js_errors}"
    page.screenshot(path=f"screenshots/mock02_cart_500_{browser_name}.png")


@pytest.mark.mock
def test_mock_03_contact_us_submit_server_error(site_page, browser_name):
    """CONTACT US (bonus): form POST returns 500 -> page must NOT claim success. Nothing is really sent to the site."""
    page = site_page
    page.on("dialog", lambda d: d.accept())    # site shows a confirm() popup on submit

    def handler(route):
        if route.request.method == "POST":
            route.fulfill(status=500, content_type="text/plain", body="Internal Server Error")
        else:
            route.continue_()

    page.route(re.compile(r"/contact_us$"), handler)
    page.goto("/contact_us")
    page.locator('[data-qa="name"]').fill("QA Tester")
    page.locator('[data-qa="email"]').fill("qa@example.com")
    page.locator('[data-qa="subject"]').fill("Mock test")
    page.locator('[data-qa="message"]').fill("Server is down in this mocked test")

    with page.expect_response(lambda r: r.url.endswith("/contact_us") and r.request.method == "POST") as info:
        page.locator('[data-qa="submit-button"]').click()
    assert info.value.status == 500
    expect(page.get_by_text("Your details have been submitted successfully")).to_have_count(0)
    page.screenshot(path=f"screenshots/mock03_contact_500_{browser_name}.png")
