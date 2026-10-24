
from playwright.sync_api import expect
from conftest import BASE_URL, TEST_EMAIL, TEST_PASSWORD


def go_to_login(page):
    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    login_link = page.get_by_role(
        "link", name="Signup / Login"
    )
    expect(login_link).to_be_visible(timeout=20000)
    login_link.click(timeout=20000)

    expect(
        page.get_by_text("Login to your account", exact=True)
    ).to_be_visible(timeout=20000)


def test_LOG001_login_with_valid_credentials(page):
    """Positive: log in using the configured credentials."""

    go_to_login(page)

    page.locator('input[data-qa="login-email"]').fill(TEST_EMAIL)
    page.locator('input[data-qa="login-password"]').fill(TEST_PASSWORD)

    page.locator('button[data-qa="login-button"]').click()

    expect(
        page.get_by_text("Logged in as", exact=False)
    ).to_be_visible(timeout=20000)



def test_LOG002_login_with_incorrect_credentials(page):
    """Negative: incorrect credentials should display an error."""

    go_to_login(page)

    page.locator('input[data-qa="login-email"]').fill(
        "not-a-real-user-98231@example.com"
    )
    page.locator('input[data-qa="login-password"]').fill(
        "WrongPassword123!"
    )

    page.locator('button[data-qa="login-button"]').click()

    error_message = page.get_by_text(
        "Your email or password is incorrect!",
        exact=True
    )

    expect(error_message).to_be_visible(timeout=20000)


def test_LOG003_login_with_empty_fields(page):
    """Negative: empty fields should not result in a successful login."""

    go_to_login(page)

    email = page.locator('input[data-qa="login-email"]')
    password = page.locator('input[data-qa="login-password"]')

    page.locator('button[data-qa="login-button"]').click()

    assert email.input_value() == ""
    assert password.input_value() == ""

    expect(
        page.get_by_text("Login to your account", exact=True)
    ).to_be_visible()

    expect(
        page.get_by_text("Logged in as", exact=False)
    ).not_to_be_visible()
