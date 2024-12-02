Feature: Get all beds

  Scenario: Get all beds
    Given the application is running
    And a request to get all beds
    And valid authentication credentials are being included
    And beds exist
    When the request to get all beds is made
    Then the user is told the request was successful
    And all beds are returned

  Scenario Outline: Get all beds
    Given the application is running
    And a request to get all beds
    And valid authentication credentials are being included
    And beds exist
    And the beds have patients assigned with status `<encounter_status>`
    When the request to get all beds is made
    Then the user is told the request was successful
    And all beds are returned

    Examples:
      | encounter_status |
      | planned          |
      | in-progress      |
      | completed        |
      | cancelled        |

  Scenario: Credentials not provided
    Given the application is running
    And a request to get all beds
    When the request to get all beds is made
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to get all beds
    And invalid authentication credentials are being included
    When the request to get all beds is made
    Then the user is told the request was unauthorized
