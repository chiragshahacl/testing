Feature: Change Password

  Scenario: Valid passwords provided
    Given the application is running
    And a valid request to change password
    And the request includes valid authentication credentials
    And the provided passwords are correct
    When the request to change password is made
    Then the user is told the request was successful

  Scenario: Invalid password provided
    Given the application is running
    And a valid request to change password
    And the request includes valid authentication credentials
    And the provided passwords are not correct
    When the request to change password is made
    Then the user is told the request was unauthorized

  Scenario Outline: Missing field
    Given the application is running
    And a valid request to change password
    And the request includes valid authentication credentials
    And the field `<field_name>` is not provided
    When the request to change password is made
    Then the user is told the request was invalid

    Examples:
      | field_name |
      | new        |
      | current    |

  Scenario: Invalid authentication
    Given the application is running
    And a valid request to change password
    And the request includes invalid authentication credentials
    When the request to change password is made
    Then the user is told the request was unauthorized
