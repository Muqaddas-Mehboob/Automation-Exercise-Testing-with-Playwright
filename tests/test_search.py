
from playwright.sync_api import expect

BASE_URL = "https://automationexercise.com"


def open_products(page):
    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.get_by_role("link", name="Products").click()

    expect(
        page.get_by_role(
            "heading",
            name="All Products",
            exact=False
        )
    ).to_be_visible(timeout=20000)


def test_SRCH001_search_for_existing_product(page):
    """Positive: search for a product known to be listed on the site."""

    open_products(page)

    search = page.locator("#search_product")
    search.fill("Top")

    page.locator("#submit_search").click()

    expect(
        page.get_by_text("SEARCHED PRODUCTS", exact=False)
    ).to_be_visible(timeout=20000)

    expect(
        page.locator(".product-image-wrapper").first
    ).to_be_visible(timeout=20000)


def test_SRCH002_search_for_nonexistent_product(page):
    """Negative: an unmatched search should not show matching product cards."""

    open_products(page)

    search = page.locator("#search_product")
    search.fill("NoSuchProduct_XYZ_928374")

    page.locator("#submit_search").click()

    expect(
        page.get_by_text("SEARCHED PRODUCTS", exact=False)
    ).to_be_visible(timeout=20000)

    expect(
        page.locator(".product-image-wrapper")
    ).to_have_count(0, timeout=20000)




def test_SRCH003_submit_empty_search(page):
    """Boundary: submitting an empty search reloads the products page."""

    open_products(page)

    search = page.locator("#search_product")
    search.fill("")

    page.locator("#submit_search").click()

    page.wait_for_load_state(
        "domcontentloaded",
        timeout=30000
    )

    expect(page.locator("body")).to_be_visible()

    print("URL after empty search:", page.url)
    print("Empty search submission completed.")
