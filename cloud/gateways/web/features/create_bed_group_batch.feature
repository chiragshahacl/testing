Feature: Create Bed Group batch

  Scenario: Create bed batch
    Given the application is running
    And a request to batch create some bed groups
    And with a valid auth credentials
    And the bed groups can be made
    When the request is made to batch create some bed groups
    Then the user is told the request was successful
    And the list of bed groups is returned

  Scenario: Create bed batch failure
    Given the application is running
    And a request to batch create some bed groups
    And with a valid auth credentials
    And the bed groups cant be made
    When the request is made to batch create some bed groups
    Then the user is told their payload is invalid

  Scenario: Create bed batch, invalid auth
    Given the application is running
    And a request to batch create some bed groups
    And with invalid auth credentials
    And the beds can be made
    When the request is made to batch create some bed groups
    Then the user is told the request was unauthorized
