Feature: Create or Update Device

  Scenario: Create or Update Device (create path)
    Given the application is running
    And a request to create or update a device (create)
    And the request includes valid authentication credentials
    And several devices exist
    And the device can be created
    When the request is made to create or update a device
    Then the user is told the request was successful with no content

  Scenario: Create or Update Device (update path)
    Given the application is running
    And a request to create or update a device (update)
    And the request includes valid authentication credentials
    And several devices exist
    And the device can be updated
    When the request is made to create or update a device
    Then the user is told the request was successful with no content

  Scenario: Invalid Auth
    Given the application is running
    And a request to create or update a device (create)
    And the request includes invalid authentication credentials
    When the request is made to create or update a device
    Then the user is told the request was unauthorized

  Scenario: Missing Auth
    Given the application is running
    And a request to create or update a device (create)
    When the request is made to create or update a device
    Then the user is told the request was forbidden
