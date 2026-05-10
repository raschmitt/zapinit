Feature: Main page renders correctly

  Scenario: User opens the app
    Given the user navigates to "/"
    Then the page title contains "zapinit"
    And a phone number input is visible
    And an "Open on WhatsApp" button is visible
    And a theme toggle button is visible
    And a GitHub repository link is visible
    And the GitHub link opens in a new tab
