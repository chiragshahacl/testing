Feature: Batch Update Beds

  Scenario: Batch Update Beds
    Given the application is running
    And a request to batch update beds
    And valid authentication credentials are being included
    And the beds to be updated exist
    When the request to batch update beds is made
    Then the user is told the request was successful
    And the requested beds are updated
    And the update of the beds is published
    And the updated beds are returned

  Scenario: Batch Update Beds - Not all bed found
    Given the application is running
    And a request to batch update `2` beds
    And the bed number `1` exist
    And valid authentication credentials are being included
    When the request to batch update beds is made
    Then the user is told the bed was not found
    And the requested beds are not updated
    And the update of the beds is not published

  Scenario: Batch Update Beds - Name already in use
    Given the application is running
    And a request to batch update `1` beds
    And valid authentication credentials are being included
    And the beds to be updated exist
    And one of the provided names is already in use by another bed
    When the request to batch update beds is made
    Then the user is told the bed name is in use
    And the requested beds are not updated
    And the update of the beds is not published

  Scenario: Credentials not provided
    Given the application is running
    And a request to batch update beds
    When the request to batch update beds is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to batch update beds
    And invalid authentication credentials are being included
    When the request to batch update beds is made
    Then the user is told the request was unauthorized
