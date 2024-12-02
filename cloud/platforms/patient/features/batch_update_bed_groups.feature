Feature: Batch Update bed groups

  Scenario: Happy Path
    Given the application is running
    And a request to batch update bed groups
    And valid authentication credentials are being included
    And the bed groups to be updated exist
    When the request to batch update bed groups is made
    Then the user is told the request was successful
    And the requested bed groups are updated
    And the update of the bed groups is published

  Scenario: Bed group with assigned beds
    Given the application is running
    And a request to batch update bed groups
    And valid authentication credentials are being included
    And the bed groups to be updated exist
    And the bed groups have beds assigned
    When the request to batch update bed groups is made
    Then the user is told the request was successful
    And the requested bed groups are updated
    And the update of the bed groups is published
    And the beds are not deleted
    And the beds still assigned to the bed group

  Scenario: Batch Update bed groups - Not all group found
    Given the application is running
    And a request to batch update `2` bed groups
    And the bed group number `1` exist
    And valid authentication credentials are being included
    When the request to batch update bed groups is made
    Then the user is told the bed group was not found
    And the requested bed groups are not updated
    And the update of the bed groups is not published

  Scenario: Batch Update bed groups - Name already in use
    Given the application is running
    And a request to batch update `1` bed groups
    And valid authentication credentials are being included
    And the bed groups to be updated exist
    And one of the provided names is already in use by another bed group
    When the request to batch update bed groups is made
    Then the user is told the bed group name is in use
    And the requested bed groups are not updated
    And the update of the bed groups is not published

  Scenario: Credentials not provided
    Given the application is running
    And a request to batch update bed groups
    When the request to batch update bed groups is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to batch update bed groups
    And invalid authentication credentials are being included
    When the request to batch update bed groups is made
    Then the user is told the request was unauthorized
