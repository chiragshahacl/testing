Feature: Get Patient by ID

  Scenario: Patient exists
    Given the application is running
    And a valid request to get a patient by id
    And valid authentication credentials are being included
    And the patient exists
    When the request is made to get a patient by id
    Then the patient is fetched
    And the user is told the request was successful

  Scenario: Patient does not exist
    Given the application is running
    And a valid request to get a patient by id
    And valid authentication credentials are being included
    When the request is made to get a patient by id
    Then the user is told the patient was not found

  Scenario: Credentials not provided
    Given the application is running
    And a valid request to get a patient by id
    When the request is made to get a patient by id
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a valid request to get a patient by id
    And invalid authentication credentials are being included
    When the request is made to get a patient by id
    Then the user is told the request was unauthorized
