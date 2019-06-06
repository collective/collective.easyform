# -*- coding: utf-8 -*-

try:
    from Products.validation import validation
    from Products.validation.validators.BaseValidators import baseValidators
except ImportError:
    validation = {}
    baseValidators = []

try:
    from Products.CMFDefault.exceptions import EmailAddressInvalid
except ImportError:
    from Products.CMFPlone.RegistrationTool import EmailAddressInvalid

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from collective.easyform import easyformMessageFactory as _
from collective.easyform.interfaces import IFieldValidator
from types import BooleanType
from types import StringTypes
from zope.component import getUtility
from zope.component import provideUtility


def isValidEmail(value):
    """Check for the user email address"""
    portal = getUtility(ISiteRoot)
    reg_tool = getToolByName(portal, 'portal_registration')
    if not (value and reg_tool.isValidEmail(value)):
        raise EmailAddressInvalid


def isCommaSeparatedEmails(value):
    """Check for one or more E-Mail Addresses separated by commas"""
    portal = getUtility(ISiteRoot)
    reg_tool = getToolByName(portal, 'portal_registration')
    for v in value.split(','):
        if not reg_tool.isValidEmail(v.strip()):
            return _(u'Must be a valid list of email addresses (separated by commas).')


def isChecked(value):
    if (type(value) == BooleanType) and value or (type(value) in StringTypes) and (value == '1'):
        return
    return _(u'Must be checked.')


def isUnchecked(value):
    if (type(value) == BooleanType) and not value or (type(value) in StringTypes) and (value == '0'):
        return
    return _(u'Must be unchecked.')


def isNotLinkSpam(value):
    # validation is optional and configured on the field
    bad_signs = ('<a ', 'www.', 'http:', '.com', )
    value = value.lower()
    for s in bad_signs:
        if s in value:
            return _('Links are not allowed.')

# Base validators


def update_validators():
    if validation and baseValidators:
        def method(name):
            def validate(value):
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
                res = validation(name, value)
                if res != 1:
                    return res
            return validate
        for validator in baseValidators:
            provideUtility(method(validator.name),
                           provides=IFieldValidator, name=validator.name)
update_validators()
