@API @DEVICE @SMOKE @SR-7.5.3
Feature: [API] List Devices

  Background:
    Given the user credentials are valid

  Scenario: Get device list
    Given The tucana application is running
    And the device exists
    When the user wants to get the list of devices
    Then the user is told the request to get the list of devices was successful
    And devices list is received
    And The device is removed to keep the application clean

  Scenario: Get device list - Authentication not provided
    Given the Tucana application is running
    And authentication credentials are not being included
    When the user wants to get the list of devices
    Then the user is told the request was forbidden

  Scenario: Get device list - Invalid credentials
    Given the Tucana application is running
    And authentication credentials are being included
    And the credentials are not valid
    When the user wants to get the list of devices
    Then the user is told the request was unauthorized
