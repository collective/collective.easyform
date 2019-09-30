# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _
from collective.easyform.api import get_expression
from collective.easyform.interfaces import IEasyForm
from collective.easyform.interfaces import IEasyFormForm
from collective.easyform.interfaces import IFieldExtender
from collective.easyform.interfaces import ILabel
from collective.easyform.interfaces import IReCaptcha
from collective.easyform.interfaces import INorobotCaptcha
from collective.easyform.interfaces import IRichLabel
from collective.easyform.validators import IFieldValidator
from plone.schemaeditor.fields import FieldFactory
from plone.supermodel.exportimport import BaseHandler
from z3c.form.interfaces import IGroup, IForm
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IValue
from zope.component import adapter, queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid
from zope.schema import Field
from zope.schema import TextLine
from zope.schema._bootstrapinterfaces import IFromUnicode
from zope.schema.interfaces import IField

def LessSpecificInterfaceWrapper(view, interface):
    """ rewrap an adapter so it its class implements a different interface """

    @implementer(interface)
    class Wrapper(object):
        def __init__(self, view):
            self.__view__ = view

        def __getattr__(self, item):
            return getattr(self.__view__, item)

    return Wrapper(view)


@implementer(IValidator)
@adapter(IEasyForm, Interface, IEasyFormForm, IField, Interface)
class FieldExtenderValidator(object):
    """ z3c.form validator class for easyform fields in the default fieldset"""

    def __init__(self, context, request, view, field, widget):
        self.context = context
        self.request = request
        self.view = view
        self.field = field
        self.widget = widget

    def validate(self, value):
        """ Validate field by TValidator """
        view = LessSpecificInterfaceWrapper(self.view, IForm)
        # view now doesn't implement IEasyFormForm so we can call another less specific validation adapter
        # that might exist for this field. The above line prevents a loop.
        # By default this will call SimpleFieldValidator.validator but allows for special fields
        # custom validation to also be called

        validator = queryMultiAdapter((self.context, self.request, view, self.field, self.widget), IValidator)
        if validator is not None:
            validator.validate(value)

        efield = IFieldExtender(self.field)
        validators = getattr(efield, "validators", [])
        if validators:
            for validator in validators:
                vmethod = queryUtility(IFieldValidator, name=validator)
                if not vmethod:
                    continue
                res = vmethod(value)
                if res:
                    raise Invalid(res)
        TValidator = getattr(efield, "TValidator", None)
        if TValidator:
            try:
                cerr = get_expression(self.context, TValidator, value=value)
            except Exception as e:
                raise Invalid(e)
            if cerr:
                raise Invalid(cerr)


@implementer(IValidator)
@adapter(IEasyForm, Interface, IGroup, IField, Interface)
class GroupFieldExtenderValidator(FieldExtenderValidator):
    """ z3c.form validator class for easyform fields in fieldset groups """

    pass


@implementer(IValue)
@adapter(IEasyForm, Interface, IEasyFormForm, IField, Interface)
class FieldExtenderDefault(object):

    """ z3c.form default class for easyform fields in the default fieldset """

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
        TDefault = getattr(efield, "TDefault", None)
        if TDefault:
            return get_expression(self.context, TDefault)

        # see if there is another default adapter for this field instead
        view = LessSpecificInterfaceWrapper(self.view, IForm)
        adapter = queryMultiAdapter((self.context, self.request, view, self.field, self.widget), IValue, name='default')
        if adapter is not None:
            return adapter.get()
        else:
            # TODO: this should have already been done by z3c.form.widget.update() so shouldn't be needed
            return self.field.default


@implementer(IValue)
@adapter(IEasyForm, Interface, IGroup, IField, Interface)
class GroupFieldExtenderDefault(FieldExtenderDefault):

    """ z3c.form default class for easyform fields in fieldset groups """

    pass


@implementer(IFromUnicode, ILabel)
class Label(Field):

    """A Label field
    """

    def validate(self, value):
        pass

    def fromUnicode(self, str):
        """
        """
        return


@implementer(IRichLabel)
class RichLabel(Label):

    """A Rich Label field
    """

    rich_label = u""

    def __init__(self, rich_label=u"", **kw):
        self.rich_label = rich_label
        super(RichLabel, self).__init__(**kw)


LabelFactory = FieldFactory(Label, _(u"label_label_field", default=u"Label"))
RichLabelFactory = FieldFactory(
    RichLabel, _(u"label_richlabel_field", default=u"Rich Label")
)

LabelHandler = BaseHandler(Label)
RichLabelHandler = BaseHandler(RichLabel)


@implementer(IReCaptcha)
class ReCaptcha(TextLine):

    """A ReCaptcha field
    """


ReCaptchaFactory = FieldFactory(
    ReCaptcha, _(u"label_recaptcha_field", default=u"ReCaptcha")
)
ReCaptchaHandler = BaseHandler(ReCaptcha)


@implementer(INorobotCaptcha)
class NorobotCaptcha(TextLine):

    """A NorobotCaptcha field
    """


NorobotFactory = FieldFactory(
    NorobotCaptcha,
    _(u'label_norobot_field', default=u'NorobotCaptcha')
)
NorobotCaptchaHandler = BaseHandler(NorobotCaptcha)
