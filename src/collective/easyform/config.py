# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode

import os


this_path = os.path.dirname(__file__)


EDIT_TALES_PERMISSION = "collective.easyform.EditTALESFields"
EDIT_PYTHON_PERMISSION = "collective.easyform.EditPythonFields"
EDIT_TECHNICAL_PERMISSION = "collective.easyform.EditTechnicalFields"
EDIT_ADVANCED_PERMISSION = "collective.easyform.EditAdvancedFields"
EDIT_ADDRESSING_PERMISSION = "collective.easyform.EditMailAddresses"
USE_ENCRYPTION_PERMISSION = "collective.easyform.EditEncryptionSpecs"
DOWNLOAD_SAVED_PERMISSION = "collective.easyform.DownloadSavedInput"

with open(
    os.path.join(this_path, "default_schemata", "model_default.xml")
) as fp:  # noqa
    MODEL_DEFAULT = safe_unicode(fp.read())

with open(
    os.path.join(this_path, "default_schemata", "fields_default.xml")
) as fp:  # noqa
    FIELDS_DEFAULT = safe_unicode(fp.read())

with open(
    os.path.join(this_path, "default_schemata", "actions_default.xml")
) as fp:  # noqa
    ACTIONS_DEFAULT = safe_unicode(fp.read())

with open(
    os.path.join(this_path, "default_schemata", "mail_body_default.pt")
) as fp:  # noqa
    MAIL_BODY_DEFAULT = safe_unicode(fp.read())


FORM_ERROR_MARKER = 'FORM_ERROR_MARKER'


DEFAULT_SCRIPT = u"""
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, easyform, request
##title=
##

# Available parameters:
#  fields  = HTTP request form fields as key value pairs
#  request = The current HTTP request.
#            Access fields by request.form["myfieldname"]
#  easyform = EasyForm object
#
# Return value is not processed -- unless you
# return a dictionary with contents. That's regarded
# as an error and will stop processing of actions
# and return the user to the form. Error dictionaries
# should be of the form {'field_id':'Error message'}
# or {request.FORM_ERROR_MARKER:'Form error message'}


assert False, "Please complete your script"

"""
