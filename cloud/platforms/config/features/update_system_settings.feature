Feature: Updated System Settings

  Scenario: Happy Path
    Given the application is running
    And a valid request to update the system settings
      | setting_name                       | setting_value |
      | patient_vitals_retention_period_ms | 3600000       |
    And valid credentials are provided
    When the request to update system settings is made
    Then the user is told the request was successful
    And the system settings are updated

  Scenario: Invalid settings
    Given the application is running
    And a valid request to update the system settings
      | setting_name                       | setting_value |
      | patient_vitals_retention_period_ms | 1000          |
    And valid credentials are provided
    When the request to update system settings is made
    Then the user is told the request payload was not valid

  Scenario: Invalid credentials
    Given the application is running
    And a valid request to update the system settings
      | setting_name                       | setting_value |
      | patient_vitals_retention_period_ms | 3600000       |
    And invalid credentials are provided
    When the request to update system settings is made
    Then the user is told the request was unauthorized
