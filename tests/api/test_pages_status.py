"""Status codes of the pages of our 4 features: real page -> 200, missing page -> 404."""
import pytest


@pytest.mark.api
@pytest.mark.parametrize("path,expected", [
    ("/login", 200),            # Login
    ("/products", 200),         # Product search
    ("/view_cart", 200),        # Cart
    ("/contact_us", 200),       # Contact Us
    ("/this-page-does-not-exist-xyz", 404),
])
def test_api_07_page_status_codes(api, path, expected):
    assert api.get(path).status == expected
