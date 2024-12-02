Feature: Group management

  Scenario: Update User Password - Happy Path
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to update a the user password
    When the logged in user updates the user password
    Then the request is successful
    And the user password is updated
    And the user updated event is logged

  Scenario: Update User Password - Empty new password
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to update a the user password
    But the new password is empty
    When the logged in user updates the user password
    Then the request fails
    And the user password is not updated

  Scenario: Update User Password - Empty current password
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to update a the user password
    But the current password is empty
    When the logged in user updates the user password
    Then the request fails
    And the user password is not updated

  Scenario: Update User Password - Invalid current password
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to update a the user password
    But the current password is incorrect
    When the logged in user updates the user password
    Then the request fails
    And the user password is not updated

  Scenario: Update User Password - Account locked
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to update a the user password
    But the user account is locked
    When the logged in user updates the user password
    Then the request fails
    And the user password is not updated

  Scenario: Update User Password - Too short password
    Given the app is running
    And a valid admin user exists
    And the user is already authenticated
    And a request to update a the user password
    But the new password is too short
    When the logged in user updates the user password
    Then the request fails
    And the user password is not updated
