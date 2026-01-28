from .validators import cssClassConstraint
from .validators import isTALES
from collective.easyform import config
from collective.easyform import easyformMessageFactory as _  # NOQA
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.schemaeditor.interfaces import IFieldContext
from plone.schemaeditor.interfaces import IFieldEditorExtender
from plone.schemaeditor.interfaces import ISchemaContext
from plone.schemaeditor.schema import ITextLinesField
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
import z3c.form
from z3c.form.interfaces import IFieldWidget
from zope import schema
from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

import z3c.form.interfaces
import zope.interface
import zope.schema.interfaces


class WidgetVocabulary(SimpleVocabulary):
    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        if not isinstance(value, str):
            value = "{}.{}".format(
                value.widget_factory.__module__, value.widget_factory.__name__
            )
        return self.getTermByToken(value)


@provider(IContextSourceBinder)
def widgetsFactory(context):
    terms = []
    adapters = [
        a.factory
        for a in getGlobalSiteManager().registeredAdapters()
        if (
            a.provided == IFieldWidget
            and len(a.required) == 2
            and a.required[0].providedBy(context)
        )
    ]
    for adapter in set(adapters):
        name = "{}.{}".format(adapter.__module__, adapter.__name__)
        terms.append(WidgetVocabulary.createTerm(name, str(name), adapter.__name__))
    return WidgetVocabulary(terms)


class IEasyFormFieldsEditorExtender(IFieldEditorExtender):
    pass


class IFieldExtender(Schema):
    fieldset(
        "advanced",
        label=_("Advanced"),
        fields=["field_widget", "validators", "THidden", "depends_on", "css_class",],
    )
    directives.write_permission(field_widget=config.EDIT_ADVANCED_PERMISSION)
    field_widget = zope.schema.Choice(
        title=_("label_field_widget", default="Field Widget"),
        description=_("help_field_widget", default=""),
        required=False,
        source=widgetsFactory,
    )
    directives.write_permission(validators=config.EDIT_ADVANCED_PERMISSION)
    validators = zope.schema.List(
        title=_("Validators"),
        description=_(
            "help_userfield_validators",
            default="Select the validators to use on this field",
        ),
        unique=True,
        required=False,
        value_type=zope.schema.Choice(vocabulary="easyform.Validators"),
    )
    directives.write_permission(THidden=config.EDIT_TALES_PERMISSION)
    THidden = zope.schema.Bool(
        title=_("label_hidden", default="Hidden"),
        description=_("help_hidden", default="Field is hidden"),
        required=False,
        default=False,
    )
    directives.write_permission(depends_on=config.EDIT_TALES_PERMISSION)
    depends_on = zope.schema.TextLine(
        title=_(
            'Field depends on',
        ),
        description=_(
            'This is using the pat-depends from patternslib, all options are supported. Please read the <a href="https://patternslib.com/demos/depends" target="_blank">pat-depends documentations</a> for options.',
        ),
        default='',
        required=False,
    )
    directives.write_permission(css_class=config.EDIT_TALES_PERMISSION)
    css_class = zope.schema.TextLine(
        title=_(
            'CSS Class',
        ),
        description=_(
            'Define additional CSS class for this field here. This allowes for formating individual fields via CSS.',
        ),
        default='',
        required=False,
        constraint=cssClassConstraint,
    )
    fieldset(
        "overrides",
        label=_("Overrides"),
        fields=["TDefault", "TEnabled", "TValidator", "serverSide"],
    )
    directives.write_permission(TDefault=config.EDIT_TALES_PERMISSION)
    TDefault = zope.schema.TextLine(
        title=_("label_tdefault_text", default="Default Expression"),
        description=_(
            "help_tdefault_text",
            default="A TALES expression that will be evaluated when the form"
            "is displayed to get the field default value. Leave "
            "empty if unneeded. Your expression should evaluate as a "
            "string. PLEASE NOTE: errors in the evaluation of this "
            "expression will cause an error on form display.",
        ),
        default="",
        constraint=isTALES,
        required=False,
    )
    directives.write_permission(TEnabled=config.EDIT_TALES_PERMISSION)
    TEnabled = zope.schema.TextLine(
        title=_("label_tenabled_text", default="Enabling Expression"),
        description=_(
            "help_tenabled_text",
            default="A TALES expression that will be evaluated when the form "
            "is displayed to determine whether or not the field is "
            "enabled. Your expression should evaluate as True if "
            "the field should be included in the form, False if it "
            "should be omitted. Leave this expression field empty "
            "if unneeded: the field will be included. PLEASE NOTE: "
            "errors in the evaluation of this expression will cause "
            "an error on form display.",
        ),
        default="",
        constraint=isTALES,
        required=False,
    )
    directives.write_permission(TValidator=config.EDIT_TALES_PERMISSION)
    TValidator = zope.schema.TextLine(
        title=_("label_tvalidator_text", default="Custom Validator"),
        description=_(
            "help_tvalidator_text",
            default="A TALES expression that will be evaluated when the form "
            "is validated. Validate against 'value', which will "
            "contain the field input. Return False if valid; if not "
            "valid return a string error message. E.G., "
            "\"python: test(value=='eggs', False, 'input must be "
            'eggs\')" will require "eggs" for input. '
            "PLEASE NOTE: errors in the evaluation of this "
            "expression will cause an error on form display.",
        ),
        default="",
        constraint=isTALES,
        required=False,
    )
    directives.write_permission(serverSide=config.EDIT_TALES_PERMISSION)
    serverSide = zope.schema.Bool(
        title=_("label_server_side_text", default="Server-Side Variable"),
        description=_(
            "description_server_side_text",
            default=""
            "Mark this field as a value to be injected into the "
            "request form for use by action adapters and is not "
            "modifiable by or exposed to the client.",
        ),
        default=False,
        required=False,
    )


