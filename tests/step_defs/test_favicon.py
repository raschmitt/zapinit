import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then, when

scenarios("../features/favicon.feature")


@given('the user navigates to "/"', target_fixture="response")
def navigate_to_root(client: TestClient):
    return client.get("/")


@then("a favicon link tag exists in the page")
def check_favicon_link(response):
    assert 'rel="icon"' in response.text
    assert 'id="favicon"' in response.text


@then('the favicon link has type "image/svg+xml"')
def check_favicon_type(response):
    assert 'type="image/svg+xml"' in response.text


@given('the theme is set to "light"')
def given_theme_light():
    pytest.skip("requires browser automation (Playwright)")


@given('the theme is set to "dark"')
def given_theme_dark():
    pytest.skip("requires browser automation (Playwright)")


@when("the page loads")
def when_page_loads():
    pytest.skip("requires browser automation (Playwright)")


@when("the user toggles to dark mode")
def when_toggle_dark():
    pytest.skip("requires browser automation (Playwright)")


@then("the favicon href points to the light-mode SVG")
def then_favicon_light():
    pytest.skip("requires browser automation (Playwright)")


@then("the favicon href points to the dark-mode SVG")
def then_favicon_dark():
    pytest.skip("requires browser automation (Playwright)")


@then("the favicon href updates to the dark-mode SVG without a page reload")
def then_favicon_updates():
    pytest.skip("requires browser automation (Playwright)")
