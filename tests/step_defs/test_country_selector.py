from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then

scenarios("../features/country_selector.feature")


@given('the user navigates to "/"', target_fixture="response")
def navigate_to_root(client: TestClient):
    return client.get("/")


@then('a country select with id "country" exists in the page')
def check_country_select(response):
    assert 'id="country"' in response.text


@then('a phone input with id "phone" exists in the page')
def check_phone_input_id(response):
    assert 'id="phone"' in response.text
