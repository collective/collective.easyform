from zope.browser.interfaces import ITerms
from zope.interface import directlyProvides
from zope.interface import implements, classProvides
from zope.schema.interfaces import ISource, IContextSourceBinder
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IBaseVocabulary, IVocabulary
from zope.schema.vocabulary import SimpleTerm

from zope.formlib.interfaces import ISourceQueryView

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.vocabularies import SlicableVocabulary
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema import getFieldsInOrder
from collective.formulator.api import (
    CONTEXT_KEY,
    get_schema,
    get_actions,
    set_schema,
    set_actions,
)


class fieldsDisplayList(object):

    """Context source binder to provide a vocabulary of users in a given
    group.
    """

    implements(IContextSourceBinder, IVocabulary)
    #implements(IVocabularyFactory), IBaseVocabulary

    def __contains__(self, value):
        return True

    def __call__(self, context):
        # print context
        terms = []
        form = context.interface.getTaggedValue(CONTEXT_KEY)
        fields = getFieldsInOrder(get_schema(form))
        for name, field in fields:
            # print repr(name), repr(field.title)
            terms.append(
                SimpleVocabulary.createTerm(name, str(name), field.title))
        return SimpleVocabulary(terms)

fieldsDisplayListFactory = fieldsDisplayList()
