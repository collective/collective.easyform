from zope.interface import implements
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabulary
from zope.schema.vocabulary import SimpleVocabulary
from collective.formulator.api import (
    get_fields,
    # get_actions,
    # set_schema,
    # set_actions,
    get_context,
)
from collective.formulator import formulatorMessageFactory as _

customActions = SimpleVocabulary.fromItems((
    (_(u"Traverse to"), u"traverse_to"),
    (_(u"Redirect to"), u"redirect_to"),
))

MIME_LIST = SimpleVocabulary.fromItems((
    (_(u'HTML'), u'html'),
    (_(u'Text'), u'plain'),
))

XINFO_HEADERS = SimpleVocabulary.fromItems((
    (u'HTTP_X_FORWARDED_FOR', u'HTTP_X_FORWARDED_FOR'),
    (u'REMOTE_ADDR', u'REMOTE_ADDR'),
    (u'PATH_INFO', u'PATH_INFO'),
    (u'HTTP_USER_AGENT', u'HTTP_USER_AGENT'),
    (u'HTTP_REFERER', u'HTTP_REFERER'),
))

getProxyRoleChoices = SimpleVocabulary.fromItems((
    (u"No proxy role", u"none"),
    (u"Manager", u"Manager"),
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
