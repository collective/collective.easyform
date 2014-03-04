*** Settings ***

Resource  plone/app/robotframework/server.robot
Resource  plone/app/robotframework/annotate.robot
Resource  plone/app/robotframework/keywords.robot

Suite Setup  Setup
Suite Teardown  Teardown

*** Keywords ***

Setup
    Setup Plone site  collective.easyform.tests.base.ACCEPTANCE_TESTING
    Import library  Remote  ${PLONE_URL}/RobotRemote

Teardown
    Teardown Plone Site

*** Test Cases ***

Add easyform

    Enable autologin as  Manager
    Set autologin username  Admin
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
    Select from list  css=.formTabs  Settings
    Capture and crop page screenshot  new-easyform-settings.png  content
    Select from list  css=.formTabs  Categorization
    Capture and crop page screenshot  new-easyform-categorization.png  content
    Select from list  css=.formTabs  Dates
    Capture and crop page screenshot  new-easyform-dates.png  content
    Select from list  css=.formTabs  Ownership
    Capture and crop page screenshot  new-easyform-ownership.png  content
    Click Button  Save
    Capture and crop page screenshot  created-easyform.png  css=.documentEditable
