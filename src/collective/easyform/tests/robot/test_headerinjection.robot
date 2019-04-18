*** Settings ***

Resource  keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Add headerinjecation as Manager

    Given a logged-in manager
    And a easyform  EasyForm

    And Click Edit
    And Click Overrides
    And Input text for sure  css=#form-widgets-headerInjection  python:'<style type="text/css"> * { color: red !important; } </style>' + '<script>alert("hello world")</script>'
    When Click Button  Save
    ${message}=  Handle Alert
    Then Should Be equal  ${message}  hello world
    And Page Should Contain  color: red !important
    And Page Should Contain  hello world
