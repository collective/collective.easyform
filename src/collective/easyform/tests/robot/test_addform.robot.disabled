*** Settings ***

Resource  keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Add easyform as Manager

    Given a logged-in manager
    Go to  ${PLONE_URL}

    Click link  css=#plone-contentmenu-factories a
    Element should be visible  css=#plone-contentmenu-factories ul
    ${dot1} =  Add dot  css=#plone-contentmenu-factories a  1
    ${note1} =  Add note
    ...    css=#plone-contentmenu-factories
    ...    At first, click Add new… to open the menu
    ...    width=180  position=left
    ${dot2} =  Add dot
    ...    css=#plone-contentmenu-factories a#easyform.contenttype-easyform  2
    ${note2} =  Add note
    ...    css=#plone-contentmenu-factories a#easyform.contenttype-easyform
    ...    Then click on 'EasyForm' to add new content
    ...    width=180  position=bottom
    Align elements horizontally  ${dot2}  ${dot1}
    Capture and crop page screenshot  add-new-menu.png
    ...    css=#plone-contentmenu-factories
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
    Click Link  Overrides
    Capture and crop page screenshot  new-easyform-overrides.png  content
    Click Link  Thanks Page
    Capture and crop page screenshot  new-easyform-thankspage.png  content
    Click Button  Save
    Capture and crop page screenshot  created-easyform.png  content
    When Clicked Fields
    Capture and crop page screenshot  created-easyform-fields.png  content
    When Clicked Actions
    Capture and crop page screenshot  created-easyform-actions.png  content

Add easyform as Contributor

    Given a logged-in contributor
    Go to  ${PLONE_URL}

    Click link  css=#plone-contentmenu-factories a
    Click link  css=#plone-contentmenu-factories a.contenttype-easyform
    ${dot1} =  Add dot  form-widgets-IDublinCore-title  3
    ${note1} =  Add note  form-widgets-IDublinCore-title  Set form title  width=180  position=right
    ${dot2} =  Add dot  form-widgets-IDublinCore-description  4
    ${note2} =  Add note  form-widgets-IDublinCore-description  And description  width=180  position=right
    Capture and crop page screenshot  new-easyform-default-contributor.png  content
    Remove elements  ${dot1}  ${note1}  ${dot2}  ${note2}
    Page should not contain  Overrides
    Input text  form-widgets-IDublinCore-title  EasyForm
    Click link  Thanks Page
    Capture and crop page screenshot  new-easyform-thankspage-contributor.png  content
    Click Button  Save
