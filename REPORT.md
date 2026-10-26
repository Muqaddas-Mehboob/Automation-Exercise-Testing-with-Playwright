# Testing Report – automationexercise.com

**Tools:** Python, Playwright, pytest, pytest-html | **Browsers:** Chromium, Firefox, WebKit
**Members:** Member A = ______ , Member B = ______

## 1. Features tested
Login, Product Search, Cart, Contact Us.

| Feature | API tests | Mock tests | Bug demo |
|---|---|---|---|
| Login | API-01 (create+login), API-05 (negative), API-07 (/login 200) | – | – |
| Product Search | API-02 (read), API-06 (negative) | MOCK-01 (empty results) | BUG-01 |
| Cart | API-03 (update qty), API-04 (delete), API-07 (/view_cart) | MOCK-02 (HTTP 500) | – |
| Contact Us | API-07 (/contact_us 200) | MOCK-03 (HTTP 500) | – |

## 2. Features NOT tested (and why)
| Feature | Reason |
|---|---|
| Payment / Checkout | Needs card details and creates real orders on a shared site |
| Signup via UI | Account creation covered at API level (API-01); UI signup would spam the shared site |
| Subscription, Test Cases page, Brands/Category filters | Not part of the 4 chosen features |
| Contact Us real submit (API) | Form likely needs CSRF/file upload and would send spam to a shared site; covered with mocking instead |

## 3. Test case table
| ID | Feature | Type | Description | Expected result | Chromium | Firefox | WebKit |
|---|---|---|---|---|---|---|---|
| API-01 | Login | CREATE | POST /api/createAccount, then POST /api/verifyLogin | 201 "User created!", then 200 "User exists!" | | | |
| API-02 | Search | READ | POST /api/searchProduct search_product=top | 200, non-empty product list | | | |
| API-03 | Cart | UPDATE | GET /add_to_cart/1 twice, GET /view_cart | Quantity = 2 | | | |
| API-04 | Cart | DELETE | GET /delete_cart/1, GET /view_cart | Product no longer in cart | | | |
| API-05 | Login | Negative | verifyLogin with unknown user / missing password | 404 "User not found!" / 400 | | | |
| API-06 | Search | Negative | searchProduct w/o param; GET on POST endpoint; productsList | 400 / 405 / 200 | | | |
| API-07 | All | Status codes | GET /login, /products, /view_cart, /contact_us, /missing | 200 ×4, 404 | | | |
| MOCK-01 | Search | Mock empty data | Search results page returns zero products | Page loads, heading visible, no JS errors | | | |
| MOCK-02 | Cart | Mock error | /add_to_cart/* returns 500 | Page stays usable, no JS errors | | | |
| MOCK-03 | Contact | Mock error | POST /contact_us returns 500 | No success message shown | | | |
| BUG-01 | Search | Deliberate bug | Search results removed (INJECT_BUG=1) | Test FAILS (normal run: passes) | | | |

## 4. Deliberate bug demo
Bug: search results page returns no products (fault injected via Playwright route with `INJECT_BUG=1`, because the deployed site is not ours).
Evidence: reports/report_with_bug.html + screenshots/bug01_search_*.png.

## 5. Bugs found on the real site
(Write real bugs/observations here – e.g. API returns HTTP 200 even for errors, browser-specific issues.)

## 6. Work division
| Member | Part |
|---|---|
| A | e.g. Login + Search API tests, report table |
| B | e.g. Cart API tests, mocking tests, bug demo, cross-browser run |
