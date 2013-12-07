from plone.supermodel import loadString
from plone.supermodel.model import Model
from plone.supermodel.serializer import serialize
from plone.directives.form import Schema

SCHEMATA_KEY = u""
CONTEXT_KEY = u"context"


def get_expression(context, expression_string):
    expression = Expression(expression_string)
    expression_context = getExprContext(context)
    return expression(expression_context)


def get_context(field):
    return field.interface.getTaggedValue(CONTEXT_KEY)


def load_schema(sschema):
    try:
        schema = loadString(sschema).schemata.get(SCHEMATA_KEY, Schema)
    except Exception:
        schema = Schema
    schema = loadString(sschema).schemata.get(SCHEMATA_KEY, Schema)
    return schema


def get_schema(context):
    data = context.model
    schema = load_schema(data)
    schema.setTaggedValue(CONTEXT_KEY, context)
    return schema


def get_actions(context):
    data = context.actions_model
    schema = load_schema(data)
    schema.setTaggedValue(CONTEXT_KEY, context)
    return schema


def serialize_schema(schema):
    model = Model({SCHEMATA_KEY: schema})
    sschema = serialize(model)
    return sschema


def set_schema(context, schema):
    # serialize the current schema
    snew_schema = serialize_schema(schema)
    # store the current schema
    context.model = snew_schema


def set_actions(context, schema):
    # serialize the current schema
    snew_schema = serialize_schema(schema)
    # store the current schema
    context.actions_model = snew_schema
