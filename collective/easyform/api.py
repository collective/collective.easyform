# -*- coding: utf-8 -*-
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext
from hashlib import md5
from plone.memoize import ram
from plone.supermodel import loadString
from plone.supermodel import serializeSchema
from re import compile

from collective.easyform.config import MODEL_DEFAULT

# SCHEMATA_KEY = u''
CONTEXT_KEY = u'context'
# regular expression for dollar-sign variable replacement.
# we want to find ${identifier} patterns
dollarRE = compile(r'\$\{(.+?)\}')


class DollarVarReplacer(object):

    """
    Initialize with a dictionary, then self.sub returns a string
    with all ${key} substrings replaced with values looked
    up from the dictionary.

    >>> from collective.easyform import api

    >>> adict = {'one':'two', '_two':'three', '.two':'four'}
    >>> dvr = api.DollarVarReplacer(adict)

    >>> dvr.sub('one one')
    'one one'

    >>> dvr.sub('one ${one}')
    'one two'

    >>> dvr.sub('one ${two}')
    'one ???'

    Skip any key beginning with _ or .
    >>> dvr.sub('one ${_two}')
    'one ???'

    >>> dvr.sub('one ${.two}')
    'one ???'

    """

    def __init__(self, adict):
        self.adict = adict

    def sub(self, s):
        return dollarRE.sub(self.repl, s)

    def repl(self, mo):
        key = mo.group(1)
        if key and key[0] not in ['_', '.']:
            try:
                return self.adict[mo.group(1)]
            except KeyError:
                pass
        return '???'


def get_expression(context, expression_string, **kwargs):
    """ Get TALES expression

    :param context: [required] TALES expression context
    :param string expression_string: [required] TALES expression string
    :param dict kwargs: additional arguments for expression
    :returns: result of TALES expression
    """
    if isinstance(expression_string, unicode):
        expression_string = expression_string.encode('utf-8')

    expression_context = getExprContext(context, context)
    for key in kwargs:
        expression_context.setGlobal(key, kwargs[key])
    expression = Expression(expression_string)
    return expression(expression_context)


def get_context(field):
    """ Get context of field

    :param field: [required] easyform field
    :returns: easyform
    """
    return field.interface.getTaggedValue(CONTEXT_KEY)


def get_fields_cache(method, context):
    data = context.fields_model + str(context.modification_date)
    if isinstance(data, unicode):
        data = data.encode('utf-8')
    return md5(data).hexdigest()


@ram.cache(get_fields_cache)
def get_fields(context):
    data = context.fields_model
    try:
        schema = loadString(data).schema
    except Exception:
        schema = loadString(MODEL_DEFAULT).schema
    schema.setTaggedValue(CONTEXT_KEY, context)
    return schema


def get_actions_cache(method, context):
    data = context.actions_model + str(context.modification_date)
    return md5(data).hexdigest()


@ram.cache(get_actions_cache)
def get_actions(context):
    data = context.actions_model
    try:
        schema = loadString(data).schema
    except Exception:
        schema = loadString(MODEL_DEFAULT).schema
    schema.setTaggedValue(CONTEXT_KEY, context)
    return schema


def set_fields(context, schema):
    # serialize the current schema
    snew_schema = serializeSchema(schema)
    # store the current schema
    context.fields_model = snew_schema
    context.notifyModified()


def set_actions(context, schema):
    # fix setting widgets
    schema.setTaggedValue('plone.autoform.widgets', {})
    # serialize the current schema
    snew_schema = serializeSchema(schema)
    # store the current schema
    context.actions_model = snew_schema
    context.notifyModified()
