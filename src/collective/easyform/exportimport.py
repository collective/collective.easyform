# -*- coding: utf-8 -*-
from collective.easyform.interfaces import IAction
from collective.easyform.interfaces import IActionExtender
from collective.easyform.interfaces import IEasyFormActionsContext
from collective.easyform.interfaces import IEasyFormFieldsContext
from collective.easyform.interfaces import IFieldExtender
from plone.autoform.interfaces import WIDGETS_KEY
from plone.supermodel.parser import IFieldMetadataHandler
from plone.supermodel.utils import ns
from zope.component import adapter
from zope.interface import implementer
from zope.schema.interfaces import IField


@adapter(IEasyFormFieldsContext, IField)
def get_field_extender(context, field):
    return IFieldExtender


def _get_(self, key):
    return self.field.interface.queryTaggedValue(
        key,
        {}
    ).get(self.field.__name__)


def _set_(self, value, key):
    data = self.field.interface.queryTaggedValue(key, {})
    data[self.field.__name__] = value
    self.field.interface.setTaggedValue(key, data)


@implementer(IFieldExtender)
@adapter(IField)
class FieldExtender(object):

    def __init__(self, field):
        self.field = field

    field_widget = property(lambda x: _get_(x, WIDGETS_KEY),
                            lambda x, value: _set_(x, value, WIDGETS_KEY))
    TDefault = property(lambda x: _get_(x, 'TDefault'),
                        lambda x, value: _set_(x, value, 'TDefault'))
    TEnabled = property(lambda x: _get_(x, 'TEnabled'),
                        lambda x, value: _set_(x, value, 'TEnabled'))
    TValidator = property(lambda x: _get_(x, 'TValidator'),
                          lambda x, value: _set_(x, value, 'TValidator'))
    serverSide = property(lambda x: _get_(x, 'serverSide'),
                          lambda x, value: _set_(x, value, 'serverSide'))
    validators = property(lambda x: _get_(x, 'validators'),
                          lambda x, value: _set_(x, value, 'validators'))


@implementer(IFieldMetadataHandler)
class EasyFormFieldMetadataHandler(object):

    """Support the easyform: namespace in model definitions.
    """

    namespace = 'http://namespaces.plone.org/supermodel/easyform'
    prefix = 'easyform'

    def read(self, fieldNode, schema, field):
        name = field.__name__
        for i in ['TDefault', 'TEnabled', 'TValidator']:
            value = fieldNode.get(ns(i, self.namespace))
            if value:
                data = schema.queryTaggedValue(i, {})
                data[name] = value
                schema.setTaggedValue(i, data)
        # serverSide
        value = fieldNode.get(ns('serverSide', self.namespace))
        if value:
            data = schema.queryTaggedValue('serverSide', {})
            data[name] = value == 'True' or value == 'true'
            schema.setTaggedValue('serverSide', data)
        # validators
        value = fieldNode.get(ns('validators', self.namespace))
        if value:
            data = schema.queryTaggedValue('validators', {})
            data[name] = value.split('|')
            schema.setTaggedValue('validators', data)

    def write(self, fieldNode, schema, field):
        name = field.__name__
        for i in ['TDefault', 'TEnabled', 'TValidator']:
            value = schema.queryTaggedValue(i, {}).get(name, None)
            if value:
                fieldNode.set(ns(i, self.namespace), value)
        # serverSide
        value = schema.queryTaggedValue('serverSide', {}).get(name, None)
        if isinstance(value, bool):
            fieldNode.set(ns('serverSide', self.namespace), str(value))
        # validators
        value = schema.queryTaggedValue('validators', {}).get(name, None)
        if value:
            fieldNode.set(ns('validators', self.namespace), "|".join(value))


@adapter(IEasyFormActionsContext, IAction)
def get_action_extender(context, action):
    return IActionExtender


@implementer(IActionExtender)
@adapter(IAction)
class ActionExtender(object):

    def __init__(self, field):
        self.field = field

    execCondition = property(lambda x: _get_(x, 'execCondition'),
                             lambda x, value: _set_(x, value, 'execCondition'))


@implementer(IFieldMetadataHandler)
class EasyFormActionMetadataHandler(object):

    """Support the easyform: namespace in model definitions.
    """

    namespace = 'http://namespaces.plone.org/supermodel/easyform'
    prefix = 'easyform'

    def read(self, fieldNode, schema, field):
        name = field.__name__
        value = fieldNode.get(ns('execCondition', self.namespace))
        data = schema.queryTaggedValue('execCondition', {})
        if value:
            data[name] = value
            schema.setTaggedValue('execCondition', data)

    def write(self, fieldNode, schema, field):
        name = field.__name__
        value = schema.queryTaggedValue('execCondition', {}).get(name, None)
        if value:
            fieldNode.set(ns('execCondition', self.namespace), value)
