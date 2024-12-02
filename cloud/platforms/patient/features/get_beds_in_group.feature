Feature: Get beds in group

  Scenario: Happy Path
    Given the application is running
    And a request to get all beds in a group
    And valid authentication credentials are being included
    And the bed group exist
    And the bed group has `2` beds assigned
    And the beds have patients assigned
    When the request to get bed group beds is made
    Then the user is told the request was successful
    And the bed group beds are returned

  Scenario Outline: Bed Group with bed with encounter
    Given the application is running
    And a request to get all beds in a group
    And valid authentication credentials are being included
    And the bed group exist
    And the bed group has `2` beds assigned
    And the beds have patients assigned with status `<encounter_status>`
    When the request to get bed group beds is made
    Then the user is told the request was successful
    And the bed group beds are returned

    Examples:
      | encounter_status |
      | planned          |
      | in-progress      |
      | completed        |
      | cancelled        |
