Feature: Group members management - Remove

  Scenario: Remove Member from a User Group - Happy Path
    Given the app is running
    And a user group exists
    And there is a member of the group
    And a valid admin user exists
    And the user is already authenticated
    When the logged in user removes the user from the group
    Then the request is successful
    And the user is not a group member
    And the member removed event is logged

  Scenario: Remove Member from a User Group - As regular user
    Given the app is running
    And a user group exists
    And there is a member of the group
    And a valid user exists
    And the user is already authenticated
    When the logged in user removes the user from the group
    Then the request fails
    And the user is a group member

  Scenario: Remove Member from a User Group - Invalid group ID
    Given the app is running
    And a user group exists
    And there is a member of the group
    And a valid admin user exists
    And the user is already authenticated
    But the group id is invalid
    When the logged in user removes the user from the group
    Then the request fails

  Scenario: Remove Member from a User Group - Invalid user ID
    Given the app is running
    And a user group exists
    And a valid admin user exists
    And the user is already authenticated
    And there is a member of the group
    But the member id is invalid
    When the logged in user removes the user from the group
    Then the request fails
