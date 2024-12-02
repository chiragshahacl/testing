Feature: Logout

  Scenario: Logout - Happy Path
    Given the application is running
    And a valid request to logout
    When the request to logout is made
    Then the user is told the request was successful

  Scenario: Logout without a token
    Given the application is running
    And an invalid request to logout
    When the request to logout is made
    Then the user is told the request was unauthorized

  Scenario: Logout with forbidden password
    Given the application is running
    And a forbidden request to logout
    When the request to logout is made
    Then the user is told the request was forbidden

  Scenario: Logout with invalid password
    Given the application is running
    And a valid request to logout
    But the password is invalid
    When the request to logout is made
    Then the user is told the request was unauthorized
