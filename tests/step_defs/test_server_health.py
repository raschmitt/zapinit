from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then, when

scenarios("../features/server_health.feature")


@given("the application is running", target_fixture="response")
def app_is_running(client: TestClient):
    return client.get("/")


@when('a GET request is made to "/"', target_fixture="response")
def get_root(client: TestClient):
    return client.get("/")


@then("the response status is 200")
def check_status(response):
    assert response.status_code == 200


@then('the response body contains "zapinit"')
def check_body_contains(response):
    assert "zapinit" in response.text
