Feature: Count of all patients

  Scenario: Get list of all patients populated
    Given the application is running
    And a request to get patients count
    And valid authentication credentials are being included
    And several patients exist
    When the request for all patients is made
    Then the user is told the request was successful
    And the total number of resources is specified

  Scenario: Get list of all patients empty
    Given the application is running
    And a request to get patients count
    And valid authentication credentials are being included
    When the request for all patients is made
    Then an empty list of all patients is returned
    And the total number of resources is `0`

  Scenario: Get list of first five patients
    Given the application is running
    And a request to get patients count
    And valid authentication credentials are being included
    And the request specifies a `page_size` of `5`
    And the request specifies a `page_number` of `1`
    And there are `6` patients
    When the request for all patients is made
    Then the user is told the request was successful
    And the total number of resources is `6`

  Scenario: Get second page of patients
    Given the application is running
    And a request to get patients count
    And valid authentication credentials are being included
    And the request specifies a `page_size` of `5`
    And the request specifies a `page_number` of `2`
    And there are `6` patients
    When the request for all patients is made
    Then the user is told the request was successful
    And the total number of resources is `6`

  Scenario: Get empty page
    Given the application is running
    And a request to get patients count
    And valid authentication credentials are being included
    And the request specifies a `page_size` of `5`
    And the request specifies a `page_number` of `3`
    And there are `6` patients
    When the request for all patients is made
    Then the user is told the request was successful
    And the total number of resources is `6`

  Scenario: Filter by identifier
    Given the application is running
    And a request to get patients count
    And valid authentication credentials are being included
    And the request specifies a `identifier` of `PID-1`
    And several patients exist including one with identifier `PID-1`
    When the request for all patients is made
    Then the user is told the request was successful
    And the total number of resources is `1`

  Scenario: Filter by identifier - No matching patient
    Given the application is running
    And a request to get patients count
    And valid authentication credentials are being included
    And the request specifies a `identifier` of `random-identifier`
    And several patients exist
    When the request for all patients is made
    Then the user is told the request was successful
    And the total number of resources is `0`

  Scenario: Credentials not provided
    Given the application is running
    And a request to get patients count
    When the request for all patients is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to get patients count
    And invalid authentication credentials are being included
    When the request for all patients is made
    Then the user is told the request was unauthorized
