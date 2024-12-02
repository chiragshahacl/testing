Feature: Insert group

  Scenario: Happy Path
    Given the application is running
    And request to create a bed group
    And valid authentication credentials are being included
    When the request to create a bed group is made
    Then the user is told the request was successful
    And the requested bed group is created
    And the creation of the bed group is published
    And the created bed group is returned

  Scenario: Name already in use
    Given the application is running
    And request to create a bed group
    And there is a group with the same name for creation
    And valid authentication credentials are being included
    When the request to create a bed group is made
    Then the user is told the bed group name is in use
    And the requested bed group is not created
    And the creation of the bed group is not published

  Scenario Outline: Missing Values
    Given the application is running
    And request to create a bed group
    And valid authentication credentials are being included
    And the request includes no create a bed group `<field_name>` field
    When the request to create a bed group is made
    And the creation of the bed group is not published
    And the user is told there payload is invalid

    Examples:
      | field_name |
      | id         |
      | name       |

  Scenario: Credentials not provided
    Given the application is running
    And request to create a bed group
    When the request to batch create beds is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And request to create a bed group
    And invalid authentication credentials are being included
    When the request to create a bed group is made
    Then the user is told the request was unauthorized
