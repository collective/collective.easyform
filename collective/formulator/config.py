MODEL_DEFAULT = u"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
    <schema>
    </schema>
</model>
"""

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
