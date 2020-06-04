# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.easyform import easyformMessageFactory as _
from collective.easyform.api import get_actions
from collective.easyform.api import get_context
from collective.easyform.api import get_schema
from collective.easyform.browser.fields import AjaxSaveHandler
from collective.easyform.interfaces import IActionEditForm
from collective.easyform.interfaces import IActionFactory
from collective.easyform.interfaces import IEasyFormActionContext
from collective.easyform.interfaces import IEasyFormActionsContext
from collective.easyform.interfaces import IEasyFormActionsEditorExtender
from collective.easyform.interfaces import IExtraData
from collective.easyform.interfaces import INewAction
from collective.easyform.interfaces import ISaveData
from collective.easyform.interfaces import ISavedDataFormWrapper
from plone.autoform.form import AutoExtensibleForm
from plone.memoize.instance import memoize
from plone.schemaeditor.browser.field.traversal import FieldContext
from plone.schemaeditor.browser.schema.add_field import FieldAddForm
from plone.schemaeditor.browser.schema.listing import SchemaListing
from plone.schemaeditor.browser.schema.listing import SchemaListingPage
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.schemaeditor.interfaces import IFieldEditFormSchema
from plone.schemaeditor.utils import SchemaModifiedEvent
from plone.z3cform import layout
from plone.z3cform.crud import crud
from plone.z3cform.interfaces import IDeferSecurityCheck
from plone.z3cform.traversal import WrapperWidgetTraversal
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import adapter
from zope.component import getAdapters
from zope.component import queryUtility
from zope.event import notify
from zope.i18nmessageid import MessageFactory
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import getFieldsInOrder
from ZPublisher.BaseRequest import DefaultPublishTraverse


PMF = MessageFactory("plone")


@adapter(ISavedDataFormWrapper, IBrowserRequest)
class SavedDataTraversal(WrapperWidgetTraversal):
    def traverse(self, name, ignored):
        form = self._prepareForm()
        alsoProvides(self.request, IDeferSecurityCheck)
        form.update()
        noLongerProvides(self.request, IDeferSecurityCheck)
        for subform in form.subforms:
            if not hasattr(subform, "subforms"):
                continue
            for subsubform in subform.subforms:
                if not name.startswith(subsubform.prefix):
                    continue
                for id_ in subsubform.widgets:
                    subformname = subsubform.prefix + subsubform.widgets.prefix + id_
                    if subformname == name:
                        target = self._form_traverse(subsubform, id_)
                        target.__parent__ = aq_inner(self.context)
                        return target
        return super(SavedDataTraversal, self).traverse(name, ignored)


class SavedDataView(BrowserView):
    def items(self):
        return [
            (name, action.__doc__)
            for name, action in getFieldsInOrder(get_actions(self.context))
            if ISaveData.providedBy(action)
        ]


class DataWrapper(dict):
    def __init__(self, sid, data, parent):
        self.__sid__ = sid
        self.update(data)
        self.__parent__ = parent


class SavedDataForm(crud.CrudForm):
    template = ViewPageTemplateFile("saveddata_form.pt")
    addform_factory = crud.NullForm

    @property
    def field(self):
        return self.context.field

    @property
    def name(self):
        return self.field.__name__

    @property
    def get_schema(self):
        return get_schema(get_context(self.field))

    def description(self):
        return _(u"${items} input(s) saved", mapping={"items": self.field.itemsSaved()})

    @property
    def update_schema(self):
        fields = field.Fields(self.get_schema)
        showFields = getattr(self.field, "showFields", [])
        if showFields:
            fields = fields.select(*showFields)
        return fields

    @property
    def view_schema(self):
        ExtraData = self.field.ExtraData
        if ExtraData:
            return field.Fields(IExtraData).select(*ExtraData)

    def get_items(self):
        return [
            (key, DataWrapper(key, value, self.context))
            for key, value in self.field.getSavedFormInputItems()
        ]

    # def add(self, data):
    # storage = self.context._inputStorage

    def before_update(self, item, data):
        id_ = item.__sid__
        item.update(data)
        self.field.setDataRow(id_, item.copy())

    def remove(self, id_and_item):
        (id, item) = id_and_item
        self.field.delDataRow(id)

    @button.buttonAndHandler(PMF(u"Download"), name="download")
    def handleDownload(self, action):
        pass

    @button.buttonAndHandler(_(u"Clear all"), name="clearall")
    def handleClearAll(self, action):
        self.field.clearSavedFormInput()


