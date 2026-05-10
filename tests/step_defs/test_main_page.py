from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then

scenarios("../features/main_page.feature")


@given('the user navigates to "/"', target_fixture="response")
def navigate_to_root(client: TestClient):
    return client.get("/")


@then('the page title contains "zapinit"')
def check_title(response):
    assert "<title>zapinit</title>" in response.text


@then("a phone number input is visible")
def check_phone_input(response):
    assert 'id="phone"' in response.text


@then('an "Open on WhatsApp" button is visible')
def check_open_wa_button(response):
    assert "Open on WhatsApp" in response.text


@then("a theme toggle button is visible")
def check_theme_toggle(response):
    assert 'id="theme-toggle"' in response.text


@then("a GitHub repository link is visible")
def check_github_link(response):
    assert 'id="github-link"' in response.text
    assert "github.com/raschmitt/zapinit" in response.text


@then("the GitHub link opens in a new tab")
def check_github_link_target(response):
    assert 'target="_blank"' in response.text
    assert 'rel="noopener noreferrer"' in response.text
