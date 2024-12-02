Feature: Retrieve App setting

  Scenario: List app settings - Happy Path
    Given the app is running
    And app settings exists
    And a valid admin user exists
    And the user is already authenticated
    When request the list of app settings
    Then the request is successful
    And the list of app settings is correct

  Scenario: List app settings - Empty list
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And there are not app settings defined
    When request the list of app settings
    Then the request is successful
    And the list of app settings is correct

  Scenario: List app settings - As regular user
    Given the app is running
    And app settings exists
    And a valid user exists
    And the user is already authenticated
    When request the list of app settings
    Then the request fails
