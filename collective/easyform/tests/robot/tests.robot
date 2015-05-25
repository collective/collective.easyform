*** Settings ***

Resource  plone/app/robotframework/annotate.robot
Resource  plone/app/robotframework/keywords.robot
Resource  keywords.robot

Suite Setup  Setup
Suite Teardown  Teardown

*** Test Cases ***

Add easyform as Manager

    Enable autologin as  Manager
    Set autologin username  Manager
    Go to  ${PLONE_URL}

    Click link  css=#plone-contentmenu-factories dt a
    Element should be visible  css=#plone-contentmenu-factories dd.actionMenuContent
    ${dot1} =  Add dot  css=#plone-contentmenu-factories dt a  1
    ${note1} =  Add note
    ...    css=#plone-contentmenu-factories
    ...    At first, click Add new… to open the menu
    ...    width=180  position=left
    ${dot2} =  Add dot
    ...    css=#plone-contentmenu-factories dd.actionMenuContent a#easyform.contenttype-easyform  2
    ${note2} =  Add note
    ...    css=#plone-contentmenu-factories dd.actionMenuContent a#easyform.contenttype-easyform
    ...    Then click on 'EasyForm' to add new content
    ...    width=180  position=bottom
    Align elements horizontally  ${dot2}  ${dot1}
    Capture and crop page screenshot  add-new-menu.png
    ...    contentActionMenus
    ...    css=#plone-contentmenu-factories dd.actionMenuContent
    ...    ${dot1}  ${note1}  ${dot2}  ${note2}
    Remove elements  ${dot1}  ${note1}  ${dot2}  ${note2}
    Click link  css=#plone-contentmenu-factories a.contenttype-easyform
    ${dot1} =  Add dot  form-widgets-IDublinCore-title  3
    ${note1} =  Add note  form-widgets-IDublinCore-title  Set form title  width=180  position=right
    ${dot2} =  Add dot  form-widgets-IDublinCore-description  4
    ${note2} =  Add note  form-widgets-IDublinCore-description  And description  width=180  position=right
    Capture and crop page screenshot  new-easyform-default.png  content
    Remove elements  ${dot1}  ${note1}  ${dot2}  ${note2}
    Input text  form-widgets-IDublinCore-title  EasyForm
    Select from list  css=.formTabs  Overrides
    Capture and crop page screenshot  new-easyform-overrides.png  content
    Select from list  css=.formTabs  Thanks Page
    Capture and crop page screenshot  new-easyform-thankspage.png  content
    Click Button  Save
    Capture and crop page screenshot  created-easyform.png  css=.documentEditable
    When Click Link  Fields
    Capture and crop page screenshot  created-easyform-fields.png  css=#content
    When Click Link  Actions
    Capture and crop page screenshot  created-easyform-actions.png  css=#content

Add easyform as Contributor

    Enable autologin as  Contributor
    Set autologin username  Contributor
    Go to  ${PLONE_URL}

    Click link  css=#plone-contentmenu-factories dt a
    Click link  css=#plone-contentmenu-factories a.contenttype-easyform
    ${dot1} =  Add dot  form-widgets-IDublinCore-title  3
    ${note1} =  Add note  form-widgets-IDublinCore-title  Set form title  width=180  position=right
    ${dot2} =  Add dot  form-widgets-IDublinCore-description  4
    ${note2} =  Add note  form-widgets-IDublinCore-description  And description  width=180  position=right
    Capture and crop page screenshot  new-easyform-default-contributor.png  content
    Remove elements  ${dot1}  ${note1}  ${dot2}  ${note2}
    Input text  form-widgets-IDublinCore-title  EasyForm
    Click link  Thanks Page
    Capture and crop page screenshot  new-easyform-thankspage-contributor.png  content
    Click Button  Save

Simple EasyForm
    Given a site owner
    And a easyform  EasyForm
    When Click Link  Fields
    When Click Link  Actions
    When Click Link  View
    And Input text  name=form.widgets.replyto  test@example.com
    And Input text  name=form.widgets.topic  test subject
    And Input text  name=form.widgets.comments  test comments
    And Click Button  Submit
    Then Page should contain  test@example.com
    And Page should contain  test subject
    And Page should contain  test comments

Add a choice field with vocabulary values
    Given a site owner
    And a easyform  EasyForm
    When Click Link  Fields
    And add field  Hobbies  hobbies  Multiple Choice
    Then Open field settings  hobbies
    And Input text  form-widgets-values  Chess\nSoccer\nBaseball\nVideo games
    When Click Button  Save
    Then Wait until page contains element  form-widgets-hobbies-3
    When Click Link  View
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
    Click link  Fields
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
    Capture and crop page screenshot  add-new-field-overlay.png  css=div.overlay
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


Add fieldset to form
    Given a site owner
    And a easyform  EasyForm
    When Click Link  Fields

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
    Capture and crop page screenshot  add-new-fieldset-overlay.png  css=div.overlay
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
    Click link  Actions
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
    Capture and crop page screenshot  add-new-action-overlay.png  css=div.overlay
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


Edit xml models
    Given a site owner
    And a easyform  EasyForm

    When Click link  Fields
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

    When Click link  Actions
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
