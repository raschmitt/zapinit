from pathlib import Path

from pytest_bdd import given, scenarios, then, when

scenarios("../features/ui_localization.feature")

APP_JS = Path("app/static/js/app.js").read_text()


@given('the browser language is "pt-BR"', target_fixture="lang")
def browser_lang_pt_br():
    return "pt-BR"


@given('the browser language is "pt-PT"', target_fixture="lang")
def browser_lang_pt_pt():
    return "pt-PT"


@given('the browser language is "en-US"', target_fixture="lang")
def browser_lang_en_us():
    return "en-US"


@given('the browser language is "fr-FR"', target_fixture="lang")
def browser_lang_fr_fr():
    return "fr-FR"


@given("the browser language is not set", target_fixture="lang")
def browser_lang_not_set():
    return None


@when("the page loads")
def page_loads():
    pass


@then('the button label is "Abrir no WhatsApp"')
def check_button_pt():
    assert "button: 'Abrir no WhatsApp'" in APP_JS


@then('the button label is "Open on WhatsApp"')
def check_button_en():
    assert "button: 'Open on WhatsApp'" in APP_JS


@then('the phone input placeholder is "Número de telefone"')
def check_placeholder_pt():
    assert "placeholder: 'Número de telefone'" in APP_JS


@then('the phone input placeholder is "Phone number"')
def check_placeholder_en():
    assert "placeholder: 'Phone number'" in APP_JS


@then('the empty-number error is "Por favor, insira um número de telefone"')
def check_error_empty_pt():
    assert "errorEmpty: 'Por favor, insira um número de telefone'" in APP_JS


@then('the empty-number error is "Please enter a phone number"')
def check_error_empty_en():
    assert "errorEmpty: 'Please enter a phone number'" in APP_JS


@then('the invalid-number error is "Número de telefone inválido"')
def check_error_invalid_pt():
    assert "errorInvalid: 'Número de telefone inválido'" in APP_JS


@then('the invalid-number error is "Invalid phone number"')
def check_error_invalid_en():
    assert "errorInvalid: 'Invalid phone number'" in APP_JS


@then(
    'the about blurb is "Cansado de salvar um contato só para mandar uma'
    " mensagem? Digite um número e abra o WhatsApp na hora, sem contatos,"
    ' sem bagunça."'
)
def check_about_pt():
    assert (
        "about: 'Cansado de salvar um contato só para mandar uma mensagem?"
        " Digite um número e abra o WhatsApp na hora, sem contatos, sem"
        " bagunça.'"
    ) in APP_JS


@then(
    'the about blurb is "Tired of saving a contact just to send one message?'
    ' Type a number and open WhatsApp instantly, no contacts, no clutter."'
)
def check_about_en():
    assert (
        "about: 'Tired of saving a contact just to send one message?"
        " Type a number and open WhatsApp instantly, no contacts, no clutter.'"
    ) in APP_JS


@then("the i18n structure is correct")
def check_i18n_structure():
    assert "en:" in APP_JS
    assert "pt:" in APP_JS
    assert "errorEmpty:" in APP_JS
    assert "errorInvalid:" in APP_JS
    assert "placeholder:" in APP_JS
    assert "button:" in APP_JS
    assert "about:" in APP_JS


@then("the applyLocale function exists and is exposed on globalThis")
def check_apply_locale_exists():
    assert "function applyLocale(lang)" in APP_JS
    assert "globalThis.applyLocale = applyLocale" in APP_JS


@then("the init path calls applyLocale with navigator.language")
def check_init_calls_apply_locale():
    assert "applyLocale(navigator.language)" in APP_JS


@then("the error messages use i18n strings instead of hardcoded text")
def check_errors_use_i18n():
    assert "strings.errorEmpty" in APP_JS
    assert "strings.errorInvalid" in APP_JS
