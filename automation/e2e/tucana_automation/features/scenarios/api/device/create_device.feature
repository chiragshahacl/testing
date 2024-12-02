@API @DEVICE @SMOKE @SR-7.5.3
Feature: [API] Create a Device

  Background:
    Given the user credentials are valid

  Scenario: Create a new device
    Given the Tucana application is running
    And A request to create a new device through Tucana's API
    And authentication credentials are being included
    When the request is made to create a device
    Then the user is told the request to create a new device was successful
    When the user wants to get the list of devices
    Then the user is told the request to get the list of devices was successful
    And the device list is received to verify the created device
    And The device is removed to keep the application clean

  Scenario: Create a new device - Authentication not provided
    Given the Tucana application is running
    And A request to create a new device through Tucana's API
    And authentication credentials are not being included
    When the request is made to create a device
    Then the user is told the request was forbidden

  Scenario: Create a new device - Invalid credentials
    Given the Tucana application is running
    And A request to create a new device through Tucana's API
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to create a device
    Then the user is told the request was unauthorized
