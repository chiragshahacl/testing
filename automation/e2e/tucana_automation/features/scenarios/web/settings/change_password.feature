@WEB @AUTHENTICATION @SMOKE
Feature: [WEB] Change Password

Background:
   Given Tom goes to "Tucana" Web APP login page
   And Tom logs in with his credentials
   Then Tom sees the dashboard

  @SR-1.1.4 @SR-1.6.10
  Scenario: Change Password - validate the minimum size for a password
    Given Tom wants to update the password
    Then Tom sees the popup message requiring the admin password
    And Tom fills the password information with is admin password
    And Tom clicks on the confirm button
    When Tom sets the new password "Xc4"
    And Tom re-enter the new password "Xc4"
    Then the application notifies him the password does not meet criteria

  @SR-1.1.22 @SR-1.1.23 @SR-1.6.10
  Scenario: Change Password - validate the re-entry of the new password with another password
    Given Tom wants to update the password
    Then Tom sees the popup message requiring the admin password
    And Tom fills the password information with is admin password
    And Tom clicks on the confirm button
    When Tom sets the new password "AcBt34TY13"
    And Tom sees the continue button in change password is "disabled"
    And Tom re-enter the new password "TvBgt67HK9"
    And Tom sees the continue button in change password is "disabled"
    Then the application notifies him the password does not match previous entry


  @SR-1.1.24 @SR-1.6.10
  Scenario: Change Password - validate incorrect admin password
    Given Tom wants to update the password
    Then Tom sees the popup message requiring the admin password
    And Tom fills the password information with an incorrect admin password
    And Tom clicks on the confirm button
    And the application notifies him the password was incorrect
    
  
    
    
    

    



