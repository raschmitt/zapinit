Feature: UI localization

  # These scenarios test the client-side localization logic.
  # They verify that the i18n object, applyLocale function, and page-load init
  # are present in the JavaScript source — the actual DOM manipulation requires
  # browser automation (e.g. Playwright) and is deferred.

  Scenario: Browser language is Portuguese (Brazil)
    Given the browser language is "pt-BR"
    When applyLocale is called
    Then the button label is "Abrir no WhatsApp"
    And the phone input placeholder is "Número de telefone"
    And the empty-number error is "Por favor, insira um número de telefone"
    And the invalid-number error is "Número de telefone inválido"
    And the about blurb is "Cansado de salvar um contato só para mandar uma mensagem? Digite um número e abra o WhatsApp na hora, sem contatos, sem bagunça."

  Scenario: Browser language is Portuguese (Portugal)
    Given the browser language is "pt-PT"
    When applyLocale is called
    Then the button label is "Abrir no WhatsApp"
    And the phone input placeholder is "Número de telefone"
    And the empty-number error is "Por favor, insira um número de telefone"
    And the invalid-number error is "Número de telefone inválido"
    And the about blurb is "Cansado de salvar um contato só para mandar uma mensagem? Digite um número e abra o WhatsApp na hora, sem contatos, sem bagunça."

  Scenario: Browser language is English
    Given the browser language is "en-US"
    When applyLocale is called
    Then the button label is "Open on WhatsApp"
    And the phone input placeholder is "Phone number"
    And the empty-number error is "Please enter a phone number"
    And the invalid-number error is "Invalid phone number"
    And the about blurb is "Tired of saving a contact just to send one message? Type a number and open WhatsApp instantly, no contacts, no clutter."

  Scenario: Browser language is unsupported (falls back to English)
    Given the browser language is "fr-FR"
    When applyLocale is called
    Then the button label is "Open on WhatsApp"
    And the phone input placeholder is "Phone number"
    And the empty-number error is "Please enter a phone number"
    And the invalid-number error is "Invalid phone number"
    And the about blurb is "Tired of saving a contact just to send one message? Type a number and open WhatsApp instantly, no contacts, no clutter."

  Scenario: Browser language is not set (falls back to English)
    Given the browser language is not set
    When applyLocale is called
    Then the button label is "Open on WhatsApp"
    And the phone input placeholder is "Phone number"
    And the empty-number error is "Please enter a phone number"
    And the invalid-number error is "Invalid phone number"
    And the about blurb is "Tired of saving a contact just to send one message? Type a number and open WhatsApp instantly, no contacts, no clutter."
