# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode

import os


this_path = os.path.dirname(__file__)


EDIT_TALES_PERMISSION = 'collective.easyform.EditTALESFields'
EDIT_PYTHON_PERMISSION = 'collective.easyform.EditPythonFields'
EDIT_ADVANCED_PERMISSION = 'collective.easyform.EditAdvancedFields'
EDIT_ADDRESSING_PERMISSION = 'collective.easyform.EditMailAddresses'
USE_ENCRYPTION_PERMISSION = 'collective.easyform.EditEncryptionSpecs'
DOWNLOAD_SAVED_PERMISSION = 'collective.easyform.DownloadSavedInput'

MODEL_DEFAULT = safe_unicode(open(os.path.join(
    this_path, "default_schemata", "model_default.xml")).read())

FIELDS_DEFAULT = safe_unicode(open(os.path.join(
    this_path, "default_schemata", "fields_default.xml")).read())

ACTIONS_DEFAULT = safe_unicode(open(os.path.join(
    this_path, "default_schemata", "actions_default.xml")).read())

MAIL_BODY_DEFAULT = safe_unicode(open(os.path.join(
    this_path, "default_schemata", "mail_body_default.pt")).read())


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


assert False, "Please complete your script"

"""
