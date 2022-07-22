# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Acquisition import aq_parent
from collective.easyform import easyformMessageFactory as _
from collective.easyform.api import get_schema
from collective.easyform.interfaces import IEasyFormFieldContext
from collective.easyform.interfaces import IEasyFormFieldsContext
from collective.easyform.interfaces import IEasyFormFieldsEditorExtender
from lxml import etree
from plone import api
from plone.schemaeditor.browser.field.edit import EditView
from plone.schemaeditor.browser.field.edit import FieldEditForm
from plone.schemaeditor.browser.field.traversal import FieldContext
from plone.schemaeditor.browser.schema.listing import SchemaListing
from plone.schemaeditor.browser.schema.listing import SchemaListingPage
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.supermodel.parser import SupermodelParseError
from Products.CMFPlone.utils import safe_bytes
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import getAdapters
from zope.component import queryMultiAdapter
from zope.interface import implementer
from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.utils import safe_unicode

import html

NAMESPACE = "{http://namespaces.plone.org/supermodel/schema}"

try:
    from plone.schemaeditor import SchemaEditorMessageFactory as __
except ImportError:
    from plone.schemaeditor import _ as __

try:
    import plone.resourceeditor

    plone.resourceeditor  # avoid PEP 8 warning
    HAVE_RESOURCE_EDITOR = True
except ImportError:  # pragma: no cover
    HAVE_RESOURCE_EDITOR = False


@implementer(IEasyFormFieldContext)
class EasyFormFieldContext(FieldContext):
    """Wrapper for published zope 3 schema fields."""


@implementer(IEasyFormFieldsContext)
class EasyFormFieldsView(SchemaContext):

    schema = None

    def __init__(self, context, request):
        self.schema = get_schema(context)
        super(EasyFormFieldsView, self).__init__(self.schema, request, name="fields")

    def publishTraverse(self, request, name):
        """Look up the field whose name matches the next URL path element,
        and wrap it.
        """
        try:
            return EasyFormFieldContext(self.schema[name], self.request).__of__(self)
        except KeyError:
            return DefaultPublishTraverse(self, request).publishTraverse(request, name)

    def browserDefault(self, request):
        """If not traversing through the schema to a field, show the
        SchemaListingPage.
        """
        return self, ("@@listing",)

    @property
    def allowedFields(self):
        fields = api.portal.get_registry_record("easyform.allowedFields")
        return fields


class FieldsSchemaListing(SchemaListing):
    template = ViewPageTemplateFile("fields_listing.pt")

    @property
    def default_fieldset_label(self):
        return (
            self.context.aq_parent.default_fieldset_label
            or super(FieldsSchemaListing, self).default_fieldset_label
        )

    def handleModelEdit(self, action):
        self.request.response.redirect("@@modeleditor")

    @button.buttonAndHandler(
        _(u'Save'),
    )
    def handleSave(self, action):
        super(FieldsSchemaListing, self).handleSaveDefaults(self, action)
        return self.request.RESPONSE.redirect(aq_parent(self.context).absolute_url())


if HAVE_RESOURCE_EDITOR:
    but = button.Button("modeleditor", title=_(u"Edit XML Fields Model"))
    FieldsSchemaListing.buttons += button.Buttons(but)
    handler = button.Handler(but, FieldsSchemaListing.handleModelEdit)
    FieldsSchemaListing.handlers.addHandler(but, handler)


class EasyFormFieldsListingPage(SchemaListingPage):
    """Form wrapper so we can get a form with layout.

    We define an explicit subclass rather than using the wrap_form method
    from plone.z3cform.layout so that we can inject the schema name into
    the form label.
    """

    form = FieldsSchemaListing
    index = ViewPageTemplateFile("model_listing.pt")


class FieldEditForm(FieldEditForm):
    @lazy_property
    def additionalSchemata(self):
        schema_context = self.context.aq_parent
        adapters = getAdapters(
            (schema_context, self.field), IEasyFormFieldsEditorExtender
        )
        return [v for k, v in adapters]


class EditView(EditView):
    form = FieldEditForm


class ModelEditorView(BrowserView):
    """Editor view.
    Mostly stolen from plone.app.dexterity.browser.modeleditor.ModelEditorView
    """

    template = ViewPageTemplateFile("modeleditor.pt")

    title = _(u"Edit XML Fields Model")

    def modelSource(self):
        return self.context.aq_parent.fields_model

    def authorized(self, context, request):
        authenticator = queryMultiAdapter((context, request), name=u"authenticator")
        return authenticator and authenticator.verify()

    def save(self, source):
        self.context.aq_parent.fields_model = source

    def __call__(self):
        """View and eventually save the form."""

        save = "form.button.save" in self.request.form
        source = self.request.form.get("source")
        if save and source:

            # First, check for authenticator
            if not self.authorized(self.context, self.request):
                raise Unauthorized

            # Is it valid XML?
            # Some safety measures.
            # We do not want to load entities, especially file:/// entities.
            # Also discard processing instructions.
            #
            source = safe_bytes(source)
            parser = etree.XMLParser(resolve_entities=False, remove_pis=True)
            try:
                root = etree.fromstring(source, parser=parser)
            except etree.XMLSyntaxError as e:
                IStatusMessage(self.request).addStatusMessage(
                    "XMLSyntaxError: {0}".format(html.escape(safe_unicode(e.args[0]))),
                    "error",
                )
                return super().__call__()

            # a little more sanity checking, look at first two element levels
            if root.tag != NAMESPACE + "model":
                IStatusMessage(self.request).addStatusMessage(
                    _(u"Error: root tag must be 'model'"),
                    "error",
                )
                return super().__call__()

            for element in root.getchildren():
                if element.tag != NAMESPACE + "schema":
                    IStatusMessage(self.request).addStatusMessage(
                        _(u"Error: all model elements must be 'schema'"),
                        "error",
                    )
                    return super().__call__()

            # can supermodel parse it?
            # This is mainly good for catching bad dotted names.
            try:
                plone.supermodel.loadString(source, policy=u"dexterity")
            except SupermodelParseError as e:
                message = e.args[0].replace('\n  File "<unknown>"', "")
                IStatusMessage(self.request).addStatusMessage(
                    u"SuperModelParseError: {0}".format(html.escape(message)),
                    "error",
                )
                return super().__call__()

            # clean up formatting sins
            source = etree.tostring(
                root, pretty_print=True, xml_declaration=True, encoding="utf8"
            )
            # and save
            self.save(source)
        # import pdb; pdb.set_trace()
        return self.template()
