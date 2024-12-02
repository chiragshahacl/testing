Feature: Batch Delete Bed Groups

  Scenario: Happy path
    Given the application is running
    And 5 bed groups exist
    And a request to delete bed groups
    And valid authentication credentials are being included
    When the request to batch delete bed groups is made
    Then the user is told the request was successful
    And the requested bed groups are deleted
    And the deletion of the bed groups is published

  Scenario: Empty payload
    Given the application is running
    And 5 bed groups exist
    And a request to delete bed groups
    But the list of bed group to delete is empty
    And valid authentication credentials are being included
    When the request to batch delete bed groups is made
    Then the user is told there payload is invalid
    And no bed groups are deleted
    And the deletion of the bed groups is not published

  Scenario: Bed group with assigned beds
    Given the application is running
    And 5 bed groups exist
    And a request to delete bed groups
    And the groups have beds assigned
    And valid authentication credentials are being included
    When the request to batch delete bed groups is made
    Then the user is told the request was successful
    And the requested bed groups are deleted
    And the deletion of the bed groups is published
    And the beds are not deleted

  Scenario: Bed Groups doesn't exist
    Given the application is running
    And 5 bed groups exist
    And a request to delete bed groups
    And valid authentication credentials are being included
    But the bed groups to delete does not exists
    When the request to batch delete bed groups is made
    Then the user is told the request was successful
    And no bed groups are deleted
    And the deletion of the bed groups is not published

  Scenario: Unauthorized
    Given the application is running
    And 5 bed groups exist
    And a request to delete bed groups
    And invalid authentication credentials are being included
    When the request to batch delete bed groups is made
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And 5 bed groups exist
    And a request to delete bed groups
    When the request to batch delete bed groups is made
    Then the user is told the request was forbidden
