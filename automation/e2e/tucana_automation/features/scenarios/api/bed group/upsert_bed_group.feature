@API @BED_GROUP @SMOKE @SR-7.5.3
Feature: [API] Upsert Bed Group

  Background:
    Given the user credentials are valid

  Scenario: Create a new bed group using upsert endpoint
    Given the Tucana application is running
    And A request to create a new bed group through upsert endpoint
    And authentication credentials are being included
    When the request is made to create a bed group through upsert endpoint
    Then the user is told the request to create a new bed group through upsert endpoint was successful
    When the user wants to get the list of the bed groups
    Then the user is told the request to get the list of the bed group was successful
    And the user verifies that all the bed group information is correct
    And The bed group is removed to keep the application clean

  Scenario: Update a bed group using upsert endpoint
    Given the Tucana application is running
    And the bed group to update exists
    And A request to update a bed group through upsert endpoint
    And authentication credentials are being included
    When the request is made to update a bed group through upsert endpoint
    Then the user is told the request to update a bed group through upsert endpoint was successful
    When the user wants to get the list of the bed groups
    Then the user is told the request to get the list of the bed group was successful
    And the user verifies that all the bed group information is correct
    And The bed group is removed to keep the application clean


  Scenario: Update a bed group - Authentication not provided
    Given the Tucana application is running
    And A request to create a new bed group through upsert endpoint
    And authentication credentials are not being included
    When the request is made to update a bed group through upsert endpoint
    Then the user is told the request was forbidden

  Scenario: Update a bed group - Invalid credentials
    Given the Tucana application is running
    And A request to create a new bed group through upsert endpoint
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to update a bed group through upsert endpoint
    Then the user is told the request was unauthorized