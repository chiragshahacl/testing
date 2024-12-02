Feature: Assign beds

  Scenario: Happy path
    Given the application is running
    And a request to assign some beds
    And with a valid auth credentials
    And the beds can be assigned
    When the request is made to assign some beds
    Then the user is told the request was successful with no content

  Scenario: Invalid payload
    Given the application is running
    And a request to assign some beds
    And with a valid auth credentials
    And the beds cant be assigned
    When the request is made to assign some beds
    Then the user is told their payload is invalid

  Scenario: Invalid auth
    Given the application is running
    And a request to assign some beds
    And with invalid auth credentials
    And the beds can be made
    When the request is made to assign some beds
    Then the user is told the request was unauthorized
