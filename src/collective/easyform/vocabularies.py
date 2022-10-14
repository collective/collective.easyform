# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _  # NOQA
from collective.easyform.api import get_context
from collective.easyform.api import get_schema
from collective.easyform.config import HAS_XLSX_SUPPORT
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
    items = [(_("Traverse to"), "traverse_to"), (_("Redirect to"), "redirect_to")]
    return _make_vocabulary(items)


@provider(IVocabularyFactory)
def MimeListVocabularyFactory(context):
    items = [("HTML", "html"), (PMF("Text"), "plain")]
    return _make_vocabulary(items)


@provider(IVocabularyFactory)
def FormMethodsVocabularyFactory(context):
    return SimpleVocabulary.fromValues(("post", "get"))


@provider(IVocabularyFactory)
def XinfoHeadersVocabularyFactory(context):
    return SimpleVocabulary.fromValues(
        (
            "HTTP_X_FORWARDED_FOR",
            "REMOTE_ADDR",
            "PATH_INFO",
            "HTTP_USER_AGENT",
            "HTTP_REFERER",
        )
    )


@provider(IVocabularyFactory)
def ProxyRoleChoicesVocabularyFactory(context):
    items = [("No proxy role", "none"), ("Manager", "Manager")]
    return _make_vocabulary(items)


@provider(IVocabularyFactory)
def ExtraDataDLVocabularyFactory(context):
    items = [
        (_("vocabulary_postingdt_text", default="Posting Date/Time"), "dt"),
        ("HTTP_X_FORWARDED_FOR", "HTTP_X_FORWARDED_FOR"),
        ("REMOTE_ADDR", "REMOTE_ADDR"),
        ("HTTP_USER_AGENT", "HTTP_USER_AGENT"),
    ]
    return _make_vocabulary(items)


@provider(IVocabularyFactory)
def FormatDLVocabularyFactory(context):
    items = [
        (_("vocabulary_tsv_text", default="Tab-Separated Values"), "tsv"),
        (_("vocabulary_csv_text", default="Comma-Separated Values"), "csv"),
    ]

    if HAS_XLSX_SUPPORT:
        items.append(
            (_("vocabulary_xlsx_text", default="XLSX"), "xlsx"),
        )
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
