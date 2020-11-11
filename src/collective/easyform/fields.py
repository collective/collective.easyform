# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _
from collective.easyform.api import get_expression
from collective.easyform.interfaces import IEasyForm
from collective.easyform.interfaces import IEasyFormForm
from collective.easyform.interfaces import IFieldExtender
from collective.easyform.interfaces import ILabel
from collective.easyform.interfaces import INorobotCaptcha
from collective.easyform.interfaces import IReCaptcha
from collective.easyform.interfaces import IRichLabel
from collective.easyform.validators import IFieldValidator
from plone.schemaeditor.fields import FieldFactory
from plone.supermodel.exportimport import BaseHandler
from z3c.form.interfaces import IGroup
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IValue
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import providedBy
from zope.schema import Field
from zope.schema import TextLine
from zope.schema._bootstrapinterfaces import IFromUnicode
from zope.schema.interfaces import IField


def superAdapter(specific_interface, adapter, objects, name=u""):
    """Find the next most specific adapter.

    This is called by a FieldExtenderValidator or FieldExtenderDefault instance.
    This is passed in with the 'adapter' parameter.
    This adapter itself is not a real validator or default factory,
    but is used to find other real validators or default factories.

    This may sound strange, but it solves a problem.
    Problem is that validators and default were not always found for fields in field sets.
    For example, a captcha field in the main form would get validated by its proper validator,
    but when in a field set, only a basic validator would be found.

    We are adjusting the view object class to provide IForm rather than
    IEasyFormForm or IGroup to make one of the objects less specific.
    Same for the default factory.
    This allows us to find another adapter other than the current one.
    This allows us to find any custom adapters for any fields that we have overridden

    """
    new_obj = []
    found = False
    for obj in objects:
        interfaces = list(providedBy(obj).interfaces())
        try:
            index = interfaces.index(specific_interface)
            found = True
        except ValueError:
            pass
        else:
            super_inferface = interfaces[index + 1]

            @implementer(super_inferface)
            class Wrapper(object):
                def __init__(self, view):
                    self.__view__ = view

                def __getattr__(self, item):
                    return getattr(self.__view__, item)

            obj = Wrapper(obj)  # Make one class less specific
        new_obj.append(obj)
    if not found:
        return None

    provided_by = providedBy(adapter)
    # With zope.interface 5.0.2, the info we seek is in 'declared'.
    # With 5.1.0+, it can also be in the 'interfaces()' iterator,
    # especially for groups (field sets).
    # But it looks like interfaces() works always.
    # adapter_interfaces = provided_by.declared
    # if not adapter_interfaces:
    adapter_interfaces = list(provided_by.interfaces())
    if not adapter_interfaces:
        return

    return queryMultiAdapter(new_obj, adapter_interfaces[0], name=name)


@implementer(IValidator)
@adapter(IEasyForm, Interface, IEasyFormForm, IField, Interface)
class FieldExtenderValidator(object):
    """z3c.form validator class for easyform fields in the default fieldset
    """

    def __init__(self, context, request, view, field, widget):
        self.context = context
        self.request = request
        self.view = view
        self.field = field
        self.widget = widget

    def validate(self, value):
        """Validate field by TValidator
        """
        # By default this will call SimpleFieldValidator.validator but allows for a fields
        # custom validation adaptor to also be called such as recaptcha
        _, _, view_interface, _, _ = self.__class__.__component_adapts__
        validator = superAdapter(
            view_interface,
            self,
            (self.context, self.request, self.view, self.field, self.widget),
        )
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
    """z3c.form validator class for easyform fields in fieldset groups
    """

    pass


@implementer(IValue)
@adapter(IEasyForm, Interface, IEasyFormForm, IField, Interface)
class FieldExtenderDefault(object):
    """z3c.form default class for easyform fields in the default fieldset
    """

    def __init__(self, context, request, view, field, widget):
        self.context = context
        self.request = request
        self.view = view
        self.field = field
        self.widget = widget

    def get(self):
        """Get default value of field from TDefault
        """
        efield = IFieldExtender(self.field)
        TDefault = getattr(efield, "TDefault", None)
        if TDefault:
            return get_expression(self.context, TDefault)

        # see if there is another default adapter for this field instead
        _, _, view_interface, _, _ = self.__class__.__component_adapts__
        adapter = superAdapter(
            view_interface,
            self,
            (self.context, self.request, self.view, self.field, self.widget),
            name="default",
        )
        if adapter is not None:
            return adapter.get()
        else:
            # TODO: this should have already been done by z3c.form.widget.update() so shouldn't be needed
            return self.field.default


@implementer(IValue)
@adapter(IEasyForm, Interface, IGroup, IField, Interface)
class GroupFieldExtenderDefault(FieldExtenderDefault):
    """z3c.form default class for easyform fields in fieldset groups
    """

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
    NorobotCaptcha, _(u"label_norobot_field", default=u"NorobotCaptcha")
)
NorobotCaptchaHandler = BaseHandler(NorobotCaptcha)
