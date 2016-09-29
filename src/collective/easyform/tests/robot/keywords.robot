*** Settings ***

Resource  plone/app/robotframework/annotate.robot
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/server.robot

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
    Click Overlay Link  xpath=//div[@data-field_id='${field_id}']//a[contains(@class,'fieldSettings')]

Wait overlay is closed
    Wait until keyword succeeds  60  1  Page should not contain element  css=div.overlay
