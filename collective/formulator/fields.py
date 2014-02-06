# -*- coding: utf-8 -*-

from plone.schemaeditor.fields import FieldFactory
from plone.supermodel.exportimport import BaseHandler
from z3c.form import validator
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IValue
from zope import schema as zs
from zope.component import adapts
from zope.component import queryUtility
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import implements
from zope.schema import Field
from zope.schema._bootstrapinterfaces import IFromUnicode

from collective.formulator import formulatorMessageFactory as _
from collective.formulator.api import get_expression
from collective.formulator.interfaces import IFieldExtender
from collective.formulator.interfaces import IFormulator
from collective.formulator.interfaces import IFormulatorForm
from collective.formulator.interfaces import ILabel
from collective.formulator.interfaces import IRichLabel
from collective.formulator.validators import IFieldValidator


class FieldExtenderValidator(validator.SimpleFieldValidator):

    """ z3c.form validator class for formulator fields """
    implements(IValidator)
    adapts(IFormulator, Interface, IFormulatorForm,
           zs.interfaces.IField, Interface)

    def validate(self, value):
        """ Validate field by TValidator """
        super(FieldExtenderValidator, self).validate(value)
        efield = IFieldExtender(self.field)
        validators = getattr(efield, 'validators', [])
        if validators:
            for validator in validators:
                vmethod = queryUtility(IFieldValidator, name=validator)
                if not vmethod:
                    continue
                res = vmethod(value)
                if res:
                    raise Invalid(res)
        TValidator = getattr(efield, 'TValidator', None)
        if TValidator:
            try:
                cerr = get_expression(self.context, TValidator, value=value)
            except Exception as e:
                raise Invalid(e)
            if cerr:
                raise Invalid(cerr)


class FieldExtenderDefault(object):

    """ z3c.form default class for formulator fields """
    implements(IValue)
    adapts(IFormulator, Interface, IFormulatorForm,
           zs.interfaces.IField, Interface)

    def __init__(self, context, request, view, field, widget):
        self.context = context
        self.request = request
        self.view = view
        self.field = field
        self.widget = widget

    def get(self):
        """ get default value of field from TDefault """
        fdefault = self.field.default
        efield = IFieldExtender(self.field)
        TDefault = getattr(efield, 'TDefault', None)
        return get_expression(self.context, TDefault) if TDefault else fdefault


@implementer(IFromUnicode)
class Label(Field):

    """A Label field
    """
    implements(ILabel)

    def validate(self, value):
        pass

    def fromUnicode(self, str):
        """
        """
        return


class RichLabel(Label):

    """A Rich Label field
    """
    implements(IRichLabel)
    rich_label = u''

    def __init__(self, rich_label=u'', **kw):
        self.rich_label = rich_label
        super(RichLabel, self).__init__(**kw)

LabelFactory = FieldFactory(Label, _(u'label_label_field', default=u'Label'))
RichLabelFactory = FieldFactory(
    RichLabel, _(u'label_richlabel_field', default=u'Rich Label'))

LabelHandler = BaseHandler(Label)
RichLabelHandler = BaseHandler(RichLabel)
