Feature: Batch Create or Update Beds

  Scenario: Batch create or update beds
    Given the application is running
    And a request to batch create or update beds
    And the request includes valid authentication credentials
    And the beds can be created or updated
    When the request is made to batch create or update some beds
    Then the user is told the request was successful with no content

  Scenario: Batch create or update beds 2
    Given the application is running
    And a request to batch create or update beds 2
    And the request includes valid authentication credentials
    And the beds can be created or updated 2
    And the request includes valid authentication credentials
    When the request is made to batch create or update some beds
    Then the user is told the request was successful with no content

  Scenario: Batch create or update beds invalid auth
    Given the application is running
    And a request to batch create or update beds
    And the request includes invalid authentication credentials
    And the beds can be created or updated
    When the request is made to batch create or update some beds
    Then the user is told the request was unauthorized

  Scenario: Batch create or update beds missing auth
    Given the application is running
    And a request to batch create or update beds
    And the beds can be created or updated
    When the request is made to batch create or update some beds
    Then the user is told the request was forbidden
