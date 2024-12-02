Feature: Get assigned beds for a group

  Scenario: Get bed group's beds by group id
    Given the application is running
    And a bed group exists
    And a bed assigned to the group
    And a request to get assigned beds for the group
    When the request is made to get assigned beds for a group
    Then the user is told the request was successful
    And a list of bed is returned

  Scenario: Get bed group's beds by non existing group id
    Given the application is running
    And no bed group exists
    And a request to get assigned beds for the group
    When the request is made to get assigned beds for a group
    Then the user is told the request was successful
    And an empty bed list is returned

  Scenario: Get bed group's beds by group id, invalid auth
    Given the application is running
    And a bed group exists
    And a bed assigned to the group
    And a request to get assigned beds for the group
    But with invalid auth credentials
    When the request is made to get assigned beds for a group
    Then the user is told the request was unauthorized
