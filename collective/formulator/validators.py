try:
    from Products.validation import validation
    from Products.validation.validators.BaseValidators import baseValidators
except ImportError:
    validation = {}
    baseValidators = []

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import Interface, implements
from zope.component import (
    getUtility,
    provideUtility,
    getUtilitiesFor,
)
from zope.component.hooks import getSite
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.exceptions import EmailAddressInvalid


class IFieldValidator(Interface):

    """Base marker for field validators"""


def get_validators(site=None):
    validators = {}
    if not site:
        site = getSite()
    for name, ut in getUtilitiesFor(IFieldValidator, site):
        validators[name] = ut
    return validators


def isValidEmail(value):
    """Check for the user email address"""
    portal = getUtility(ISiteRoot)

    reg_tool = getToolByName(portal, 'portal_registration')
    if not (value and reg_tool.isValidEmail(value)):
        raise EmailAddressInvalid

# Base validators
provideUtility(isValidEmail, provides=IFieldValidator, name='isValidEmail')

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


class ValidatorsVocabulary(object):

    """Field validators vocabulary"""
    implements(IVocabularyFactory)

    def __call__(self, context, key=None):
        validators = get_validators()
        return SimpleVocabulary([SimpleVocabulary.createTerm(i, i, i) for i in validators.keys()])

ValidatorsVocabularyFactory = ValidatorsVocabulary()
