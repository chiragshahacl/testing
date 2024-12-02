@API @AUDIT_TRAIL @SMOKE @SR-7.5.3
Feature: [API] Get Bed Audit Trail

  Background:
    Given the user credentials are valid
    And the tucana application is running
    And A request to create a new bed through Tucana's API
    When the request is made to create a bed
    Then the user is told the request to create was successful
    And the bed is created

  @SR-1.5.2
  Scenario: Get bed audit trail
    When the user wants to get the audit trail for the recently created bed
    Then the user is told the get audit trail request was successful
    And the user verifies that all the bed audit trail information is correct
    And The bed is removed to keep the application clean