Feature: Health Check

  Scenario: Everything fine
    Given the application is running
    When I make a health check request to the app
    Then I'm told the app is working
