Feature: Create User

  Scenario Outline: Happy Path
    Given the application is running
    And a request to create an user with roles `<role_name>`
    And the user will have username `jack@sibel.com`
    And the user will have password `techieJack`
    And the requester has role `admin`
    And valid credentials are provided
    When the request to create an user is made
    Then the user is told the request was successful
    And the user is created

    Examples:
      | role_name    |
      | admin        |
      | clinical     |
      | tech         |
      | organization |
      | tech, admin  |

  Scenario: Unauthorized
    Given the application is running
    And a request to create an user with roles `admin`
    And the user will have username `jack@sibel.com`
    And the user will have password `techieJack`
    And the requester has role `clinical`
    And valid credentials are provided
    When the request to create an user is made
    Then the user is told the request was forbidden
    And the user is not created
