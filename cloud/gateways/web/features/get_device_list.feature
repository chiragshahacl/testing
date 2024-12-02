Feature: Get device list

  Scenario: Happy Path
    Given the application is running
    And devices are found
    And a request to get a device list
    And with a valid auth credentials
    When the request is made to get a device list
    Then the user is told the request was successful
    And a device list is returned

  Scenario: Filter by all params
    Given the application is running
    And devices are found
    And a request to get a device list
    And filtering by all the params
    And with a valid auth credentials
    When the request is made to get a device list
    Then the user is told the request was successful
    And a device list is returned

  Scenario Outline: Filter by params
    Given the application is running
    And devices are found
    And a request to get a device list
    And bed group has beds
    And filtering by `<query_param>` `<value>`
    And with a valid auth credentials
    When the request is made to get a device list
    Then the user is told the request was successful
    And a device list is returned

    Examples:
      | query_param | value                                |
      | gateway     | 8adea8ff-320f-48d3-8d3d-0d5e7007994c |
      | isGateway   | True                                 |
      | isGateway   | False                                |
      | deviceCode  | device-code-1                        |
      | deviceCode  | device-code-2                        |
      | deviceCode  | device-code-3                        |
      | bedGroup    | 0ee875b1-7722-4fe4-b26e-889fa5b257ec |

  Scenario: invalid auth
    Given the application is running
    And devices are found
    And a request to get a device list
    But with invalid auth credentials
    When the request is made to get a device list
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And devices are found
    And a request to get a device list
    When the request is made to get a device list
    Then the user is told the request was forbidden
