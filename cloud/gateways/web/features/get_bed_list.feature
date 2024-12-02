Feature: Get Bed List

  Scenario: Get Beds List
    Given the application is running
    And beds are found
    And a request to get a bed list
    And with a valid auth credentials
    When the request is made to get a bed list
    Then the user is told the request was successful
    And a bed list is returned

  Scenario: Get Empty Beds List
    Given the application is running
    And beds not found
    And a request to get a bed list
    And with a valid auth credentials
    When the request is made to get a bed list
    Then the user is told the request was successful
    And an empty bed list is returned

  Scenario: invalid auth
    Given the application is running
    And beds are found
    And a request to get a bed list
    But with invalid auth credentials
    When the request is made to get a bed list
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And beds are found
    And a request to get a bed list
    When the request is made to get a bed list
    Then the user is told the request was forbidden
