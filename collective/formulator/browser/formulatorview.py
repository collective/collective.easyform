from zope.interface import implements, Interface
from z3c.form import button
#from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces import IPublishTraverse
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from plone.supermodel.model import Model
from plone.supermodel.serializer import serialize
from plone.supermodel import loadString
from collective.formulator import formulatorMessageFactory as _

#SCHEMATA_KEY = "FormulatorSchema"
SCHEMATA_KEY = u""


class IFormulatorView(Interface):

    """
    Formulator view interface
    """


class FormulatorForm(DefaultEditForm):

    """
    Formulator form
    """
    ignoreContext = True
    ignoreRequest = True

    @property
    def schema(self):
        schema = get_schema(self.context)
        return schema

    @property
    def additionalSchemata(self):
        return []

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        view_url = self.context.absolute_url()
        return view_url

    def updateActions(self):
        super(FormulatorForm, self).updateActions()
        if 'save' in self.actions:
            self.actions["save"].addClass("context")
        if 'cancel' in self.actions:
            self.actions["cancel"].addClass("standalone")

    @property
    def label(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.Description()

FormulatorView = layout.wrap_form(FormulatorForm)


class IFormulatorSchemaContext(Interface):

    """
    Formulator schema view interface
    """


def get_schema(context):
    try:
        data = context.model
        schema = loadString(data).schemata.get(SCHEMATA_KEY, None)
    except Exception:
        schema = None
    return schema


class FormulatorSchemaView(SchemaContext):
    #implements(IFormulatorSchemaContext, ISchemaContext, IBrowserPublisher)
    implements(IFormulatorSchemaContext, IPublishTraverse)
    #schemaEditorView = 'fields'

    def __init__(self, context, request):
        self.basecontext = context
        schema = get_schema(context)
        super(FormulatorSchemaView, self).__init__(
            schema,
            request,
            name='fields'
        )


def set_schema(string, context):
    context.model = string


def updateSchema(object, event):
    # serialize the current schema
    snew_schema = serialize_schema(object.schema)
    # store the current schema
    set_schema(snew_schema, object.basecontext)


def serialize_schema(schema):
    model = Model({SCHEMATA_KEY: schema})
    sschema = serialize(model)
    return sschema
