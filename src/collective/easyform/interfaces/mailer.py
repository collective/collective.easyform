# -*- coding: utf-8 -*-
from .validators import isTALES
from collective.easyform import config
from collective.easyform import easyformMessageFactory as _  # NOQA
from collective.easyform.interfaces import IAction
from plone import api
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.schema import Email
from plone.supermodel.directives import fieldset
from Products.CMFPlone.utils import safe_unicode
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.textarea import TextAreaWidget

import zope.i18nmessageid
import zope.interface
import zope.schema.interfaces


PMF = zope.i18nmessageid.MessageFactory("plone")
MODIFY_PORTAL_CONTENT = "cmf.ModifyPortalContent"


def default_mail_body():
    """ Default mail body for mailer action.
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
        title=_(
            u"label_formmailer_recipient_fullname", default=u"Recipient's full name"
        ),
        description=_(
            u"help_formmailer_recipient_fullname",
            default=u"The full name of the recipient of the mailed form.",
        ),
        default=u"",
        missing_value=u"",
        required=False,
    )

    directives.write_permission(recipient_email=config.EDIT_ADDRESSING_PERMISSION)
    directives.read_permission(recipient_email=MODIFY_PORTAL_CONTENT)
    recipient_email = Email(
        title=_(
            u"label_formmailer_recipient_email", default=u"Recipient's e-mail address"
        ),
        description=_(
            u"help_formmailer_recipient_email",
            default=u"The recipients e-mail address.",
        ),
        required=False,
    )
    fieldset(
        u"addressing",
        label=_("Addressing"),
        fields=["to_field", "cc_recipients", "bcc_recipients", "replyto_field"],
    )
    directives.write_permission(to_field=config.EDIT_ADDRESSING_PERMISSION)
    directives.read_permission(to_field=MODIFY_PORTAL_CONTENT)
    to_field = zope.schema.Choice(
        title=_(u"label_formmailer_to_extract", default=u"Extract Recipient From"),
        description=_(
            u"help_formmailer_to_extract",
            default=u"Choose a form field from which you wish to extract "
            u"input for the To header. If you choose anything other "
            u'than "None", this will override the "Recipient\'s " '
            u"e-mail address setting above. Be very cautious about "
            u"allowing unguarded user input for this purpose.",
        ),
        required=False,
        vocabulary="easyform.Fields",
    )

    directives.write_permission(cc_recipients=config.EDIT_ADDRESSING_PERMISSION)
    directives.read_permission(cc_recipients=MODIFY_PORTAL_CONTENT)
    cc_recipients = zope.schema.Text(
        title=_(u"label_formmailer_cc_recipients", default=u"CC Recipients"),
        description=_(
            u"help_formmailer_cc_recipients",
            default=u"E-mail addresses which receive a carbon copy.",
        ),
        default=u"",
        missing_value=u"",
        required=False,
    )

    directives.write_permission(bcc_recipients=config.EDIT_ADDRESSING_PERMISSION)
    directives.read_permission(bcc_recipients=MODIFY_PORTAL_CONTENT)
    bcc_recipients = zope.schema.Text(
        title=_(u"label_formmailer_bcc_recipients", default=u"BCC Recipients"),
        description=_(
            u"help_formmailer_bcc_recipients",
            default=u"E-mail addresses which receive a blind carbon copy.",
        ),
        default=u"",
        missing_value=u"",
        required=False,
    )

    directives.write_permission(replyto_field=config.EDIT_TECHNICAL_PERMISSION)
    directives.read_permission(replyto_field=MODIFY_PORTAL_CONTENT)
    replyto_field = zope.schema.Choice(
        title=_(u"label_formmailer_replyto_extract", default=u"Extract Reply-To From"),
        description=_(
            u"help_formmailer_replyto_extract",
            default=u"Choose a form field from which you wish to extract "
            u"input for the Reply-To header. NOTE: You should "
            u"activate e-mail address verification for the "
            u"designated field.",
        ),
        required=False,
        vocabulary="easyform.Fields",
    )
    fieldset(
        u"message",
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
        ],
    )
    directives.read_permission(msg_subject=MODIFY_PORTAL_CONTENT)
    msg_subject = zope.schema.TextLine(
        title=_(u"label_formmailer_subject", default=u"Subject"),
        description=_(
            u"help_formmailer_subject",
            default=u""
            u"Subject line of message. This is used if you "
            u"do not specify a subject field or if the field "
            u"is empty.",
        ),
        default=u"Form Submission",
        missing_value=u"",
        required=False,
    )

    directives.write_permission(subject_field=config.EDIT_ADVANCED_PERMISSION)
    directives.read_permission(subject_field=MODIFY_PORTAL_CONTENT)
    subject_field = zope.schema.Choice(
        title=_(u"label_formmailer_subject_extract", default=u"Extract Subject From"),
        description=_(
            u"help_formmailer_subject_extract",
            default=u""
            u"Choose a form field from which you wish to extract "
            u"input for the mail subject line.",
        ),
        required=False,
        vocabulary="easyform.Fields",
    )
    directives.read_permission(body_pre=MODIFY_PORTAL_CONTENT)
    directives.widget("body_pre", TextAreaWidget)

    body_pre = RichText(
        title=_(u"label_formmailer_body_pre", default=u"Body (prepended)"),
        description=_(
            u"help_formmailer_body_pre",
            default=u"Text prepended to fields listed in mail-body",
        ),
        default=u"",
        missing_value=u"",
        default_mime_type="text/x-web-intelligent",
        allowed_mime_types=("text/x-web-intelligent",),
        output_mime_type="text/x-html-safe",
        required=False,
    )
    directives.read_permission(body_post=MODIFY_PORTAL_CONTENT)
    directives.widget("body_post", TextAreaWidget)
    body_post = RichText(
        title=_(u"label_formmailer_body_post", default=u"Body (appended)"),
        description=_(
            u"help_formmailer_body_post",
            default=u"Text appended to fields listed in mail-body",
        ),
        default=u"",
        missing_value=u"",
        default_mime_type="text/x-web-intelligent",
        allowed_mime_types=("text/x-web-intelligent",),
        output_mime_type="text/x-html-safe",
        required=False,
    )
    directives.read_permission(body_footer=MODIFY_PORTAL_CONTENT)
    directives.widget("body_footer", TextAreaWidget)
    body_footer = RichText(
        title=_(u"label_formmailer_body_footer", default=u"Body (signature)"),
        description=_(
            u"help_formmailer_body_footer",
            default=u"Text used as the footer at "
            u"bottom, delimited from the body by a dashed line.",
        ),
        default=u"",
        missing_value=u"",
        default_mime_type="text/x-web-intelligent",
        allowed_mime_types=("text/x-web-intelligent",),
        output_mime_type="text/x-html-safe",
        required=False,
    )

    directives.read_permission(showAll=MODIFY_PORTAL_CONTENT)
    showAll = zope.schema.Bool(
        title=_(u"label_mailallfields_text", default=u"Include All Fields"),
        description=_(
            u"help_mailallfields_text",
            default=u""
            u"Check this to include input for all fields "
            u"(except label and file fields). If you check "
            u"this, the choices in the pick box below "
            u"will be ignored.",
        ),
        default=True,
        required=False,
    )

    directives.read_permission(showFields=MODIFY_PORTAL_CONTENT)
    showFields = zope.schema.List(
        title=_(u"label_mailfields_text", default=u"Show Responses"),
        description=_(
            u"help_mailfields_text",
            default=u"Pick the fields whose inputs you'd like to include in "
            u"the e-mail.",
        ),
        unique=True,
        required=False,
        value_type=zope.schema.Choice(vocabulary="easyform.Fields"),
    )

    directives.read_permission(includeEmpties=MODIFY_PORTAL_CONTENT)
    includeEmpties = zope.schema.Bool(
        title=_(u"label_mailEmpties_text", default=u"Include Empties"),
        description=_(
            u"help_mailEmpties_text",
            default=u""
            u"Check this to include titles "
            u"for fields that received no input. Uncheck "
            u"to leave fields with no input out of the e-mail.",
        ),
        default=True,
        required=False,
    )

    directives.read_permission(sendCSV=MODIFY_PORTAL_CONTENT)
    sendCSV = zope.schema.Bool(
        title=_(u"label_sendCSV_text", default=u"Send CSV data attachment"),
        description=_(
            u"help_sendCSV_text",
            default=u""
            u"Check this to send a CSV file "
            u"attachment containing the values "
            u"filled out in the form.",
        ),
        default=False,
        required=False,
    )

    directives.read_permission(sendXML=MODIFY_PORTAL_CONTENT)
    sendXML = zope.schema.Bool(
        title=_(u"label_sendXML_text", default=u"Send XML data attachment"),
        description=_(
            u"help_sendXML_text",
            default=u""
            u"Check this to send an XML file "
            u"attachment containing the values "
            u"filled out in the form.",
        ),
        default=False,
        required=False,
    )

    fieldset(u"template", label=PMF("Template"), fields=["body_pt", "body_type"])
    directives.write_permission(body_pt=config.EDIT_TALES_PERMISSION)
    directives.read_permission(body_pt=MODIFY_PORTAL_CONTENT)
    body_pt = zope.schema.Text(
        title=_(u"label_formmailer_body_pt", default=u"Mail-Body Template"),
        description=_(
            u"help_formmailer_body_pt",
            default=u"This is a Zope Page Template used for rendering of "
            u"the mail-body. You don't need to modify it, but if you "
            u"know TAL (Zope's Template Attribute Language) have "
            u"the full power to customize your outgoing mails.",
        ),
        defaultFactory=default_mail_body,
        missing_value=u"",
    )

    directives.write_permission(body_type=config.EDIT_ADVANCED_PERMISSION)
    directives.read_permission(body_type=MODIFY_PORTAL_CONTENT)
    body_type = zope.schema.Choice(
        title=_(u"label_formmailer_body_type", default=u"Mail Format"),
        description=_(
            u"help_formmailer_body_type",
            default=u"Set the mime-type of the mail-body. Change this "
            u"setting only if you know exactly what you are doing. "
            u"Leave it blank for default behaviour.",
        ),
        default=u"html",
        vocabulary="easyform.MimeList",
    )
    fieldset(
        u"headers", label=_("Headers"), fields=["xinfo_headers", "additional_headers"]
    )
    directives.widget(xinfo_headers=CheckBoxFieldWidget)
    directives.write_permission(xinfo_headers=config.EDIT_TECHNICAL_PERMISSION)
    directives.read_permission(xinfo_headers=MODIFY_PORTAL_CONTENT)
    xinfo_headers = zope.schema.List(
        title=_(u"label_xinfo_headers_text", default=u"HTTP Headers"),
        description=_(
            u"help_xinfo_headers_text",
            default=u""
            u"Pick any items from the HTTP headers that "
            u"you'd like to insert as X- headers in the message.",
        ),
        unique=True,
        required=False,
        default=[u"HTTP_X_FORWARDED_FOR", u"REMOTE_ADDR", u"PATH_INFO"],
        missing_value=[u"HTTP_X_FORWARDED_FOR", u"REMOTE_ADDR", u"PATH_INFO"],
        value_type=zope.schema.Choice(vocabulary="easyform.XinfoHeaders"),
    )
    directives.write_permission(additional_headers=config.EDIT_TECHNICAL_PERMISSION)
    directives.read_permission(additional_headers=MODIFY_PORTAL_CONTENT)
    additional_headers = zope.schema.List(
        title=_(u"label_formmailer_additional_headers", default=u"Additional Headers"),
        description=_(
            u"help_formmailer_additional_headers",
            default=u"Additional e-mail-header lines. Only use "
            u"RFC822-compliant headers.",
        ),
        unique=True,
        required=False,
        value_type=zope.schema.TextLine(
            title=_(
                u"extra_header", default=u"${name} Header", mapping={u"name": u"HTTP"}
            )
        ),
    )

    fieldset(
        u"overrides",
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
        title=_(u"label_subject_override_text", default=u"Subject Expression"),
        description=_(
            u"help_subject_override_text",
            default=u"A TALES expression that will be evaluated to override "
            u"any value otherwise entered for the e-mail subject "
            u"header. Leave empty if unneeded. Your expression "
            u"should evaluate as a string. PLEASE NOTE: errors in "
            u"the evaluation of this expression will cause an error "
            u"on form display.",
        ),
        required=False,
        default=u"",
        missing_value=u"",
        constraint=isTALES,
    )

    directives.write_permission(senderOverride=config.EDIT_TALES_PERMISSION)
    directives.read_permission(senderOverride=MODIFY_PORTAL_CONTENT)
    senderOverride = zope.schema.TextLine(
        title=_(u"label_sender_override_text", default=u"Sender Expression"),
        description=_(
            u"help_sender_override_text",
            default=u"A TALES expression that will be evaluated to override "
            u'the "From" header. Leave empty if unneeded. '
            u"Your expression should evaluate as a string. "
            u"PLEASE NOTE: errors in the evaluation of this "
            u"expression will cause an error on form display.",
        ),
        required=False,
        default=u"",
        missing_value=u"",
        constraint=isTALES,
    )

    directives.write_permission(recipientOverride=config.EDIT_TALES_PERMISSION)
    directives.read_permission(recipientOverride=MODIFY_PORTAL_CONTENT)
    recipientOverride = zope.schema.TextLine(
        title=_(u"label_recipient_override_text", default=u"Recipient Expression"),
        description=_(
            u"help_recipient_override_text",
            default=u"A TALES expression that will be evaluated to override "
            u"any value otherwise entered for the recipient "
            u"e-mail address. You are strongly cautioned against using"
            u"unvalidated data from the request for this purpose. "
            u"Leave empty if unneeded. Your expression should "
            u"evaluate as a string. PLEASE NOTE: errors in the "
            u"evaluation of this expression will cause "
            u"an error on form display.",
        ),
        required=False,
        default=u"",
        missing_value=u"",
        constraint=isTALES,
    )

    directives.write_permission(ccOverride=config.EDIT_TALES_PERMISSION)
    directives.read_permission(ccOverride=MODIFY_PORTAL_CONTENT)
    ccOverride = zope.schema.TextLine(
        title=_(u"label_cc_override_text", default=u"CC Expression"),
        description=_(
            u"help_cc_override_text",
            default=u"A TALES expression that will be evaluated to override "
            u"any value otherwise entered for the CC list. You are "
            u"strongly cautioned against using unvalidated data from "
            u"the request for this purpose. Leave empty if unneeded. "
            u"Your expression should evaluate as a sequence of "
            u"strings. PLEASE NOTE: errors in the evaluation of this "
            u"expression will cause an error on form display.",
        ),
        required=False,
        default=u"",
        missing_value=u"",
        constraint=isTALES,
    )

    directives.write_permission(bccOverride=config.EDIT_TALES_PERMISSION)
    directives.read_permission(bccOverride=MODIFY_PORTAL_CONTENT)
    bccOverride = zope.schema.TextLine(
        title=_(u"label_bcc_override_text", default=u"BCC Expression"),
        description=_(
            u"help_bcc_override_text",
            default=u"A TALES expression that will be evaluated to override "
            u"any value otherwise entered for the BCC list. "
            u"You are strongly cautioned against using "
            u"unvalidated data from the request for this purpose. "
            u"Leave empty if unneeded. Your expression should "
            u"evaluate as a sequence of strings. PLEASE NOTE: errors "
            u"in the evaluation of this expression will cause "
            u"an error on form display.",
        ),
        required=False,
        default=u"",
        missing_value=u"",
        constraint=isTALES,
    )
