Feature: Dynamic favicon

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
