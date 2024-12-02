Feature: Group management

  Scenario: List Users - Happy Path
    Given the app is running
    And a list of user groups exist
    And a valid admin user exists
    And the user is already authenticated
    When request the list of user groups
    Then the request is successful
    And the list of user groups data is correct

  Scenario: List Users - Empty users groups list
    Given the app is running
    And there are no user groups
    And a valid admin user exists
    And the user is already authenticated
    When request the list of user groups
    Then the request is successful
    And the list of user groups data is correct

  Scenario: List Users - As regular user
    Given the app is running
    And a list of user groups exist
    And a valid user exists
    And the user is already authenticated
    When request the list of user groups
    Then the request fails
