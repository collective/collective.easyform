*** Settings ***

Resource  keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Add a choice field with vocabulary values
    Given a site owner
    And a easyform  EasyForm
    When Clicked Fields
    And add field  Hobbies  hobbies  Multiple Choice
    Then Open field settings  hobbies
    And Input text  form-widgets-values  Chess\nSoccer\nBaseball\nVideo games
    When Click Button  Save
    Then Wait until page contains element  form-widgets-hobbies-3

Add field to form
    Given a site owner
    And a easyform  EasyForm

    ${dot1} =  Add dot  contentview-fields  1
    ${note1} =  Add note
    ...    contentview-fields
    ...    At first, click 'Fields' to open fields edit page
    ...    width=360  position=top
    Capture and crop page screenshot  click-fields-contentview.png
    ...    content-views  ${dot1}  ${note1}
    Remove elements  ${dot1}  ${note1}
    Clicked Fields
    ${dot1} =  Add dot  css=#add-field  2
    ${note1} =  Add note
    ...    css=#add-field
    ...    Then click at 'Add new field…' button
    ...    width=320  position=left
    Capture and crop page screenshot  click-add-new-field.png
    ...    css=#add-field  ${dot1}  ${note1}
    Remove elements  ${dot1}  ${note1}
    Click Overlay Button  Add new field…
    ${dot1} =  Add dot  form-widgets-title  3
    ${note1} =  Add note  form-widgets-title  Set field title  position=right
    ${dot2} =  Add dot  form-widgets-__name__  4
    ${note2} =  Add note  form-widgets-__name__  And name  position=right
    ${dot3} =  Add dot  form-widgets-description  5
    ${note3} =  Add note  form-widgets-description  And description  position=right
    ${dot4} =  Add dot  form-widgets-factory  6
    ${note4} =  Add note  form-widgets-factory  And type  position=right
    Capture and crop page screenshot  add-new-field-overlay.png  css=div.plone-modal
    ...    ${dot1}  ${note1}  ${dot2}  ${note2}
    ...    ${dot3}  ${note3}  ${dot4}  ${note4}
    Remove elements
    ...    ${dot1}  ${note1}  ${dot2}  ${note2}
    ...    ${dot3}  ${note3}  ${dot4}  ${note4}
    Input text for sure  form-widgets-title  Field Title
    Focus  form-widgets-__name__
    Wait until keyword succeeds  10  1  Textfield Value Should Be  form-widgets-__name__  field_title
    Click button  Add
    Wait until page contains element  xpath=//div[@data-field_id="field_title"]
    Assign Id To Element  xpath=//div[@data-field_id="field_title"]  field_title
    Capture and crop page screenshot  added-new-field.png  field_title
