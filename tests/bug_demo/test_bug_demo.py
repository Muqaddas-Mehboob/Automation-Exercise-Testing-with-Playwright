"""Proof that the suite catches bugs (feature: PRODUCT SEARCH).
Normal run   : PASS.
INJECT_BUG=1 : search results are removed from the response -> test FAILS."""
import pytest
from playwright.sync_api import expect


@pytest.mark.bug
def test_bug_01_search_shows_results(site_page, browser_name):
    page = site_page
    page.goto("/products")
    page.fill("#search_product", "top")
    page.click("#submit_search")

    expect(page.locator("h2.title").first).to_contain_text("Searched Products")
    cards = page.locator(".features_items .product-image-wrapper")
    page.screenshot(path=f"screenshots/bug01_search_{browser_name}.png")
    assert cards.count() > 0, "Search for 'top' returned no products!"
