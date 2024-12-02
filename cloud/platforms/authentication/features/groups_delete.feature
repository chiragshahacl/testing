Feature: Group management

  Scenario: Delete Group - Happy Path
    Given the app is running
    And a user group exists
    And a valid admin user exists
    And the user is already authenticated
    When request to delete the user group
    Then the request is successful
    And the group is deleted
    And the group deleted event is logged

  Scenario: Delete Group - As regular user
    Given the app is running
    And a user group exists
    And a valid user exists
    And the user is already authenticated
    When request to delete the user group
    Then the request fails

  Scenario: Delete Group - Invalid group id
    Given the app is running
    And a user group exists
    And a valid admin user exists
    And the user is already authenticated
    But the user group to delete does not exit
    When request to delete the user group
    Then the request fails
