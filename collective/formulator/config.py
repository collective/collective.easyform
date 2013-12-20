MODEL_DEFAULT = u"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
    <schema>
    </schema>
</model>
"""

FIELDS_DEFAULT = u"""
<model xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:formulator="http://namespaces.plone.org/supermodel/formulator" xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="replyto" type="zope.schema.TextLine" formulator:TDefault="python:member.getProperty('email', '')" formulator:serverSide="False">
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
      <bccOverride/>
      <bcc_recipients/>
      <body_footer/>
      <body_post/>
      <body_pre/>
      <body_pt>&lt;html xmlns="http://www.w3.org/1999/xhtml"&gt;&#13;
  &lt;head&gt;&lt;title&gt;&lt;/title&gt;&lt;/head&gt;&#13;
  &lt;body&gt;&#13;
    &lt;p tal:content="mailer/body_pre | nothing" /&gt;&#13;
    &lt;dl&gt;&#13;
        &lt;tal:block repeat="field data | nothing"&gt;&#13;
            &lt;dt tal:content="python:fields[field]" /&gt;&#13;
            &lt;dd tal:content="structure python:data[field]" /&gt;&#13;
        &lt;/tal:block&gt;&#13;
    &lt;/dl&gt;&#13;
    &lt;p tal:content="mailer/body_post | nothing" /&gt;&#13;
    &lt;pre tal:content="mailer/body_footer | nothing" /&gt;&#13;
  &lt;/body&gt;&#13;
&lt;/html&gt;&#13;
</body_pt>
      <ccOverride/>
      <cc_recipients/>
      <description>E-Mails Form Input</description>
      <recipientOverride/>
      <recipient_email/>
      <recipient_name/>
      <replyto_field>replyto</replyto_field>
      <senderOverride/>
      <showFields/>
      <subjectOverride/>
      <subject_field>topic</subject_field>
      <title>Mailer</title>
      <xinfo_headers/>
    </field>
  </schema>
</model>
"""

# obj.setFgStringValidator('isEmail')
# obj.setFgTDefault('here/memberEmail')
#obj.setFgDefault('dynamically overridden')

# create a thanks page
#self.invokeFactory('FormThanksPage', 'thank-you')
#obj = self['thank-you']

# obj.setTitle(zope.i18n.translate(
    #_(u'pfg_thankyou_title', u'Thank You'), context=self.REQUEST))
# obj.setDescription(zope.i18n.translate(
    #_(u'pfg_thankyou_description', u'Thanks for your input.'),
    # context=self.REQUEST))

# self._pfFixup(obj)

MAIL_BODY_DEFAULT = u"""<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title></title></head>
  <body>
    <p tal:content="mailer/body_pre | nothing" />
    <dl>
        <tal:block repeat="field data | nothing">
            <dt tal:content="python:fields[field]" />
            <dd tal:content="structure python:data[field]" />
        </tal:block>
    </dl>
    <p tal:content="mailer/body_post | nothing" />
    <pre tal:content="mailer/body_footer | nothing" />
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
