Feature: Create Bed Batch

  Scenario: Happy Path
    Given the application is running
    And a request to batch create some beds
    And with a valid auth credentials
    And the beds can be made
    When the request is made to batch create some beds
    Then the user is told the request was successful
    And the list of beds is returned

  Scenario: Invalid payload
    Given the application is running
    And a request to batch create some beds
    And with a valid auth credentials
    And the beds cant be made
    When the request is made to batch create some beds
    Then the user is told their payload is invalid

  Scenario: Invalid auth
    Given the application is running
    And a request to batch create some beds
    And with invalid auth credentials
    And the beds can be made
    When the request is made to batch create some beds
    Then the user is told the request was unauthorized

  Scenario: Auth not provided
    Given the application is running
    And a request to batch create some beds
    And the beds can be made
    When the request is made to batch create some beds
    Then the user is told the request was forbidden
