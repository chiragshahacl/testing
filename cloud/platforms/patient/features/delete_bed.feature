Feature: Delete Bed

  Scenario: Delete Bed, group doesn't exist (Happy Path)
    Given the application is running
    And a request to delete bed by id
    And valid authentication credentials are being included
    And no group is assigned to the bed
    When the request is made to delete bed by id
    Then the user is told the request was successful
    And the deleted bed no longer exists
    And the delete bed event is published

  Scenario: Delete Bed, group exists
    Given the application is running
    And a request to delete bed by id
    And valid authentication credentials are being included
    And a group is assigned to the bed
    When the request is made to delete bed by id
    Then the user is told the bed is assigned to the group
    And no bed is deleted

  Scenario: Delete Bed, group exists
    Given the application is running
    And a request to delete bed by id
    And valid authentication credentials are being included
    And a bed does not exist
    When the request is made to delete bed by id
    Then the user is told the bed was not found
