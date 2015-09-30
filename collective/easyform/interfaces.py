# -*- coding: utf-8 -*-
from Products.PageTemplates.Expressions import getEngine
from collective.easyform import easyformMessageFactory as _
from collective.easyform.config import ACTIONS_DEFAULT
from collective.easyform.config import DEFAULT_SCRIPT
from collective.easyform.config import EDIT_ADDRESSING_PERMISSION
from collective.easyform.config import EDIT_ADVANCED_PERMISSION
from collective.easyform.config import EDIT_PYTHON_PERMISSION
from collective.easyform.config import EDIT_TALES_PERMISSION
from collective.easyform.config import FIELDS_DEFAULT
from collective.easyform.config import MAIL_BODY_DEFAULT
from collective.easyform.vocabularies import FORM_METHODS
from collective.easyform.vocabularies import MIME_LIST
from collective.easyform.vocabularies import XINFO_HEADERS
from collective.easyform.vocabularies import customActions
from collective.easyform.vocabularies import fieldsFactory
from collective.easyform.vocabularies import getProxyRoleChoices
from collective.easyform.vocabularies import vocabExtraDataDL
from collective.easyform.vocabularies import vocabFormatDL
from collective.easyform.vocabularies import widgetsFactory
from plone.app.textfield import RichText
from plone.autoform.directives import omitted
from plone.autoform.directives import read_permission
from plone.autoform.directives import widget
from plone.autoform.directives import write_permission
from plone.schemaeditor.interfaces import ID_RE
from plone.schemaeditor.interfaces import IFieldContext
from plone.schemaeditor.interfaces import IFieldEditorExtender
from plone.schemaeditor.interfaces import ISchemaContext
from plone.supermodel.model import Schema
from plone.supermodel.model import fieldset
from plone.z3cform.interfaces import IFormWrapper
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.interfaces import IEditForm
from z3c.form.interfaces import IWidget
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Bytes
from zope.schema import Choice
from zope.schema import List
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import ValidationError
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IField
from zope.schema.interfaces import ITextLine
from zope.tales.tales import CompilerError

try:
    from plone.schemaeditor import SchemaEditorMessageFactory as __
except ImportError:
    from plone.schemaeditor import _ as __

PMF = MessageFactory('plone')
MODIFY_PORTAL_CONTENT = 'cmf.ModifyPortalContent'


def isValidFieldName(value):
    if not ID_RE.match(value):
        raise Invalid(__(u'Please use only letters, numbers and '
                         u'the following characters: _.'))
    return True


class InvalidTALESError(ValidationError):
    __doc__ = u'Please enter a valid TALES expression.'


def isTALES(value):
    if value.strip():
        try:
            getEngine().compile(value)
        except CompilerError:
            raise InvalidTALESError
    return True


class ISavedDataFormWrapper(IFormWrapper):
    pass


class IEasyFormFieldsEditorExtender(IFieldEditorExtender):
    pass


class IEasyFormActionsEditorExtender(IFieldEditorExtender):
    pass


class INewAction(Interface):

    title = TextLine(
        title=__(u'Title'),
        required=True
    )

    __name__ = ASCIILine(
        title=__(u'Short Name'),
        description=__(u'Used for programmatic access to the field.'),
        required=True,
        constraint=isValidFieldName,
    )

    description = Text(
        title=__(u'Help Text'),
        description=__(u'Shows up in the form as help text for the field.'),
        required=False
    )

    factory = Choice(
        title=_(u'Action type'),
        vocabulary='EasyFormActions',
        required=True,
    )

    @invariant
    def checkTitleAndDescriptionTypes(data):
        if data.__name__ is not None and data.factory is not None:
            if data.__name__ == 'title' and data.factory.fieldcls is not TextLine:
                raise Invalid(
                    __(u"The 'title' field must be a Text line (string) field."))
            if data.__name__ == 'description' and data.factory.fieldcls is not Text:
                raise Invalid(
                    __(u"The 'description' field must be a Text field."))


class IActionFactory(IField):

    """ A component that instantiates a action when called.
    """
    title = TextLine(title=__(u'Title'))


class IEasyFormImportFormSchema(Interface):

    """Schema for easyform import form.
    """
    upload = Bytes(
        title=PMF(u'Upload'),
        required=True)


@provider(IContextAwareDefaultFactory)
def default_submitLabel(context):
    return translate(
        'default_submitLabel',
        'collective.easyform',
        default=u'Submit',
        context=getRequest()
    )
    foo = _(u'default_submitLabel', u'Submit')  # dummy msgid for i18ndude to translate  # noqa


@provider(IContextAwareDefaultFactory)
def default_resetLabel(context):
    return translate(
        'default_resetLabel',
        'collective.easyform',
        default=u'Reset',
        context=getRequest()
    )
    foo = _(u'default_resetLabel', u'Reset')  # dummy msgid for i18ndude to translate  # noqa


