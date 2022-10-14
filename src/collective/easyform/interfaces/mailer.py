# -*- coding: utf-8 -*-
from .validators import isTALES
from collective.easyform import config
from collective.easyform import easyformMessageFactory as _  # NOQA
from collective.easyform.config import HAS_XLSX_SUPPORT
from collective.easyform.interfaces import IAction
from plone import api
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.autoform.interfaces import OMITTED_KEY
from plone.schema import Email
from plone.supermodel.directives import fieldset
from Products.CMFPlone.utils import safe_unicode
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.textarea import TextAreaWidget
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

import zope.i18nmessageid
import zope.interface
import zope.schema.interfaces


PMF = zope.i18nmessageid.MessageFactory("plone")
MODIFY_PORTAL_CONTENT = "cmf.ModifyPortalContent"


@provider(IContextAwareDefaultFactory)
def default_mail_subject(context):
    return translate(_("Form Submission"), context=getRequest())


def default_mail_body():
    """Default mail body for mailer action.
    Acquire 'mail_body_default.pt' or return hard coded default
    """
    try:
        portal = api.portal.get()
    except api.exc.CannotGetPortalError:
        return config.MAIL_BODY_DEFAULT

    mail_body_default = portal.restrictedTraverse(
        "easyform_mail_body_default.pt", default=None
    )
    if mail_body_default:
        return safe_unicode(mail_body_default.file.data)
    else:
        return config.MAIL_BODY_DEFAULT


