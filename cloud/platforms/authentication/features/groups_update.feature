Feature: Group management

  Scenario: Update User Group - Happy Path
    Given the app is running
    And a user group exists
    And a valid admin user exists
    And the user is already authenticated
    And a request to update a user group
    When the logged in user updates the created user group
    Then the request is successful
    And the user group is updated
    And the group updated event is logged

# Scenario: Create User Group - Duplicate name
# Given the app is running
# And a valid admin user exists
# And the user is already authenticated
# And a request to create a user group
# But the group name is already taken
# When the logged in user creates a new user group
# Then the request fails
