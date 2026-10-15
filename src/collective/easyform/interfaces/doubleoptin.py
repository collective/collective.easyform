from .actions import IAction
from collective.easyform import easyformMessageFactory as _
from zope.globalrequest import getRequest
from zope.i18n import translate

import zope.schema


def default_doi_subject():
    return translate(_("Please confirm your submission"), context=getRequest())


def default_doi_body():
    return translate(
        _(
            "default_doi_body",
            default=(
                "Hello,\n\n"
                "someone entered this e-mail address in the form "
                '"${form_title}". To complete the submission, please confirm '
                "it by opening the following link:\n\n"
                "${confirm_url}\n\n"
                "The link is valid for ${expiry_hours} hours. If you did not "
                "fill in this form, simply ignore this e-mail - nothing will "
                "be submitted without your confirmation."
            ),
        ),
        context=getRequest(),
    )


def default_doi_pending_title():
    return translate(_("Please confirm your e-mail address"), context=getRequest())


def default_doi_pending_text():
    return translate(
        _(
            "default_doi_pending_text",
            default=(
                "We have sent a confirmation link to the e-mail address you "
                "entered. Your submission is only complete once you have "
                "opened that link. If the e-mail does not arrive, please "
                "check your spam folder."
            ),
        ),
        context=getRequest(),
    )


class IDoubleOptIn(IAction):
    """A form action adapter that holds a submission back until the entered
    e-mail address confirmed it via a token link. Only then the remaining
    actions of the form (mailer, save data, ...) are executed."""

    email_field = zope.schema.Choice(
        title=_("label_doi_email_field", default="E-mail field"),
        description=_(
            "help_doi_email_field",
            default="The form field holding the e-mail address that has to "
            "confirm the submission.",
        ),
        vocabulary="easyform.Fields",
        required=True,
    )

    msg_subject = zope.schema.TextLine(
        title=_("label_doi_subject", default="Subject of the confirmation e-mail"),
        defaultFactory=default_doi_subject,
        required=True,
    )

    body = zope.schema.Text(
        title=_("label_doi_body", default="Text of the confirmation e-mail"),
        description=_(
            "help_doi_body",
            default="Plain text. Placeholders: ${confirm_url} (the confirmation "
            "link, required), ${expiry_hours}, ${form_title}, ${email} and "
            "${<field name>} for any form field.",
        ),
        defaultFactory=default_doi_body,
        required=True,
    )

    expiry_hours = zope.schema.Int(
        title=_(
            "label_doi_expiry_hours",
            default="Validity of the confirmation link (hours)",
        ),
        default=48,
        min=1,
        required=True,
    )

    pending_title = zope.schema.TextLine(
        title=_(
            "label_doi_pending_title",
            default="Title of the page shown after submitting the form",
        ),
        defaultFactory=default_doi_pending_title,
        required=True,
    )

    pending_text = zope.schema.Text(
        title=_(
            "label_doi_pending_text",
            default="Text of the page shown after submitting the form",
        ),
        defaultFactory=default_doi_pending_text,
        required=True,
    )
