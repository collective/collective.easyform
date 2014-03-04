*** Settings ***

Resource  plone/app/robotframework/server.robot
Resource  plone/app/robotframework/keywords.robot

Suite Setup  Setup
Suite Teardown  Teardown

*** Test Cases ***

Simple EasyForm
    a site owner
    a easyform  EasyForm
    Click Link  Fields
    Click Link  Actions
    Click Link  View
    Input text  name=form.widgets.replyto  test@example.com
    Input text  name=form.widgets.topic  test subject
    Input text  name=form.widgets.comments  test comments
    Click Button  Submit
    Page should contain  test@example.com
    Page should contain  test subject
    Page should contain  test comments

Add a choice field with vocabulary values
    a site owner
    a easyform  EasyForm
    Click Link  Fields
    Add field  Hobbies  hobbies  Multiple Choice
    Open field settings  hobbies
    Input text  form-widgets-values  Chess\nSoccer\nBaseball\nVideo games
    Click Button  Save
    Wait until page contains element  form-widgets-hobbies-3
    Click Link  View
    Wait until page contains element  form-widgets-hobbies-3


*** Keywords ***

Setup
    Setup Plone site  collective.easyform.tests.base.ACCEPTANCE_TESTING
    Import library  Remote  ${PLONE_URL}/RobotRemote

Teardown
    Teardown Plone Site

a easyform
    [Arguments]  ${title}
    Go to  ${PLONE_URL}/++add++EasyForm
    Input text  name=form.widgets.IDublinCore.title  ${title}
    Click Button  Save

a site owner
    Enable autologin as  Manager
    Set autologin username  Admin

Add field
    [Arguments]    ${field_title}    ${field_id}    ${field_type}
    [Documentation]    Add field in current easyform

    Click Overlay Button  Add new field…
    Input text for sure  form-widgets-title  ${field_title}
    Focus  form-widgets-__name__
    Wait until keyword succeeds  10  1  Textfield Value Should Be  form-widgets-__name__  ${field_id}
    Select from list  form-widgets-factory  ${field_type}
    Click button  Add
    Wait overlay is closed

Open field settings
    [Arguments]    ${field_id}
    Click Overlay Link  xpath=//div[@data-field_id='${field_id}']//a[@class='fieldSettings link-overlay']

Wait overlay is closed
    Wait until keyword succeeds  60  1  Page should not contain element  css=div.overlay
