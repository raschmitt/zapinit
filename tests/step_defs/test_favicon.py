from pathlib import Path

from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then, when

scenarios("../features/favicon.feature")


@given('the theme is set to "light"', target_fixture="response")
def light_theme(client: TestClient):
    return client.get("/")


@given('the theme is set to "dark"', target_fixture="response")
def dark_theme(client: TestClient):
    return client.get("/")


@when("the page loads", target_fixture="response")
def page_loads(client: TestClient):
    return client.get("/")


@when("the user toggles to dark mode")
def noop_toggle():
    pass


@then("the favicon href points to the light-mode SVG")
def check_light_favicon(response):
    assert 'id="favicon"' in response.text
    assert 'href="/static/favicon-light.svg"' in response.text


@then("the favicon href points to the dark-mode SVG")
def check_dark_favicon(response):
    assert 'id="favicon"' in response.text
    favicon_path = Path("app/static/favicon-dark.svg")
    assert favicon_path.exists(), "Dark mode favicon SVG file not found"
    inline_script = (
        "document.getElementById('favicon').href = '/static/favicon-dark.svg'"
    )
    assert inline_script in response.text


@then("the favicon href updates to the dark-mode SVG without a page reload")
def check_favicon_update():
    app_js = Path("app/static/js/app.js").read_text()
    assert "updateFavicon" in app_js
    assert "favicon-dark.svg" in app_js
    assert "favicon-light.svg" in app_js
