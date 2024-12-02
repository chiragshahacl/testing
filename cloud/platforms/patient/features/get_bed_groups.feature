Feature: Get bed groups

  Scenario: Get bed groups
    Given the application is running
    And a valid request to get bed groups
    And valid authentication credentials are being included
    And bed groups exist
    When the request is made to get bed groups
    Then the user is told the request was successful
    And the existing bed groups are returned

  Scenario: Bed groups with beds assigned
    Given the application is running
    And a valid request to get bed groups
    And valid authentication credentials are being included
    And bed groups exist
    And the bed groups have beds assigned
    When the request is made to get bed groups
    Then the user is told the request was successful
    And the existing bed groups are returned

  Scenario: Get bed groups - No groups
    Given the application is running
    And a valid request to get bed groups
    And valid authentication credentials are being included
    When the request is made to get bed groups
    Then the user is told the request was successful
    And no bed groups are returned

  Scenario: Credentials not provided
    Given the application is running
    And a valid request to get bed groups
    When the request is made to get bed groups
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a valid request to get bed groups
    And invalid authentication credentials are being included
    When the request is made to get bed groups
    Then the user is told the request was unauthorized
