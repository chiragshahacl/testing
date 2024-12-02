@API @BED @SMOKE @SR-7.5.3
Feature: [API] Upsert Bed

  Background:
    Given the user credentials are valid

  Scenario: Create a new bed using upsert endpoint
    Given the Tucana application is running
    And A request to create a new bed through upsert endpoint
    And authentication credentials are being included
    When the request is made to create a bed through upsert endpoint
    Then the user is told the request to create a new bed through upsert endpoint was successful
    When the user wants to get the list of beds
    Then the user is told the request to get the list of beds was successful
    And the user verifies that all the bed information is correct
    And The bed is removed to keep the application clean

  Scenario: Update a bed using upsert endpoint
    Given the Tucana application is running
    And the bed to update exists
    And A request to update a bed through upsert endpoint
    And authentication credentials are being included
    When the request is made to update a bed through upsert endpoint
    Then the user is told the request to update a bed through upsert endpoint was successful
    When the user wants to get the list of beds
    Then the user is told the request to get the list of beds was successful
    And the user verifies that all the bed information is correct
    And The bed is removed to keep the application clean

  Scenario: Update a bed - Authentication not provided
    Given the Tucana application is running
    And A request to create a new bed through upsert endpoint
    And authentication credentials are not being included
    When the request is made to update a bed through upsert endpoint
    Then the user is told the request was forbidden

  Scenario: Update a bed - Invalid credentials
    Given the Tucana application is running
    And A request to create a new bed through upsert endpoint
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to update a bed through upsert endpoint
    Then the user is told the request was unauthorized