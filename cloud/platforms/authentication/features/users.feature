Feature: User management

  Scenario: Create User - Happy Path
    Given the app is running
    And a request to crate a user
    And a valid admin user exists
    And the user is already authenticated
    When the logged in user creates a new regular user
    Then the request is successful
    And the user is created
    And the user created event is logged
    And the new user can request to login
    And the request is successful
    And the user gets a valid session

  Scenario: Create User - By a regular user
    Given the app is running
    And a request to crate a user
    And a valid user exists
    And the user is already authenticated
    When the logged in user creates a new regular user
    Then the request fails

  Scenario: Create User - Empty username
    Given the app is running
    And a request to crate a user
    And a valid admin user exists
    And the user is already authenticated
    But the `username` is not provided
    When the logged in user creates a new regular user
    Then the request fails

  Scenario: Create User - Empty password
    Given the app is running
    And a request to crate a user
    And a valid admin user exists
    And the user is already authenticated
    But the `password` is not provided
    When the logged in user creates a new regular user
    Then the request fails

  Scenario: Update User  - Happy Path
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to update a user
    When the logged in user updates the user
    Then the request is successful
    And the user is updated
    And the user updated event is logged

  Scenario: Get User Details of another user - As an admin
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    When request for another user details
    Then the request is successful
    And the user data is correct

  Scenario: Get User Details of another user - As a regular user
    Given the app is running
    And a valid user exists
    And the user is already authenticated
    When request for another user details
    Then the request fails

  Scenario: Get User Details
    Given the app is running
    And a valid user exists
    And the user is already authenticated
    When request for its user details
    Then the request is successful
    And the user data is correct

  Scenario: Get User List - As admin user
    Given the app is running
    And there are users registered
    And a valid admin user exists
    And the user is already authenticated
    When request the list of users
    Then the request is successful
    And the list of user data is correct

  Scenario: Get User List - As a regular user
    Given the app is running
    And there are users registered
    And a valid user exists
    And the user is already authenticated
    When request the list of users
    Then the request fails

  Scenario: Delete User - Happy Path
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    When request to delete the user
    Then the request is successful
    And the user is deleted
    And the user deleted event is logged
