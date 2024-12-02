Feature: Create Bed

  Scenario: Create Bed - Happy path
    Given the application is running
    And a request to create a bed
    And valid authentication credentials are being included
    When the request to create a bed is made
    Then the user is told the request was successful
    And the requested bed is created
    And the creation of the bed is published
    And the created bed is returned

  Scenario: Create Bed - Max beds reached
    Given the application is running
    And a request to create a bed
    And 64 beds exist
    And valid authentication credentials are being included
    When the request to create a bed is made
    Then the user is told the maximum amount of beds has been reached
    And the requested bed is not created
    And the creation of the bed is not published

  Scenario: Create Bed - Name already in use
    Given the application is running
    And a request to create a bed
    And there is a bed with the same name for creation
    And valid authentication credentials are being included
    When the request to create a bed is made
    Then the user is told the bed name is in use
    And the requested bed is not created
    And the creation of the bed is not published

  Scenario Outline: Create Bed - Missing Values
    Given the application is running
    And a request to create a bed
    And valid authentication credentials are being included
    And the request includes no create bed `<field_name>` field
    When the request to create a bed is made
    And the creation of the bed is not published
    And the user is told there payload is invalid

    Examples:
      | field_name |
      | id         |
      | name       |

  Scenario: Credentials not provided
    Given the application is running
    And a request to create a bed
    When the request to create a bed is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to create a bed
    And invalid authentication credentials are being included
    When the request to create a bed is made
    Then the user is told the request was unauthorized
