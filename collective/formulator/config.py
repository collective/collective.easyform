# -*- coding: utf-8 -*-

EDIT_TALES_PERMISSION = 'collective.formulator.EditTALESFields'
EDIT_PYTHON_PERMISSION = 'collective.formulator.EditPythonFields'
EDIT_ADVANCED_PERMISSION = 'collective.formulator.EditAdvancedFields'
EDIT_ADDRESSING_PERMISSION = 'collective.formulator.EditMailAddresses'
USE_ENCRYPTION_PERMISSION = 'collective.formulator.EditEncryptionSpecs'
DOWNLOAD_SAVED_PERMISSION = 'collective.formulator.DownloadSavedInput'

MODEL_DEFAULT = u"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
    <schema>
    </schema>
</model>
"""

FIELDS_DEFAULT = u"""
<model xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:formulator="http://namespaces.plone.org/supermodel/formulator" xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="replyto" type="zope.schema.TextLine" formulator:TDefault="python:member and member.getProperty('email', '') or ''" formulator:serverSide="False" formulator:validators="isValidEmail">
      <description/>
      <title>Your E-Mail Address</title>
    </field>
    <field name="topic" type="zope.schema.TextLine">
      <description/>
      <title>Subject</title>
    </field>
    <field name="comments" type="zope.schema.Text">
      <description/>
      <title>Comments</title>
    </field>
  </schema>
</model>
"""

ACTIONS_DEFAULT = u"""
<model xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:formulator="http://namespaces.plone.org/supermodel/formulator" xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="mailer" type="collective.formulator.actions.Mailer">
      <description>E-Mails Form Input</description>
      <replyto_field>replyto</replyto_field>
      <subject_field>topic</subject_field>
      <title>Mailer</title>
    </field>
  </schema>
</model>
"""

MAIL_BODY_DEFAULT = u"""<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title></title></head>
  <body>
    <p tal:content="body_pre | nothing" />
    <dl>
        <tal:block repeat="field data | nothing">
            <dt tal:content="python:fields[field]" />
            <dd tal:content="structure python:data[field]" />
        </tal:block>
    </dl>
    <p tal:content="body_post | nothing" />
    <pre tal:content="body_footer | nothing" />
  </body>
</html>
"""

DEFAULT_SCRIPT = u"""
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, formulator, request
##title=
##

# Available parameters:
#  fields  = HTTP request form fields as key value pairs
#  request = The current HTTP request.
#            Access fields by request.form["myfieldname"]
#  formulator = Formulator object
#
# Return value is not processed -- unless you
# return a dictionary with contents. That's regarded
# as an error and will stop processing of actions
# and return the user to the form. Error dictionaries
# should be of the form {'field_id':'Error message'}


assert False, "Please complete your script"

"""
