# -*- coding: utf-8 -*-

from z3c.form.interfaces import IFieldWidget
from zope.component import getGlobalSiteManager
from zope.component import getUtilitiesFor
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import directlyProvides
from zope.interface import implements
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabulary
from zope.schema.vocabulary import SimpleVocabulary

from collective.formulator import formulatorMessageFactory as _
from collective.formulator.api import get_context
from collective.formulator.api import get_fields


PMF = MessageFactory('plone')

customActions = SimpleVocabulary.fromItems((
    (_(u'Traverse to'), u'traverse_to'),
    (_(u'Redirect to'), u'redirect_to'),
))

MIME_LIST = SimpleVocabulary.fromItems((
    (u'HTML', u'html'),
    (PMF(u'Text'), u'plain'),
))

XINFO_HEADERS = SimpleVocabulary.fromItems((
    (u'HTTP_X_FORWARDED_FOR', u'HTTP_X_FORWARDED_FOR'),
    (u'REMOTE_ADDR', u'REMOTE_ADDR'),
    (u'PATH_INFO', u'PATH_INFO'),
    (u'HTTP_USER_AGENT', u'HTTP_USER_AGENT'),
    (u'HTTP_REFERER', u'HTTP_REFERER'),
))

getProxyRoleChoices = SimpleVocabulary.fromItems((
    (u'No proxy role', u'none'),
    (u'Manager', u'Manager'),
))

vocabExtraDataDL = SimpleVocabulary.fromItems((
    (_(u'vocabulary_postingdt_text', default=u'Posting Date/Time'), u'dt'),
    (u'HTTP_X_FORWARDED_FOR', u'HTTP_X_FORWARDED_FOR'),
    (u'REMOTE_ADDR', u'REMOTE_ADDR'),
    (u'HTTP_USER_AGENT', u'HTTP_USER_AGENT'),
))

vocabFormatDL = SimpleVocabulary.fromItems((
    (_(u'vocabulary_tsv_text', default=u'Tab-Separated Values'), u'tsv'),
    (_(u'vocabulary_csv_text', default=u'Comma-Separated Values'), u'csv'),
))


class fields(object):

    """Context source binder to provide a vocabulary of users in a given
    group.
    """

    implements(IContextSourceBinder, IVocabulary)

    def __contains__(self, value):
        return True

    def __call__(self, context):
        terms = []
        if hasattr(context, 'interface'):
            form = get_context(context)
        elif hasattr(context, 'fields_model'):
            form = context
        else:
            return SimpleVocabulary(terms)
        fields = getFieldsInOrder(get_fields(form))
        for name, field in fields:
            terms.append(
                SimpleVocabulary.createTerm(name, str(name), field.title))
        return SimpleVocabulary(terms)

fieldsFactory = fields()


class WidgetVocabulary(SimpleVocabulary):

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        if not isinstance(value, basestring):
            value = '{0}.{1}'.format(
                value.widget_factory.__module__, value.widget_factory.__name__)
        return self.getTermByToken(value)


def widgetsFactory(context):
    terms = []
    adapters = [
        a
        for a in getGlobalSiteManager().registeredAdapters()
        if a.provided == IFieldWidget and a.required[0].providedBy(context)
    ]
    for adapter in adapters:
        name = u'{0}.{1}'.format(
            adapter.factory.__module__, adapter.factory.__name__)
        terms.append(WidgetVocabulary.createTerm(
            name, str(name), adapter.factory.__name__))
    return WidgetVocabulary(terms)

directlyProvides(widgetsFactory, IContextSourceBinder)


def FormulatorActionsVocabularyFactory(context):
    """Formulator actions vocabulary"""
    from collective.formulator.interfaces import IActionFactory
    return SimpleVocabulary([
        SimpleVocabulary.createTerm(
            factory, translate(factory.title), factory.title)
        for (id, factory) in getUtilitiesFor(IActionFactory)
    ])


def ValidatorsVocabularyFactory(context):
    """Field validators vocabulary"""
    from collective.formulator.interfaces import IFieldValidator
    return SimpleVocabulary([
        SimpleVocabulary.createTerm(i, i, i)
        for i, u in getUtilitiesFor(IFieldValidator)
    ])
