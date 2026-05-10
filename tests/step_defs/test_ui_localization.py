import multiprocessing
import time
from typing import Generator

import pytest
import uvicorn
from playwright.sync_api import sync_playwright
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/ui_localization.feature")


@pytest.fixture(scope="session")
def server_url() -> Generator[str, None, None]:
    import app.main

    host = "127.0.0.1"
    port = 8765
    proc = multiprocessing.Process(
        target=uvicorn.run,
        args=(app.main.app,),
        kwargs={"host": host, "port": port, "log_level": "error"},
        daemon=True,
    )
    proc.start()
    time.sleep(1)
    yield f"http://{host}:{port}"
    proc.terminate()
    proc.join()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser, server_url):
    context = browser.new_context()
    page = context.new_page()
    page.goto(server_url)
    yield page
    context.close()


@pytest.fixture
def lang():
    """Fixture to hold the language code between given/when steps."""
    return ""


@given(parsers.parse('the browser language is "{lang_code}"'), target_fixture="lang")
def given_browser_language(lang_code):
    return lang_code


@given("the browser language is not set", target_fixture="lang")
def given_language_not_set():
    return ""


@when("the locale is applied")
def apply_locale(page, lang):
    page.evaluate("l => globalThis.applyLocale(l)", lang)


@then(parsers.re(r'the button label is "(?P<expected>[^"]+)"'))
def check_button_label(page, expected):
    text = page.text_content("#open-wa-text")
    assert text == expected, f"Expected '{expected}', got '{text}'"


@then(parsers.re(r'the phone input placeholder is "(?P<expected>[^"]+)"'))
def check_phone_placeholder(page, expected):
    placeholder = page.get_attribute("#phone", "placeholder")
    assert placeholder == expected, f"Expected '{expected}', got '{placeholder}'"


@then(parsers.re(r'the empty-number error is "(?P<expected>[^"]+)"'))
def check_empty_error(page, expected):
    actual = page.evaluate("globalThis.__errorEmpty")
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


@then(parsers.re(r'the invalid-number error is "(?P<expected>[^"]+)"'))
def check_invalid_error(page, expected):
    actual = page.evaluate("globalThis.__errorInvalid")
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


@then(parsers.re(r'the about blurb is "(?P<expected>[^"]+)"'))
def check_about_blurb(page, expected):
    text = page.text_content("#about-blurb")
    assert text == expected, f"Expected '{expected}', got '{text}'"


# --- Init path tests: verify navigator.language is read on page load ---


def _init_page(browser, server_url, lang):
    """Create a new page with navigator.language stubbed before page load."""
    context = browser.new_context()
    page = context.new_page()
    page.add_init_script(f"""
        Object.defineProperty(globalThis.navigator, 'language', {{
            get: () => '{lang}',
            configurable: true,
        }});
    """)
    page.goto(server_url)
    page.wait_for_load_state("networkidle")
    return page, context


def test_startup_applies_portuguese_locale(browser, server_url):
    page, ctx = _init_page(browser, server_url, "pt-BR")
    assert page.text_content("#open-wa-text") == "Abrir no WhatsApp"
    assert page.get_attribute("#phone", "placeholder") == "Número de telefone"
    assert page.text_content("#about-blurb") == (
        "Cansado de salvar um contato só para mandar uma mensagem? "
        "Digite um número e abra o WhatsApp na hora, sem contatos, sem bagunça."
    )
    ctx.close()


def test_startup_applies_english_locale(browser, server_url):
    page, ctx = _init_page(browser, server_url, "en-US")
    assert page.text_content("#open-wa-text") == "Open on WhatsApp"
    assert page.get_attribute("#phone", "placeholder") == "Phone number"
    assert page.text_content("#about-blurb") == (
        "Tired of saving a contact just to send one message? "
        "Type a number and open WhatsApp instantly, no contacts, no clutter."
    )
    ctx.close()


def test_startup_falls_back_to_english(browser, server_url):
    page, ctx = _init_page(browser, server_url, "fr-FR")
    assert page.text_content("#open-wa-text") == "Open on WhatsApp"
    ctx.close()
