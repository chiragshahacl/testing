Feature: Automatic removal of old entries in InternalAudit table

  Scenario: Automatic removal of old entries in InternalAudit table
    Given The MAX_REGISTRY_IN_DB setting is set to 5
    And There are entries in InternalAudit table with the following dates
      """
      - 2022-01-01 00:00:00
      - 2022-01-02 00:00:00
      - 2022-01-03 00:00:00
      - 2022-01-04 00:00:00
      - 2022-01-05 00:00:00
      - 2022-01-06 00:00:00
      - 2022-01-07 00:00:00
      """
    When Remove old registry process is called
    Then The only remaining entries in the InternalAudit tables have the following dates
      """
      - 2022-01-03 00:00:00
      - 2022-01-04 00:00:00
      - 2022-01-05 00:00:00
      - 2022-01-06 00:00:00
      - 2022-01-07 00:00:00
      """
