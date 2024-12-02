Feature: Batch delete beds

  Scenario: Delete one bed
    Given the application is running
    And a request to batch delete a bed
    And with a valid auth credentials
    And the beds can be deleted
    And several devices exist for batch delete beds
    And the device can be unassigned when deleting a bed
    When the request is made to batch delete beds
    Then the user is told the request was successful with no content

  Scenario: Delete multiple beds
    Given the application is running
    And a request to batch delete beds
    And with a valid auth credentials
    And the beds can be deleted
    And several devices exist for batch delete beds
    And the devices can be unassigned
    When the request is made to batch delete beds
    Then the user is told the request was successful with no content

  Scenario: Invalid payload
    Given the application is running
    And a request to batch delete beds
    And with a valid auth credentials
    And the beds can't be deleted
    And several devices exist for batch delete beds
    And the devices can be unassigned
    When the request is made to batch delete beds
    Then the user is told their payload is invalid

  Scenario: Invalid auth
    Given the application is running
    And a request to batch delete beds
    And with invalid auth credentials
    When the request is made to batch delete beds
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And a request to batch delete beds
    When the request is made to batch delete beds
    Then the user is told the request was forbidden
