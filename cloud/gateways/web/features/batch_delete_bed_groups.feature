Feature: Batch delete bed groups

  Scenario: Delete one bed group
    Given the application is running
    And a request to batch delete a bed group
    And with a valid auth credentials
    And the bed groups can be deleted
    When the request is made to batch delete bed groups
    Then the user is told the request was successful with no content

  Scenario: Delete multiple bed groups
    Given the application is running
    And a request to batch delete bed groups
    And with a valid auth credentials
    And the bed groups can be deleted
    When the request is made to batch delete bed groups
    Then the user is told the request was successful with no content

  Scenario: Invalid payload
    Given the application is running
    And a request to batch delete bed groups
    And with a valid auth credentials
    And the bed groups can't be deleted
    When the request is made to batch delete bed groups
    Then the user is told their payload is invalid

  Scenario: Invalid auth
    Given the application is running
    And a request to batch delete bed groups
    And with invalid auth credentials
    When the request is made to batch delete bed groups
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And a request to batch delete bed groups
    When the request is made to batch delete bed groups
    Then the user is told the request was forbidden
