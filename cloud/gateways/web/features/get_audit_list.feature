Feature: Get Audit List

  Scenario: Get Audit List
    Given the application is running
    And a request to get list of audit events
    And several audit events exist
    And the request includes valid authentication credentials
    When the request is made to get list of audit events
    Then the user is told the request was successful
    And the list of audit events is returned

  Scenario: Get Audit List no events
    Given the application is running
    And a request to get list of audit events
    And no audit events exist
    And the request includes valid authentication credentials
    When the request is made to get list of audit events
    Then the user is told the request was not found

  Scenario: Get audit list missing auth
    Given the application is running
    And a request to get list of audit events
    When the request is made to get list of audit events
    Then the user is told the request was forbidden

  Scenario: Get audit list invalid auth
    Given the application is running
    And a request to get list of audit events
    And the request includes invalid authentication credentials
    When the request is made to get list of audit events
    Then the user is told the request was unauthorized
