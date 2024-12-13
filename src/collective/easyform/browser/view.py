# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_chain
from Acquisition import aq_parent
from collections import OrderedDict
from collective.easyform import easyformMessageFactory as _
from collective.easyform.api import dollar_replacer
from collective.easyform.api import filter_fields
from collective.easyform.api import get_actions
from collective.easyform.api import get_expression
from collective.easyform.api import get_schema
from collective.easyform.config import FORM_ERROR_MARKER
from collective.easyform.interfaces import IActionExtender
from collective.easyform.interfaces import IEasyFormForm
from collective.easyform.interfaces import IEasyFormThanksPage
from collective.easyform.interfaces import IEasyFormWidget
from collective.easyform.interfaces import IFieldExtender
from collective.easyform.interfaces import ISaveData
from logging import getLogger
from os.path import splitext
from plone.app.z3cform.inline_validation import InlineValidationView
from plone.autoform.form import AutoExtensibleForm
from plone.namedfile.interfaces import INamed
from plone.z3cform.layout import FormWrapper
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import form
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IErrorViewSnippet
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.schema import getFieldsInOrder
from zope.schema import ValidationError
from ZPublisher.mapply import mapply

import six


logger = getLogger("collective.easyform")
PMF = MessageFactory("plone")

try:
    from Products.CMFPlone.utils import safe_encode
except ImportError:
    # only thing needed to maintain 5.0.x compatibility
    def safe_bytes(value, encoding="utf-8"):
        """Convert text to bytes of the specified encoding."""
        if isinstance(value, six.text_type):
            value = value.encode(encoding)
        return value

    safe_encode = safe_bytes


