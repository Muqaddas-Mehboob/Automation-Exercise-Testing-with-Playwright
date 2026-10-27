
from playwright.sync_api import expect

BASE_URL = "https://automationexercise.com"


def open_contact(page):
    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    contact_link = page.get_by_role("link", name="Contact us")
    expect(contact_link).to_be_visible(timeout=30000)
    contact_link.click()

    expect(
        page.get_by_text("Get In Touch", exact=False)
    ).to_be_visible(timeout=20000)


def test_CONT001_submit_complete_contact_form(page):
    open_contact(page)

    # 1. Register the dialog handler to automatically click "OK" on the popup
    page.once("dialog", lambda dialog: dialog.accept())

    # 2. Fill in the form fields
    page.locator('input[data-qa="name"]').fill("Test User")
    page.locator('input[data-qa="email"]').fill("test.user@example.com")
    page.locator('input[data-qa="subject"]').fill("Playwright test message")
    page.locator("#message").fill("This is an automated test submission.")

    # 3. Bypass ad overlays completely using JavaScript evaluation to click submit
    submit_button = page.locator('input[data-qa="submit-button"]')
    submit_button.scroll_into_view_if_needed()
    submit_button.evaluate("button => button.click()")

    # 4. Verify the success message using the specific CSS class and text
    success_message = page.locator(".status.alert.alert-success")
    
    expect(success_message).to_contain_text(
        "Success! Your details have been submitted successfully.",
        timeout=20000
    )
    
def test_CONT002_submit_contact_form_with_missing_fields(page):
    # Step 1: Open Contact Us
    open_contact(page)

    # Step 2: Submit without entering any details
    page.locator('input[data-qa="submit-button"]').click()

    # Step 3: Verify that success is not displayed
    success_message = page.get_by_text(
        "Success! Your details have been submitted successfully.",
        exact=False
    )

    expect(success_message).to_have_count(0)


def test_CONT003_contact_form_invalid_email(page):
    # Step 1: Open Contact Us
    open_contact(page)

    # Step 2: Fill in the form with an invalid email
    page.locator('input[data-qa="name"]').fill("Test User")

    email = page.locator('input[data-qa="email"]')
    email.fill("not-an-email")

    page.locator('input[data-qa="subject"]').fill(
        "Email validation test"
    )
    page.locator("#message").fill(
        "Checking invalid email handling."
    )

    # Step 3: Try to submit the form
    page.locator('input[data-qa="submit-button"]').click()

    # Step 4: Verify browser email validation
    assert not email.evaluate("(el) => el.checkValidity()")
