Feature: Get Patient by Id

  Scenario: Get Patient by existing patient id
    Given the application is running
    And a patient exists
    And a request to get a patient
    When the request is made to get a patient
    Then the user is told the request was successful
    And a patient is returned

  Scenario: Get Patient by non existing patient id
    Given the application is running
    And no patient exists
    And a request to get a patient
    When the request is made to get a patient
    Then the user is told the request was not found