class IEasyFormFieldsContext(ISchemaContext):
    """EasyForm schema view interface."""


class IEasyFormFieldContext(IFieldContext):
    """EasyForm field content marker."""


class ILabel(zope.schema.interfaces.IField):
    """Label Field."""


class IRichLabel(ILabel):
    """Rich Label Field."""

    rich_label = RichText(title=_("Rich Label"), default="", missing_value="")


class IEasyFormWidget(z3c.form.interfaces.IWidget):
    """General marker for easyform widgets."""


class ILabelWidget(IEasyFormWidget):
    """Label Widget."""


class IRichLabelWidget(IEasyFormWidget):
    """Rich Label Field Widget."""


class IReCaptcha(zope.schema.interfaces.ITextLine):
    """ReCaptcha Field."""


class IHCaptcha(zope.schema.interfaces.ITextLine):
    """ReCaptcha Field."""


class INorobotCaptcha(zope.schema.interfaces.ITextLine):
    """Norobot Field."""


class ILikert(zope.schema.interfaces.IField):

    questions = zope.schema.List(
        title=_('Possible questions'),
        description=_('Enter allowed choices one per line.'),
        required=zope.schema.interfaces.IChoice['vocabulary'].required,
        default=zope.schema.interfaces.IChoice['vocabulary'].default,
        value_type=zope.schema.TextLine())
    zope.interface.alsoProvides(questions, ITextLinesField)

    answers = zope.schema.List(
        title=_('Possible answers'),
        description=_('Enter allowed choices one per line.'),
        required=zope.schema.interfaces.IChoice['vocabulary'].required,
        default=zope.schema.interfaces.IChoice['vocabulary'].default,
        value_type=zope.schema.TextLine())
    zope.interface.alsoProvides(questions, ITextLinesField)

class ILikertWidget(IEasyFormWidget):
    """Likert widget."""


class IFieldValidator(Interface):
    """Base marker for field validators."""
