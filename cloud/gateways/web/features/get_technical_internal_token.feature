Feature: Get Internal Token

  Scenario: Get Technical Internal Token - Happy Path
    Given the application is running
    And a valid request to obtain a technical internal token
    When the request to get a technical internal token is made
    Then the user is told the request was successful
    And the token is included in the response

  Scenario: Get Technical Internal Token - Invalid request
    Given the application is running
    And a valid request to obtain a technical internal token
    But the password is incorrect
    When the request to get a technical internal token is made
    Then the user is told the request was unauthorized

  Scenario: Get Technical Internal Token - Account locked
    Given the application is running
    And a valid request to obtain a technical internal token
    But the account is locked
    When the request to get a technical internal token is made
    Then the user is told the request was forbidden

  Scenario: Get Technical Internal Token - Empty password
    Given the application is running
    And a valid request to obtain a technical internal token
    But the password is empty
    When the request to get a technical internal token is made
    Then the user is told the request was invalid

  Scenario: Get Technical Internal Token - Whitespaces
    Given the application is running
    And a valid request to obtain a technical internal token
    But the password field contains only whitespace characters
    When the request to get a technical internal token is made
    Then the user is told the request was invalid

  Scenario: Get Technical Internal Token - Bad Request
    Given the application is running
    And a valid request to obtain a technical internal token
    But the request is a bad request
    When the request to get a technical internal token is made
    Then the user is told the request was unauthorized