@implementer(ISavedDataFormWrapper)
class SavedDataFormWrapper(layout.FormWrapper):
    def __call__(self):
        if hasattr(self.request, "form.buttons.download"):
            self.context.field.download(self.request.response)
            return u""
        else:
            return super(SavedDataFormWrapper, self).__call__()


ActionSavedDataView = layout.wrap_form(
    SavedDataForm, __wrapper_class=SavedDataFormWrapper
)


@implementer(IEasyFormActionContext)
class EasyFormActionContext(FieldContext):
    """Wrapper for published zope 3 schema fields.
    """

    def publishTraverse(self, request, name):
        """It's not valid to traverse to anything below a field context.
        """
        # hack to make inline validation work
        # (plone.app.z3cform doesn't know the form is the default view)
        if name == self.__name__:
            return ActionEditView(self, request)

        return DefaultPublishTraverse(self, request).publishTraverse(request, name)


@implementer(IEasyFormActionsContext)
class EasyFormActionsView(SchemaContext):

    schema = None

    def __init__(self, context, request):
        self.schema = get_actions(context)
        super(EasyFormActionsView, self).__init__(self.schema, request, name="actions")

    def publishTraverse(self, request, name):
        """Look up the field whose name matches the next URL path element,
        and wrap it.
        """
        try:
            return EasyFormActionContext(self.schema[name], self.request).__of__(self)
        except KeyError:
            return DefaultPublishTraverse(self, request).publishTraverse(request, name)

    def browserDefault(self, request):
        """If not traversing through the schema to a field, show the
        SchemaListingPage.
        """
        return self, ("@@listing",)


class EasyFormActionsListing(SchemaListing):
    template = ViewPageTemplateFile("actions_listing.pt")

    @memoize
    def _field_factory(self, field):
        field_identifier = u"{0}.{1}".format(field.__module__, field.__class__.__name__)
        return queryUtility(IActionFactory, name=field_identifier)

    @button.buttonAndHandler(PMF(u"Save"))
    def handleSaveDefaults(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        for fname, value in data.items():
            self.context.schema[fname].required = value
        notify(SchemaModifiedEvent(self.context))

        # update widgets to take the new defaults into account
        self.updateWidgets()
        self.request.response.redirect(self.context.absolute_url())

    def handleModelEdit(self, action):
        self.request.response.redirect("@@modeleditor")


class EasyFormActionsListingPage(SchemaListingPage):
    """Form wrapper so we can get a form with layout.

    We define an explicit subclass rather than using the wrap_form method
    from plone.z3cform.layout so that we can inject the schema name into
    the form label.
    """

    form = EasyFormActionsListing
    index = ViewPageTemplateFile("model_listing.pt")


class ActionAddForm(FieldAddForm):

    fields = field.Fields(INewAction)
    label = _("Add new action")


ActionAddFormPage = layout.wrap_form(ActionAddForm)


@implementer(IActionEditForm)
class ActionEditForm(AutoExtensibleForm, form.EditForm):
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
        adapters = getAdapters(
            (schema_context, self.field), IEasyFormActionsEditorExtender
        )
        return [v for k, v in adapters]

    @button.buttonAndHandler(PMF(u"Save"), name="save")
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        changes = self.applyChanges(data)

        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

        notify(SchemaModifiedEvent(self.context.aq_parent))
        self.redirectToParent()

    @button.buttonAndHandler(PMF(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        self.redirectToParent()

    def redirectToParent(self):
        parent = aq_parent(aq_inner(self.context))
        url = parent.absolute_url()
        self.request.response.redirect(url)


class ActionEditView(layout.FormWrapper):
    form = ActionEditForm

    def __init__(self, context, request):
        super(ActionEditView, self).__init__(context, request)
        self.field = context.field

    @lazy_property
    def label(self):
        return _(
            u"Edit Action '${fieldname}'", mapping={"fieldname": self.field.__name__}
        )


but = button.Button("modeleditor", title=_(u"Edit XML Actions Model"))
EasyFormActionsListing.buttons += button.Buttons(but)
handler = button.Handler(but, EasyFormActionsListing.handleModelEdit)
EasyFormActionsListing.handlers.addHandler(but, handler)


class ModelEditorView(BrowserView):
    """Editor view
    """

    title = _(u"Edit XML Actions Model")

    def modelSource(self):
        return self.context.aq_parent.actions_model


class AjaxSaveHandler(AjaxSaveHandler):
    """Handle AJAX save posts
    """

    def save(self, source):
        self.context.aq_parent.actions_model = source