class IMailer(IAction):
    """A form action adapter that will e-mail form input."""

    directives.write_permission(recipient_name=config.EDIT_ADDRESSING_PERMISSION)
    directives.read_permission(recipient_name=MODIFY_PORTAL_CONTENT)
    recipient_name = zope.schema.TextLine(
        title=_("label_formmailer_recipient_fullname", default="Recipient's full name"),
        description=_(
            "help_formmailer_recipient_fullname",
            default="The full name of the recipient of the mailed form.",
        ),
        default="",
        missing_value="",
        required=False,
    )

    directives.write_permission(recipient_email=config.EDIT_ADDRESSING_PERMISSION)
    directives.read_permission(recipient_email=MODIFY_PORTAL_CONTENT)
    recipient_email = Email(
        title=_(
            "label_formmailer_recipient_email", default="Recipient's e-mail address"
        ),
        description=_(
            "help_formmailer_recipient_email",
            default="The recipients e-mail address.",
        ),
        required=False,
    )
    fieldset(
        "addressing",
        label=_("Addressing"),
        fields=["to_field", "cc_recipients", "bcc_recipients", "replyto_field"],
    )
    directives.write_permission(to_field=config.EDIT_ADDRESSING_PERMISSION)
    directives.read_permission(to_field=MODIFY_PORTAL_CONTENT)
    to_field = zope.schema.Choice(
        title=_("label_formmailer_to_extract", default="Extract Recipient From"),
        description=_(
            "help_formmailer_to_extract",
            default="Choose a form field from which you wish to extract "
            "input for the To header. If you choose anything other "
            'than "None", this will override the "Recipient\'s " '
            "e-mail address setting above. Be very cautious about "
            "allowing unguarded user input for this purpose.",
        ),
        required=False,
        vocabulary="easyform.Fields",
    )

    directives.write_permission(cc_recipients=config.EDIT_ADDRESSING_PERMISSION)
    directives.read_permission(cc_recipients=MODIFY_PORTAL_CONTENT)
    cc_recipients = zope.schema.Text(
        title=_("label_formmailer_cc_recipients", default="CC Recipients"),
        description=_(
            "help_formmailer_cc_recipients",
            default="E-mail addresses which receive a carbon copy.",
        ),
        default="",
        missing_value="",
        required=False,
    )

    directives.write_permission(bcc_recipients=config.EDIT_ADDRESSING_PERMISSION)
    directives.read_permission(bcc_recipients=MODIFY_PORTAL_CONTENT)
    bcc_recipients = zope.schema.Text(
        title=_("label_formmailer_bcc_recipients", default="BCC Recipients"),
        description=_(
            "help_formmailer_bcc_recipients",
            default="E-mail addresses which receive a blind carbon copy.",
        ),
        default="",
        missing_value="",
        required=False,
    )

    directives.write_permission(replyto_field=config.EDIT_TECHNICAL_PERMISSION)
    directives.read_permission(replyto_field=MODIFY_PORTAL_CONTENT)
    replyto_field = zope.schema.Choice(
        title=_("label_formmailer_replyto_extract", default="Extract Reply-To From"),
        description=_(
            "help_formmailer_replyto_extract",
            default="Choose a form field from which you wish to extract "
            "input for the Reply-To header. NOTE: You should "
            "activate e-mail address verification for the "
            "designated field.",
        ),
        required=False,
        vocabulary="easyform.Fields",
    )
    fieldset(
        "message",
        label=PMF("Message"),
        fields=[
            "msg_subject",
            "subject_field",
            "body_pre",
            "body_post",
            "body_footer",
            "showAll",
            "showFields",
            "includeEmpties",
            "sendCSV",
            "sendXML",
            "sendXLSX",
            "sendWithHeader",
        ],
    )
    directives.read_permission(msg_subject=MODIFY_PORTAL_CONTENT)
    msg_subject = zope.schema.TextLine(
        title=_("label_formmailer_subject", default="Subject"),
        description=_(
            "help_formmailer_subject",
            default=""
            "Subject line of message. This is used if you "
            "do not specify a subject field or if the field "
            "is empty.",
        ),
        defaultFactory=default_mail_subject,
        missing_value="",
        required=False,
    )

    directives.write_permission(subject_field=config.EDIT_ADVANCED_PERMISSION)
    directives.read_permission(subject_field=MODIFY_PORTAL_CONTENT)
    subject_field = zope.schema.Choice(
        title=_("label_formmailer_subject_extract", default="Extract Subject From"),
        description=_(
            "help_formmailer_subject_extract",
            default=""
            "Choose a form field from which you wish to extract "
            "input for the mail subject line.",
        ),
        required=False,
        vocabulary="easyform.Fields",
    )
    directives.read_permission(body_pre=MODIFY_PORTAL_CONTENT)
    directives.widget("body_pre", TextAreaWidget)

    body_pre = RichText(
        title=_("label_formmailer_body_pre", default="Body (prepended)"),
        description=_(
            "help_formmailer_body_pre",
            default="Text prepended to fields listed in mail-body",
        ),
        default="",
        missing_value="",
        default_mime_type="text/x-web-intelligent",
        allowed_mime_types=("text/x-web-intelligent",),
        output_mime_type="text/x-html-safe",
        required=False,
    )
    directives.read_permission(body_post=MODIFY_PORTAL_CONTENT)
    directives.widget("body_post", TextAreaWidget)
    body_post = RichText(
        title=_("label_formmailer_body_post", default="Body (appended)"),
        description=_(
            "help_formmailer_body_post",
            default="Text appended to fields listed in mail-body",
        ),
        default="",
        missing_value="",
        default_mime_type="text/x-web-intelligent",
        allowed_mime_types=("text/x-web-intelligent",),
        output_mime_type="text/x-html-safe",
        required=False,
    )
    directives.read_permission(body_footer=MODIFY_PORTAL_CONTENT)
    directives.widget("body_footer", TextAreaWidget)
    body_footer = RichText(
        title=_("label_formmailer_body_footer", default="Body (signature)"),
        description=_(
            "help_formmailer_body_footer",
            default="Text used as the footer at "
            "bottom, delimited from the body by a dashed line.",
        ),
        default="",
        missing_value="",
        default_mime_type="text/x-web-intelligent",
        allowed_mime_types=("text/x-web-intelligent",),
        output_mime_type="text/x-html-safe",
        required=False,
    )

    directives.read_permission(showAll=MODIFY_PORTAL_CONTENT)
    showAll = zope.schema.Bool(
        title=_("label_mailallfields_text", default="Include All Fields"),
        description=_(
            "help_mailallfields_text",
            default=""
            "Check this to include input for all fields "
            "(except label and file fields). If you check "
            "this, the choices in the pick box below "
            "will be ignored.",
        ),
        default=True,
        required=False,
    )

    directives.read_permission(showFields=MODIFY_PORTAL_CONTENT)
    showFields = zope.schema.List(
        title=_("label_mailfields_text", default="Show Responses"),
        description=_(
            "help_mailfields_text",
            default="Pick the fields whose inputs you'd like to include in "
            "the e-mail.",
        ),
        unique=True,
        required=False,
        value_type=zope.schema.Choice(vocabulary="easyform.Fields"),
    )

    directives.read_permission(includeEmpties=MODIFY_PORTAL_CONTENT)
    includeEmpties = zope.schema.Bool(
        title=_("label_mailEmpties_text", default="Include Empties"),
        description=_(
            "help_mailEmpties_text",
            default=""
            "Check this to include titles "
            "for fields that received no input. Uncheck "
            "to leave fields with no input out of the e-mail.",
        ),
        default=True,
        required=False,
    )

    directives.read_permission(sendCSV=MODIFY_PORTAL_CONTENT)
    sendCSV = zope.schema.Bool(
        title=_("label_sendCSV_text", default="Send CSV data attachment"),
        description=_(
            "help_sendCSV_text",
            default=""
            "Check this to send a CSV file "
            "attachment containing the values "
            "filled out in the form.",
        ),
        default=False,
        required=False,
    )

    directives.read_permission(sendWithHeader=MODIFY_PORTAL_CONTENT)
    sendWithHeader = zope.schema.Bool(
        title=_(
            "label_sendWithHeader_text",
            default="Include header in attached CSV/XLSX data",
        ),
        description=_(
            "help_sendWithHeader_text",
            default=""
            "Check this to include the CSV/XLSX header "
            "in file attachments.",
        ),
        default=False,
        required=False,
    )

    directives.read_permission(sendXLSX=MODIFY_PORTAL_CONTENT)
    sendXLSX = zope.schema.Bool(
        title=_("label_sendXLSX_text", default="Send XLSX data attachment"),
        description=_(
            "help_sendXLSX_text",
            default=""
            "Check this to send a XLSX file "
            "attachment containing the values "
            "filled out in the form.",
        ),
        default=False,
        required=False,
    )

    directives.read_permission(sendXML=MODIFY_PORTAL_CONTENT)
    sendXML = zope.schema.Bool(
        title=_("label_sendXML_text", default="Send XML data attachment"),
        description=_(
            "help_sendXML_text",
            default=""
            "Check this to send an XML file "
            "attachment containing the values "
            "filled out in the form.",
        ),
        default=False,
        required=False,
    )

    fieldset("template", label=PMF("Template"), fields=["body_pt", "body_type"])
    directives.write_permission(body_pt=config.EDIT_TALES_PERMISSION)
    directives.read_permission(body_pt=MODIFY_PORTAL_CONTENT)
    body_pt = zope.schema.Text(
        title=_("label_formmailer_body_pt", default="Mail-Body Template"),
        description=_(
            "help_formmailer_body_pt",
            default="This is a Zope Page Template used for rendering of "
            "the mail-body. You don't need to modify it, but if you "
            "know TAL (Zope's Template Attribute Language) have "
            "the full power to customize your outgoing mails.",
        ),
        defaultFactory=default_mail_body,
        missing_value="",
    )

    directives.write_permission(body_type=config.EDIT_ADVANCED_PERMISSION)
    directives.read_permission(body_type=MODIFY_PORTAL_CONTENT)
    body_type = zope.schema.Choice(
        title=_("label_formmailer_body_type", default="Mail Format"),
        description=_(
            "help_formmailer_body_type",
            default="Set the mime-type of the mail-body. Change this "
            "setting only if you know exactly what you are doing. "
            "Leave it blank for default behaviour.",
        ),
        default="html",
        vocabulary="easyform.MimeList",
    )
    fieldset(
        "headers", label=_("Headers"), fields=["xinfo_headers", "additional_headers"]
    )
    directives.widget(xinfo_headers=CheckBoxFieldWidget)
    directives.write_permission(xinfo_headers=config.EDIT_TECHNICAL_PERMISSION)
    directives.read_permission(xinfo_headers=MODIFY_PORTAL_CONTENT)
    xinfo_headers = zope.schema.List(
        title=_("label_xinfo_headers_text", default="HTTP Headers"),
        description=_(
            "help_xinfo_headers_text",
            default=""
            "Pick any items from the HTTP headers that "
            "you'd like to insert as X- headers in the message.",
        ),
        unique=True,
        required=False,
        default=["HTTP_X_FORWARDED_FOR", "REMOTE_ADDR", "PATH_INFO"],
        missing_value=["HTTP_X_FORWARDED_FOR", "REMOTE_ADDR", "PATH_INFO"],
        value_type=zope.schema.Choice(vocabulary="easyform.XinfoHeaders"),
    )
    directives.write_permission(additional_headers=config.EDIT_TECHNICAL_PERMISSION)
    directives.read_permission(additional_headers=MODIFY_PORTAL_CONTENT)
    additional_headers = zope.schema.List(
        title=_("label_formmailer_additional_headers", default="Additional Headers"),
        description=_(
            "help_formmailer_additional_headers",
            default="Additional e-mail-header lines. Only use "
            "RFC822-compliant headers.",
        ),
        unique=True,
        required=False,
        value_type=zope.schema.TextLine(
            title=_("extra_header", default="${name} Header", mapping={"name": "HTTP"})
        ),
    )

    fieldset(
        "overrides",
        label=_("Overrides"),
        fields=[
            "subjectOverride",
            "senderOverride",
            "recipientOverride",
            "ccOverride",
            "bccOverride",
        ],
    )

    directives.write_permission(subjectOverride=config.EDIT_TALES_PERMISSION)
    directives.read_permission(subjectOverride=MODIFY_PORTAL_CONTENT)
    subjectOverride = zope.schema.TextLine(
        title=_("label_subject_override_text", default="Subject Expression"),
        description=_(
            "help_subject_override_text",
            default="A TALES expression that will be evaluated to override "
            "any value otherwise entered for the e-mail subject "
            "header. Leave empty if unneeded. Your expression "
            "should evaluate as a string. PLEASE NOTE: errors in "
            "the evaluation of this expression will cause an error "
            "on form display.",
        ),
        required=False,
        default="",
        missing_value="",
        constraint=isTALES,
    )

    directives.write_permission(senderOverride=config.EDIT_TALES_PERMISSION)
    directives.read_permission(senderOverride=MODIFY_PORTAL_CONTENT)
    senderOverride = zope.schema.TextLine(
        title=_("label_sender_override_text", default="Sender Expression"),
        description=_(
            "help_sender_override_text",
            default="A TALES expression that will be evaluated to override "
            'the "From" header. Leave empty if unneeded. '
            "Your expression should evaluate as a string. "
            "Example: python:fields['replyto'] "
            "PLEASE NOTE: errors in the evaluation of this "
            "expression will cause an error on form display.",
        ),
        required=False,
        default="",
        missing_value="",
        constraint=isTALES,
    )

    directives.write_permission(recipientOverride=config.EDIT_TALES_PERMISSION)
    directives.read_permission(recipientOverride=MODIFY_PORTAL_CONTENT)
    recipientOverride = zope.schema.TextLine(
        title=_("label_recipient_override_text", default="Recipient Expression"),
        description=_(
            "help_recipient_override_text",
            default="A TALES expression that will be evaluated to override "
            "any value otherwise entered for the recipient "
            "e-mail address. You are strongly cautioned against using"
            "unvalidated data from the request for this purpose. "
            "Leave empty if unneeded. Your expression should "
            "evaluate as a string. PLEASE NOTE: errors in the "
            "evaluation of this expression will cause "
            "an error on form display.",
        ),
        required=False,
        default="",
        missing_value="",
        constraint=isTALES,
    )

    directives.write_permission(ccOverride=config.EDIT_TALES_PERMISSION)
    directives.read_permission(ccOverride=MODIFY_PORTAL_CONTENT)
    ccOverride = zope.schema.TextLine(
        title=_("label_cc_override_text", default="CC Expression"),
        description=_(
            "help_cc_override_text",
            default="A TALES expression that will be evaluated to override "
            "any value otherwise entered for the CC list. You are "
            "strongly cautioned against using unvalidated data from "
            "the request for this purpose. Leave empty if unneeded. "
            "Your expression should evaluate as a sequence of "
            "strings. PLEASE NOTE: errors in the evaluation of this "
            "expression will cause an error on form display.",
        ),
        required=False,
        default="",
        missing_value="",
        constraint=isTALES,
    )

    directives.write_permission(bccOverride=config.EDIT_TALES_PERMISSION)
    directives.read_permission(bccOverride=MODIFY_PORTAL_CONTENT)
    bccOverride = zope.schema.TextLine(
        title=_("label_bcc_override_text", default="BCC Expression"),
        description=_(
            "help_bcc_override_text",
            default="A TALES expression that will be evaluated to override "
            "any value otherwise entered for the BCC list. "
            "You are strongly cautioned against using "
            "unvalidated data from the request for this purpose. "
            "Leave empty if unneeded. Your expression should "
            "evaluate as a sequence of strings. PLEASE NOTE: errors "
            "in the evaluation of this expression will cause "
            "an error on form display.",
        ),
        required=False,
        default="",
        missing_value="",
        constraint=isTALES,
    )


# extend list of omitted fields if XLSX extra is not available
if not HAS_XLSX_SUPPORT:
    omitted_fields = IMailer.queryTaggedValue(OMITTED_KEY, [])[:]
    omitted_fields.append((zope.interface.Interface, "sendXLSX", "true"))
    IMailer.setTaggedValue(OMITTED_KEY, omitted_fields)