@implementer(IEasyFormForm)
class EasyFormForm(AutoExtensibleForm, form.Form):
    """EasyForm form."""

    form_template = ViewPageTemplateFile("easyform_form.pt")
    thank_you_template = ViewPageTemplateFile("thank_you.pt")
    ignoreContext = True
    css_class = "easyformForm row"
    thanksPage = False

    # allow prefill - see Products/CMFPlone/patches/z3c_form
    allow_prefill_from_GET_request = True

    @property
    def method(self):
        return self.context.method

    @property
    def prologue(self):
        return self.context.prologue

    @property
    def epilogue(self):
        return self.context.epilogue

    @property
    def default_fieldset_label(self):
        return (
            self.context.default_fieldset_label
            or super(EasyFormForm, self).default_fieldset_label
        )

    def action(self):
        """Redefine <form action=''> attribute."""
        action = getattr(self.context, "formActionOverride")
        if action:
            action = get_expression(self.context, action)
        if not action:
            action = self.context.absolute_url()
        if self.context.forceSSL:
            action = action.replace("http://", "https://")
        return action

    @property
    def enable_form_tabbing(self):
        return self.context.form_tabbing

    @property
    def enable_autofocus(self):
        return self.context.autofocus

    @property
    def enable_unload_protection(self):
        return self.context.unload_protection

    @property
    def enableCSRFProtection(self):
        return self.context.CSRFProtection

    @property
    def label(self):
        return self.thanksPage and self.context.thankstitle or self.context.Title()

    @property
    def description(self):
        return (
            self.thanksPage
            and self.context.thanksdescription
            or self.context.Description()
        )

    @property
    def schema(self):
        return get_schema(self.context)

    def updateServerSideData(self, data):
        for fname in self.schema:
            field = self.schema[fname]
            efield = IFieldExtender(field)
            serverSide = getattr(efield, "serverSide", False)
            if not serverSide:
                continue
            fdefault = field.default
            TDefault = getattr(efield, "TDefault", None)
            value = get_expression(self.context, TDefault) if TDefault else fdefault
            data[fname] = value
        return data

    def processActions(self, fields):
        # get a list of adapters with no duplicates, retaining order
        actions = getFieldsInOrder(get_actions(self.context))
        for name, action in actions:
            if not action.required:
                continue
            # Now, see if we should execute it.
            # Check to see if execCondition exists and has contents
            execCondition = IActionExtender(action).execCondition
            if execCondition:
                doit = get_expression(self.context, execCondition)
            else:
                doit = True
            if doit and hasattr(action, "onSuccess"):
                result = action.onSuccess(fields, self.request)
                if isinstance(result, dict) and len(result):
                    return result

    def setErrorsMessage(self, errors):
        for field in errors:
            if field not in self.widgets:
                if field == FORM_ERROR_MARKER:
                    self.formErrorsMessage = errors[field]
                continue
            error = ValidationError()
            error.doc = lambda: errors[field]
            view = getMultiAdapter(
                (
                    error,
                    self.request,
                    self.widgets[field],
                    self.widgets[field].field,
                    self,
                    self.context,
                ),
                IErrorViewSnippet,
            )
            view.update()
            self.widgets.errors += (view,)
            self.widgets[field].error = view
        self.status = self.formErrorsMessage

    @button.buttonAndHandler(
        PMF(u"Submit"), name="submit", condition=lambda form: not form.thanksPage
    )
    def handleSubmit(self, action):
        unsorted_data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        unsorted_data = self.updateServerSideData(unsorted_data)
        errors = self.processActions(unsorted_data)
        if errors:
            return self.setErrorsMessage(errors)
        data = OrderedDict(
            [x for x in getFieldsInOrder(self.schema) if x[0] in unsorted_data]
        )
        data.update(unsorted_data)
        thanksPageOverride = self.context.thanksPageOverride
        if not thanksPageOverride:
            # we come back to the form itself.
            # the thanks page is handled in the __call__ method
            return
        thanksPageOverrideAction = self.context.thanksPageOverrideAction
        thanksPage = get_expression(self.context, thanksPageOverride)
        if six.PY2 and isinstance(thanksPage, six.text_type):
            thanksPage = thanksPage.encode("utf-8")
        if thanksPageOverrideAction == "redirect_to":
            self.request.response.redirect(thanksPage)
            return
        if thanksPageOverrideAction == "traverse_to":
            thanksPage = self.context.restrictedTraverse(thanksPage)
            thanksPage = mapply(thanksPage, self.request.args, self.request)
            self.request.response.write(safe_encode(thanksPage))

    @button.buttonAndHandler(
        _(u"Reset"), name="reset", condition=lambda form: form.context.useCancelButton
    )
    def handleReset(self, action):
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return self.context.absolute_url()

    def setOmitFields(self, fields):
        omit = []
        new_fields = []
        for fname, field in fields.items():
            efield = IFieldExtender(field.field)
            TEnabled = getattr(efield, "TEnabled", None)
            serverSide = getattr(efield, "serverSide", False)
            if TEnabled and not get_expression(self.context, TEnabled) or serverSide:
                omit.append(fname)
            if getattr(efield, "THidden", False):
                field.mode = HIDDEN_MODE
                field.field.ignoreRequest = False
            new_fields.append(field)
        fields = fields.__class__(*new_fields)
        if omit:
            fields = fields.omit(*omit)
        return fields

    def setThanksFields(self, fields, data):
        omit = filter_fields(self.context, self.schema, data, omit=True)
        new_fields = []
        for fname, field in fields.items():
            if field.mode == HIDDEN_MODE:
                field.mode = DISPLAY_MODE
            new_fields.append(field)
        fields = fields.__class__(*new_fields)
        if omit:
            fields = fields.omit(*omit)

        return fields

    def set_depends_on(self, fields):
        for fname, field in fields.items():
            efield = IFieldExtender(field.field)
            depends_on = getattr(efield, "depends_on", None)
            if depends_on:
                field.field.setTaggedValue("depends_on", depends_on)
        return fields

    def set_css_class(self, fields):
        for fname, field in fields.items():
            efield = IFieldExtender(field.field)
            css_class = getattr(efield, "css_class", None)
            if css_class:
                field.field.setTaggedValue("css_class", css_class)
        return fields

    def updateFields(self):
        if self.thanksPage:
            return
        super(EasyFormForm, self).updateFields()
        if not hasattr(self, "base_fields"):
            self.base_fields = self.fields
        if not hasattr(self, "base_groups"):
            self.base_groups = dict([(i.label, i.fields) for i in self.groups])
        self.fields = self.setOmitFields(self.base_fields)
        self.fields = self.set_depends_on(self.fields)
        self.fields = self.set_css_class(self.fields)
        for group in self.groups:
            group.fields = self.setOmitFields(self.base_groups.get(group.label))
            group.fields = self.set_depends_on(group.fields)
            group.fields = self.set_css_class(group.fields)

    def updateActions(self):
        super(EasyFormForm, self).updateActions()
        if "submit" in self.actions:
            if self.context.submitLabelOverride:
                self.actions["submit"].title = get_expression(
                    self.context, self.context.submitLabelOverride
                )
            else:
                self.actions["submit"].title = self.context.submitLabel
        if "reset" in self.actions:
            self.actions["reset"].title = self.context.resetLabel

    def markWidgets(self):
        for w in self.widgets.values():
            if not IEasyFormWidget.providedBy(w):
                alsoProvides(w, IEasyFormWidget)
        for g in self.groups:
            for w in g.widgets.values():
                if not IEasyFormWidget.providedBy(w):
                    alsoProvides(w, IEasyFormWidget)

    def formMaybeForceSSL(self):
        """Redirect to an https:// URL if the 'force SSL' option is on.

        However, don't do so for those with rights to edit the form,
        to avoid making the form uneditable if SSL isn't configured
        properly.  These users will still get an SSL-ified form
        action for when the form is submitted.
        """
        sm = getSecurityManager()
        if self.context.forceSSL and not sm.checkPermission(
            "cmf.ModifyPortalContent", self.context
        ):
            # Make sure we're being accessed via a secure connection
            if self.request["SERVER_URL"].startswith("http://"):
                secure_url = self.request["URL"].replace("http://", "https://")
                self.request.response.redirect(secure_url, status="movedtemporarily")

    def update(self):
        """Update form - see interfaces.IForm"""
        self.formMaybeForceSSL()
        super(EasyFormForm, self).update()
        self.markWidgets()
        self.template = self.form_template
        if self.request.method != "POST" or self.context.thanksPageOverride:
            # go with all but default thank you page rendering
            return
        # If an adapter has already set errors, don't re-run extraction and
        # validation, just bail out:
        # (we copy the logic from plone.app.z3cform at templates/macros.pt)
        if self.widgets.errors or self.status == getattr(
            self, "formErrorsMessage", None
        ):
            return
        data, errors = self.extractData()
        if errors:
            # render errors
            return
        data = self.updateServerSideData(data)
        self.thanksPage = True
        self.template = self.thank_you_template
        self.fields = self.setThanksFields(self.base_fields, data)
        for name in list(self.widgets.keys()):
            if name not in self.fields:
                del self.widgets[name]
        self.widgets.mode = self.mode = DISPLAY_MODE
        self.widgets.update()

        for group in self.groups:
            group.fields = self.setThanksFields(self.base_groups.get(group.label), data)
            for name in list(group.widgets.keys()):
                if name not in group.fields:
                    del group.widgets[name]
            group.widgets.mode = DISPLAY_MODE
            group.widgets.update()
        prologue = self.context.thanksPrologue
        epilogue = self.context.thanksEpilogue
        self.thanksPrologue = prologue and dollar_replacer(prologue.output, data)
        self.thanksEpilogue = epilogue and dollar_replacer(epilogue.output, data)
        alsoProvides(self.request, IEasyFormThanksPage)

    def header_injection(self):
        tal_expression = self.context.headerInjection
        if not tal_expression:
            return ""
        header_to_inject = get_expression(self.context, tal_expression)
        if six.PY2 and isinstance(header_to_inject, six.text_type):
            header_to_inject = header_to_inject.encode("utf-8")

        return header_to_inject

    def form_name(self):
        if self.context.nameAttribute:
            return self.context.nameAttribute
        return None


