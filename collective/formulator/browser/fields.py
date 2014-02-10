# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.schemaeditor.browser.schema.listing import SchemaListing
from plone.schemaeditor.browser.schema.listing import SchemaListingPage
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from zope.interface import implements

from collective.formulator.api import get_fields
from collective.formulator.interfaces import IFormulatorFieldsContext


class FormulatorFieldsView(SchemaContext):
    implements(IFormulatorFieldsContext)

    schema = None

    def __init__(self, context, request):
        schema = get_fields(context)
        super(FormulatorFieldsView, self).__init__(
            schema,
            request,
            name='fields'
        )

    def browserDefault(self, request):
        """ If not traversing through the schema to a field, show the SchemaListingPage.
        """
        return self, ('@@fields',)


class FieldsSchemaListing(SchemaListing):

    @property
    def default_fieldset_label(self):
        return self.context.aq_parent.default_fieldset_label or super(FieldsSchemaListing, self).default_fieldset_label


class FormulatorFieldsListingPage(SchemaListingPage):

    """ Form wrapper so we can get a form with layout.

        We define an explicit subclass rather than using the wrap_form method
        from plone.z3cform.layout so that we can inject the schema name into
        the form label.
    """
    form = FieldsSchemaListing
    index = ViewPageTemplateFile('model_listing.pt')
