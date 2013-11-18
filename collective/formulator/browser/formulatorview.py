import copy
from collective.formulator import formulatorMessageFactory as _
from plone.dexterity.browser.edit import DefaultEditForm
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.schemaeditor.browser.schema.add_field import FieldAddForm
from plone.schemaeditor.interfaces import ISchemaContext
from plone.supermodel import loadString
from plone.supermodel.model import Model
from plone.supermodel.serializer import serialize
from plone.z3cform import layout
from z3c.form import button, form, field
from zope.component import getUtilitiesFor
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements, Interface, implementer
from zope.i18n import translate
from zope import schema as zs
from collective.formulator.interfaces import INewAction, IActionFactory


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


class IFormulatorSchemaContext(ISchemaContext):

    """
    Formulator schema view interface
    """

class IFormulatorActionsContext(ISchemaContext):

    """
    Formulator actions view interface
    """


def get_schema(context):
    try:
        data = context.model
        schema = loadString(data).schemata.get(SCHEMATA_KEY, None)
    except Exception:
        schema = None
    return schema


class FormulatorSchemaView(SchemaContext):
    implements(IFormulatorSchemaContext)
    #schemaEditorView = 'fields'

    def __init__(self, context, request):
        self.basecontext = context
        schema = get_schema(context)
        super(FormulatorSchemaView, self).__init__(
            schema,
            request,
            name='fields'
        )


def get_actions(context):
    try:
        data = context.actions_model
        schema = loadString(data).schemata.get(SCHEMATA_KEY, None)
    except Exception:
        schema = None
    return schema


class FormulatorActionsView(SchemaContext):
    implements(IFormulatorActionsContext)
    #schemaEditorView = 'actions'

    def __init__(self, context, request):
        self.basecontext = context
        schema = get_actions(context)
        super(FormulatorActionsView, self).__init__(
            schema,
            request,
            name='actions'
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

def set_actions(string, context):
    context.actions_model = string


def updateActions(object, event):
    # serialize the current schema
    snew_schema = serialize_schema(object.schema)
    # store the current schema
    set_actions(snew_schema, object.basecontext)



class ActionAddForm(FieldAddForm):

    fields = field.Fields(INewAction)
    label = _("Add new action")
    id = 'add-action-form'

ActionAddFormPage = layout.wrap_form(ActionAddForm)

def FormulatorActionsVocabularyFactory(context):
    field_factories = getUtilitiesFor(IActionFactory)
    terms = []
    for (id, factory) in field_factories:
        terms.append(SimpleVocabulary.createTerm(factory, translate(factory.title), factory.title))
    return SimpleVocabulary(terms)

class ActionFactory(object):
    implements(IActionFactory)

    title = u''

    def __init__(self, fieldcls, title, *args, **kw):
        self.fieldcls = fieldcls
        self.title = title
        self.args = args
        self.kw = kw

    def __call__(self, *args, **kw):
        kwargs = copy.deepcopy(self.kw)
        kwargs.update(**kw)
        return self.fieldcls(*(self.args+args), **kwargs)


IntAction = ActionFactory(zs.Int, _(u'label_integer_action', default=u'Integer'))


class IMailer(zs.interfaces.IField):
    """Field represents Form Mailer."""

@implementer(IMailer)
class Mailer(zs.Field):
    __doc__ = IMailer.__doc__

MailerAction = ActionFactory(Mailer, _(u'label_mailer_action', default=u'Mailer'))

import plone.supermodel.exportimport
MailerHandler = plone.supermodel.exportimport.BaseHandler(Mailer)


import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser import widget

class IMailerWidget(interfaces.IWidget):
    """Mailer widget."""


@zope.interface.implementer_only(IMailerWidget)
class MailerWidget(widget.HTMLTextInputWidget, Widget):
    """Input type text widget implementation."""

    klass = u'mailer-widget'
    css = u'mailer'
    value = u''

    def update(self):
        super(MailerWidget, self).update()
        widget.addFieldClass(self)


@zope.component.adapter(IMailer, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def MailerActionWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, MailerWidget(request))