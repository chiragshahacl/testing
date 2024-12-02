Feature: Delete Bed Group

  Scenario: Delete bed group that exists
    Given the application is running
    And a request to delete group by id
    And valid authentication credentials are being included
    And several bed groups exist, including the one to be deleted
    When the request is made to delete bed group by id
    Then the user is told the request was successful
    And the deleted bed group no longer exists
    And the other bed groups still exist

  Scenario: Delete bed group that doesn't exist
    Given the application is running
    And a request to delete group by id
    And valid authentication credentials are being included
    And several bed groups exist, not including one to be deleted
    When the request is made to delete bed group by id
    Then the user is told there payload is invalid
    And the other bed groups still exist

  Scenario: Delete bed group, invalid auth
    Given the application is running
    And a request to delete group by id
    And invalid authentication credentials are being included
    When the request is made to delete bed group by id
    Then the user is told the request was unauthorized

  Scenario: Delete bed group, missing auth
    Given the application is running
    And a request to delete group by id
    When the request is made to delete bed group by id
    Then the user is told the request was forbidden
