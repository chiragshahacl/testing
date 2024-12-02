Feature: Dismiss cancelled patient admission

  Scenario: Happy Path
    Given the application is running
    And a request is made to dismiss an admission
    And valid authentication credentials are being included
    And the patient exists
    And the encounter exists with status `cancelled`
    When the request to dismiss an admission is made
    Then the user is told the request was successful with no content
    And the admission doesn't exist any more
    And the admission dismissal is published

  Scenario: Happy Path
    Given the application is running
    And a request is made to dismiss an admission
    And valid authentication credentials are being included
    And the patient exists
    When the request to dismiss an admission is made
    Then the user is told the request was rejected

  Scenario Outline: Dismiss non cancelled admission
    Given the application is running
    And a request is made to dismiss an admission
    And valid authentication credentials are being included
    And the patient exists
    And the encounter exists with status `<status>`
    When the request to dismiss an admission is made
    Then the user is told the request was rejected

    Examples:
      | status      |
      | in-progress |
      | completed   |
      | planned     |
