Feature: Dynamic favicon

  # Dynamic switching scenarios below require browser automation (e.g. Playwright)
  # and are deferred to a future task. The server-rendered check is covered above.

  Scenario: Favicon link tag is present in the page
    Given the user navigates to "/"
    Then a favicon link tag exists in the page
    And the favicon link has type "image/svg+xml"

  Scenario: Light mode favicon is active in light mode
    Given the theme is set to "light"
    When the page loads
    Then the favicon href points to the light-mode SVG

  Scenario: Dark mode favicon is active in dark mode
    Given the theme is set to "dark"
    When the page loads
    Then the favicon href points to the dark-mode SVG

  Scenario: Favicon updates when theme is toggled
    Given the theme is set to "light"
    When the user toggles to dark mode
    Then the favicon href updates to the dark-mode SVG without a page reload
