Feature: Server health

  Scenario: Root route responds
    Given the application is running
    When a GET request is made to "/"
    Then the response status is 200
    And the response body contains "zapinit"
