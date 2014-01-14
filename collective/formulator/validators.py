try:
    from Products.validation import validation
    from Products.validation.validators.BaseValidators import baseValidators
except ImportError:
    validation = {}
    baseValidators = []

from types import BooleanType, StringTypes
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import Interface, implements
from zope.component import (
    getUtility,
    provideUtility,
    getUtilitiesFor,
)
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.exceptions import EmailAddressInvalid
from collective.formulator import formulatorMessageFactory as _


class IFieldValidator(Interface):

    """Base marker for field validators"""


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
    for v in value.split(","):
        if not reg_tool.isValidEmail(v.strip()):
            return _(u"Must be a valid list of email addresses (separated by commas).")


def isChecked(value):
    if (type(value) == BooleanType) and value or (type(value) in StringTypes) and (value == '1'):
        return
    return _(u"Must be checked.")


def isUnchecked(value):
    if (type(value) == BooleanType) and not value or (type(value) in StringTypes) and (value == '0'):
        return
    return _(u"Must be unchecked.")


def isNotLinkSpam(value):
    # validation is optional and configured on the field
    bad_signs = ("<a ", "www.", "http:", ".com", )
    value = value.lower()
    for s in bad_signs:
        if s in value:
            return _("Links are not allowed.")

# Base validators


def update_validators():
    if validation and baseValidators:
        def method(name):
            def validate(value):
                if isinstance(value, unicode):
                    value = value.encode("utf-8")
                res = validation(name, value)
                if res != 1:
                    return res
            return validate
        for validator in baseValidators:
            provideUtility(method(validator.name),
                           provides=IFieldValidator, name=validator.name)
update_validators()


class ValidatorsVocabulary(object):

    """Field validators vocabulary"""
    implements(IVocabularyFactory)

    def __call__(self, context, key=None):
        return SimpleVocabulary([SimpleVocabulary.createTerm(i, i, i) for i, u in getUtilitiesFor(IFieldValidator)])

ValidatorsVocabularyFactory = ValidatorsVocabulary()
