# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import getUtility
from zope.interface import Interface


def getContent(self):
    return getUtility(IRegistry).forInterface(self.schema, prefix=self.schema_prefix)


class IEasyFormControlPanel(Interface):

    allowedFields = schema.List(
        title=_(u"Allowed Fields"),
        description=_(u"These Fields are available for your forms."),
        value_type=schema.Choice(
            required=False,
            vocabulary="easyform.SchemaEditorFields",
        ),
        default=[],
    )

    csv_delimiter = schema.TextLine(
        title=_(u"CSV delimiter"),
        max_length=1,
        description=_(u"Set the default delimiter for CSV download."),
        required=True,
        default=u",",
    )


class EasyFormControlPanelForm(RegistryEditForm):
    schema = IEasyFormControlPanel
    schema_prefix = "easyform"
    label = _(u"easyform Settings")

    def updateFields(self):
        super(EasyFormControlPanelForm, self).updateFields()
        self.fields["allowedFields"].widgetFactory = CheckBoxFieldWidget


EasyFormControlPanelView = layout.wrap_form(
    EasyFormControlPanelForm, ControlPanelFormWrapper
)
