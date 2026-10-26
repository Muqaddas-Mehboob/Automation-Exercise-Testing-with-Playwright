"""CART feature - API tests. The cart has no JSON API; it is session based:
   GET /add_to_cart/<id>, GET /view_cart, GET /delete_cart/<id>.
   Each test uses its own request context (own cookies => own cart).
   TIP: verify selectors/URLs in browser DevTools -> Network tab before the demo."""
import pytest
from conftest import soup

PRODUCT_ID = 1   # "Blue Top"


@pytest.mark.api
def test_api_03_UPDATE_cart_quantity_increases(cart_api):
    """UPDATE (Cart): adding the same product twice updates its quantity to 2"""
    assert cart_api.get(f"/add_to_cart/{PRODUCT_ID}").status == 200
    assert cart_api.get(f"/add_to_cart/{PRODUCT_ID}").status == 200

    cart = soup(cart_api.get("/view_cart"))
    qty = cart.select_one(f"tr#product-{PRODUCT_ID} td.cart_quantity")
    assert qty is not None, "product not found in cart"
    assert qty.get_text(strip=True) == "2"


@pytest.mark.api
def test_api_04_DELETE_item_removed_from_cart(cart_api):
    """DELETE (Cart): GET /delete_cart/<id> removes the product from the cart"""
    cart_api.get(f"/add_to_cart/{PRODUCT_ID}")
    assert soup(cart_api.get("/view_cart")).select_one(f"tr#product-{PRODUCT_ID}") is not None

    assert cart_api.get(f"/delete_cart/{PRODUCT_ID}").status == 200
    after = soup(cart_api.get("/view_cart"))
    assert after.select_one(f"tr#product-{PRODUCT_ID}") is None
