Feature: Batch Create or Update Configs

  Scenario: Batch create or update configs
    Given the application is running
    And a request to batch create or update configs
    And the request includes valid authentication credentials
    And the configs can be created or updated
    And payload contains valid password
    When the request is made to batch create or update some configs
    Then the user is told the request was successful with no content

  Scenario: Batch create or update configs: Unauthorized user
    Given the application is running
    And a request to batch create or update configs
    And the request includes valid authentication credentials
    And the configs can be created or updated
    And payload contains invalid password
    When the request is made to batch create or update some configs
    Then the user is told the request was unauthorized

  Scenario Outline: Batch create or update configs: Invalid params
    Given the application is running
    And a request to batch create or update configs with `<field_name>` `<field_value>`
    And the request includes valid authentication credentials
    And the configs can be created or updated
    And payload contains valid password
    When the request is made to batch create or update some configs
    Then the user is told the request was invalid

    Examples:
      | field_name                   | field_value       |
      | MLLP_PORT                    | 65536             |
      | MLLP_EXPORT_INTERVAL_MINUTES | 0                 |
      | MLLP_EXPORT_INTERVAL_MINUTES | 101               |
      | MLLP_HOST                    | http://localhost  |
      | MLLP_HOST                    | https://localhost |

  Scenario: Batch create or update configs invalid auth
    Given the application is running
    And a request to batch create or update configs
    And the request includes invalid authentication credentials
    And the configs can be created or updated
    When the request is made to batch create or update some configs
    Then the user is told the request was unauthorized

  Scenario: Batch create or update configs missing auth
    Given the application is running
    And a request to batch create or update configs
    And the configs can be created or updated
    When the request is made to batch create or update some configs
    Then the user is told the request was forbidden
