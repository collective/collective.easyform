from .validators import isTALES
from collective.easyform import config
from collective.easyform import easyformMessageFactory as _  # NOQA
from plone import api
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
from plone.base.utils import safe_text
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import provider

import zope.i18nmessageid
import zope.interface
import zope.schema.interfaces


PMF = zope.i18nmessageid.MessageFactory("plone")


@provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_submitLabel(context):
    return translate(
        _("default_submitLabel", "Submit"),
        target_language=api.portal.get_current_language(),
    )


@provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_resetLabel(context):
    return translate(
        _("default_resetLabel", "Reset"),
        target_language=api.portal.get_current_language(),
    )


@provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_thankstitle(context):
    return translate(
        _("default_thankstitle", "Thank You"),
        target_language=api.portal.get_current_language(),
    )


@provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_thanksdescription(context):
    return translate(
        _("default_thanksdescription", "Thanks for your input."),
        target_language=api.portal.get_current_language(),
    )


@zope.interface.provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_actions(context):
    """Default mail body for mailer action.
    Acquire 'mail_body_default.pt' or return hard coded default
    """
    portal = api.portal.get()
    default_actions = portal.restrictedTraverse(
        "easyform_default_actions.xml", default=None
    )
    if default_actions:
        return safe_text(default_actions.file.data)
    else:
        return config.ACTIONS_DEFAULT


@zope.interface.provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_fields(context):
    """Default form fields.
    Acquire 'easyform_default_fields.xml' or return hard coded default
    """
    portal = api.portal.get()
    default_fields = portal.restrictedTraverse(
        "easyform_default_fields.xml", default=None
    )
    if default_fields:
        return safe_text(default_fields.file.data)
    else:
        return config.FIELDS_DEFAULT


