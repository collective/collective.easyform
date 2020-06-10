# -*- coding: utf-8 -*-
from .validators import isTALES
from collective.easyform import config
from collective.easyform import easyformMessageFactory as _  # NOQA
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.schemaeditor.interfaces import IFieldContext
from plone.schemaeditor.interfaces import IFieldEditorExtender
from plone.schemaeditor.interfaces import ISchemaContext
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
from z3c.form.interfaces import IFieldWidget
from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

import six
import z3c.form.interfaces
import zope.interface
import zope.schema.interfaces


class WidgetVocabulary(SimpleVocabulary):
    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        if not isinstance(value, six.string_types):
            value = "{0}.{1}".format(
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
        name = u"{0}.{1}".format(adapter.__module__, adapter.__name__)
        terms.append(WidgetVocabulary.createTerm(name, str(name), adapter.__name__))
    return WidgetVocabulary(terms)


class IEasyFormFieldsEditorExtender(IFieldEditorExtender):
    pass


class IFieldExtender(Schema):
    fieldset(
        u"advanced",
        label=_("Advanced"),
        fields=["field_widget", "validators", "THidden"],
    )
    directives.write_permission(field_widget=config.EDIT_ADVANCED_PERMISSION)
    field_widget = zope.schema.Choice(
        title=_(u"label_field_widget", default=u"Field Widget"),
        description=_(u"help_field_widget", default=u""),
        required=False,
        source=widgetsFactory,
    )
    directives.write_permission(validators=config.EDIT_ADVANCED_PERMISSION)
    validators = zope.schema.List(
        title=_("Validators"),
        description=_(
            u"help_userfield_validators",
            default=u"Select the validators to use on this field",
        ),
        unique=True,
        required=False,
        value_type=zope.schema.Choice(vocabulary="easyform.Validators"),
    )
    directives.write_permission(THidden=config.EDIT_TALES_PERMISSION)
    THidden = zope.schema.Bool(
        title=_(u"label_hidden", default=u"Hidden"),
        description=_(u"help_hidden", default=u"Field is hidden"),
        required=False,
        default=False,
    )
    fieldset(
        u"overrides",
        label=_("Overrides"),
        fields=["TDefault", "TEnabled", "TValidator", "serverSide"],
    )
    directives.write_permission(TDefault=config.EDIT_TALES_PERMISSION)
    TDefault = zope.schema.TextLine(
        title=_(u"label_tdefault_text", default=u"Default Expression"),
        description=_(
            u"help_tdefault_text",
            default=u"A TALES expression that will be evaluated when the form"
            u"is displayed to get the field default value. Leave "
            u"empty if unneeded. Your expression should evaluate as a "
            u"string. PLEASE NOTE: errors in the evaluation of this "
            u"expression will cause an error on form display.",
        ),
        default=u"",
        constraint=isTALES,
        required=False,
    )
    directives.write_permission(TEnabled=config.EDIT_TALES_PERMISSION)
    TEnabled = zope.schema.TextLine(
        title=_(u"label_tenabled_text", default=u"Enabling Expression"),
        description=_(
            u"help_tenabled_text",
            default=u"A TALES expression that will be evaluated when the form "
            u"is displayed to determine whether or not the field is "
            u"enabled. Your expression should evaluate as True if "
            u"the field should be included in the form, False if it "
            u"should be omitted. Leave this expression field empty "
            u"if unneeded: the field will be included. PLEASE NOTE: "
            u"errors in the evaluation of this expression will cause "
            u"an error on form display.",
        ),
        default=u"",
        constraint=isTALES,
        required=False,
    )
    directives.write_permission(TValidator=config.EDIT_TALES_PERMISSION)
    TValidator = zope.schema.TextLine(
        title=_(u"label_tvalidator_text", default=u"Custom Validator"),
        description=_(
            u"help_tvalidator_text",
            default=u"A TALES expression that will be evaluated when the form "
            u"is validated. Validate against 'value', which will "
            u"contain the field input. Return False if valid; if not "
            u"valid return a string error message. E.G., "
            u"\"python: test(value=='eggs', False, 'input must be "
            u'eggs\')" will require "eggs" for input. '
            u"PLEASE NOTE: errors in the evaluation of this "
            u"expression will cause an error on form display.",
        ),
        default=u"",
        constraint=isTALES,
        required=False,
    )
    directives.write_permission(serverSide=config.EDIT_TALES_PERMISSION)
    serverSide = zope.schema.Bool(
        title=_(u"label_server_side_text", default=u"Server-Side Variable"),
        description=_(
            u"description_server_side_text",
            default=u""
            u"Mark this field as a value to be injected into the "
            u"request form for use by action adapters and is not "
            u"modifiable by or exposed to the client.",
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

    rich_label = RichText(title=_(u"Rich Label"), default=u"", missing_value=u"")


class ILabelWidget(z3c.form.interfaces.IWidget):
    """Label Widget."""


class IRichLabelWidget(ILabelWidget):
    """Rich Label Field Widget."""


class IReCaptcha(zope.schema.interfaces.ITextLine):
    """ReCaptcha Field."""


class INorobotCaptcha(zope.schema.interfaces.ITextLine):
    """Norobot Field."""


class IFieldValidator(Interface):
    """Base marker for field validators."""
