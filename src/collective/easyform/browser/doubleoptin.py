from collective.easyform.actions import doubleoptin_confirm
from collective.easyform.actions import doubleoptin_peek
from collective.easyform.actions import doubleoptin_substitution_data
from collective.easyform.actions import get_doubleoptin_action
from collective.easyform.api import dollar_replacer
from collective.easyform.api import get_expression
from html import escape
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides


def paragraphs(text):
    """Plain text as escaped HTML paragraphs (blank line = new paragraph)."""
    result = []
    for block in (text or "").split("\n\n"):
        block = block.strip()
        if block:
            result.append("<p>{}</p>".format(escape(block).replace("\n", "<br />")))
    return "".join(result)


class DoubleOptInPendingView(BrowserView):
    """Shown right after submitting: please check your mailbox."""

    template = ViewPageTemplateFile("doubleoptin_pending.pt")

    def __call__(self):
        self.action = get_doubleoptin_action(self.context)
        return self.template()

    @property
    def title(self):
        if self.action is None:
            return self.context.Title()
        return self.action.pending_title

    @property
    def text(self):
        if self.action is None:
            return ""
        return paragraphs(self.action.pending_text)


class DoubleOptInConfirmView(BrowserView):
    """Target of the confirmation link.

    GET only shows a button, the token is consumed on POST: mail security
    scanners that open every link in an e-mail must not confirm anything.
    """

    template = ViewPageTemplateFile("doubleoptin_confirm.pt")
    status = "invalid"
    errors = None
    thanks_title = ""
    thanks_description = ""
    thanks_prologue = ""
    thanks_epilogue = ""

    def __call__(self):
        # the token is the secret; the visitor has no CSRF token here but
        # the writes (consume the token, run the actions) are intended
        alsoProvides(self.request, IDisableCSRFProtection)
        self.token = self.request.get("token", "")
        if self.request.method != "POST":
            if doubleoptin_peek(self.context, self.token) is not None:
                self.status = "ask"
            return self.template()

        self.status, payload = doubleoptin_confirm(
            self.context, self.token, self.request
        )
        if self.status == "error":
            self.errors = payload
        elif self.status == "confirmed":
            redirect = self.thanks_redirect()
            if redirect:
                self.request.response.redirect(redirect)
                return ""
            self.set_thanks_texts(payload)
        return self.template()

    def thanks_redirect(self):
        form = self.context
        if form.thanksPageOverride and form.thanksPageOverrideAction == "redirect_to":
            return get_expression(form, form.thanksPageOverride)
        return None

    def set_thanks_texts(self, fields):
        form = self.context
        data = doubleoptin_substitution_data(get_doubleoptin_action(form), form, fields)
        self.thanks_title = dollar_replacer(form.thankstitle or "", data)
        self.thanks_description = dollar_replacer(form.thanksdescription or "", data)
        if form.thanksPrologue:
            self.thanks_prologue = dollar_replacer(form.thanksPrologue.output, data)
        if form.thanksEpilogue:
            self.thanks_epilogue = dollar_replacer(form.thanksEpilogue.output, data)
