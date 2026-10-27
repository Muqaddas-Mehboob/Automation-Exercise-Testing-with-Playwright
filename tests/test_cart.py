
from playwright.sync_api import expect

BASE_URL = "https://automationexercise.com"


def open_products(page):
    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    products_link = page.locator('a[href="/products"]').first
    expect(products_link).to_be_visible(timeout=15000)
    products_link.click(timeout=15000)

    expect(
        page.get_by_role("heading", name="All Products", exact=False)
    ).to_be_visible(timeout=15000)


def add_first_product(page):
    first_card = page.locator(".product-image-wrapper").first
    first_card.scroll_into_view_if_needed()
    first_card.locator("a.add-to-cart").first.click()

    expect(
        page.get_by_text("Your product has been added to cart", exact=False)
    ).to_be_visible()

    page.get_by_role("link", name="View Cart").click()
    assert "/view_cart" in page.url


def test_CART001_add_one_product_to_cart(page):
    """Positive: add one product and verify a cart row exists."""
    open_products(page)
    add_first_product(page)

    expect(
        page.locator("#cart_info_table tbody tr")
    ).to_have_count(1)


def test_CART002_add_two_products_to_cart(page):
    """Positive: add two different products and verify both rows exist."""
    open_products(page)
    cards = page.locator(".product-image-wrapper")

    cart_modal = page.locator("#cartModal")

    for index in (0, 1):
        card = cards.nth(index)
        card.scroll_into_view_if_needed()
        card.locator("a.add-to-cart").first.click()

        expect(cart_modal).to_be_visible(timeout=15000)

        expect(
            cart_modal.get_by_text(
                "Your product has been added to cart",
                exact=False
            )
        ).to_be_visible(timeout=10000)

        cart_modal.get_by_role(
            "button",
            name="Continue Shopping"
        ).click()
    page.locator('a[href="/view_cart"]').first.click()
    assert "/view_cart" in page.url

    expect(
        page.locator("#cart_info_table tbody tr")
    ).to_have_count(2)


def test_CART003_remove_product_and_check_empty_cart(page):
    """Boundary: remove the only cart item and verify the cart is empty."""
    open_products(page)
    add_first_product(page)

    expect(
        page.locator("#cart_info_table tbody tr")
    ).to_have_count(1)

    page.locator(".cart_quantity_delete").first.click()

    expect(
        page.locator("#cart_info_table tbody tr")
    ).to_have_count(0)
