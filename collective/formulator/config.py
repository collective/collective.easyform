MODEL_DEFAULT = u"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
    <schema>
    </schema>
</model>
"""

MAIL_BODY_DEFAULT = u"""<html xmlns="http://www.w3.org/1999/xhtml">

  <head><title></title></head>

  <body>
    <p tal:content="here/getBody_pre | nothing" />
    <dl>
        <tal:block repeat="field options/wrappedFields | nothing">
            <dt tal:content="field/fgField/widget/label" />
            <dd tal:content="structure python:field.htmlValue(request)" />
        </tal:block>
    </dl>
    <p tal:content="here/getBody_post | nothing" />
    <pre tal:content="here/getBody_footer | nothing" />
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
