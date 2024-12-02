Feature: Get Config List

  Scenario: Get Config List
    Given the application is running
    And configs are found
    And a request to get the config list
    And with a valid auth credentials
    When the request is made to get the config list
    Then the user is told the request was successful
    And a config list is returned

  Scenario: Get Empty Config List
    Given the application is running
    And configs not found
    And a request to get the config list
    And with a valid auth credentials
    When the request is made to get the config list
    Then the user is told the request was successful
    And an empty config list is returned

  Scenario: invalid auth
    Given the application is running
    And configs are found
    And a request to get the config list
    But with invalid auth credentials
    When the request is made to get the config list
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And configs are found
    And a request to get the config list
    When the request is made to get the config list
    Then the user is told the request was forbidden
