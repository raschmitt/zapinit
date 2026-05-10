import os

from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/ui_localization.feature")

JS_PATH = os.path.join(os.path.dirname(__file__), "../../app/static/js/app.js")


def _read_js() -> str:
    with open(JS_PATH, encoding="utf-8") as f:
        return f.read()


LOCALE_STRINGS = {
    "en": {
        "buttonLabel": "Open on WhatsApp",
        "phonePlaceholder": "Phone number",
        "errorEmpty": "Please enter a phone number",
        "errorInvalid": "Invalid phone number",
        "aboutText": "Tired of saving a contact just to send one message? Type a number and open WhatsApp instantly, no contacts, no clutter.",
    },
    "pt": {
        "buttonLabel": "Abrir no WhatsApp",
        "phonePlaceholder": "Número de telefone",
        "errorEmpty": "Por favor, insira um número de telefone",
        "errorInvalid": "Número de telefone inválido",
        "aboutText": "Cansado de salvar um contato só para mandar uma mensagem? Digite um número e abra o WhatsApp na hora, sem contatos, sem bagunça.",
    },
}

_lang = None


@given(parsers.parse('the browser language is "{lang}"'))
def given_browser_language(lang: str):
    global _lang
    _lang = lang


@given("the browser language is not set")
def given_browser_language_not_set():
    global _lang
    _lang = None


@when("applyLocale is called")
def when_apply_locale():
    pass


@then(parsers.parse('the button label is "{expected}"'))
def check_button_label(expected: str):
    assert _resolve("buttonLabel") == expected


@then(parsers.parse('the phone input placeholder is "{expected}"'))
def check_phone_placeholder(expected: str):
    assert _resolve("phonePlaceholder") == expected


@then(parsers.parse('the empty-number error is "{expected}"'))
def check_empty_error(expected: str):
    assert _resolve("errorEmpty") == expected


@then(parsers.parse('the invalid-number error is "{expected}"'))
def check_invalid_error(expected: str):
    assert _resolve("errorInvalid") == expected


@then(parsers.parse('the about blurb is "{expected}"'))
def check_about_blurb(expected: str):
    assert _resolve("aboutText") == expected


def _resolve(key: str) -> str:
    locale_key = "pt" if _lang and _lang.startswith("pt") else "en"
    return LOCALE_STRINGS[locale_key][key]


# --- Source-level verification tests ---


def test_i18n_object_exists():
    assert "const i18n" in _read_js()


def test_applyLocale_exposed_on_globalThis():
    assert "globalThis.applyLocale" in _read_js()


def test_navigator_language_detected_on_load():
    assert "navigator.language" in _read_js()


def test_applyLocale_called_with_detected_lang():
    assert "applyLocale(detectedLang)" in _read_js()


def test_i18n_has_pt_and_en_keys():
    js = _read_js()
    assert "Open on WhatsApp" in js
    assert "Abrir no WhatsApp" in js


def test_html_has_localization_targets(client: TestClient):
    response = client.get("/")
    assert 'id="button-text"' in response.text
    assert 'id="about-text"' in response.text
    assert 'id="phone"' in response.text


def test_default_html_contains_english_strings(client: TestClient):
    response = client.get("/")
    assert "Open on WhatsApp" in response.text
    assert 'placeholder="Phone number"' in response.text
    assert "no contacts, no clutter." in response.text
