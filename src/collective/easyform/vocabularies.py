# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _  # NOQA
from collective.easyform.api import get_context
from collective.easyform.api import get_schema
from plone.schemaeditor.interfaces import IFieldFactory
from zope.component import getUtilitiesFor
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import provider
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

import operator


PMF = MessageFactory("plone")


def _make_vocabulary(items):
    return SimpleVocabulary(
        [SimpleVocabulary.createTerm(token, token, name) for (name, token) in items]
    )


@provider(IVocabularyFactory)
def CustomActionsVocabularyFactory(context):
    items = [(_(u"Traverse to"), u"traverse_to"), (_(u"Redirect to"), u"redirect_to")]
    return _make_vocabulary(items)


@provider(IVocabularyFactory)
def MimeListVocabularyFactory(context):
    items = [(u"HTML", u"html"), (PMF(u"Text"), u"plain")]
    return _make_vocabulary(items)


@provider(IVocabularyFactory)
def FormMethodsVocabularyFactory(context):
    return SimpleVocabulary.fromValues((u"post", u"get"))


@provider(IVocabularyFactory)
def XinfoHeadersVocabularyFactory(context):
    return SimpleVocabulary.fromValues(
        (
            u"HTTP_X_FORWARDED_FOR",
            u"REMOTE_ADDR",
            u"PATH_INFO",
            u"HTTP_USER_AGENT",
            u"HTTP_REFERER",
        )
    )


@provider(IVocabularyFactory)
def ProxyRoleChoicesVocabularyFactory(context):
    items = [(u"No proxy role", u"none"), (u"Manager", u"Manager")]
    return _make_vocabulary(items)


@provider(IVocabularyFactory)
def ExtraDataDLVocabularyFactory(context):
    items = [
        (_(u"vocabulary_postingdt_text", default=u"Posting Date/Time"), u"dt"),
        (u"HTTP_X_FORWARDED_FOR", u"HTTP_X_FORWARDED_FOR"),
        (u"REMOTE_ADDR", u"REMOTE_ADDR"),
        (u"HTTP_USER_AGENT", u"HTTP_USER_AGENT"),
    ]
    return _make_vocabulary(items)


@provider(IVocabularyFactory)
def FormatDLVocabularyFactory(context):
    items = [
        (_(u"vocabulary_tsv_text", default=u"Tab-Separated Values"), u"tsv"),
        (_(u"vocabulary_csv_text", default=u"Comma-Separated Values"), u"csv"),
    ]
    return _make_vocabulary(items)


@provider(IVocabularyFactory)
def FieldsVocabularyFactory(context):
    terms = []
    if hasattr(context, "interface"):
        form = get_context(context)
    elif hasattr(context, "fields_model"):
        form = context
    else:
        return SimpleVocabulary(terms)
    fields = getFieldsInOrder(get_schema(form))
    for name, field in fields:
        terms.append(SimpleVocabulary.createTerm(name, str(name), field.title))
    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def EasyFormActionsVocabularyFactory(context):
    """EasyForm actions vocabulary"""
    from collective.easyform.interfaces import IActionFactory

    return SimpleVocabulary(
        [
            SimpleVocabulary.createTerm(
                factory, translate(factory.title), factory.title
            )
            for (id, factory) in getUtilitiesFor(IActionFactory)
            if factory.available(context)
        ]
    )


@provider(IVocabularyFactory)
def ValidatorsVocabularyFactory(context):
    """Field validators vocabulary"""
    from collective.easyform.interfaces import IFieldValidator

    return SimpleVocabulary(
        [
            SimpleVocabulary.createTerm(i, i, i)
            for i, u in getUtilitiesFor(IFieldValidator)
        ]
    )


@provider(IVocabularyFactory)
def SchemaEditorFieldsVocabularyFactory(context=None):
    request = getRequest()
    terms = []
    for (field_id, factory) in getUtilitiesFor(IFieldFactory):
        terms.append(
            SimpleVocabulary.createTerm(
                field_id, factory.title, translate(factory.title, context=request)
            )
        )
    terms = sorted(terms, key=operator.attrgetter("title"))
    return SimpleVocabulary(terms)
