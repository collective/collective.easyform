*** Settings ***

Resource  keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Simple EasyForm
    Given a site owner
    And a easyform  EasyForm
    And Input text  name=form.widgets.replyto  test@example.com
    And Input text  name=form.widgets.topic  test subject
    And Input text  name=form.widgets.comments  test comments
    And Click Button  Submit
    Then Page should contain  test@example.com
    And Page should contain  test subject
    And Page should contain  test comments
