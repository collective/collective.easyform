# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from collections import OrderedDict as BaseDict
from collective.easyform.config import MODEL_DEFAULT
from email.utils import formataddr
from hashlib import md5
from plone.memoize import ram
from plone.namedfile.interfaces import INamedBlobFile
from plone.namedfile.interfaces import INamedFile
from plone.supermodel import loadString
from plone.supermodel import serializeSchema
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext
from Products.CMFPlone.utils import safe_unicode
from re import compile
from types import StringTypes
from zope.schema import getFieldsInOrder


# SCHEMATA_KEY = u''
CONTEXT_KEY = u'context'
# regular expression for dollar-sign variable replacement.
# we want to find ${identifier} patterns
dollarRE = compile(r'\$\{(.+?)\}')


class OrderedDict(BaseDict):
    """
    A wrapper around dictionary objects that provides an ordering for
    keys() and items().
    """

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    def reverse(self):
        items = list(self.items())
        items.reverse()
        return items


InitializeClass(OrderedDict)


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


def format_addresses(addresses, names=[]):
    """Format destination (To) input.
    Input may be a string or sequence of strings;
    returns a well-formatted address string.

    :param addresses: [required] Mail addresses.
    :type addresses: sequence or string
    :param names: Names corresponding to mail addresses.
    :type addresses: sequence or string
    :returns: Well formatted address string.
    :rtype: String

    >>> from collective.easyform import api

    >>> api.format_addresses('sim@sala.bim')
    'sim@sala.bim'

    >>> api.format_addresses('sim@sala.bim', 'sim')
    'sim <sim@sala.bim>'

    >>> api.format_addresses('ähm@öhm.ühm', 'ähm')
    '\xc3\xa4hm <\xc3\xa4hm@\xc3\xb6hm.\xc3\xbchm>'

    >>> api.format_addresses('sim@sala.bim, hokus@pokus.fidibus')
    'sim@sala.bim, hokus@pokus.fidibus'

    >>> api.format_addresses('sim@sala.bim, hokus@pokus.fidibus', 'sim')
    'sim <sim@sala.bim>, hokus@pokus.fidibus'

    >>> api.format_addresses('sim@sala.bim, hokus@pokus.fidibus', 'sim, hokus')
    'sim <sim@sala.bim>, hokus <hokus@pokus.fidibus>'

    >>> api.format_addresses(['sim@sala.bim', 'hokus@pokus.fidibus'],
    ...                      ['sim', 'hokus'])
    'sim <sim@sala.bim>, hokus <hokus@pokus.fidibus>'

    >>> api.format_addresses(('sim@sala.bim', 'hokus@pokus.fidibus'),
    ...                      ('sim', 'hokus'))
    'sim <sim@sala.bim>, hokus <hokus@pokus.fidibus>'

    >>> api.format_addresses([])
    ''

    >>> api.format_addresses('')
    ''

    """

    if type(addresses) in StringTypes:
        addresses = [s for s in addresses.split(',')]
    assert(isinstance(addresses, list) or isinstance(addresses, tuple))  # ensure iterable  # noqa
    addresses = [
        safe_unicode(s).strip().encode('utf-8') for s in addresses if s
    ]

    if names and type(names) in StringTypes:
        names = [s for s in names.split(',')]
    if not names:
        names = []
    assert(isinstance(names, list) or isinstance(names, tuple))
    names = [safe_unicode(s).strip().encode('utf-8') for s in names if s]

    address_pairs = []
    for cnt, address in enumerate(addresses):
        address_pairs.append((
            names[cnt] if len(names) > cnt else False,
            address
        ))

    ret = ', '.join([formataddr(pair) for pair in address_pairs])
    return ret


def is_file_data(field):
    """Return True, if field is a file field.
    """
    ifaces = (INamedFile, INamedBlobFile)
    for i in ifaces:
        if i.providedBy(field):
            return True
    return False


def filter_fields(context, schema, unsorted_data, omit=False):
    """Filter according to ``showAll``, ``showFields`` and ``includeEmpties``
    settings to display in result mailings, thanks pages and the like.
    """
    # Prevent cyclic import
    from collective.easyform.interfaces import IFieldExtender

    data = OrderedDict(
        [
            (x[0], unsorted_data[x[0]])
            for x in getFieldsInOrder(schema)
            if x[0] in unsorted_data
        ]
    )

    # TODO: Exclude labels
    fields = [
        f
        for f in data
        if not (is_file_data(data[f]))
        and not (
            # TODO: serverSide should always be excluded
            # Also, when shoAll = 0 and serverSite = 1, it will be included
            # which is wrong.
            getattr(context, "showAll", True)
            and IFieldExtender(schema[f]).serverSide
        )
    ]

    if not getattr(context, "showAll", True):
        showFields = getattr(context, "showFields", []) or []
        # Only show fields from 'showFields', and also keep the order,
        # even when that is not always needed or used by code that calls us.
        # Note that showFields may contain fields that are not in the schema
        # or the data: the schema may be limited to one fieldset.
        # fields = [f for f in fields if f in showFields]
        ordered_fields = []
        for fieldname in showFields:
            for f in fields:
                if f == fieldname:
                    ordered_fields.append(f)
                    fields.remove(f)
                    break
        fields = ordered_fields

    if not getattr(context, "includeEmpties", True):
        fields = [f for f in fields if data[f]]

    ret = []
    if omit:
        # return field ids to omit
        ret = [f for f in data if f not in fields]
    else:
        # return field ids and field instances to include
        ret = OrderedDict([(f, data[f]) for f in fields])

    return ret