@provider(IContextAwareDefaultFactory)
def default_thankstitle(context):
    return translate(
        'default_thankstitle',
        'collective.easyform',
        default=u'Thank You',
        context=getRequest()
    )
    foo = _(u'default_thankstitle', u'Thank You')  # dummy msgid for i18ndude to translate  # noqa


@provider(IContextAwareDefaultFactory)
def default_thanksdescription(context):
    return translate(
        'default_thanksdescription',
        'collective.easyform',
        default=u'Thanks for your input.',
        context=getRequest()
    )
    foo = _(u'default_thanksdescription', u'Thanks for your input.')  # dummy msgid for i18ndude to translate  # noqa


class IEasyForm(Schema):

    """Forms for Plone"""

#     fieldset(u'models', label=_('Models'),
#                   fields=['fields_model', 'actions_model'])
    omitted('fields_model', 'actions_model')
    fields_model = Text(
        title=_(u'Fields Model'),
        default=FIELDS_DEFAULT,
    )
    actions_model = Text(
        title=_(u'Actions Model'),
        default=ACTIONS_DEFAULT,
    )
    submitLabel = TextLine(
        title=_(u'label_submitlabel_text', default=u'Submit Button Label'),
        description=_(u'help_submitlabel_text', default=u''),
        defaultFactory=default_submitLabel,
        required=False,
    )
    useCancelButton = Bool(
        title=_(u'label_showcancel_text', default=u'Show Reset Button'),
        description=_(u'help_showcancel_text', default=u''),
        default=False,
        required=False,
    )
    resetLabel = TextLine(
        title=_(u'label_reset_button', default=u'Reset Button Label'),
        description=_(u'help_reset_button', default=u''),
        defaultFactory=default_resetLabel,
        required=False,
    )
    method = Choice(
        title=_(u'label_method', default=u'Form method'),
        description=_(u'help_method', default=u''),
        default=u'post',
        required=False,
        vocabulary=FORM_METHODS,
    )
    form_tabbing = Bool(
        title=_(u'label_form_tabbing',
                default=u'Turn fieldsets to tabs'),
        description=_(u'help_form_tabbing', default=u''),
        default=True,
        required=False,
    )
    default_fieldset_label = TextLine(
        title=_(u'label_default_fieldset_label_text',
                default=u'Custom Default Fieldset Label'),
        description=_(u'help_default_fieldset_label_text',
                      default=u'This field allows you to change default fieldset label.'),
        required=False,
        default=u'',
    )
    unload_protection = Bool(
        title=_(u'label_unload_protection',
                default=u'Unload protection'),
        description=_(u'help_unload_protection', default=u''),
        default=True,
        required=False,
    )
    CSRFProtection = Bool(
        title=_(u'label_csrf', default=u'CSRF Protection'),
        description=_(u'help_csrf', default=u'Check this to employ Cross-Site '
                      u'Request Forgery protection. Note that only HTTP Post '
                      u'actions will be allowed.'),
        default=True,
        required=False,
    )
    write_permission(forceSSL=EDIT_ADVANCED_PERMISSION)
    forceSSL = Bool(
        title=_(u'label_force_ssl', default=u'Force SSL connection'),
        description=_(u'help_force_ssl', default=u''
                      u'Check this to make the form redirect to an SSL-enabled '
                      u'version of itself (https://) if accessed via a non-SSL '
                      u'URL (http://).  In order to function properly, '
                      u'this requires a web server that has been configured to '
                      u'handle the HTTPS protocol on port 443 and forward it to Zope.'),
        default=False,
        required=False,
    )
    formPrologue = RichText(
        title=_(u'label_prologue_text', default=u'Form Prologue'),
        description=_(u'help_prologue_text',
                      default=u'This text will be displayed above the form fields.'),
        required=False,
    )
    formEpilogue = RichText(
        title=_(u'label_epilogue_text', default=u'Form Epilogue'),
        description=_(u'help_epilogue_text',
                      default=u'The text will be displayed after the form fields.'),
        required=False,
    )
    fieldset(u'overrides', label=_('Overrides'),
             fields=['thanksPageOverrideAction', 'thanksPageOverride', 'formActionOverride', 'onDisplayOverride', 'afterValidationOverride', 'headerInjection', 'submitLabelOverride'])
    write_permission(thanksPageOverrideAction=EDIT_TALES_PERMISSION)
    thanksPageOverrideAction = Choice(
        title=_(u'label_thankspageoverrideaction_text',
                default=u'Custom Success Action Type'),
        description=_(u'help_thankspageoverrideaction_text', default=u''
                      u'Use this field in place of a thanks-page designation '
                      u'to determine final action after calling '
                      u'your action adapter (if you have one). You would usually use '
                      u'this for a custom success template or script. '
                      u'Leave empty if unneeded. Otherwise, specify as you would a '
                      u'CMFFormController action type and argument, '
                      u'complete with type of action to execute '
                      u'(e.g., "redirect_to" or "traverse_to") '
                      u'and a TALES expression. For example, '
                      u'"Redirect to" and "string:thanks-page" would redirect to '
                      u'"thanks-page".'),
        default=u'redirect_to',
        required=False,
        vocabulary=customActions,
    )
    write_permission(thanksPageOverride=EDIT_TALES_PERMISSION)
    thanksPageOverride = TextLine(
        title=_(u'label_thankspageoverride_text',
                default=u'Custom Success Action'),
        description=_(u'help_thankspageoverride_text', default=u''
                      u'Use this field in place of a thanks-page designation '
                      u'to determine final action after calling '
                      u'your action adapter (if you have one). You would usually use '
                      u'this for a custom success template or script. '
                      u'Leave empty if unneeded. Otherwise, specify as you would a '
                      u'CMFFormController action type and argument, '
                      u'complete with type of action to execute '
                      u'(e.g., "redirect_to" or "traverse_to") '
                      u'and a TALES expression. For example, '
                      u'"Redirect to" and "string:thanks-page" would redirect to '
                      u'"thanks-page".'),
        default=u'',
        constraint=isTALES,
        required=False,
    )
    write_permission(formActionOverride=EDIT_TALES_PERMISSION)
    formActionOverride = TextLine(
        title=_(u'label_formactionoverride_text',
                default=u'Custom Form Action'),
        description=_(u'help_formactionoverride_text', default=u''
                      u'Use this field to override the form action attribute. '
                      u'Specify a URL to which the form will post. '
                      u'This will bypass form validation, success action '
                      u'adapter and thanks page.'),
        default=u'',
        required=False,
        constraint=isTALES,
    )
    write_permission(onDisplayOverride=EDIT_TALES_PERMISSION)
    onDisplayOverride = TextLine(
        title=_(u'label_OnDisplayOverride_text', default=u'Form Setup Script'),
        description=_(u'help_OnDisplayOverride_text', default=u''
                      u'A TALES expression that will be called when the form is '
                      u'displayed. '
                      u'Leave empty if unneeded. '
                      u'The most common use of this field is to call a python script '
                      u'that sets defaults for multiple fields by pre-populating '
                      u'request.form. '
                      u'Any value returned by the expression is ignored. '
                      u'PLEASE NOTE: errors in the evaluation of this expression '
                      u'will cause an error on form display.'),
        constraint=isTALES,
        required=False,
        default=u'',
    )
    write_permission(afterValidationOverride=EDIT_TALES_PERMISSION)
    afterValidationOverride = TextLine(
        title=_(u'label_AfterValidationOverride_text',
                default=u'After Validation Script'),
        description=_(u'help_AfterValidationOverride_text', default=u''
                      u'A TALES expression that will be called after the form is'
                      u'successfully validated, but before calling an action adapter'
                      u'(if any) or displaying a thanks page.'
                      u'Form input will be in the request.form dictionary.'
                      u'Leave empty if unneeded.'
                      u'The most common use of this field is to call a python script'
                      u'to clean up form input or to script an alternative action.'
                      u'Any value returned by the expression is ignored.'
                      u'PLEASE NOTE: errors in the evaluation of this expression will'
                      u'cause an error on form display.'),
        constraint=isTALES,
        required=False,
        default=u'',
    )
    write_permission(headerInjection=EDIT_TALES_PERMISSION)
    headerInjection = TextLine(
        title=_(u'label_headerInjection_text', default=u'Header Injection'),
        description=_(u'help_headerInjection_text', default=u''
                      u'This override field allows you to insert content into the xhtml '
                      u'head. The typical use is to add custom CSS or JavaScript. '
                      u'Specify a TALES expression returning a string. The string will '
                      u'be inserted with no interpretation. '
                      u'PLEASE NOTE: errors in the evaluation of this expression will '
                      u'cause an error on form display.'),
        constraint=isTALES,
        required=False,
        default=u'',
    )
    write_permission(submitLabelOverride=EDIT_TALES_PERMISSION)
    submitLabelOverride = TextLine(
        title=_(u'label_submitlabeloverride_text',
                default=u'Custom Submit Button Label'),
        description=_(u'help_submitlabeloverride_text', default=u''
                      u'This override field allows you to change submit button label. '
                      u'The typical use is to set label with request parameters. '
                      u'Specify a TALES expression returning a string. '
                      u'PLEASE NOTE: errors in the evaluation of this expression will '
                      u'cause an error on form display.'),
        constraint=isTALES,
        required=False,
        default=u'',
    )
    fieldset(u'thankyou', label=_('Thanks Page'),
             fields=['thankstitle', 'thanksdescription', 'showAll', 'showFields', 'includeEmpties', 'thanksPrologue', 'thanksEpilogue'])
    thankstitle = TextLine(
        title=_(u'label_thankstitle', default=u'Thanks title'),
        defaultFactory=default_thankstitle,
        required=True
    )
    thanksdescription = Text(
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
#     obj.setDescription(_(u'pfg_thankyou_description', u'Thanks for your input.'))
    showAll = Bool(
        title=_(u'label_showallfields_text', default=u'Show All Fields'),
        description=_(u'help_showallfields_text', default=u''
                      u'Check this to display input for all fields '
                      u'(except label and file fields). If you check '
                      u'this, the choices in the pick box below '
                      u'will be ignored.'),
        default=True,
        required=False,
    )
    showFields = List(
        title=_(u'label_showfields_text', default=u'Show Responses'),
        description=_(u'help_showfields_text',
                      default=u'Pick the fields whose inputs you\'d like to display on the success page.'),
        unique=True,
        required=False,
        value_type=Choice(vocabulary=fieldsFactory),
    )
    includeEmpties = Bool(
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
        description=_(u'help_thanksprologue_text',
                      default=u'This text will be displayed above the selected field inputs.'),
        required=False,
    )
    thanksEpilogue = RichText(
        title=_(u'label_thanksepilogue_text', default=u'Thanks Epilogue'),
        description=_(u'help_thanksepilogue_text',
                      default=u'The text will be displayed after the field inputs.'),
        required=False,
    )


class IEasyFormView(Interface):

    """
    EasyForm view interface
    """


class IEasyFormForm(Interface):

    """
    EasyForm view interface
    """


class IEasyFormFieldsContext(ISchemaContext):

    """
    EasyForm schema view interface
    """


class IEasyFormActionsContext(ISchemaContext):

    """
    EasyForm actions view interface
    """


class IFieldExtender(Schema):
    field_widget = Choice(
        title=_(u'label_field_widget',
                default=u'Field Widget'),
        description=_(u'help_field_widget', default=u''),
        required=False,
        source=widgetsFactory,
    )
    fieldset(u'overrides', label=_('Overrides'),
             fields=['TDefault', 'TEnabled', 'TValidator', 'serverSide'])
    write_permission(TDefault=EDIT_TALES_PERMISSION)
    TDefault = TextLine(
        title=_(u'label_tdefault_text', default=u'Default Expression'),
        description=(_(u'help_tdefault_text', default=u''
                       u'A TALES expression that will be evaluated when the form is displayed '
                       u'to get the field default value. '
                       u'Leave empty if unneeded. Your expression should evaluate as a string. '
                       u'PLEASE NOTE: errors in the evaluation of this expression will cause '
                       u'an error on form display.')),
        default=u'',
        constraint=isTALES,
        required=False,
    )
    write_permission(TEnabled=EDIT_TALES_PERMISSION)
    TEnabled = TextLine(
        title=_(u'label_tenabled_text', default=u'Enabling Expression'),
        description=(_(u'help_tenabled_text', default=u''
                       u'A TALES expression that will be evaluated when the form is displayed '
                       u'to determine whether or not the field is enabled. '
                       u'Your expression should evaluate as True if '
                       u'the field should be included in the form, False if it should be omitted. '
                       u'Leave this expression field empty if unneeded: the field will be included. '
                       u'PLEASE NOTE: errors in the evaluation of this expression will cause '
                       u'an error on form display.')),
        default=u'',
        constraint=isTALES,
        required=False,
    )
    write_permission(TValidator=EDIT_TALES_PERMISSION)
    TValidator = TextLine(
        title=_(u'label_tvalidator_text', default=u'Custom Validator'),
        description=(_(u'help_tvalidator_text', default=u''
                       u'A TALES expression that will be evaluated when the form is validated. '
                       u'Validate against \'value\', which will contain the field input. '
                       u'Return False if valid; if not valid return a string error message. '
                       u'E.G., "python: test(value==\'eggs\', False, \'input must be eggs\')" will '
                       u'require "eggs" for input. '
                       u'PLEASE NOTE: errors in the evaluation of this expression will cause '
                       u'an error on form display.')),
        default=u'',
        constraint=isTALES,
        required=False,
    )
    write_permission(serverSide=EDIT_TALES_PERMISSION)
    serverSide = Bool(
        title=_(u'label_server_side_text', default=u'Server-Side Variable'),
        description=_(u'description_server_side_text', default=u''
                      u'Mark this field as a value to be injected into the '
                      u'request form for use by action adapters and is not '
                      u'modifiable by or exposed to the client.'),
        default=False,
        required=False,
    )
    validators = List(
        title=_('Validators'),
        description=_(
            u'help_userfield_validators',
            default=u'Select the validators to use on this field'),
        unique=True,
        required=False,
        value_type=Choice(
            vocabulary='collective.easyform.validators'),
    )


class IActionExtender(Schema):
    fieldset(u'overrides', label=_('Overrides'), fields=['execCondition'])
    read_permission(execCondition=MODIFY_PORTAL_CONTENT)
    write_permission(execCondition=EDIT_TALES_PERMISSION)
    execCondition = TextLine(
        title=_(u'label_execcondition_text', default=u'Execution Condition'),
        description=(_(u'help_execcondition_text', default=u''
                       u'A TALES expression that will be evaluated to determine whether '
                       u'or not to execute this action. Leave empty if unneeded, and '
                       u'the action will be executed. Your expression should evaluate '
                       u'as a boolean; return True if you wish the action to execute. '
                       u'PLEASE NOTE: errors in the evaluation of this expression will '
                       u'cause an error on form display.')
                     ),
        default=u'',
        constraint=isTALES,
        required=False,
    )


class IEasyFormFieldContext(IFieldContext):

    """
    EasyForm field content marker
    """


class IEasyFormActionContext(IFieldContext):

    """
    EasyForm action content marker
    """


class IActionEditForm(IEditForm):

    """ Marker interface for action edit forms
    """


class IAction(Schema, IField):
    omitted('required', 'order', 'default', 'missing_value', 'readonly')
#     required = Bool(
#         title=_('Enabled'),
#        description=_('Tells whether a action is enabled.'),
#         default=True)

    def onSuccess(fields, request):
        pass


class IMailer(IAction):

    """A form action adapter that will e-mail form input."""
#     default_method='getDefaultRecipientName',
    write_permission(recipient_name=EDIT_ADDRESSING_PERMISSION)
    read_permission(recipient_name=MODIFY_PORTAL_CONTENT)
    recipient_name = TextLine(
        title=_(u'label_formmailer_recipient_fullname',
                default=u"Recipient's full name"),
        description=_(u'help_formmailer_recipient_fullname',
                      default=u'The full name of the recipient of the mailed form.'),
        default=u'',
        missing_value=u'',
        required=False,
    )
#     default_method='getDefaultRecipient',
#     validators=('isEmail',),
#     TODO defaultFactory
#     TODO IContextAwareDefaultFactory
    write_permission(recipient_email=EDIT_ADDRESSING_PERMISSION)
    read_permission(recipient_email=MODIFY_PORTAL_CONTENT)
    recipient_email = TextLine(
        title=_(u'label_formmailer_recipient_email',
                default=u"Recipient's e-mail address"),
        description=_(u'help_formmailer_recipient_email',
                      default=u'The recipients e-mail address.'),
        default=u'',
        missing_value=u'',
        required=False,
    )
    fieldset(u'addressing', label=_('Addressing'), fields=[
             'to_field', 'cc_recipients', 'bcc_recipients', 'replyto_field'])
    write_permission(to_field=EDIT_ADVANCED_PERMISSION)
    read_permission(to_field=MODIFY_PORTAL_CONTENT)
    to_field = Choice(
        title=_(u'label_formmailer_to_extract',
                default=u'Extract Recipient From'),
        description=_(u'help_formmailer_to_extract', default=u''
                      u'Choose a form field from which you wish to extract '
                      u'input for the To header. If you choose anything other '
                      u'than "None", this will override the "Recipient\'s e-mail address" '
                      u'setting above. Be very cautious about allowing unguarded user '
                      u'input for this purpose.'),
        required=False,
        vocabulary=fieldsFactory,
    )
#     default_method='getDefaultCC',
    write_permission(cc_recipients=EDIT_ADDRESSING_PERMISSION)
    read_permission(cc_recipients=MODIFY_PORTAL_CONTENT)
    cc_recipients = Text(
        title=_(u'label_formmailer_cc_recipients',
                default=u'CC Recipients'),
        description=_(u'help_formmailer_cc_recipients',
                      default=u'E-mail addresses which receive a carbon copy.'),
        default=u'',
        missing_value=u'',
        required=False,
    )
#     default_method='getDefaultBCC',
    write_permission(bcc_recipients=EDIT_ADDRESSING_PERMISSION)
    read_permission(bcc_recipients=MODIFY_PORTAL_CONTENT)
    bcc_recipients = Text(
        title=_(u'label_formmailer_bcc_recipients',
                default=u'BCC Recipients'),
        description=_(u'help_formmailer_bcc_recipients',
                      default=u'E-mail addresses which receive a blind carbon copy.'),
        default=u'',
        missing_value=u'',
        required=False,
    )
    write_permission(replyto_field=EDIT_ADVANCED_PERMISSION)
    read_permission(replyto_field=MODIFY_PORTAL_CONTENT)
    replyto_field = Choice(
        title=_(u'label_formmailer_replyto_extract',
                default=u'Extract Reply-To From'),
        description=_(u'help_formmailer_replyto_extract', default=u''
                      u'Choose a form field from which you wish to extract '
                      u'input for the Reply-To header. NOTE: You should '
                      u'activate e-mail address verification for the designated '
                      u'field.'),
        required=False,
        vocabulary=fieldsFactory,
    )
    fieldset(u'message', label=PMF('Message'), fields=[
             'msg_subject', 'subject_field', 'body_pre', 'body_post',
             'body_footer', 'showAll', 'showFields', 'includeEmpties'])
    read_permission(msg_subject=MODIFY_PORTAL_CONTENT)
    msg_subject = TextLine(
        title=_(u'label_formmailer_subject', default=u'Subject'),
        description=_(u'help_formmailer_subject', default=u''
                      u'Subject line of message. This is used if you '
                      u'do not specify a subject field or if the field '
                      u'is empty.'),
        default=u'Form Submission',
        missing_value=u'',
        required=False,
    )
    write_permission(subject_field=EDIT_ADVANCED_PERMISSION)
    read_permission(subject_field=MODIFY_PORTAL_CONTENT)
    subject_field = Choice(
        title=_(u'label_formmailer_subject_extract',
                default=u'Extract Subject From'),
        description=_(u'help_formmailer_subject_extract', default=u''
                      u'Choose a form field from which you wish to extract '
                      u'input for the mail subject line.'),
        required=False,
        vocabulary=fieldsFactory,
    )
#     accessor='getBody_pre',
    read_permission(body_pre=MODIFY_PORTAL_CONTENT)
    body_pre = Text(
        title=_(u'label_formmailer_body_pre', default=u'Body (prepended)'),
        description=_(u'help_formmailer_body_pre',
                      default=u'Text prepended to fields listed in mail-body'),
        default=u'',
        missing_value=u'',
        required=False,
    )
    read_permission(body_post=MODIFY_PORTAL_CONTENT)
    body_post = Text(
        title=_(u'label_formmailer_body_post', default=u'Body (appended)'),
        description=_(u'help_formmailer_body_post',
                      default=u'Text appended to fields listed in mail-body'),
        default=u'',
        missing_value=u'',
        required=False,
    )
    read_permission(body_footer=MODIFY_PORTAL_CONTENT)
    body_footer = Text(
        title=_(u'label_formmailer_body_footer',
                default=u'Body (signature)'),
        description=_(u'help_formmailer_body_footer',
                      default=u'Text used as the footer at '
                      u'bottom, delimited from the body by a dashed line.'),
        default=u'',
        missing_value=u'',
        required=False,
    )
    read_permission(showAll=MODIFY_PORTAL_CONTENT)
    showAll = Bool(
        title=_(u'label_mailallfields_text', default=u'Include All Fields'),
        description=_(u'help_mailallfields_text', default=u''
                      u'Check this to include input for all fields '
                      u'(except label and file fields). If you check '
                      u'this, the choices in the pick box below '
                      u'will be ignored.'),
        default=True,
        required=False,
    )
    read_permission(showFields=MODIFY_PORTAL_CONTENT)
    showFields = List(
        title=_(u'label_mailfields_text', default=u'Show Responses'),
        description=_(u'help_mailfields_text',
                      default=u'Pick the fields whose inputs you\'d like to include in the e-mail.'),
        unique=True,
        required=False,
        value_type=Choice(vocabulary=fieldsFactory),
    )
    read_permission(includeEmpties=MODIFY_PORTAL_CONTENT)
    includeEmpties = Bool(
        title=_(u'label_mailEmpties_text', default=u'Include Empties'),
        description=_(u'help_mailEmpties_text', default=u''
                      u'Check this to include titles '
                      u'for fields that received no input. Uncheck '
                      u'to leave fields with no input out of the e-mail.'),
        default=True,
        required=False,
    )
    fieldset(u'template', label=PMF(
        'Template'), fields=['body_pt', 'body_type'])
#     ZPTField('body_pt',
#     default_method='getMailBodyDefault',
#     validators=('zptvalidator',),
    write_permission(body_pt=EDIT_TALES_PERMISSION)
    read_permission(body_pt=MODIFY_PORTAL_CONTENT)
    body_pt = Text(
        title=_(u'label_formmailer_body_pt', default=u'Mail-Body Template'),
        description=_(u'help_formmailer_body_pt', default=u''
                      u'This is a Zope Page Template '
                      u'used for rendering of the mail-body. You don\'t need to modify '
                      u'it, but if you know TAL (Zope\'s Template Attribute Language) '
                      u'you have the full power to customize your outgoing mails.'),
        default=MAIL_BODY_DEFAULT,
        missing_value=u'',
    )
#     default_method='getMailBodyTypeDefault',
    write_permission(body_type=EDIT_ADVANCED_PERMISSION)
    read_permission(body_type=MODIFY_PORTAL_CONTENT)
    body_type = Choice(
        title=_(u'label_formmailer_body_type', default=u'Mail Format'),
        description=_(u'help_formmailer_body_type', default=u''
                      u'Set the mime-type of the mail-body. '
                      u'Change this setting only if you know exactly what you are doing. '
                      u'Leave it blank for default behaviour.'),
        default=u'html',
        vocabulary=MIME_LIST,
    )
    fieldset(u'headers', label=_('Headers'),
             fields=['xinfo_headers', 'additional_headers'])
    widget(xinfo_headers=CheckBoxFieldWidget)
#     default_method='getDefaultXInfo',
    write_permission(xinfo_headers=EDIT_ADVANCED_PERMISSION)
    read_permission(xinfo_headers=MODIFY_PORTAL_CONTENT)
    xinfo_headers = List(
        title=_(u'label_xinfo_headers_text', default=u'HTTP Headers'),
        description=_(u'help_xinfo_headers_text', default=u''
                      u'Pick any items from the HTTP headers that '
                      u'you\'d like to insert as X- headers in the message.'),
        unique=True,
        required=False,
        default=[u'HTTP_X_FORWARDED_FOR', u'REMOTE_ADDR', u'PATH_INFO'],
        missing_value=[u'HTTP_X_FORWARDED_FOR', u'REMOTE_ADDR', u'PATH_INFO'],
        value_type=Choice(vocabulary=XINFO_HEADERS),
    )
#     default_method='getDefaultAddHdrs',
    write_permission(additional_headers=EDIT_ADVANCED_PERMISSION)
    read_permission(additional_headers=MODIFY_PORTAL_CONTENT)
    additional_headers = List(
        title=_(u'label_formmailer_additional_headers',
                default=u'Additional Headers'),
        description=_(u'help_formmailer_additional_headers',
                      default=u'Additional e-mail-header lines. Only use RFC822-compliant headers.'),
        unique=True,
        required=False,
        value_type=TextLine(
            title=_(u'extra_header',
                    default=u'${name} Header', mapping={u'name': u'HTTP'}),
        ),
    )
#     if gpg is not None:
#         formMailerAdapterSchema = formMailerAdapterSchema + Schema((
#             StringField('gpg_keyid',
#                 schemata='encryption',
#                 accessor='getGPGKeyId',
#                 mutator='setGPGKeyId',
#                 write_permission=USE_ENCRYPTION_PERMISSION,
#                 read_permission=ModifyPortalContent,
#                 widget=StringWidget(
#                     description=_(u'help_gpg_key_id', default=u"""
#                         Give your key-id, e-mail address or
#                         whatever works to match a public key from current keyring.
#                         It will be used to encrypt the message body (not attachments).
#                         Contact the site administrator if you need to
#                         install a new public key.
#                         Note that you will probably wish to change your message
#                         template to plain text if you're using encryption.
#                         TEST THIS FEATURE BEFORE GOING PUBLIC!
#                        """),
#                    label=_(u'label_gpg_key_id', default=u'Key-Id'),
#                    ),
#                ),
#            ))
    fieldset(u'overrides', label=_('Overrides'), fields=[
             'subjectOverride', 'senderOverride', 'recipientOverride', 'ccOverride', 'bccOverride'])
    write_permission(subjectOverride=EDIT_TALES_PERMISSION)
    read_permission(subjectOverride=MODIFY_PORTAL_CONTENT)
    subjectOverride = TextLine(
        title=_(u'label_subject_override_text', default=u'Subject Expression'),
        description=_(u'help_subject_override_text', default=u''
                      u'A TALES expression that will be evaluated to override any value '
                      u'otherwise entered for the e-mail subject header. '
                      u'Leave empty if unneeded. Your expression should evaluate as a string. '
                      u'PLEASE NOTE: errors in the evaluation of this expression will cause '
                      u'an error on form display.'),
        required=False,
        default=u'',
        missing_value=u'',
        constraint=isTALES,
    )
    write_permission(senderOverride=EDIT_TALES_PERMISSION)
    read_permission(senderOverride=MODIFY_PORTAL_CONTENT)
    senderOverride = TextLine(
        title=_(u'label_sender_override_text', default=u'Sender Expression'),
        description=_(u'help_sender_override_text', default=u''
                      u'A TALES expression that will be evaluated to override the "From" header. '
                      u'Leave empty if unneeded. Your expression should evaluate as a string. '
                      u'PLEASE NOTE: errors in the evaluation of this expression will cause '
                      u'an error on form display.'),
        required=False,
        default=u'',
        missing_value=u'',
        constraint=isTALES,
    )
    write_permission(recipientOverride=EDIT_TALES_PERMISSION)
    read_permission(recipientOverride=MODIFY_PORTAL_CONTENT)
    recipientOverride = TextLine(
        title=_(u'label_recipient_override_text',
                default=u'Recipient Expression'),
        description=_(u'help_recipient_override_text', default=u''
                      u'A TALES expression that will be evaluated to override any value '
                      u'otherwise entered for the recipient e-mail address. You are strongly '
                      u'cautioned against using unvalidated data from the request for this purpose. '
                      u'Leave empty if unneeded. Your expression should evaluate as a string. '
                      u'PLEASE NOTE: errors in the evaluation of this expression will cause '
                      u'an error on form display.'),
        required=False,
        default=u'',
        missing_value=u'',
        constraint=isTALES,
    )
    write_permission(ccOverride=EDIT_TALES_PERMISSION)
    read_permission(ccOverride=MODIFY_PORTAL_CONTENT)
    ccOverride = TextLine(
        title=_(u'label_cc_override_text', default=u'CC Expression'),
        description=_(u'help_cc_override_text', default=u''
                      u'A TALES expression that will be evaluated to override any value '
                      u'otherwise entered for the CC list. You are strongly '
                      u'cautioned against using unvalidated data from the request for this purpose. '
                      u'Leave empty if unneeded. Your expression should evaluate as a sequence of strings. '
                      u'PLEASE NOTE: errors in the evaluation of this expression will cause '
                      u'an error on form display.'),
        required=False,
        default=u'',
        missing_value=u'',
        constraint=isTALES,
    )
    write_permission(bccOverride=EDIT_TALES_PERMISSION)
    read_permission(bccOverride=MODIFY_PORTAL_CONTENT)
    bccOverride = TextLine(
        title=_(u'label_bcc_override_text', default=u'BCC Expression'),
        description=_(u'help_bcc_override_text', default=u''
                      u'A TALES expression that will be evaluated to override any value '
                      u'otherwise entered for the BCC list. You are strongly '
                      u'cautioned against using unvalidated data from the request for this purpose. '
                      u'Leave empty if unneeded. Your expression should evaluate as a sequence of strings. '
                      u'PLEASE NOTE: errors in the evaluation of this expression will cause '
                      u'an error on form display.'),
        required=False,
        default=u'',
        missing_value=u'',
        constraint=isTALES,
    )


class ICustomScript(IAction):

    """Executes a Python script for form data"""
    read_permission(ProxyRole=MODIFY_PORTAL_CONTENT)
    write_permission(ProxyRole=EDIT_PYTHON_PERMISSION)
    ProxyRole = Choice(
        title=_(u'label_script_proxy', default=u'Proxy role'),
        description=_(u'help_script_proxy',
                      default=u'Role under which to run the script.'),
        default=u'none',
        required=True,
        vocabulary=getProxyRoleChoices,
    )
    read_permission(ScriptBody=MODIFY_PORTAL_CONTENT)
    write_permission(ScriptBody=EDIT_PYTHON_PERMISSION)
    ScriptBody = Text(
        title=_(u'label_script_body', default=u'Script body'),
        description=_(u'help_script_body', default=u'Write your script here.'),
        default=DEFAULT_SCRIPT,
        required=False,
        missing_value=u'',
    )


class IExtraData(Interface):
    dt = TextLine(
        title=_(u'Posting Date/Time'),
        required=False,
        default=u'',
        missing_value=u'',
    )
    HTTP_X_FORWARDED_FOR = TextLine(
        title=_(u'extra_header', default=u'${name} Header',
                mapping={u'name': u'HTTP_X_FORWARDED_FOR'}),
        required=False,
        default=u'',
        missing_value=u'',
    )
    REMOTE_ADDR = TextLine(
        title=_(u'extra_header',
                default=u'${name} Header', mapping={u'name': u'REMOTE_ADDR'}),
        required=False,
        default=u'',
        missing_value=u'',
    )
    HTTP_USER_AGENT = TextLine(
        title=_(u'extra_header',
                default=u'${name} Header', mapping={u'name': u'HTTP_USER_AGENT'}),
        required=False,
        default=u'',
        missing_value=u'',
    )


class ISaveData(IAction):

    """A form action adapter that will save form input data and
       return it in csv- or tab-delimited format."""
    showFields = List(
        title=_(u'label_savefields_text', default=u'Saved Fields'),
        description=_(u'help_savefields_text', default=u''
                      u'Pick the fields whose inputs you\'d like to include in '
                      u'the saved data. If empty, all fields will be saved.'),
        unique=True,
        required=False,
        value_type=Choice(vocabulary=fieldsFactory),
    )
    widget(ExtraData=CheckBoxFieldWidget)
    ExtraData = List(
        title=_(u'label_savedataextra_text', default='Extra Data'),
        description=_(u'help_savedataextra_text',
                      default=u'Pick any extra data you\'d like saved with the form input.'),
        unique=True,
        value_type=Choice(vocabulary=vocabExtraDataDL),
    )
    DownloadFormat = Choice(
        title=_(u'label_downloadformat_text', default=u'Download Format'),
        default=u'csv',
        vocabulary=vocabFormatDL,
    )
    UseColumnNames = Bool(
        title=_(u'label_usecolumnnames_text', default=u'Include Column Names'),
        description=_(u'help_usecolumnnames_text',
                      default=u'Do you wish to have column names on the first line of downloaded input?'),
        required=False,
    )
#     ExLinesField('SavedFormInput',
#     edit_accessor='getSavedFormInputForEdit',
#     mutator='setSavedFormInput',
#     searchable=0,
#     required=0,
#     primary=1,
#    schemata='saved data',
#     read_permission=DOWNLOAD_SAVED_PERMISSION,
#     widget=TextAreaWidget(
#        label=_(u'label_savedatainput_text', default=u'Saved Form Input'),
#         description=_(u'help_savedatainput_text'),
#        ),
#    ),


class ILabel(IField):

    """Label Field."""


class IRichLabel(ILabel):

    """Rich Label Field."""
    rich_label = RichText(
        title=_(u'Rich Label'),
        default=u'',
        missing_value=u'',
    )


class ILabelWidget(IWidget):

    """Label Widget."""


class IRichLabelWidget(ILabelWidget):

    """Rich Label Field Widget."""


class IReCaptcha(ITextLine):

    """ReCaptcha Field."""


class IFieldValidator(Interface):

    """Base marker for field validators"""
