Feature: Group management

  Scenario: Create User Group - Happy Path
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to create a user group
    When the logged in user creates a new user group
    Then the request is successful
    And the user group is created
    And the group created event is logged

  Scenario: Create User Group - By a regular user
    Given the app is running
    And a valid user exists
    And the user is already authenticated
    And a request to create a user group
    When the logged in user creates a new user group
    Then the request fails

  Scenario: Create User Group - Empty group name
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to create a user group
    But the group name is empty
    When the logged in user creates a new user group
    Then the request fails

  Scenario: Create User Group - Duplicate name
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to create a user group
    But the group name is already taken
    When the logged in user creates a new user group
    Then the request fails
