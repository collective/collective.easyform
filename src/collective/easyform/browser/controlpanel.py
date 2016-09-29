# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class IEasyFormControlPanel(Interface):

    migrate_all_forms = schema.Bool(
        title=u'migrate all the forms to dexterity',
        description=u'This will migrate all the forms already present '
                    u'in the site from archetype to dexterity',
        required=False,
        default=False,
    )


class EasyFormControlPanelForm(RegistryEditForm):
    schema = IEasyFormControlPanel
    schema_prefix = "easyform"
    label = u'easyform Settings'


EasyFormControlPanelView = layout.wrap_form(
    EasyFormControlPanelForm, ControlPanelFormWrapper)
