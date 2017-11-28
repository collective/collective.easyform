# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from collections import OrderedDict as BaseDict
from collective.easyform.config import MODEL_DEFAULT
from collective.easyform.interfaces import IFieldExtender
from email.utils import formataddr
from plone import api
from plone.namedfile.interfaces import INamedBlobFile
from plone.namedfile.interfaces import INamedFile
from plone.supermodel import loadString
from plone.supermodel import serializeSchema
from plone.supermodel.parser import SupermodelParseError
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext
from Products.CMFPlone.utils import safe_unicode
from re import compile
from types import StringTypes
from zope.schema import getFieldsInOrder


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
    security.setDefaultAccess('allow')

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


def get_model(data, context):
    schema = None
    # if schema is set on context it has priority
    if data is not None:
        try:
            schema = loadString(data).schema
        except SupermodelParseError:  # pragma: no cover
            pass

    # 2nd we try aquire the model
    if not schema:
        nav_root = api.portal.get_navigation_root(context)
        schema = nav_root.get('easyform_model_default.xml')

    # finally we fall back to the hardcoded example
    if not schema:
        schema = loadString(MODEL_DEFAULT).schema
    schema.setTaggedValue(CONTEXT_KEY, context)
    return schema


# caching this breaks with memcached
def get_schema(context):
    try:
        data = context.fields_model
    except AttributeError:
        data = None
    return get_model(data, context)


# caching this breaks with memcached
def get_actions(context):
    try:
        data = context.actions_model
    except AttributeError:
        data = None
    return get_model(data, context)


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
    """
    Format destination (To) input.
    Input may be a string or sequence of strings;
    returns a well-formatted address string.

    :param addresses: [required] Mail addresses.
    :type addresses: sequence or string
    :param names: Names corresponding to mail addresses.
    :type addresses: sequence or string
    :returns: Well formatted address string.
    :rtype: String

    >>> from collective.easyform.api import format_addresses

    >>> format_addresses('sim@sala.bim')
    'sim@sala.bim'

    >>> format_addresses('sim@sala.bim', 'sim')
    'sim <sim@sala.bim>'

    >>> format_addresses('ähm@öhm.ühm', 'ähm')
    '\xc3\xa4hm <\xc3\xa4hm@\xc3\xb6hm.\xc3\xbchm>'

    >>> format_addresses('sim@sala.bim, hokus@pokus.fidibus')
    'sim@sala.bim, hokus@pokus.fidibus'

    >>> format_addresses('sim@sala.bim\nhokus@pokus.fidibus')
    'sim@sala.bim, hokus@pokus.fidibus'

    >>> format_addresses('sim@sala.bim, hokus@pokus.fidibus', 'sim')
    'sim <sim@sala.bim>, hokus@pokus.fidibus'

    >>> format_addresses('sim@sala.bim, hokus@pokus.fidibus', 'sim, hokus')
    'sim <sim@sala.bim>, hokus <hokus@pokus.fidibus>'

    >>> format_addresses('sim@sala.bim, hokus@pokus.fidibus', 'sim\nhokus')
    'sim <sim@sala.bim>, hokus <hokus@pokus.fidibus>'

    >>> format_addresses(['sim@sala.bim', 'hokus@pokus.fidibus'],
    ...                      ['sim', 'hokus'])
    'sim <sim@sala.bim>, hokus <hokus@pokus.fidibus>'

    >>> format_addresses(('sim@sala.bim', 'hokus@pokus.fidibus'),
    ...                      ('sim', 'hokus'))
    'sim <sim@sala.bim>, hokus <hokus@pokus.fidibus>'

    >>> format_addresses([])
    ''

    >>> format_addresses('')
    ''

    """
    if type(addresses) in StringTypes:
        # replace common separators `;` and `,` with newlines so the
        # splitlines method works
        addresses = addresses.replace(',', '\n').replace(';', '\n')
        addresses = [s.strip() for s in addresses.splitlines()]
    assert(isinstance(addresses, list) or isinstance(addresses, tuple))  # ensure iterable  # noqa
    addresses = [
        safe_unicode(s).strip().encode('utf-8') for s in addresses if s
    ]

    if names and type(names) in StringTypes:
        # replace common separators `;` and `,` with newlines so the
        # splitlines method works
        names = names.replace(',', '\n').replace(';', '\n')
        names = [s for s in names.splitlines()]
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


def dollar_replacer(s, data):
    dr = DollarVarReplacer(data)
    return dr.sub(s)


def lnbr(text):
    """Converts line breaks to html breaks
    """
    return "<br/>".join(text.strip().splitlines()) if text else text


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
    data = OrderedDict([
        (x[0], unsorted_data[x[0]])
        for x in getFieldsInOrder(schema)
        if x[0] in unsorted_data
    ])

    # TODO: Exclude labels
    fields = [
        f for f in data
        if not (is_file_data(data[f])) and not (
            # TODO: serverSide should always be excluded
            # Also, when shoAll = 0 and serverSite = 1, it will be included
            # which is wrong.
            getattr(context, 'showAll', True) and
            IFieldExtender(schema[f]).serverSide
        )
    ]

    if not getattr(context, 'showAll', True):
        showFields = getattr(context, 'showFields', []) or []
        fields = [f for f in fields if f in showFields]

    if not getattr(context, 'includeEmpties', True):
        fields = [f for f in fields if data[f]]

    ret = []
    if omit:
        # return field ids to omit
        ret = [f for f in data if f not in fields]
    else:
        # return field ids and field instances to include
        ret = OrderedDict([(f, data[f]) for f in fields])

    return ret
