"""PRODUCT SEARCH feature - API tests."""
import pytest
from conftest import body


@pytest.mark.api
def test_api_02_READ_search_products(api):
    """READ (Search): POST /api/searchProduct search_product=top -> 200 + non-empty product list"""
    data = body(api.post("/api/searchProduct", form={"search_product": "top"}))
    assert data["responseCode"] == 200
    assert len(data["products"]) > 0
    for p in data["products"]:
        assert "name" in p and "price" in p


@pytest.mark.api
def test_api_06_search_negative_missing_param_and_wrong_method(api):
    """NEGATIVE (Search): no search_product -> 400 ; GET on POST-only endpoint -> 405 ; product list -> 200"""
    missing = body(api.post("/api/searchProduct"))
    assert missing["responseCode"] == 400

    wrong_method = body(api.get("/api/searchProduct"))
    assert wrong_method["responseCode"] == 405

    all_products = body(api.get("/api/productsList"))
    assert all_products["responseCode"] == 200
    assert len(all_products["products"]) > 0
