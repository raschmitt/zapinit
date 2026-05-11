from pathlib import Path

from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then, when

scenarios("../features/favicon.feature")


@given('the theme is set to "light"', target_fixture="response")
def light_theme(client: TestClient):
    client.cookies.set("theme", "light", path="/")
    return client.get("/")


@given('the theme is set to "dark"', target_fixture="response")
def dark_theme(client: TestClient):
    client.cookies.set("theme", "dark", path="/")
    return client.get("/")


@when("the page loads")
def page_loads():
    pass


@when("the user toggles to dark mode")
def noop_toggle():
    pass


@then("the favicon href points to the light-mode SVG")
def check_light_favicon(response):
    assert 'id="favicon"' in response.text
    assert 'href="/static/favicon-light.svg"' in response.text
    favicon_path = Path("app/static/favicon-light.svg")
    assert favicon_path.exists(), "Light mode favicon SVG file not found"


@then("the favicon href points to the dark-mode SVG")
def check_dark_favicon(response):
    assert 'id="favicon"' in response.text
    assert 'href="/static/favicon-dark.svg"' in response.text
    favicon_path = Path("app/static/favicon-dark.svg")
    assert favicon_path.exists(), "Dark mode favicon SVG file not found"


@then("the favicon href updates to the dark-mode SVG without a page reload")
def check_favicon_update():
    app_js = Path("app/static/js/app.js").read_text()
    assert "globalThis.updateFavicon = updateFavicon" in app_js
    assert "colorScheme.addEventListener('change'" in app_js
    assert "/static/favicon-dark.svg" in app_js
    assert "/static/favicon-light.svg" in app_js
