# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _  # NOQA
from collective.easyform import config
from collective.easyform import vocabularies
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.supermodel.model import fieldset
from plone.supermodel.model import Schema
from validators import isTALES
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import provider

import zope.i18nmessageid
import zope.interface
import zope.schema.interfaces


PMF = zope.i18nmessageid.MessageFactory('plone')


@provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_submitLabel(context):
    return translate(
        'default_submitLabel',
        'collective.easyform',
        default=u'Submit',
        context=getRequest()
    )


# dummy msgid for i18ndude to translate
dummy = _(u'default_submitLabel', u'Submit')


@provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_resetLabel(context):
    return translate(
        'default_resetLabel',
        'collective.easyform',
        default=u'Reset',
        context=getRequest()
    )


# dummy msgid for i18ndude to translate
dummy = _(u'default_resetLabel', u'Reset')


@provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_thankstitle(context):
    return translate(
        'default_thankstitle',
        'collective.easyform',
        default=u'Thank You',
        context=getRequest()
    )


# dummy msgid for i18ndude to translate
dummy = _(u'default_thankstitle', u'Thank You')


@provider(zope.schema.interfaces.IContextAwareDefaultFactory)
def default_thanksdescription(context):
    return translate(
        'default_thanksdescription',
        'collective.easyform',
        default=u'Thanks for your input.',
        context=getRequest()
    )


# dummy msgid for i18ndude to translate
dummy = _(u'default_thanksdescription', u'Thanks for your input.')


class IEasyForm(Schema):

    """Forms for Plone"""

