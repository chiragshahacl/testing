Feature: Delete Patient

  Scenario: Delete Patient by ID, patient exists
    Given the application is running
    And a request to delete patient by id
    And valid authentication credentials are being included
    And several patients exist, including patient to be deleted
    When the request is made to delete patient by id
    Then the user is told the request was successful
    And the deleted patient no longer exists
    And the delete patient event is published

  Scenario: Delete Patient by ID, patient doesn't exist
    Given the application is running
    And a request to delete patient by id
    And valid authentication credentials are being included
    And several patients exist, not including ID to be deleted
    When the request is made to delete patient by id
    Then the user is told the request was successful
    And no patients were deleted

  Scenario: Delete Patient with alerts assigned
    Given the application is running
    And a request to delete patient by id
    And valid authentication credentials are being included
    And several patients exist, including patient to be deleted
    And physiological alerts have been triggered for the patient
    When the request is made to delete patient by id
    Then the user is told the request was successful
    And the deleted patient no longer exists
    And the delete patient event is published

  Scenario: Delete Patient with observations assigned
    Given the application is running
    And a request to delete patient by id
    And valid authentication credentials are being included
    And several patients exist, including patient to be deleted
    And the patient has observations assigned
    When the request is made to delete patient by id
    Then the user is told the request was successful
    And the deleted patient no longer exists
    And the delete patient event is published
