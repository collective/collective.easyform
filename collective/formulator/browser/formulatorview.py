from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZPublisher.BaseRequest import DefaultPublishTraverse
from collective.formulator import formulatorMessageFactory as _
from collective.formulator.interfaces import (
    INewAction,
    IActionFactory,
    IFormulatorSchemaContext,
    IFormulatorActionsContext,
    IActionContext,
    IActionEditForm,
    IMailer,
    IMailerWidget,
    ICustomScript,
    ISaveData,
)
from copy import deepcopy
from plone.autoform.form import AutoExtensibleForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.memoize.instance import memoize
from plone.schemaeditor.browser.field.traversal import FieldContext
from plone.schemaeditor.browser.schema.add_field import FieldAddForm
from plone.schemaeditor.browser.schema.listing import SchemaListing, SchemaListingPage
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.schemaeditor.interfaces import IFieldEditFormSchema, IFieldEditorExtender
from plone.supermodel import loadString
from plone.supermodel.exportimport import BaseHandler
from plone.supermodel.model import Model
from plone.supermodel.serializer import serialize
from plone.z3cform import layout
from z3c.form import button, form, field
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.widget import Widget, FieldWidget
from zope import schema as zs
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import getUtilitiesFor, adapter
from zope.component import queryUtility, getAdapters
from zope.i18n import translate
from zope.interface import implements, implementer, implementer_only
from zope.schema.vocabulary import SimpleVocabulary
from zope.event import notify
from plone.schemaeditor.utils import SchemaModifiedEvent
from Acquisition import aq_parent, aq_inner


#SCHEMATA_KEY = "FormulatorSchema"
SCHEMATA_KEY = u""


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
        return ()

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


class ActionContext(FieldContext):

    """ wrapper for published zope 3 schema fields
    """
    implements(IActionContext)

    def publishTraverse(self, request, name):
        """ It's not valid to traverse to anything below a field context.
        """
        # hack to make inline validation work
        # (plone.app.z3cform doesn't know the form is the default view)
        if name == self.__name__:
            return EditView(self, request).__of__(self)

        return DefaultPublishTraverse(self, request).publishTraverse(request, name)


class FormulatorActionsView(SchemaContext):
    implements(IFormulatorActionsContext)
    #schemaEditorView = 'actions'

    def __init__(self, context, request):
        schema = get_actions(context)
        super(FormulatorActionsView, self).__init__(
            schema,
            request,
            name='actions'
        )

    def publishTraverse(self, request, name):
        """ Look up the field whose name matches the next URL path element, and wrap it.
        """
        try:
            return ActionContext(self.schema[name], self.request).__of__(self)
        except KeyError:
            return DefaultPublishTraverse(self, request).publishTraverse(request, name)


def set_schema(string, context):
    context.model = string


def updateSchema(obj, event):
    # serialize the current schema
    snew_schema = serialize_schema(obj.schema)
    # store the current schema
    set_schema(snew_schema, obj.aq_parent)


def serialize_schema(schema):
    model = Model({SCHEMATA_KEY: schema})
    sschema = serialize(model)
    return sschema


def set_actions(string, context):
    context.actions_model = string


def updateActions(obj, event):
    # serialize the current schema
    snew_schema = serialize_schema(obj.schema)
    # store the current schema
    set_actions(snew_schema, obj.aq_parent)


class FormulatorActionsListing(SchemaListing):
    template = ViewPageTemplateFile('actions_listing.pt')

    @memoize
    def _field_factory(self, field):
        field_identifier = u'%s.%s' % (
            field.__module__, field.__class__.__name__)
        if self.context.allowedFields is not None:
            if field_identifier not in self.context.allowedFields:
                return None
        return queryUtility(IActionFactory, name=field_identifier)


class FormulatorActionsListingPage(SchemaListingPage):

    """ Form wrapper so we can get a form with layout.

        We define an explicit subclass rather than using the wrap_form method
        from plone.z3cform.layout so that we can inject the schema name into
        the form label.
    """
    form = FormulatorActionsListing


class ActionAddForm(FieldAddForm):

    fields = field.Fields(INewAction)
    label = _("Add new action")
    #id = 'add-action-form'

ActionAddFormPage = layout.wrap_form(ActionAddForm)


class ActionEditForm(AutoExtensibleForm, form.EditForm):
    implements(IActionEditForm)

    def __init__(self, context, request):
        super(form.EditForm, self).__init__(context, request)
        self.field = context.field

    def getContent(self):
        return self.field

    @lazy_property
    def schema(self):
        return IFieldEditFormSchema(self.field)

    @lazy_property
    def additionalSchemata(self):
        schema_context = self.context.aq_parent
        return [v for k, v in getAdapters((schema_context, self.field), IFieldEditorExtender)]

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # clear current min/max to avoid range errors
        if 'min' in data:
            self.field.min = None
        if 'max' in data:
            self.field.max = None

        changes = self.applyChanges(data)

        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

        notify(SchemaModifiedEvent(self.context.aq_parent))
        self.redirectToParent()

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.redirectToParent()

    def redirectToParent(self):
        parent = aq_parent(aq_inner(self.context))
        url = parent.absolute_url()
        if hasattr(parent, 'schemaEditorView') and parent.schemaEditorView:
            url += '/@@' + parent.schemaEditorView

        self.request.response.redirect(url)


class EditView(layout.FormWrapper):
    form = ActionEditForm

    def __init__(self, context, request):
        super(EditView, self).__init__(context, request)
        self.field = context.field

    @lazy_property
    def label(self):
        return _(u"Edit Field '${fieldname}'", mapping={'fieldname': self.field.__name__})


def FormulatorActionsVocabularyFactory(context):
    field_factories = getUtilitiesFor(IActionFactory)
    terms = []
    for (id, factory) in field_factories:
        terms.append(SimpleVocabulary.createTerm(
            factory, translate(factory.title), factory.title))
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
        kwargs = deepcopy(self.kw)
        kwargs.update(**kw)
        return self.fieldcls(*(self.args + args), **kwargs)


IntAction = ActionFactory(
    zs.Int, _(u'label_integer_action', default=u'Integer'))


class Action(zs.Field):

    """ Base action class """
    execCondition = u""

    def __init__(self, execCondition=u"", **kw):
        self.execCondition = execCondition
        super(Action, self).__init__(**kw)


@implementer(IMailer)
class Mailer(Action):
    __doc__ = IMailer.__doc__


@implementer(ICustomScript)
class CustomScript(Action):
    __doc__ = ICustomScript.__doc__


@implementer(ISaveData)
class SaveData(Action):
    __doc__ = ISaveData.__doc__


MailerAction = ActionFactory(
    Mailer, _(u'label_mailer_action', default=u'Mailer'))
CustomScriptAction = ActionFactory(
    CustomScript, _(u'label_customscript_action', default=u'CustomScript'))
SaveDataAction = ActionFactory(
    SaveData, _(u'label_savedata_action', default=u'SaveData'))

MailerHandler = BaseHandler(Mailer)
CustomScriptHandler = BaseHandler(CustomScript)
SaveDataHandler = BaseHandler(SaveData)


@implementer_only(IMailerWidget)
class MailerWidget(widget.HTMLTextInputWidget, Widget):

    """Input type text widget implementation."""

    klass = u'mailer-widget'
    css = u'mailer'
    value = u''

    def update(self):
        super(MailerWidget, self).update()
        widget.addFieldClass(self)


@adapter(IMailer, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def MailerActionWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, MailerWidget(request))
