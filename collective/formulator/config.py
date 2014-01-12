MODEL_DEFAULT = u"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
    <schema>
    </schema>
</model>
"""

#<model xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:formulator="http://namespaces.plone.org/supermodel/formulator" xmlns="http://namespaces.plone.org/supermodel/schema">
  #<schema name="Formulator" based-on="zope.interface.Interface">
    #<field name="some_text" type="zope.schema.TextLine">
      #<description/>
      #<title>Some Text</title>
    #</field>
    #<fieldset name="set2" label="Set2">
      #<field name="next_text" type="zope.schema.TextLine">
        #<description/>
        #<title>Next Text</title>
      #</field>
    #</fieldset>
  #</schema>
#</model>

# replyto fgStringValidator 'isEmail'

FIELDS_DEFAULT = u"""
<model xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:formulator="http://namespaces.plone.org/supermodel/formulator" xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="replyto" type="zope.schema.TextLine" formulator:TDefault="python:member and member.getProperty('email', '') or ''" formulator:serverSide="False">
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
    <field name="mailer" type="collective.formulator.browser.formulatorview.Mailer">
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
##parameters=fields, ploneformgen, request
##title=
##

# Available parameters:
#  fields  = HTTP request form fields as key value pairs
#  request = The current HTTP request.
#            Access fields by request.form["myfieldname"]
#  ploneformgen = PloneFormGen object
#
# Return value is not processed -- unless you
# return a dictionary with contents. That's regarded
# as an error and will stop processing of actions
# and return the user to the form. Error dictionaries
# should be of the form {'field_id':'Error message'}


assert False, "Please complete your script"

"""
