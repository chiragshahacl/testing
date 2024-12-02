Feature: App settings management

  Scenario: Create app setting as admin user - Happy Path
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to add the app setting 'port' : '8080'
    When the logged in user creates the app setting
    Then the request is successful
    And the app setting 'port' is created
    And the app setting create event is logged

  Scenario: Create app setting as technical user - Happy Path
    Given the app is running
    And a valid user with group "tech" exists
    And the user is already authenticated
    And a request to add the app setting 'port' : '8080'
    When the logged in user creates the app setting
    Then the request is successful
    And the app setting 'port' is created
    And the app setting create event is logged

  Scenario: Create app setting as regular user - Do not have privileges
    Given the app is running
    And a valid user exists
    And the user is already authenticated
    And a request to add the app setting 'port' : '8080'
    When the logged in user creates the app setting
    Then the request fails
    And the app setting 'port' is not created

  Scenario: Create multiple app settings - Happy Path
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to add a set of app settings
    When the logged in user creates the app setting
    Then the request is successful
    And the app settings are created
    And the app setting create events are logged

  Scenario: Update app setting value - Happy Path
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And an app setting 'port':'3030' exists
    And a request to update the app setting 'port' to '8080'
    When the logged in user updates the app setting
    Then the request is successful
    And the app setting 'port' is updated
    And the app setting update event is logged
