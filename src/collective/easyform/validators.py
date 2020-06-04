# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _
from collective.easyform.interfaces import IFieldValidator
from plone import api
from Products.CMFPlone.RegistrationTool import EmailAddressInvalid
from Products.validation import validation
from Products.validation.validators.BaseValidators import baseValidators
from zope.component import provideUtility

import six


BAD_SIGNS = frozenset(["<a ", "www.", "http:", ".com", "https:"])


def isValidEmail(value):
    """Check for the user email address.
    """
    if value is None:
        return
    reg_tool = api.portal.get_tool("portal_registration")
    if not (value and reg_tool.isValidEmail(value)):
        raise EmailAddressInvalid


def isCommaSeparatedEmails(value):
    """Check for one or more E-Mail Addresses separated by commas.
    """
    if value is None:
        # Let the system for required take care of None values
        return
    reg_tool = api.portal.get_tool("portal_registration")
    for v in value.split(","):
        if not reg_tool.isValidEmail(v.strip()):
            return _(
                u"Must be a valid list of email addresses " u"(separated by commas)."
            )


def isChecked(value):
    if not (
        (isinstance(value, bool) and value)
        or (isinstance(value, six.string_types) and value == "1")
    ):
        return _(u"Must be checked.")


def isUnchecked(value):
    if not isChecked(value):
        return _(u"Must be unchecked.")


def isNotLinkSpam(value):
    if not value:
        return  # No value can't be SPAM
    # validation is optional and configured on the field
    value = value.lower()
    for s in BAD_SIGNS:
        if s in value:
            return _("Links are not allowed.")


# Base validators
def update_validators():
    if validation and baseValidators:

        def method(name):
            def validate(value):
                if value is None:
                    # Let the system for required take care of None values
                    return
                if six.PY2 and isinstance(value, six.text_type):
                    value = value.encode("utf-8")
                res = validation(name, value)
                if res != 1:
                    return res

            return validate

        for validator in baseValidators:
            provideUtility(
                method(validator.name), provides=IFieldValidator, name=validator.name
            )


update_validators()
