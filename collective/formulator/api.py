from plone.supermodel import loadString
from plone.supermodel.model import Model
from plone.supermodel.serializer import serialize
from plone.directives.form import Schema
from Products.CMFCore.Expression import getExprContext, Expression

SCHEMATA_KEY = u""
CONTEXT_KEY = u"context"
CACHE_FIELDS_KEY = '_v_fields_model'
CACHE_ACTIONS_KEY = '_v_actions_model'


def get_expression(context, expression_string, **kwargs):
    expression_context = getExprContext(context, context)
    for key in kwargs:
        expression_context.setGlobal(key, kwargs[key])
    expression = Expression(expression_string)
    return expression(expression_context)


def get_context(field):
    return field.interface.getTaggedValue(CONTEXT_KEY)


def load_schema(sschema):
    try:
        schema = loadString(sschema).schemata.get(SCHEMATA_KEY, Schema)
    except Exception:
        schema = Schema
    return schema


def get_fields(context):
    if hasattr(context, CACHE_FIELDS_KEY):
        return getattr(context, CACHE_FIELDS_KEY)
    data = context.fields_model
    schema = load_schema(data)
    schema.setTaggedValue(CONTEXT_KEY, context)
    setattr(context, CACHE_FIELDS_KEY, schema)
    return schema


def get_actions(context):
    if hasattr(context, CACHE_ACTIONS_KEY):
        return getattr(context, CACHE_ACTIONS_KEY)
    data = context.actions_model
    schema = load_schema(data)
    schema.setTaggedValue(CONTEXT_KEY, context)
    setattr(context, CACHE_ACTIONS_KEY, schema)
    return schema


def serialize_schema(schema):
    model = Model({SCHEMATA_KEY: schema})
    sschema = serialize(model)
    return sschema


def set_fields(context, schema):
    delattr(context, CACHE_FIELDS_KEY)
    # serialize the current schema
    snew_schema = serialize_schema(schema)
    # store the current schema
    context.fields_model = snew_schema


def set_actions(context, schema):
    delattr(context, CACHE_ACTIONS_KEY)
    # fix setting widgets
    schema.setTaggedValue('plone.autoform.widgets', {})
    # serialize the current schema
    snew_schema = serialize_schema(schema)
    # store the current schema
    context.actions_model = snew_schema
