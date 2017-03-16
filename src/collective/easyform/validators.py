# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _
from collective.easyform.interfaces import IFieldValidator
from plone import api
from zope.component import provideUtility


try:
    from Products.validation import validation
    from Products.validation.validators.BaseValidators import baseValidators
except ImportError:  # pragma: no cover
    validation = {}
    baseValidators = []


from Products.CMFPlone.RegistrationTool import EmailAddressInvalid


def isValidEmail(value):
    """Check for the user email address"""
    reg_tool = api.portal.get_tool('portal_registration')
    if not (value and reg_tool.isValidEmail(value)):
        raise EmailAddressInvalid


def isCommaSeparatedEmails(value):
    """Check for one or more E-Mail Addresses separated by commas"""
    reg_tool = api.portal.get_tool('portal_registration')
    for v in value.split(','):
        if not reg_tool.isValidEmail(v.strip()):
            return _(
                u'Must be a valid list of email addresses '
                u'(separated by commas).'
            )


def isChecked(value):
    if not (
        (isinstance(value, bool) and value) or
        (isinstance(value, basestring) and value == '1')
    ):
        return _(u'Must be checked.')


def isUnchecked(value):
    if not isChecked(value):
        return _(u'Must be unchecked.')


BAD_SIGNS = frozenset('<a ', 'www.', 'http:', '.com', 'https:')


def isNotLinkSpam(value):
    if not value:
        return    # No value can't be SPAM
    # validation is optional and configured on the field
    value = value.lower()
    for s in BAD_SIGNS:
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
            provideUtility(
                method(validator.name),
                provides=IFieldValidator,
                name=validator.name
            )


update_validators()
