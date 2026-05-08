Feature: Country selector is present on the page

  # Browser-behaviour tests (navigator.language detection) require
  # browser automation (e.g. Playwright) and are tracked for a future task.

  Scenario: Country selector element is rendered
    Given the user navigates to "/"
    Then a country select with id "country" exists in the page

  Scenario: Phone input is available alongside the selector
    Given the user navigates to "/"
    Then a phone input with id "phone" exists in the page
