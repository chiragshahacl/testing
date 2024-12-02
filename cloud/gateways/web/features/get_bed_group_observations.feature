Feature: Get Bed Group Observations

  Scenario: Get Bed Group Observations
    Given the application is running
    And a request to get bed group observations
    And the request includes valid authentication credentials
    And several patients exist within the bed group
    And the patients have some observations
    When the request is made to get bed group observations
    Then the user is told the request was successful
    And the bed groups observations are returned

  Scenario: invalid auth
    Given the application is running
    And a request to get bed group observations
    But with invalid auth credentials
    When the request is made to get bed group observations
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And a request to get bed group observations
    When the request is made to get bed group observations
    Then the user is told the request was forbidden

  Scenario: Get Bed Group Observations with empty patients
    Given the application is running
    And a request to get empty bed group observations
    And the request includes valid authentication credentials
    And patients doesn't exist within the bed group
