Feature: Get Audit Trail

  Scenario: Get audit trail for an entity
    Given the application is running
    And a request to get audit trail for entity with id `entity_id`
    And valid authentication credentials are being included
    And some audit trails exist
    When the request for audit trails is made
    Then the user is told the request was successful
    And the list of all audit events are returned

  Scenario: Get audit trail for an entity
    Given the application is running
    And a request to get audit trail for entity with id `entity_id`
    And valid authentication credentials are being included
    And multiple audit trails exist
    When the request for audit trails is made
    Then the user is told the request was successful
    And the list of all audit events are returned
    And the list of events is sorted

  Scenario: Get audit trail for an entity - No events
    Given the application is running
    And a request to get audit trail for entity with id `no-events-recorded`
    And valid authentication credentials are being included
    When the request for audit trails is made
    Then the user is told the requested resource was not found

  Scenario: Credentials not provided
    Given the application is running
    And a request to get audit trail for entity with id `entity_id`
    When the request for audit trails is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to get audit trail for entity with id `entity_id`
    And invalid authentication credentials are being included
    When the request for audit trails is made
    Then the user is told the request was unauthorized
