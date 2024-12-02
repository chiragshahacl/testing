Feature: Get System Settings

  Scenario: Happy Path
    Given the application is running
    And the current system settings are being requested
    And system settings exists with values
      | setting_name                       | setting_value |
      | patient_vitals_retention_period_ms | 3600000       |
    And valid credentials are provided
    When the users requests the current system settings
    Then the user is told the request was successful
    And the current system settings are returned

  Scenario: Invalid credentials
    Given the application is running
    And the current system settings are being requested
    And system settings exists with values
      | setting_name                       | setting_value |
      | patient_vitals_retention_period_ms | 3600000       |
    And invalid credentials are provided
    When the users requests the current system settings
    Then the user is told the request was unauthorized
