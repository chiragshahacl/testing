Feature: Get Patient Session Physiological Alerts

  Scenario: Get list of session Physiological Alerts
    Given the application is running
    And A patient exists
    And A request to get the physiological alerts of the patient
    And There are 5 paired physiological alerts to the patient
    And valid authentication credentials are being included
    When The request is made to get physiological alerts
    Then the user is told the request was successful
    And The expected physiological alert response is returned

  Scenario: Get list of session Physiological Alerts - Only active
    Given the application is running
    And A patient exists
    And A request to get the physiological alerts of the patient
    And There are 5 only active physiological alerts to the patient
    And valid authentication credentials are being included
    When The request is made to get physiological alerts
    Then the user is told the request was successful
    And The response is an empty list

  Scenario: Get list of session Physiological Alerts - Only inactive
    Given the application is running
    And A patient exists
    And A request to get the physiological alerts of the patient
    And There are 5 only inactive physiological alerts to the patient
    And valid authentication credentials are being included
    When The request is made to get physiological alerts
    Then the user is told the request was successful
    And The response is an empty list

  Scenario: Get list of session Physiological Alerts - Mixed
    Given the application is running
    And A patient exists
    And A request to get the physiological alerts of the patient
    And There are a mixed of paired and incomplete physiological alerts to the patient
    And valid authentication credentials are being included
    When The request is made to get physiological alerts
    Then the user is told the request was successful
    And The expected physiological alert response is returned

  Scenario: Get list of session Physiological Alerts - Same alert, multiple times
    Given the application is running
    And A patient exists
    And A request to get the physiological alerts of the patient
    And There is an alert paired multiple times for the patient
    And valid authentication credentials are being included
    When The request is made to get physiological alerts
    Then the user is told the request was successful
    And The expected physiological alert response is returned

  Scenario: Get list of session Physiological Alerts - Multiple actives for same alert
    Given the application is running
    And A patient exists
    And A request to get the physiological alerts of the patient
    And There is an alert paired but active multiple times
    And valid authentication credentials are being included
    When The request is made to get physiological alerts
    Then the user is told the request was successful
    And The expected physiological alert response is returned

  Scenario: Get list of session Physiological Alerts - Multiple inactives for same alert
    Given the application is running
    And A patient exists
    And A request to get the physiological alerts of the patient
    And There is an alert paired but inactive multiple times
    And valid authentication credentials are being included
    When The request is made to get physiological alerts
    Then the user is told the request was successful
    And The expected physiological alert response is returned

  Scenario: Unauthorized
    Given the application is running
    And A patient exists
    And A request to get the physiological alerts of the patient
    And invalid authentication credentials are being included
    When The request is made to get physiological alerts
    Then the user is told the request was unauthorized
