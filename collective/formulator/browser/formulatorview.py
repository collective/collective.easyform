from zope.interface import implements, Interface
from z3c.form import form, button
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.directives import form
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from collective.formulator import formulatorMessageFactory as _


class IFormulatorView(Interface):
    """
    Formulator view interface
    """


class FormulatorForm(DefaultEditForm):
    """
    Formulator form
    """

    @property
    def schema(self):
        return self.context.schema

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"), "info")
        self.request.response.redirect(self.nextURL())
        notify(EditFinishedEvent(self.context))

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect(self.nextURL())
        notify(EditCancelledEvent(self.context))

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
        return _(u"Edit ${name}", mapping={'name': u'Formulator'})


FormulatorView = layout.wrap_form(FormulatorForm)

class IFormulatorSchemaView(Interface):
    """
    Formulator schema view interface
    """

class FormulatorSchemaView(SchemaContext):
    implements(IFormulatorSchemaView)

    def __init__(self, context, request):
        schema = self.context.schema
        super(FormulatorSchemaView, self).__init__(
            schema,
            request,
            name='schema'
        )

    def label(self):
        return _("Edit form fields")