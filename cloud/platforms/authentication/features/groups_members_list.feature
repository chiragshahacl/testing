Feature: Group management

  Scenario: List group members - Happy Path
    Given the app is running
    And a user group exists
    And a valid admin user exists
    And the user is already authenticated
    When request the list of group members
    Then the request is successful
    And the list of group members data is correct

  Scenario: List group members - Empty members list
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a user group exists
    But the group has no members
    When request the list of group members
    Then the request is successful
    And the list of group members data is correct

  Scenario: List group members - As regular user
    Given the app is running
    And a user group exists
    And a valid user exists
    And the user is already authenticated
    When request the list of group members
    Then the request fails

  Scenario: List group members - Invalid group ID
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    But the group does not exist
    When request the list of group members
    Then the request fails
