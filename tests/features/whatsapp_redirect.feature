Feature: WhatsApp redirect

  # All scenarios below require browser automation (e.g. Playwright) and are
  # deferred to a future task.

  Scenario: Valid Brazilian number
    Given the country is set to "Brazil (+55)"
    And the user types "11 99999-9999"
    When the user clicks "Open on WhatsApp"
    Then the browser opens "https://wa.me/5511999999999" in a new tab

  Scenario: Valid US number
    Given the country is set to "United States (+1)"
    And the user types "415 555 0100"
    When the user clicks "Open on WhatsApp"
    Then the browser opens "https://wa.me/14155550100" in a new tab

  Scenario: Empty number
    Given the phone input is empty
    When the user clicks "Open on WhatsApp"
    Then an error message "Please enter a phone number" is displayed
    And no redirect occurs

  Scenario: Number too short
    Given the country is set to "Brazil (+55)"
    And the user types "123"
    When the user clicks "Open on WhatsApp"
    Then an error message "Invalid phone number" is displayed
    And no redirect occurs

  Scenario: Submit via Enter key
    Given the country is set to "Brazil (+55)"
    And the user types "11 99999-9999"
    When the user presses the Enter key
    Then the browser opens "https://wa.me/5511999999999" in a new tab

  Scenario: Pasted international number with plus prefix is not double-prefixed
    Given the country is set to "United States (+1)"
    And the user types "+14155550100"
    When the user clicks "Open on WhatsApp"
    Then the browser opens "https://wa.me/14155550100" in a new tab

  Scenario: Pasted international number with 00 prefix is not double-prefixed
    Given the country is set to "United States (+1)"
    And the user types "0014155550100"
    When the user clicks "Open on WhatsApp"
    Then the browser opens "https://wa.me/14155550100" in a new tab

  Scenario: National trunk prefix is stripped before dial code is prepended
    Given the country is set to "United Kingdom (+44)"
    And the user types "07911 123456"
    When the user clicks "Open on WhatsApp"
    Then the browser opens "https://wa.me/447911123456" in a new tab

  Scenario: Significant leading zero in area code is preserved
    Given the country is set to "Italy (+39)"
    And the user types "06 1234 5678"
    When the user clicks "Open on WhatsApp"
    Then the browser opens "https://wa.me/390612345678" in a new tab

  Scenario: Digits-only international number is not double-prefixed
    Given the country is set to "United States (+1)"
    And the user types "14155550100"
    When the user clicks "Open on WhatsApp"
    Then the browser opens "https://wa.me/14155550100" in a new tab