class EasyFormFormWrapper(FormWrapper):
    form = EasyFormForm
    index = ViewPageTemplateFile("easyform_layout.pt")

    def header_injection(self):
        header_injection = self.form_instance.header_injection()
        return header_injection

    def css_class(self):
        css_class = None
        if self.form_instance.thanksPage:
            css_class = u"easyform-thankspage"
        return css_class


EasyFormView = EasyFormFormWrapper


class EasyFormFormEmbedded(EasyFormForm):
    """EasyForm form embedded."""

    form_template = ViewPageTemplateFile("easyform_form_embedded.pt")


class EasyFormInlineValidationView(InlineValidationView):
    def __call__(self, fname=None, fset=None):
        self.context = EasyFormForm(self.context, self.request)
        return super(EasyFormInlineValidationView, self).__call__(fname, fset)


class GetSaveDataAdaptersView(BrowserView):
    def __call__(self, *args, **kwargs):
        """Return all contained save data adapters."""
        view = EasyFormForm(self.context, self.request)
        form = view.context
        adapters = []
        actions = get_actions(form)
        for action_id in actions:
            action = actions[action_id]
            if ISaveData.providedBy(action):
                adapters.append(action)
        return adapters


class ValidateFile(BrowserView):
    def __call__(self, value, size=1048576, allowed_types=None, forbidden_types=None):
        if not value:
            return False
        if not INamed.providedBy(value):
            return False
        if size and value.getSize() > size:
            return _(
                "msg_file_too_big",
                mapping={"size": size},
                default=u"File is bigger than allowed size of ${size} bytes!",
            )
        ftype = splitext(value.filename)[-1]
        # remove leading dot '.' from file extension
        ftype = ftype and ftype[1:].lower() or ""
        if allowed_types and ftype not in allowed_types:
            return _(
                "msg_file_not_allowed",
                mapping={"ftype": ftype.upper()},
                default=u'File type "${ftype}" is not allowed!',
            )
        if forbidden_types and ftype in forbidden_types:
            return _(
                "msg_file_not_allowed",
                mapping={"ftype": ftype.upper()},
                default=u'File type "${ftype}" is not allowed!',
            )
        return False


