@API @DEVICE @SR-7.5.3
Feature: [API] Assign Bed to a Device

  Background:
    Given the user credentials are valid

  Scenario: Assign bed to a device
    Given the Tucana application is running
    And authentication credentials are being included
    And the device exists
    And the bed exists
    And A request to assign bed to a device through Tucana's API
    When the request is made to assign bed to a device
    Then the user is told the request to assign bed to a device was successful
    When the user wants to get the list of devices filtered by bed
    Then the user is told the request to get the list of devices was successful
    And the device list filtered by bed is received to verify the created device
    And The device is removed to keep the application clean
    And The bed is removed to keep the application clean

  Scenario: Assign bed to a device - Authentication not provided
    Given the Tucana application is running
    And the device and the bed exist
    And A request to assign bed to a device through Tucana's API
    And authentication credentials are not being included
    When the request is made to assign bed to a device
    Then the user is told the request was forbidden


  Scenario: Assign bed to a device - Invalid credentials
    Given the Tucana application is running
    And the device and the bed exist
    And A request to assign bed to a device through Tucana's API
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to assign bed to a device
    Then the user is told the request was unauthorized
