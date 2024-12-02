Feature: Login User

  Scenario: Login User - Happy Path
    Given the app is running
    And a valid user exists
    When the user requests to login
    Then the request is successful
    And the user gets a valid session
    And the login event is logged

  Scenario: Login User - User associated to groups
    Given the app is running
    And a valid admin user exists
    And the user is a member of groups
    When the user requests to login
    Then the request is successful
    And the user gets a valid session

  Scenario: Login User - Invalid Password
    Given the app is running
    And a valid user exists
    When the user requests to login with an incorrect password
    Then the request fails

  Scenario: Login User - Invalid Password max tries
    Given the app is running
    And a valid user exists
    When the user requests to login with an incorrect password as many times as possible
    Then the request fails
    And the account is locked
    And the account locked event is logged

  Scenario: Login User - Account locked
    Given the app is running
    And a valid user exists
    But the user account is locked
    When the user requests to login
    Then the request fails

  Scenario: Login User - Invalid Username
    Given the app is running
    And a valid user exists
    When the user requests to login with an incorrect username
    Then the request fails

  Scenario: Refresh token - Happy Path
    Given the app is running
    And a valid user exists
    And the user is already authenticated
    When the user requests a new token
    Then the request is successful
    And the user gets a valid refreshed session

  Scenario Outline: Login User - User with group
    Given the app is running
    And a valid user with group "<group>" exists
    When the user requests to login
    Then the request is successful
    And the user gets a valid session
    And the user group "<group>" is in the token

    Examples:
      | group        |
      | admin        |
      | tech         |
      | organization |
      | clinical     |
