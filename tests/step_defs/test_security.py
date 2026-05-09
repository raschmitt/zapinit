from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then

scenarios("../features/security.feature")


@given("the app JavaScript is loaded", target_fixture="app_js")
def load_app_js(client: TestClient):
    return client.get("/static/js/app.js").text


@then('the WhatsApp redirect uses "noopener,noreferrer" to prevent tabnabbing')
def check_noopener(app_js):
    assert "noopener,noreferrer" in app_js
