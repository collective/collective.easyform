from z3c.form import validator
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IValue
from zope import schema as zs
from zope.component import adapts
from zope.component import queryUtility
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import implements

from collective.formulator.api import get_expression
from collective.formulator.interfaces import IFieldExtender
from collective.formulator.interfaces import IFormulator
from collective.formulator.interfaces import IFormulatorForm
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
