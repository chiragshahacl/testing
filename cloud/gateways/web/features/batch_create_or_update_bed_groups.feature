Feature: Batch Create or Update Bed Groups

  Scenario: Batch create or update bed groups
    Given the application is running
    And a request to batch create or update bed groups
    And the request includes valid authentication credentials
    And the bed groups can be created or updated
    When the request is made to batch create or update some bed groups
    Then the user is told the request was successful with no content

  Scenario: Batch create or update bed groups 2
    Given the application is running
    And a request to batch create or update bed groups 2
    And the request includes valid authentication credentials
    And the bed groups can be created or updated 2
    And the request includes valid authentication credentials
    When the request is made to batch create or update some bed groups
    Then the user is told the request was successful with no content

  Scenario: Batch create or update bed groups invalid auth
    Given the application is running
    And a request to batch create or update bed groups
    And the request includes invalid authentication credentials
    And the bed groups can be created or updated
    When the request is made to batch create or update some bed groups
    Then the user is told the request was unauthorized

  Scenario: Batch create or update bed groups missing auth
    Given the application is running
    And a request to batch create or update bed groups
    And the bed groups can be created or updated
    When the request is made to batch create or update some bed groups
    Then the user is told the request was forbidden
