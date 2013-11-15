from zope.component import (
    getUtility,
    provideAdapter,
    adapter,
    adapts,
    provideUtility,
    getUtilitiesFor,
)
from zope.schema.interfaces import IField
from zope.interface import implements, Interface
from z3c.form import form, button
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
#from plone.directives import form
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces import IPublishTraverse
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.schemaeditor.interfaces import ISchemaContext
from plone.schemaeditor.interfaces import IFieldEditorExtender
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from z3c.form import field
from plone.supermodel.model import Model, finalizeSchemas, SchemaClass
from plone.supermodel.serializer import serialize
from plone.supermodel import loadString
from collective.formulator.interfaces import IFormulator
from collective.formulator import formulatorMessageFactory as _

#SCHEMATA_KEY = "FormulatorSchema"
SCHEMATA_KEY = u""

# class FormulatorSchemaContext(object):
    #schemaEditorView = 'fields'
    #additionalSchemata = ()
    # allowedFields = None  # all fields

    #@property
    # def schema(self):
        # print "schema"
        #context = self.context
        # return context.schema


# provideAdapter(
    # FormulatorSchemaContext,
    # adapts=(IFormulator,),
    # provides=ISchemaContext)


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

    #def update(self):
        #self.fields = field.Fields(self.context.schema)
        #super(FormulatorForm, self).update()

    @property
    def schema(self):
        #schema = getSchema(self.context)
        #schema = copy_schema(schema)
        #print "view:schema", self.context, self.context.schema, self.context.model, schema
        #import pdb; pdb.set_trace()
        schema = get_edited_schema(self.context)
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
        #IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"), "info")
        self.request.response.redirect(self.nextURL())
        # notify(EditFinishedEvent(self.context))

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        #IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect(self.nextURL())
        # notify(EditCancelledEvent(self.context))

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

#@adapter(IFormulatorSchemaContext, IField)
# def get_field_schema(schema_context, field):
    # print "get_field_schema"
    # return IField

# provideAdapter(
    # get_field_schema,
    # provides=IFieldEditorExtender,
    # name='collective.formulator.fields')


def getSchema(context):
    """
    """
    attrs = dict([(n, context.schema[n])
                  for n in context.schema])
    print "getSchema1", context.schema.getTaggedValueTags()
    ttwschema = get_edited_schema(context)
    if ttwschema:
        attrs.update(dict([(a, ttwschema[a]) for a in ttwschema]))
    schema = SchemaClass(SCHEMATA_KEY,
                         bases=(context.schema,),
                         attrs=attrs)
    print "getSchema2", schema.getTaggedValueTags()
    finalizeSchemas(schema)
    print "getSchema3", schema.getTaggedValueTags()
    return schema


def get_schema(context):
    print "get_schema", context.model
    return context.model


def load_schema(string):
    schema = loadString(string).schemata.get(SCHEMATA_KEY, None)
    #schema = loadString(string).schema
    return schema


def get_edited_schema(context):
    try:
        data = get_schema(context)
        oschema = load_schema(data)
        print "get_edited_schema", oschema.getTaggedValueTags()
        #import pdb; pdb.set_trace()
    except Exception, e:
        oschema = None
    #print "get_edited_schema", schema
    return oschema


def copy_schema(schema):
    fields = {}
    for item in schema:
        fields[item] = schema[item]
    oschema = SchemaClass(SCHEMATA_KEY, attrs=fields)
    print "copy_schema", schema.getTaggedValueTags()
    # copy base tagged values
    for i in schema.getTaggedValueTags():
        oschema.setTaggedValue(
            item, schema.queryTaggedValue(i))
    finalizeSchemas(oschema)
    return oschema


class FormulatorSchemaView(SchemaContext):
    #implements(IFormulatorSchemaContext, ISchemaContext, IBrowserPublisher)
    implements(IFormulatorSchemaContext, IPublishTraverse)
    #schemaEditorView = 'fields'

    def __init__(self, context, request):
        self.basecontext = context
        #baseSchema = getSchema(context)
        #schema = copy_schema(baseSchema)
        schema = get_edited_schema(context)
        #finalizeSchemas(schema)
        #schema = getSchema(context)
        print "__init__", context, schema
        super(FormulatorSchemaView, self).__init__(
            schema,
            request,
            name='fields'
        )
        print "self.schema", self.basecontext, self.schema

    def label(self):
        return _("Edit form fields")

    def publishTraverse(self, request, name):
        """ Look up the field whose name matches the next URL path element, and wrap it.
        """
        print "publishTraverse", name
        return super(FormulatorSchemaView, self).publishTraverse(request, name)

#FormulatorSchemaView = layout.wrap_form(FormulatorSchemaForm)


def set_schema(string, context):
    context.model = string


def updateSchema(object, event):
    print 'updateSchema', object, object.schema, object.basecontext
    # serialize the current schema
    snew_schema = serialize_schema(object.schema, object.basecontext)
    # store the current schema
    set_schema(snew_schema, object.basecontext)


def serialize_schema(schema, context):
    print 'serialize_schema0', schema, context
    model = Model({SCHEMATA_KEY: schema})
    sschema = serialize(model)
    print 'serialize_schema1', sschema
    return sschema
