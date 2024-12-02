Feature: Log out user

  Scenario: Log out - Happy Path
    Given the app is running
    And a valid user exists
    And the user is already authenticated
    And a request to log out
    When the user logs out
    Then the request is successful
    And the logout event is logged

  Scenario: Log out - Empty password
    Given the app is running
    And a valid user exists
    And the user is already authenticated
    And a request to log out
    But the password is empty
    When the user logs out
    Then the request fails

  Scenario: Log out - Logout invalid password
    Given the app is running
    And a valid user exists
    And the user is already authenticated
    And a request to log out
    But the password is incorrect
    When the user logs out
    Then the request fails

  Scenario: Log out - Logout account locked
    Given the app is running
    And a valid user exists
    And the user is already authenticated
    And a request to log out
    But the user account is locked
    When the user logs out
    Then the request fails

  Scenario: Log out - Not logged in user
    Given the app is running
    And a valid user exists
    And a request to log out
    But the user is not authenticated
    When the user logs out
    Then the request fails
