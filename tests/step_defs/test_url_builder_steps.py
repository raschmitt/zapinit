from pytest_bdd import given, parsers, scenarios, then, when

from app.main import build_wa_url

scenarios("../features/whatsapp_url_builder.feature")


@given(parsers.parse('the E.164 number is "{e164}"'), target_fixture="e164_number")
def e164_number(e164: str) -> str:
    return e164


@when("the URL is built", target_fixture="url_result")
def build_url(e164_number: str) -> str:
    return build_wa_url(e164_number)


@then(parsers.parse('the result is "{expected_url}"'))
def check_result(url_result: str, expected_url: str) -> None:
    assert url_result == expected_url
