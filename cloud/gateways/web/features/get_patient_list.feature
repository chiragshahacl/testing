Feature: Get Patient List

  Scenario: Get Patient List
    Given the application is running
    And patients are found
    And a request to get a patient list
    When the request is made to get a patient list
    Then the user is told the request was successful
    And a patient list is returned

  Scenario: Get Empty Patient List
    Given the application is running
    And patients not found
    And a request to get a patient list
    When the request is made to get a patient list
    Then the user is told the request was successful
    And an empty patient list is returned

  Scenario: invalid auth
    Given the application is running
    And patients are found
    And a request to get a patient list
    But with invalid auth credentials
    When the request is made to get a patient list
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And patients are found
    And a request to get a patient list without auth creds
    When the request is made to get a patient list
    Then the user is told the request was forbidden
