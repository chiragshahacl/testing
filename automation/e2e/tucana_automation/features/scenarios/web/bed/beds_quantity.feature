@WEB @SMOKE
Feature: [WEB] List all beds available in the system

    @BED @SR-1.2.3
    Scenario: Get bed list and verify quantity and names inside web
        Given The tucana application is running
        When the user wants to get the list of beds
        Then the user is told the request to get the list of beds was successful
        And the beds list is received
        Then Tom goes to "Tucana" Web APP login page
        And Tom logs in with his credentials
        And Tom sees the dashboard
        When Tom clicks on "Bed Management" Option
        Then Tom sees the "Bed Management" Page
        And Tom clicks on the "Back to Step One" button
        Then Tom sees the Bed list quantity and names already obtained by API

