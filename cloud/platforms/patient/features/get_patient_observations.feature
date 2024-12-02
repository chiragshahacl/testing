Feature: Get Patient Observations

  Scenario: Get Patient Observations (1 param)
    Given the application is running
    And a valid request to get patient observations
    And valid authentication credentials are being included
    And several patient observations exist
    And the request is supplied query params for 1 of the existing observations
    When the request is made to get patient observations
    Then the user is told the request was successful
    And the expected patient observations are returned

  Scenario: Get Patient Observations (2 param)
    Given the application is running
    And a valid request to get patient observations
    And valid authentication credentials are being included
    And several patient observations exist
    And the request is supplied query params for 2 of the existing observations
    When the request is made to get patient observations
    Then the user is told the request was successful
    And the expected patient observations are returned

  Scenario: Get Patient Observations (3 param)
    Given the application is running
    And a valid request to get patient observations
    And valid authentication credentials are being included
    And several patient observations exist
    And the request is supplied query params for 3 of the existing observations
    When the request is made to get patient observations
    Then the user is told the request was successful
    And the expected patient observations are returned

  Scenario: Get Patient Observations (1 param & isAlert false)
    Given the application is running
    And a valid request to get patient observations
    And valid authentication credentials are being included
    And several patient observations exist
    And the request is supplied query params for 1 of the existing observations and not an alert
    When the request is made to get patient observations
    Then the user is told the request was successful
    And the expected patient observations are returned

  Scenario: Get Patient Observations (2 param & isAlert false)
    Given the application is running
    And a valid request to get patient observations
    And valid authentication credentials are being included
    And several patient observations exist
    And the request is supplied query params for 2 of the existing observations and not an alert
    When the request is made to get patient observations
    Then the user is told the request was successful
    And the expected patient observations are returned

  Scenario: Get Patient Observations (3 param & isAlert false)
    Given the application is running
    And a valid request to get patient observations
    And valid authentication credentials are being included
    And several patient observations exist
    And the request is supplied query params for 3 of the existing observations and not an alert
    When the request is made to get patient observations
    Then the user is told the request was successful
    And the expected patient observations are returned

  Scenario: Credentials not provided
    Given the application is running
    And a valid request to get patient observations
    When the request is made to get patient observations
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a valid request to get patient observations
    And invalid authentication credentials are being included
    When the request is made to get patient observations
    Then the user is told the request was unauthorized
