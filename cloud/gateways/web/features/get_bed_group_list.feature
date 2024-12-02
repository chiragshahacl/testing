Feature: Get Bed Group List

  Scenario: Get Bed Group List
    Given the application is running
    And bed groups are found
    And a request to get a bed group list
    When the request is made to get a bed group list
    Then the user is told the request was successful
    And a bed group list is returned

  Scenario: Get Empty Bed Group List
    Given the application is running
    And bed groups not found
    And a request to get a bed group list
    When the request is made to get a bed group list
    Then the user is told the request was successful
    And an empty bed group list is returned

  Scenario: Get Bed Group List, invalid auth
    Given the application is running
    And bed groups are found
    And a request to get a bed group list
    But with invalid auth credentials
    When the request is made to get a bed group list
    Then the user is told the request was unauthorized