class IEasyForm(Schema):
    """Forms for Plone."""

    directives.omitted("fields_model", "actions_model")
    fields_model = zope.schema.Text(
        title=_("Fields Model"), defaultFactory=default_fields
    )
    actions_model = zope.schema.Text(
        title=_("Actions Model"), defaultFactory=default_actions
    )

    # DEFAULT
    formPrologue = RichText(
        title=_("label_prologue_text", default="Form Prologue"),
        description=_(
            "help_prologue_text",
            default="This text will be displayed above the form fields.",
        ),
        required=False,
    )
    formEpilogue = RichText(
        title=_("label_epilogue_text", default="Form Epilogue"),
        description=_(
            "help_epilogue_text",
            default="The text will be displayed after the form fields.",
        ),
        required=False,
    )

    # THANKYOU
    fieldset(
        "thankyou",
        label=_("Thanks Page"),
        fields=[
            "thankstitle",
            "thanksdescription",
            "showAll",
            "showFields",
            "includeEmpties",
            "thanksPrologue",
            "thanksEpilogue",
        ],
        order=10,
    )
    thankstitle = zope.schema.TextLine(
        title=_("label_thankstitle", default="Thanks title"),
        defaultFactory=default_thankstitle,
        required=True,
    )
    thanksdescription = zope.schema.Text(
        title=_("label_thanksdescription", default="Thanks summary"),
        description=_("help_thanksdescription", default="Used in thanks page."),
        defaultFactory=default_thanksdescription,
        required=False,
        missing_value="",
    )
    showAll = zope.schema.Bool(
        title=_("label_showallfields_text", default="Show All Fields"),
        description=_(
            "help_showallfields_text",
            default=""
            "Check this to display input for all fields "
            "(except label and file fields). If you check "
            "this, the choices in the pick box below "
            "will be ignored.",
        ),
        default=True,
        required=False,
    )
    showFields = zope.schema.List(
        title=_("label_showfields_text", default="Show Responses"),
        description=_(
            "help_showfields_text",
            default="Pick the fields whose inputs you'd like to display on "
            "the success page.",
        ),
        unique=True,
        required=False,
        value_type=zope.schema.Choice(vocabulary="easyform.Fields"),  # noqa
    )
    includeEmpties = zope.schema.Bool(
        title=_("label_includeEmpties_text", default="Include Empties"),
        description=_(
            "help_includeEmpties_text",
            default=""
            "Check this to display field titles "
            "for fields that received no input. Uncheck "
            "to leave fields with no input off the list.",
        ),
        default=True,
        required=False,
    )
    thanksPrologue = RichText(
        title=_("label_thanksprologue_text", default="Thanks Prologue"),
        description=_(
            "help_thanksprologue_text",
            default="This text will be displayed above the selected field " "inputs.",
        ),
        required=False,
    )
    thanksEpilogue = RichText(
        title=_("label_thanksepilogue_text", default="Thanks Epilogue"),
        description=_(
            "help_thanksepilogue_text",
            default="The text will be displayed after the field inputs.",
        ),
        required=False,
    )

    # ADVANCED
    fieldset(
        "advanced",
        label=_("Advanced"),
        fields=[
            "submitLabel",
            "useCancelButton",
            "resetLabel",
            "form_tabbing",
            "autofocus",
            "nameAttribute",
            "default_fieldset_label",
            "method",
            "unload_protection",
            "CSRFProtection",
            "forceSSL",
        ],
        order=20,
    )
    submitLabel = zope.schema.TextLine(
        title=_("label_submitlabel_text", default="Submit Button Label"),
        description=_("help_submitlabel_text", default=""),
        defaultFactory=default_submitLabel,
        required=False,
    )
    useCancelButton = zope.schema.Bool(
        title=_("label_showcancel_text", default="Show Reset Button"),
        description=_("help_showcancel_text", default=""),
        default=False,
        required=False,
    )
    resetLabel = zope.schema.TextLine(
        title=_("label_reset_button", default="Reset Button Label"),
        description=_("help_reset_button", default=""),
        defaultFactory=default_resetLabel,
        required=False,
    )
    nameAttribute = zope.schema.TextLine(
        title=_("label_name_attribute", default="Name attribute"),
        description=_(
            "help_name_attribute",
            default="optional, sets the name attribute on the form container. " \
                    "can be used for form analytics"),
        required=False,
    )
    directives.write_permission(form_tabbing=config.EDIT_ADVANCED_PERMISSION)
    form_tabbing = zope.schema.Bool(
        title=_("label_form_tabbing", default="Turn fieldsets to tabs"),
        description=_("help_form_tabbing", default=""),
        default=True,
        required=False,
    )
    directives.write_permission(autofocus=config.EDIT_ADVANCED_PERMISSION)
    autofocus = zope.schema.Bool(
        title=_("label_autofocus", default="Enable focus on the first input"),
        description=_("help_autofocus", default=""),
        default=True,
        required=False,
    )
    directives.write_permission(default_fieldset_label=config.EDIT_ADVANCED_PERMISSION)
    default_fieldset_label = zope.schema.TextLine(
        title=_(
            "label_default_fieldset_label_text",
            default="Custom Default Fieldset Label",
        ),
        description=_(
            "help_default_fieldset_label_text",
            default="This field allows you to change default fieldset label.",
        ),
        required=False,
        default="",
    )
    directives.write_permission(method=config.EDIT_TECHNICAL_PERMISSION)
    method = zope.schema.Choice(
        title=_("label_method", default="Form method"),
        description=_("help_method", default=""),
        default="post",
        required=False,
        vocabulary="easyform.FormMethods",
    )
    directives.write_permission(unload_protection=config.EDIT_TECHNICAL_PERMISSION)
    unload_protection = zope.schema.Bool(
        title=_("label_unload_protection", default="Unload protection"),
        description=_("help_unload_protection", default=""),
        default=True,
        required=False,
    )
    directives.write_permission(CSRFProtection=config.EDIT_TECHNICAL_PERMISSION)
    CSRFProtection = zope.schema.Bool(
        title=_("label_csrf", default="CSRF Protection"),
        description=_(
            "help_csrf",
            default="Check this to employ Cross-Site "
            "Request Forgery protection. Note that only HTTP Post "
            "actions will be allowed.",
        ),
        default=True,
        required=False,
    )
    directives.write_permission(forceSSL=config.EDIT_TECHNICAL_PERMISSION)
    forceSSL = zope.schema.Bool(
        title=_("label_force_ssl", default="Force SSL connection"),
        description=_(
            "help_force_ssl",
            default="Check this to make the form redirect to an SSL-enabled "
            "version of itself (https://) if accessed via a non-SSL "
            "URL (http://).  In order to function properly, "
            "this requires a web server that has been configured to "
            "handle the HTTPS protocol on port 443 and forward it to "
            "Zope.",
        ),
        default=False,
        required=False,
    )

    # OVERRIDES
    fieldset(
        "overrides",
        label=_("Overrides"),
        fields=[
            "thanksPageOverrideAction",
            "thanksPageOverride",
            "formActionOverride",
            "onDisplayOverride",
            "afterValidationOverride",
            "headerInjection",
            "submitLabelOverride",
        ],
        order=30,
    )
    directives.write_permission(thanksPageOverrideAction=config.EDIT_TALES_PERMISSION)
    thanksPageOverrideAction = zope.schema.Choice(
        title=_(
            "label_thankspageoverrideaction_text",
            default="Custom Success Action Type",
        ),
        description=_(
            "help_thankspageoverrideaction_text",
            default="Use this field in place of a thanks-page designation "
            "to determine final action after calling "
            "your action adapter (if you have one). You would "
            "usually use this for a custom success template or "
            "script. Leave empty if unneeded. Otherwise, specify as "
            "you would a CMFFormController action type and argument, "
            "complete with type of action to execute "
            '(e.g., "redirect_to" or "traverse_to") '
            "and a TALES expression. For example, "
            '"Redirect to" and "string:thanks-page" would redirect '
            'to "thanks-page".',
        ),
        default="redirect_to",
        required=False,
        vocabulary="easyform.CustomActions",
    )
    directives.write_permission(thanksPageOverride=config.EDIT_TALES_PERMISSION)
    thanksPageOverride = zope.schema.TextLine(
        title=_("label_thankspageoverride_text", default="Custom Success Action"),
        description=_(
            "help_thankspageoverride_text",
            default="Use this field in place of a thanks-page designation "
            "to determine final action after calling your action "
            "adapter (if you have one). You would usually use "
            "this for a custom success template or script. "
            "Leave empty if unneeded. Otherwise, specify as you "
            "would a CMFFormController action type and argument, "
            "complete with type of action to execute "
            '(e.g., "redirect_to" or "traverse_to") '
            "and a TALES expression. For example, "
            '"Redirect to" and "string:thanks-page" would redirect '
            'to "thanks-page".',
        ),
        default="",
        constraint=isTALES,
        required=False,
    )
    directives.write_permission(formActionOverride=config.EDIT_TALES_PERMISSION)
    formActionOverride = zope.schema.TextLine(
        title=_("label_formactionoverride_text", default="Custom Form Action"),
        description=_(
            "help_formactionoverride_text",
            default="Use this field to override the form action attribute. "
            "Specify a URL to which the form will post. "
            "This will bypass form validation, success action "
            "adapter and thanks page.",
        ),
        default="",
        required=False,
        constraint=isTALES,
    )
    directives.write_permission(onDisplayOverride=config.EDIT_TALES_PERMISSION)
    onDisplayOverride = zope.schema.TextLine(
        title=_("label_OnDisplayOverride_text", default="Form Setup Script"),
        description=_(
            "help_OnDisplayOverride_text",
            default="A TALES expression that will be called when the form is "
            "displayed. Leave empty if unneeded. The most common "
            "use of this field is to call a python script that "
            "sets defaults for multiple fields by pre-populating "
            "request.form. "
            "Any value returned by the expression is ignored. "
            "PLEASE NOTE: errors in the evaluation of this "
            "expression will cause an error on form display.",
        ),
        constraint=isTALES,
        required=False,
        default="",
    )
    directives.write_permission(afterValidationOverride=config.EDIT_TALES_PERMISSION)
    afterValidationOverride = zope.schema.TextLine(
        title=_(
            "label_AfterValidationOverride_text", default="After Validation Script"
        ),
        description=_(
            "help_AfterValidationOverride_text",
            default="A TALES expression that will be called after the form is"
            "successfully validated, but before calling an action "
            "adapter (if any) or displaying a thanks page."
            "Form input will be in the request.form dictionary."
            "Leave empty if unneeded. The most "
            "common use of this field is to call a python script"
            "to clean up form input or to script an alternative "
            "action. Any value returned by the expression is ignored."
            "PLEASE NOTE: errors in the evaluation of this "
            "expression willcause an error on form display.",
        ),
        constraint=isTALES,
        required=False,
        default="",
    )
    directives.write_permission(headerInjection=config.EDIT_TALES_PERMISSION)
    headerInjection = zope.schema.TextLine(
        title=_("label_headerInjection_text", default="Header Injection"),
        description=_(
            "help_headerInjection_text",
            default="This override field allows you to insert content into "
            "the xhtml head. The typical use is to add custom CSS "
            "or JavaScript. Specify a TALES expression returning a "
            "string. The string will be inserted with no "
            "interpretation. PLEASE NOTE: errors in the evaluation "
            "of this expression will cause an error on form display.",
        ),
        constraint=isTALES,
        required=False,
        default="",
    )
    directives.write_permission(submitLabelOverride=config.EDIT_TALES_PERMISSION)
    submitLabelOverride = zope.schema.TextLine(
        title=_(
            "label_submitlabeloverride_text", default="Custom Submit Button Label"
        ),
        description=_(
            "help_submitlabeloverride_text",
            default="This override field allows you to change submit button "
            "label. The typical use is to set label with request "
            "parameters. Specify a TALES expression returning a "
            "string. PLEASE NOTE: errors in the evaluation of this "
            "expression will cause an error on form display.",
        ),
        constraint=isTALES,
        required=False,
        default="",
    )


class IEasyFormImportFormSchema(Interface):
    """Schema for easyform import form."""

    upload = zope.schema.Bytes(title=PMF("Upload"), required=True)


class IEasyFormThanksPage(Interface):
    """Marker interface for thanks page."""


class IRenderWidget(Interface):
    """Marker for widget render BrowserView"""
