*** Settings ***

Resource  keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Edit xml models
    Given a site owner
    And a easyform  EasyForm

    When Clicked Fields
    ${note1} =  Add note  form-buttons-modeleditor
    ...    Click 'Edit XML Fields Model' button to open edit xml fields model page
    ...    width=300  position=right
    Capture and crop page screenshot  edit-xml-fields-model-button.png  form-buttons-modeleditor  ${note1}
    Remove elements  ${note1}
    And Click button  Edit XML Fields Model
    When Execute JavaScript  ace.edit("modelEditor").setValue(ace.edit("modelEditor").getValue())
    Capture and crop page screenshot  edit-xml-fields-model-page.png  page-intro  rules-editor
    And Click button  Save
    Then Page should contain  Saved

    When Click link  Back to the schema editor

    When Clicked Actions
    ${note1} =  Add note  form-buttons-modeleditor
    ...    Click 'Edit XML Actions Model' button to open edit xml actions model page
    ...    width=310  position=right
    Capture and crop page screenshot  edit-xml-actions-model-button.png  form-buttons-modeleditor  ${note1}
    Remove elements  ${note1}
    And Click button  Edit XML Actions Model
    When Execute JavaScript  ace.edit("modelEditor").setValue(ace.edit("modelEditor").getValue())
    Capture and crop page screenshot  edit-xml-actions-model-page.png  page-intro  rules-editor
    And Click button  Save
    Then Page should contain  Saved
