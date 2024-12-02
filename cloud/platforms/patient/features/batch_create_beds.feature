Feature: Batch Create Beds

  Scenario: Batch Create Beds
    Given the application is running
    And a request to batch create `64` beds
    And valid authentication credentials are being included
    When the request to batch create beds is made
    Then the user is told the request was successful
    And the requested beds are created
    And the creation of the beds is published
    And the created beds are returned

  Scenario: Batch Create Beds - Max beds reached
    Given the application is running
    And a request to batch create `64` beds
    And one bed exists
    And valid authentication credentials are being included
    When the request to batch create beds is made
    Then the user is told the maximum amount of beds has been reached
    And the requested beds are not created
    And the creation of the beds is not published

  Scenario: Batch Create Beds - Name already in use
    Given the application is running
    And a request to batch create beds
    And there is a bed with the same name
    And valid authentication credentials are being included
    When the request to batch create beds is made
    Then the user is told the bed name is in use
    And the requested beds are not created
    And the creation of the beds is not published

  Scenario Outline: Batch Create Beds - Missing Values
    Given the application is running
    And a request to batch create beds
    And valid authentication credentials are being included
    And the request includes no batch create bed `<field_name>` field
    When the request to batch create beds is made
    And the creation of the beds is not published
    And the user is told there payload is invalid

    Examples:
      | field_name |
      | id         |
      | name       |
      | beds       |

  Scenario: Credentials not provided
    Given the application is running
    And a request to batch create beds
    When the request to batch create beds is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to batch create beds
    And invalid authentication credentials are being included
    When the request to batch create beds is made
    Then the user is told the request was unauthorized
