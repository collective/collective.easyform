# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _  # NOQA
from collective.easyform.api import get_context
from collective.easyform.api import get_fields
from z3c.form.interfaces import IFieldWidget
from zope.component import getGlobalSiteManager
from zope.component import getUtilitiesFor
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from zope.interface import provider
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabulary
from zope.schema.vocabulary import SimpleVocabulary


PMF = MessageFactory('plone')


def _make_vocabulary(items):
    return SimpleVocabulary([
        SimpleVocabulary.createTerm(token, token, name)
        for (name, token) in items
    ])


customActions = _make_vocabulary((
    (_(u'Traverse to'), u'traverse_to'),
    (_(u'Redirect to'), u'redirect_to'),
))

MIME_LIST = _make_vocabulary((
    (u'HTML', u'html'),
    (PMF(u'Text'), u'plain'),
))

FORM_METHODS = SimpleVocabulary.fromValues((
    u'post',
    u'get',
))

XINFO_HEADERS = SimpleVocabulary.fromValues((
    u'HTTP_X_FORWARDED_FOR',
    u'REMOTE_ADDR',
    u'PATH_INFO',
    u'HTTP_USER_AGENT',
    u'HTTP_REFERER',
))

getProxyRoleChoices = _make_vocabulary((
    (u'No proxy role', u'none'),
    (u'Manager', u'Manager'),
))

vocabExtraDataDL = _make_vocabulary((
    (_(u'vocabulary_postingdt_text', default=u'Posting Date/Time'), u'dt'),
    (u'HTTP_X_FORWARDED_FOR', u'HTTP_X_FORWARDED_FOR'),
    (u'REMOTE_ADDR', u'REMOTE_ADDR'),
    (u'HTTP_USER_AGENT', u'HTTP_USER_AGENT'),
))

vocabFormatDL = _make_vocabulary((
    (_(u'vocabulary_tsv_text', default=u'Tab-Separated Values'), u'tsv'),
    (_(u'vocabulary_csv_text', default=u'Comma-Separated Values'), u'csv'),
))


@implementer(IContextSourceBinder, IVocabulary)
class Fields(object):

    """
    Context source binder to provide a vocabulary of fields in a form.
    """

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


fieldsFactory = Fields()


class WidgetVocabulary(SimpleVocabulary):

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        if not isinstance(value, basestring):
            value = '{0}.{1}'.format(
                value.widget_factory.__module__, value.widget_factory.__name__)
        return self.getTermByToken(value)


@provider(IContextSourceBinder)
def widgetsFactory(context):
    terms = []
    adapters = [
        a.factory
        for a in getGlobalSiteManager().registeredAdapters()
        if (
            a.provided == IFieldWidget and
            len(a.required) == 2 and
            a.required[0].providedBy(context)
        )
    ]
    for adapter in set(adapters):
        name = u'{0}.{1}'.format(
            adapter.__module__, adapter.__name__)
        terms.append(WidgetVocabulary.createTerm(
            name, str(name), adapter.__name__))
    return WidgetVocabulary(terms)


def EasyFormActionsVocabularyFactory(context):
    """EasyForm actions vocabulary"""
    from collective.easyform.interfaces import IActionFactory
    return SimpleVocabulary([
        SimpleVocabulary.createTerm(
            factory, translate(factory.title), factory.title)
        for (id, factory) in getUtilitiesFor(IActionFactory)
        if factory.available(context)
    ])


def ValidatorsVocabularyFactory(context):
    """Field validators vocabulary"""
    from collective.easyform.interfaces import IFieldValidator
    return SimpleVocabulary([
        SimpleVocabulary.createTerm(i, i, i)
        for i, u in getUtilitiesFor(IFieldValidator)
    ])