#     fieldset(u'models', label=_('Models'),
#                   fields=['fields_model', 'actions_model'])
    directives.omitted('fields_model', 'actions_model')
    fields_model = zope.schema.Text(
        title=_(u'Fields Model'),
        default=config.FIELDS_DEFAULT,
    )
    actions_model = zope.schema.Text(
        title=_(u'Actions Model'),
        default=config.ACTIONS_DEFAULT,
    )
    submitLabel = zope.schema.TextLine(
        title=_(u'label_submitlabel_text', default=u'Submit Button Label'),
        description=_(u'help_submitlabel_text', default=u''),
        defaultFactory=default_submitLabel,
        required=False,
    )
    useCancelButton = zope.schema.Bool(
        title=_(u'label_showcancel_text', default=u'Show Reset Button'),
        description=_(u'help_showcancel_text', default=u''),
        default=False,
        required=False,
    )
    resetLabel = zope.schema.TextLine(
        title=_(u'label_reset_button', default=u'Reset Button Label'),
        description=_(u'help_reset_button', default=u''),
        defaultFactory=default_resetLabel,
        required=False,
    )
    method = zope.schema.Choice(
        title=_(u'label_method', default=u'Form method'),
        description=_(u'help_method', default=u''),
        default=u'post',
        required=False,
        vocabulary=vocabularies.FORM_METHODS,
    )
    form_tabbing = zope.schema.Bool(
        title=_(u'label_form_tabbing',
                default=u'Turn fieldsets to tabs'),
        description=_(u'help_form_tabbing', default=u''),
        default=True,
        required=False,
    )
    default_fieldset_label = zope.schema.TextLine(
        title=_(u'label_default_fieldset_label_text',
                default=u'Custom Default Fieldset Label'),
        description=_(
            u'help_default_fieldset_label_text',
            default=u'This field allows you to change default fieldset label.'
        ),
        required=False,
        default=u'',
    )
    unload_protection = zope.schema.Bool(
        title=_(u'label_unload_protection',
                default=u'Unload protection'),
        description=_(u'help_unload_protection', default=u''),
        default=True,
        required=False,
    )
    CSRFProtection = zope.schema.Bool(
        title=_(u'label_csrf', default=u'CSRF Protection'),
        description=_(u'help_csrf', default=u'Check this to employ Cross-Site '
                      u'Request Forgery protection. Note that only HTTP Post '
                      u'actions will be allowed.'),
        default=True,
        required=False,
    )
    directives.write_permission(forceSSL=config.EDIT_ADVANCED_PERMISSION)
    forceSSL = zope.schema.Bool(
        title=_(u'label_force_ssl', default=u'Force SSL connection'),
        description=_(
            u'help_force_ssl',
            default=u'Check this to make the form redirect to an SSL-enabled '
                    u'version of itself (https://) if accessed via a non-SSL '
                    u'URL (http://).  In order to function properly, '
                    u'this requires a web server that has been configured to '
                    u'handle the HTTPS protocol on port 443 and forward it to '
                    u'Zope.'
        ),
        default=False,
        required=False,
    )
    formPrologue = RichText(
        title=_(u'label_prologue_text', default=u'Form Prologue'),
        description=_(
            u'help_prologue_text',
            default=u'This text will be displayed above the form fields.'
        ),
        required=False,
    )
    formEpilogue = RichText(
        title=_(u'label_epilogue_text', default=u'Form Epilogue'),
        description=_(
            u'help_epilogue_text',
            default=u'The text will be displayed after the form fields.'
        ),
        required=False,
    )
    fieldset(
        u'overrides',
        label=_('Overrides'),
        fields=[
            'thanksPageOverrideAction',
            'thanksPageOverride',
            'formActionOverride',
            'onDisplayOverride',
            'afterValidationOverride',
            'headerInjection',
            'submitLabelOverride'
        ]
    )
    directives.write_permission(
        thanksPageOverrideAction=config.EDIT_TALES_PERMISSION)
    thanksPageOverrideAction = zope.schema.Choice(
        title=_(u'label_thankspageoverrideaction_text',
                default=u'Custom Success Action Type'),
        description=_(
            u'help_thankspageoverrideaction_text',
            default=u'Use this field in place of a thanks-page designation '
                    u'to determine final action after calling '
                    u'your action adapter (if you have one). You would '
                    u'usually use this for a custom success template or '
                    u'script. Leave empty if unneeded. Otherwise, specify as '
                    u'you would a CMFFormController action type and argument, '
                    u'complete with type of action to execute '
                    u'(e.g., "redirect_to" or "traverse_to") '
                    u'and a TALES expression. For example, '
                    u'"Redirect to" and "string:thanks-page" would redirect '
                    u'to "thanks-page".'),
        default=u'redirect_to',
        required=False,
        vocabulary=vocabularies.customActions,
    )
    directives.write_permission(
        thanksPageOverride=config.EDIT_TALES_PERMISSION)
    thanksPageOverride = zope.schema.TextLine(
        title=_(u'label_thankspageoverride_text',
                default=u'Custom Success Action'),
        description=_(
            u'help_thankspageoverride_text',
            default=u'Use this field in place of a thanks-page designation '
                    u'to determine final action after calling your action '
                    u'adapter (if you have one). You would usually use '
                    u'this for a custom success template or script. '
                    u'Leave empty if unneeded. Otherwise, specify as you '
                    u'would a CMFFormController action type and argument, '
                    u'complete with type of action to execute '
                    u'(e.g., "redirect_to" or "traverse_to") '
                    u'and a TALES expression. For example, '
                    u'"Redirect to" and "string:thanks-page" would redirect '
                    u'to "thanks-page".'),
        default=u'',
        constraint=isTALES,
        required=False,
    )
    directives.write_permission(
        formActionOverride=config.EDIT_TALES_PERMISSION)
    formActionOverride = zope.schema.TextLine(
        title=_(u'label_formactionoverride_text',
                default=u'Custom Form Action'),
        description=_(
            u'help_formactionoverride_text',
            default=u'Use this field to override the form action attribute. '
                    u'Specify a URL to which the form will post. '
                    u'This will bypass form validation, success action '
                    u'adapter and thanks page.'
        ),
        default=u'',
        required=False,
        constraint=isTALES,
    )
    directives.write_permission(onDisplayOverride=config.EDIT_TALES_PERMISSION)
    onDisplayOverride = zope.schema.TextLine(
        title=_(u'label_OnDisplayOverride_text', default=u'Form Setup Script'),
        description=_(
            u'help_OnDisplayOverride_text',
            default=u'A TALES expression that will be called when the form is '
                    u'displayed. Leave empty if unneeded. The most common '
                    u'use of this field is to call a python script that '
                    u'sets defaults for multiple fields by pre-populating '
                    u'request.form. '
                    u'Any value returned by the expression is ignored. '
                    u'PLEASE NOTE: errors in the evaluation of this '
                    u'expression will cause an error on form display.'
        ),
        constraint=isTALES,
        required=False,
        default=u'',
    )
    directives.write_permission(
        afterValidationOverride=config.EDIT_TALES_PERMISSION)
    afterValidationOverride = zope.schema.TextLine(
        title=_(u'label_AfterValidationOverride_text',
                default=u'After Validation Script'),
        description=_(
            u'help_AfterValidationOverride_text',
            default=u'A TALES expression that will be called after the form is'
                    u'successfully validated, but before calling an action '
                    u'adapter (if any) or displaying a thanks page.'
                    u'Form input will be in the request.form dictionary.'
                    u'Leave empty if unneeded. The most '
                    u'common use of this field is to call a python script'
                    u'to clean up form input or to script an alternative '
                    u'action. Any value returned by the expression is ignored.'
                    u'PLEASE NOTE: errors in the evaluation of this '
                    u'expression willcause an error on form display.'
        ),
        constraint=isTALES,
        required=False,
        default=u'',
    )
    directives.write_permission(headerInjection=config.EDIT_TALES_PERMISSION)
    headerInjection = zope.schema.TextLine(
        title=_(u'label_headerInjection_text', default=u'Header Injection'),
        description=_(
            u'help_headerInjection_text',
            default=u'This override field allows you to insert content into '
                    u'the xhtml head. The typical use is to add custom CSS '
                    u'or JavaScript. Specify a TALES expression returning a '
                    u'string. The string will be inserted with no '
                    u'interpretation. PLEASE NOTE: errors in the evaluation '
                    u'of this expression will cause an error on form display.'
        ),
        constraint=isTALES,
        required=False,
        default=u'',
    )
    directives.write_permission(
        submitLabelOverride=config.EDIT_TALES_PERMISSION)
    submitLabelOverride = zope.schema.TextLine(
        title=_(u'label_submitlabeloverride_text',
                default=u'Custom Submit Button Label'),
        description=_(
            u'help_submitlabeloverride_text',
            default=u'This override field allows you to change submit button '
                    u'label. The typical use is to set label with request '
                    u'parameters. Specify a TALES expression returning a '
                    u'string. PLEASE NOTE: errors in the evaluation of this '
                    u'expression will cause an error on form display.'
        ),
        constraint=isTALES,
        required=False,
        default=u'',
    )
    fieldset(
        u'thankyou',
        label=_('Thanks Page'),
        fields=[
            'thankstitle',
            'thanksdescription',
            'showAll',
            'showFields',
            'includeEmpties',
            'thanksPrologue',
            'thanksEpilogue'
        ]
    )
    thankstitle = zope.schema.TextLine(
        title=_(u'label_thankstitle', default=u'Thanks title'),
        defaultFactory=default_thankstitle,
        required=True
    )
    thanksdescription = zope.schema.Text(
        title=_(u'label_thanksdescription', default=u'Thanks summary'),
        description=_(
            u'help_thanksdescription',
            default=u'Used in thanks page.'
        ),
        defaultFactory=default_thanksdescription,
        required=False,
        missing_value=u'',
    )