class GetEasyFormURL(BrowserView):
    """Helper view for calculating the right url in actions.xml.

    A url like /fields or /actions needs to be called an the easyform object.
    Danger is that you get a url like easyform/fields/fields.
    This is because /fields and /actions may look like browser views,
    but to Plone they look like content items.
    This messes up some logic in plone_context_state.

    Usage in a url_expr:

      python:context.restrictedTraverse('@@get-easyform-url')('fields')

    That will give the correct url:

      easyform-object-url/fields

    """

    def __call__(self, name=""):
        # First get the real easyform, if we can find it.
        form = self.get_form()
        if form is None:
            # We did not find the form.  View is called on the wrong item.
            # Give back a relative link anyway.
            base = "."
            if not name.startswith("/"):
                name = "/" + name
            return base + name
        base = form.absolute_url()
        if not name:
            # Do not add a needless slash at the end.
            return base
        if not name.startswith("/"):
            name = "/" + name
        return base + name

    def get_form(self):
        for item in aq_chain(self.context):
            # Note that the fields/actions contexts also have
            # portal_type EasyForm, but this is due to acquisition.
            base = aq_base(item)
            if not hasattr(base, "portal_type"):
                continue
            if base.portal_type == "EasyForm":
                return item
            if base.portal_type == "Plone Site":
                # We have gone too far already.
                return


class IsSubEasyForm(GetEasyFormURL):
    """Is this a sub object of an easyform?

    For use in actions.xml.

    If this is a sub object of easyform,
    then if has portal_type EasyForm,
    but only due to acquisition.
    """

    def __call__(self):
        if self.context.portal_type != "EasyForm":
            # The wrong portal_type.
            return False
        if hasattr(aq_base(self.context), "portal_type"):
            # An actual EasyForm
            return False
        return True


class FolderContentsView(BrowserView):
    """folder_contents view for EasyForm.

    When you are at url easyform/fields the Contents link in the toolbar
    points to easyform/folder_contents, which does not exist.
    So let's redirect to the parent.
    """

    def __call__(self):
        url = aq_parent(self.context).absolute_url() + "/folder_contents"
        self.request.response.redirect(url)
        return url


# BBB
ValidateFileSize = ValidateFile
