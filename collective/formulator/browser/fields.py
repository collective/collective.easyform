from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.schemaeditor.browser.schema.listing import SchemaListingPage
from zope.interface import implements

from collective.formulator.interfaces import IFormulatorFieldsContext
from collective.formulator.api import get_fields


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


class FormulatorFieldsListingPage(SchemaListingPage):

    """ Form wrapper so we can get a form with layout.

        We define an explicit subclass rather than using the wrap_form method
        from plone.z3cform.layout so that we can inject the schema name into
        the form label.
    """
    index = ViewPageTemplateFile("model_listing.pt")
