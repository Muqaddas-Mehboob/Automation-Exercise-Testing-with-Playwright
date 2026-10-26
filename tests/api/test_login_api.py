"""LOGIN feature - API tests.
NOTE: this site returns HTTP 200 for most calls; the real result is the JSON `responseCode`."""
import pytest
from conftest import body, make_user


@pytest.mark.api
def test_api_01_CREATE_account_then_login_works(api):
    """CREATE (Login): POST /api/createAccount -> 201, then POST /api/verifyLogin -> 200 'User exists!'"""
    user = make_user()
    try:
        created = body(api.post("/api/createAccount", form=user))
        assert created["responseCode"] == 201
        assert created["message"] == "User created!"

        login = body(api.post("/api/verifyLogin", form={"email": user["email"], "password": user["password"]}))
        assert login["responseCode"] == 200
        assert login["message"] == "User exists!"
    finally:  # cleanup so we don't leave test users on the shared site
        api.delete("/api/deleteAccount", form={"email": user["email"], "password": user["password"]})


@pytest.mark.api
def test_api_05_login_negative_wrong_and_missing_credentials(api):
    """NEGATIVE (Login): unknown user -> 404 'User not found!' ; missing password -> 400"""
    wrong = body(api.post("/api/verifyLogin", form={"email": "nobody_xyz@example.com", "password": "wrong"}))
    assert wrong["responseCode"] == 404
    assert wrong["message"] == "User not found!"

    missing = body(api.post("/api/verifyLogin", form={"email": "nobody_xyz@example.com"}))
    assert missing["responseCode"] == 400