#     TODO
#     obj.setTitle(_(u'pfg_thankyou_title', u'Thank You'))
#     obj.setDescription(
#         _(u'pfg_thankyou_description', u'Thanks for your input.')
#     )
    showAll = zope.schema.Bool(
        title=_(u'label_showallfields_text', default=u'Show All Fields'),
        description=_(u'help_showallfields_text', default=u''
                      u'Check this to display input for all fields '
                      u'(except label and file fields). If you check '
                      u'this, the choices in the pick box below '
                      u'will be ignored.'),
        default=True,
        required=False,
    )
    showFields = zope.schema.List(
        title=_(u'label_showfields_text', default=u'Show Responses'),
        description=_(
            u'help_showfields_text',
            default=u'Pick the fields whose inputs you\'d like to display on '
                    u'the success page.'),
        unique=True,
        required=False,
        value_type=zope.schema.Choice(vocabulary=vocabularies.fieldsFactory),
    )
    includeEmpties = zope.schema.Bool(
        title=_(u'label_includeEmpties_text', default=u'Include Empties'),
        description=_(u'help_includeEmpties_text', default=u''
                      u'Check this to display field titles '
                      u'for fields that received no input. Uncheck '
                      u'to leave fields with no input off the list.'),
        default=True,
        required=False,
    )
    thanksPrologue = RichText(
        title=_(u'label_thanksprologue_text', default=u'Thanks Prologue'),
        description=_(
            u'help_thanksprologue_text',
            default=u'This text will be displayed above the selected field '
                    u'inputs.'
        ),
        required=False,
    )
    thanksEpilogue = RichText(
        title=_(u'label_thanksepilogue_text', default=u'Thanks Epilogue'),
        description=_(
            u'help_thanksepilogue_text',
            default=u'The text will be displayed after the field inputs.'
        ),
        required=False,
    )


class IEasyFormImportFormSchema(Interface):

    """Schema for easyform import form.
    """
    upload = zope.schema.Bytes(
        title=PMF(u'Upload'),
        required=True)
