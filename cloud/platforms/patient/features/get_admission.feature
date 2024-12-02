Feature: Get device admission

  Scenario: Get device admission successfully
    Given the application is running
    And a device with an encounter assigned exists
    And a request to get the admission of the device
    And valid authentication credentials are being included
    When the request is made to get the admission
    Then the user is told the request was successful
    And the admission is returned

  Scenario: Get empty device admission
    Given the application is running
    And a device without any encounter assigned exists
    And a request to get the admission of the device
    And valid authentication credentials are being included
    When the request is made to get the admission
    Then the user is told the request was successful
    And the empty admission is returned
