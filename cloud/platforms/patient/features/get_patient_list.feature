Feature: List of all patients

  Scenario: Get list of all patients populated
    Given the application is running
    And a request to get list of all patients
    And valid authentication credentials are being included
    And several patients exist
    When the request for all patients is made
    Then the user is told the request was successful
    And the list of all patients is returned

  Scenario: Get list of all patients empty
    Given the application is running
    And a request to get list of all patients
    And valid authentication credentials are being included
    When the request for all patients is made
    Then an empty list of all patients is returned
    And the user is told the request was successful

  Scenario: Filter by identifier
    Given the application is running
    And a request to get list of all patients
    And valid authentication credentials are being included
    And the request specifies a `identifier` of `PID-1`
    And several patients exist including one with identifier `PID-1`
    When the request for all patients is made
    Then the user is told the request was successful
    And all the patients with identifier `PID-1` are returned

  Scenario: Filter by identifier - No matching patient
    Given the application is running
    And a request to get list of all patients
    And valid authentication credentials are being included
    And the request specifies a `identifier` of `random-identifier`
    And several patients exist
    When the request for all patients is made
    Then the user is told the request was successful
    And an empty list of all patients is returned

  Scenario: Credentials not provided
    Given the application is running
    And a request to get list of all patients
    When the request for all patients is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to get list of all patients
    And invalid authentication credentials are being included
    When the request for all patients is made
    Then the user is told the request was unauthorized
