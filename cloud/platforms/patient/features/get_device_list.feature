Feature: Get Device list

  Scenario: Get Device list
    Given the application is running
    And a request to get a device list by gateway and location
    And valid authentication credentials are being included
    And the bed exists
    And a device exists with gateway and location ID
    When the request is made to get a device list
    Then the user is told the request was successful
    And the devices are returned

  Scenario: Get Device list with multiple location filter
    Given the application is running
    And a request to get a device list by multiple locations
    And valid authentication credentials are being included
    And the beds exist
    And several devices exist
    When the request is made to get a device list
    Then the user is told the request was successful
    And the devices associated with filtered locations are returned

  Scenario: Get Device list multiple exist
    Given the application is running
    And a request to get a device list by gateway and location
    And valid authentication credentials are being included
    And the bed exists
    And a patient monitor with several sensors exist
    When the request is made to get a device list
    Then the user is told the request was successful
    And sensors are returned

  Scenario: Get Device List without location query param
    Given the application is running
    And a request to get a device list by gateway_id
    And valid authentication credentials are being included
    And the bed exists
    And a patient monitor with several sensors exist
    When the request is made to get a device list
    Then the user is told the request was successful
    And sensors are returned

  Scenario: Get Device list with is_gateway flag is true
    Given the application is running
    And a request to get a device list by gateway and location and is_gateway
    And valid authentication credentials are being included
    And the bed exists
    And a patient monitor with several sensors exist
    When the request is made to get a device list
    Then the user is told the request was successful
    And only the monitor device is returned

  Scenario: Get Device list with only is_gateway flag
    Given the application is running
    And a request to get a device list by is_gateway
    And valid authentication credentials are being included
    And several gateways exist and a couple non-gateways
    When the request is made to get a device list
    Then the user is told the request was successful
    And all the gateways are returned

  Scenario: Get Device list with no query params (return everything)
    Given the application is running
    And a request to get a device list with no params
    And valid authentication credentials are being included
    And several gateways exist and a several non-gateways
    When the request is made to get a device list
    Then the user is told the request was successful
    And all the gateways and non-gateways are returned

  Scenario: Get Device list with all filters applied
    Given the application is running
    And a request to get a device list by device code only
    And valid authentication credentials are being included
    And a device exists with device code
    When the request is made to get a device list
    Then the user is told the request was successful
    And only specific types of devices are returned

  Scenario: Get Device list missing auth
    Given the application is running
    And a request to get a device list by gateway and location
    When the request is made to get a device list
    Then the user is told the request was forbidden

  Scenario: Get Device list invalid auth
    Given the application is running
    And a request to get a device list by gateway and location
    And invalid authentication credentials are being included
    When the request is made to get a device list
    Then the user is told the request was unauthorized
