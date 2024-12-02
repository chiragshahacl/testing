Feature: Group members management - Add

  Scenario: Add Member to a User Group - Happy Path
    Given the app is running
    And a user group exists
    And a valid admin user exists
    And the user is already authenticated
    And a request to add a user as group member
    When the logged in user adds the user to the group
    Then the request is successful
    And the user is a group member
    And the member added event is logged

  Scenario: Add Member to a User Group - As regular user
    Given the app is running
    And a user group exists
    And a valid user exists
    And the user is already authenticated
    And a request to add a user as group member
    When the logged in user adds the user to the group
    Then the request fails
    And the user is not a group member

  Scenario: Add Member to a User Group - The user is already a member
    Given the app is running
    And a user group exists
    And a valid admin user exists
    And the user is already authenticated
    And a request to add a user as group member
    But the user is already a group member
    When the logged in user adds the user to the group
    Then the request is successful
    And the user is a group member
    And the member added event is logged

  Scenario: Add Member to a User Group - Invalid group ID
    Given the app is running
    And a user group exists
    And a valid admin user exists
    And the user is already authenticated
    And a request to add a user as group member
    But the group id is invalid
    When the logged in user adds the user to the group
    Then the request fails

  Scenario: Add Member to a User Group - Invalid user ID
    Given the app is running
    And a user group exists
    And a valid admin user exists
    And the user is already authenticated
    And a request to add a user as group member
    But the user id is invalid
    When the logged in user adds the user to the group
    Then the request fails
