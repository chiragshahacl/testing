Feature: Batch Assign Beds to Groups

  Scenario: Assign beds to one group
    Given the application is running
    And a request to batch assign beds to a group
    And with a valid auth credentials
    And the beds can be assigned
    When the request is made to assign some beds
    Then the user is told the request was successful with no content

  Scenario: Assign beds to multiple groups
    Given the application is running
    And a request to batch assign beds to multiple groups
    And with a valid auth credentials
    And the beds can be assigned
    When the request is made to assign some beds
    Then the user is told the request was successful with no content

  Scenario: Invalid payload
    Given the application is running
    And a request to batch assign beds to a group
    And with a valid auth credentials
    And the beds cant be assigned
    When the request is made to assign some beds
    Then the user is told their payload is invalid

  Scenario: Invalid auth
    Given the application is running
    And a request to batch assign beds to a group
    And with invalid auth credentials
    And the beds can be assigned
    When the request is made to assign some beds
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And a request to batch assign beds to a group
    When the request is made to assign some beds
    Then the user is told the request was forbidden
