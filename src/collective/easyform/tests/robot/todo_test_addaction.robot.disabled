*** Settings ***

Resource  keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Add action to form
    Given a site owner
    And a easyform  EasyForm

    ${dot1} =  Add dot  contentview-actions  1
    ${note1} =  Add note
    ...    contentview-actions
    ...    At first, click 'Actions' to open actions edit page
    ...    width=380  position=top
    Capture and crop page screenshot  click-actions-contentview.png
    ...    content-views  ${dot1}  ${note1}
    Remove elements  ${dot1}  ${note1}
    Clicked Actions
    ${dot1} =  Add dot  css=#add-field  2
    ${note1} =  Add note
    ...    css=#add-field
    ...    Then click at 'Add new action…' button
    ...    width=330  position=left
    Capture and crop page screenshot  click-add-new-action.png
    ...    css=#add-field  ${dot1}  ${note1}
    Remove elements  ${dot1}  ${note1}
    Click Overlay Button  Add new action…
    ${dot1} =  Add dot  form-widgets-title  3
    ${note1} =  Add note  form-widgets-title  Set action title  position=right
    ${dot2} =  Add dot  form-widgets-__name__  4
    ${note2} =  Add note  form-widgets-__name__  And name  position=right
    ${dot3} =  Add dot  form-widgets-description  5
    ${note3} =  Add note  form-widgets-description  And description  position=right
    ${dot4} =  Add dot  form-widgets-factory  6
    ${note4} =  Add note  form-widgets-factory  And type  position=right
    Capture and crop page screenshot  add-new-action-overlay.png  css=div.plone-modal
    ...    ${dot1}  ${note1}  ${dot2}  ${note2}
    ...    ${dot3}  ${note3}  ${dot4}  ${note4}
    Remove elements
    ...    ${dot1}  ${note1}  ${dot2}  ${note2}
    ...    ${dot3}  ${note3}  ${dot4}  ${note4}
    Input text for sure  form-widgets-title  Action Title
    Focus  form-widgets-__name__
    Wait until keyword succeeds  10  1  Textfield Value Should Be  form-widgets-__name__  action_title
    Click button  Add
    Wait until page contains element  xpath=//div[@data-field_id="action_title"]
    Assign Id To Element  xpath=//div[@data-field_id="action_title"]  action_title
    Capture and crop page screenshot  added-new-action.png  action_title
