# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZPublisher.BaseRequest import DefaultPublishTraverse
from collective.easyform import easyformMessageFactory as _
from collective.easyform.api import get_fields
from collective.easyform.interfaces import IEasyFormFieldContext
from collective.easyform.interfaces import IEasyFormFieldsContext
from collective.easyform.interfaces import IEasyFormFieldsEditorExtender
from json import dumps
from lxml import etree
from plone.schemaeditor.browser.field.edit import EditView
from plone.schemaeditor.browser.field.edit import FieldEditForm
from plone.schemaeditor.browser.field.traversal import FieldContext
from plone.schemaeditor.browser.schema.listing import SchemaListing
from plone.schemaeditor.browser.schema.listing import SchemaListingPage
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.supermodel import loadString
from plone.supermodel.parser import SupermodelParseError
from z3c.form import button
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import getAdapters
from zope.component import queryMultiAdapter
from zope.interface import implements

try:
    from plone.schemaeditor import SchemaEditorMessageFactory as __
except ImportError:
    from plone.schemaeditor import _ as __

try:
    import plone.resourceeditor
    plone.resourceeditor  # avoid PEP 8 warning
    HAVE_RESOURCE_EDITOR = True
except ImportError:
    HAVE_RESOURCE_EDITOR = False


class EasyFormFieldContext(FieldContext):

    """ wrapper for published zope 3 schema fields
    """
    implements(IEasyFormFieldContext)


class EasyFormFieldsView(SchemaContext):
    implements(IEasyFormFieldsContext)

    schema = None

    def __init__(self, context, request):
        self.schema = get_fields(context)
        super(EasyFormFieldsView, self).__init__(
            self.schema,
            request,
            name='fields'
        )

    def publishTraverse(self, request, name):
        """ Look up the field whose name matches the next URL path element, and wrap it.
        """
        try:
            return EasyFormFieldContext(self.schema[name], self.request).__of__(self)
        except KeyError:
            return DefaultPublishTraverse(self, request).publishTraverse(request, name)

    def browserDefault(self, request):
        """ If not traversing through the schema to a field, show the SchemaListingPage.
        """
        return self, ('@@listing',)


class FieldsSchemaListing(SchemaListing):
    template = ViewPageTemplateFile('fields_listing.pt')

    @property
    def default_fieldset_label(self):
        return self.context.aq_parent.default_fieldset_label or super(FieldsSchemaListing, self).default_fieldset_label

    def handleModelEdit(self, action):
        self.request.response.redirect('@@modeleditor')


if HAVE_RESOURCE_EDITOR:
    but = button.Button("modeleditor", title=_(u'Edit XML Fields Model'))
    FieldsSchemaListing.buttons += button.Buttons(but)
    handler = button.Handler(but, FieldsSchemaListing.handleModelEdit)
    FieldsSchemaListing.handlers.addHandler(but, handler)


class EasyFormFieldsListingPage(SchemaListingPage):

    """ Form wrapper so we can get a form with layout.

        We define an explicit subclass rather than using the wrap_form method
        from plone.z3cform.layout so that we can inject the schema name into
        the form label.
    """
    form = FieldsSchemaListing
    index = ViewPageTemplateFile('model_listing.pt')


class FieldEditForm(FieldEditForm):

    @lazy_property
    def additionalSchemata(self):
        schema_context = self.context.aq_parent
        return [v for k, v in getAdapters((schema_context, self.field), IEasyFormFieldsEditorExtender)]


class EditView(EditView):
    form = FieldEditForm


class ModelEditorView(BrowserView):

    """ editor view """
    title = _(u'Edit XML Fields Model')

    def modelSource(self):
        return self.context.aq_parent.fields_model


class AjaxSaveHandler(BrowserView):

    """ handle AJAX save posts """

    def authorized(self):
        authenticator = queryMultiAdapter((self.context, self.request),
                                          name=u'authenticator')
        return authenticator and authenticator.verify()

    def save(self, source):
        self.context.aq_parent.fields_model = source

    def __call__(self):
        """ handle AJAX save post """

        if not self.authorized():
            raise Unauthorized

        source = self.request.form.get('source')
        if source:
            # Some safety measures.
            # We do not want to load entities, especially file:/// entities.
            # Also discard processing instructions.
            parser = etree.XMLParser(resolve_entities=False, remove_pis=True)
            # Is it valid XML?
            try:
                root = etree.fromstring(source, parser=parser)
            except etree.XMLSyntaxError, e:
                return dumps({
                    'success': False,
                    'message': "XMLSyntaxError: {0}".format(e.message.encode('utf8'))
                })

            # a little more sanity checking, look at first two element levels
            if root.tag != '{http://namespaces.plone.org/supermodel/schema}model':
                return dumps({
                    'success': False,
                    'message': __(u"Error: root tag must be 'model'")
                })
            for element in root.getchildren():
                if element.tag != '{http://namespaces.plone.org/supermodel/schema}schema':
                    return dumps({
                        'success': False,
                        'message': __(u"Error: all model elements must be 'schema'")
                    })

            # can supermodel parse it?
            # This is mainly good for catching bad dotted names.
            try:
                loadString(source)
            except SupermodelParseError, e:
                message = e.args[0].replace('\n  File "<unknown>"', '')
                return dumps({
                    'success': False,
                    'message': u"SuperModelParseError: {0}".format(message)
                })

            # clean up formatting sins
            source = etree.tostring(
                root,
                pretty_print=True,
                xml_declaration=True,
                encoding='utf8'
            )
            # and save
            self.save(source)

            self.request.response.setHeader('Content-Type', 'application/json')
            return dumps({'success': True, 'message': __(u"Saved")})
