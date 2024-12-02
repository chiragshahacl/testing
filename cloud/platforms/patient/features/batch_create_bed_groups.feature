Feature: Batch insert bed groups

  Scenario: Happy Path
    Given the application is running
    And request to batch create bed groups
    And valid authentication credentials are being included
    When the request to batch create bed groups is made
    Then the user is told the request was successful
    And the requested bed groups are created
    And the creation of the bed groups is published
    And the created bed groups are returned

  Scenario: Name already in use
    Given the application is running
    And request to batch create bed groups
    And there is a group with the same name
    And valid authentication credentials are being included
    When the request to batch create bed groups is made
    Then the user is told the bed group name is in use
    And the requested bed groups are not created
    And the creation of the bed groups is not published

  Scenario Outline: Missing Values
    Given the application is running
    And request to batch create bed groups
    And valid authentication credentials are being included
    And the request includes no batch create bed groups `<field_name>` field
    When the request to batch create bed groups is made
    And the creation of the bed groups is not published
    And the user is told there payload is invalid

    Examples:
      | field_name |
      | id         |
      | name       |
      | groups     |

  Scenario: Credentials not provided
    Given the application is running
    And request to batch create bed groups
    When the request to batch create beds is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And request to batch create bed groups
    And invalid authentication credentials are being included
    When the request to batch create bed groups is made
    Then the user is told the request was unauthorized
