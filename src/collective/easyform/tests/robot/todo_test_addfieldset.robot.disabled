*** Settings ***

Resource  keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Add fieldset to form
    Given a site owner
    And a easyform  EasyForm
    When Clicked Fields

    ${dot1} =  Add dot  css=#add-fieldset  2
    ${note1} =  Add note
    ...    css=#add-fieldset
    ...    Then click at 'Add new fieldset…' button
    ...    width=330  position=left
    Capture and crop page screenshot  click-add-new-fieldset.png
    ...    css=#add-fieldset  ${dot1}  ${note1}
    Remove elements  ${dot1}  ${note1}
    Click Overlay Button  Add new fieldset…
    ${dot1} =  Add dot  form-widgets-label  3
    ${note1} =  Add note  form-widgets-label  Set fieldset label  position=right
    ${dot2} =  Add dot  form-widgets-__name__  4
    ${note2} =  Add note  form-widgets-__name__  And name  position=right
    Capture and crop page screenshot  add-new-fieldset-overlay.png  css=div.plone-modal
    ...  ${dot1}  ${note1}  ${dot2}  ${note2}
    Remove elements
    ...  ${dot1}  ${note1}  ${dot2}  ${note2}
    Input text for sure  form-widgets-label  Fieldset Label
    Focus  form-widgets-__name__
    Wait until keyword succeeds  10  1
    ...  Textfield Value Should Be  form-widgets-__name__  fieldset_label
    Click button  Add
    Wait until page contains element  css=ul.formTabs li.formTab.lastFormTab
    Capture and crop page screenshot  added-new-fieldset.png  css=ul.formTabs
