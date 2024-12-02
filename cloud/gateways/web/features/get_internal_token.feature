Feature: Get Internal Token

  Scenario: Get Internal Token - Happy Path
    Given the application is running
    And a valid request to obtain an internal token
    When the request to get an internal token is made
    Then the user is told the request was successful
    And the token is included in the response

  Scenario: Get Internal Token - Invalid request
    Given the application is running
    And a valid request to obtain an internal token
    But the password is incorrect
    When the request to get an internal token is made
    Then the user is told the request was unauthorized

  Scenario: Get Internal Token - Account locked
    Given the application is running
    And a valid request to obtain an internal token
    But the account is locked
    When the request to get an internal token is made
    Then the user is told the request was forbidden

  Scenario: Get Internal Token - Empty password
    Given the application is running
    And a valid request to obtain an internal token
    But the password is empty
    When the request to get an internal token is made
    Then the user is told the request was invalid

  Scenario: Get Internal Token - Whitespaces
    Given the application is running
    And a valid request to obtain an internal token
    But the password field contains only whitespace characters
    When the request to get an internal token is made
    Then the user is told the request was invalid

  Scenario: Get Internal Token - Bad Request
    Given the application is running
    And a valid request to obtain an internal token
    But the request is a bad request
    When the request to get an internal token is made
    Then the user is told the request was unauthorized
