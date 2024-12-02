Feature: Batch Delete Beds

  Scenario: Batch Delete Beds - Happy path
    Given the application is running
    And beds have been created in the system
    And a request to delete beds
    And valid authentication credentials are being included
    When the request to batch delete beds is made
    Then the user is told the request was successful
    And the requested beds are deleted
    And the deletion of the beds is published

  Scenario: Beds assigned to a group
    Given the application is running
    And beds have been created in the system
    And beds are assigned to a group
    And a request to delete beds
    And valid authentication credentials are being included
    When the request to batch delete beds is made
    Then the user is told the request was successful
    And the requested beds are deleted
    And the deletion of the beds is published
    And the bed group is not deleted

  Scenario: Empty payload
    Given the application is running
    And beds have been created in the system
    And a request to delete beds
    But the list of bed to delete is empty
    And valid authentication credentials are being included
    When the request to batch delete beds is made
    Then the user is told there payload is invalid
    And no beds are deleted
    And the deletion of the beds is not published

  Scenario: Batch Delete Beds - Beds doesn't exist
    Given the application is running
    And beds have been created in the system
    And a request to delete beds
    And valid authentication credentials are being included
    But the beds to delete does not exists
    When the request to batch delete beds is made
    Then the user is told the request was successful
    And no beds are deleted
    And the deletion of the beds is not published

  Scenario: Batch Delete Beds - Unauthorized
    Given the application is running
    And beds have been created in the system
    And a request to delete beds
    And invalid authentication credentials are being included
    When the request to batch delete beds is made
    Then the user is told the request was unauthorized

  Scenario: Batch Delete Beds - Credentials not provided
    Given the application is running
    And beds have been created in the system
    And a request to delete beds
    When the request to batch delete beds is made
    Then the user is told the request was forbidden
