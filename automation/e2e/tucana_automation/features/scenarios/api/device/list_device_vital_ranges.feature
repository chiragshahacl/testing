@API @DEVICE @SMOKE @SR-7.5.3
Feature: [API] List Device Vital Ranges

  Background:
    Given the user credentials are valid

  Scenario: Get device vital ranges list
    Given The tucana application is running
    When the user wants to get the list of vital ranges of the devices
    Then the user is told the request to get the vital ranges list of devices was successful
    And vital ranges list is received to verify device ranges

  Scenario: Get device vital ranges list - Authentication not provided
    Given the Tucana application is running
    And authentication credentials are not being included
    When the user wants to get the list of vital ranges of the devices
    Then the user is told the request was forbidden

  Scenario: Get device vital ranges list - Invalid credentials
    Given the Tucana application is running
    And authentication credentials are being included
    And the credentials are not valid
    When the user wants to get the list of vital ranges of the devices
    Then the user is told the request was unauthorized
