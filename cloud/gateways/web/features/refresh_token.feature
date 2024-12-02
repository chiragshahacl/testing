Feature: Refresh AccessToken

  Scenario: Refresh AccessToken - Happy Path
    Given the application is running
    And a request to refresh an access token
    When the request to get an access token is made
    Then the user is told the request was successful
    And the refreshed token is included in the response

  Scenario: Refresh AccessToken - Invalid request
    Given the application is running
    And an invalid request to refresh an access token
    When the request to get an access token is made
    Then the user is told the request was unauthorized
