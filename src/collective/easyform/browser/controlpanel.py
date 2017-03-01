# -*- coding: utf-8 -*-
from collective.easyform import easyformMessageFactory as _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.registry.interfaces import IRegistry
from plone.schemaeditor.interfaces import IFieldFactory
from plone.z3cform import layout
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

import operator


def getContent(self):
        return getUtility(IRegistry).forInterface(
            self.schema,
            prefix=self.schema_prefix)


@implementer(IVocabularyFactory)
def FieldsVocabularyFactory(context=None):
    request = getRequest()
    terms = []
    for (field_id, factory) in getUtilitiesFor(IFieldFactory):
        terms.append(
            SimpleVocabulary.createTerm(
                field_id,
                factory.title,
                translate(factory.title, context=request)
            )
        )
    terms = sorted(terms, key=operator.attrgetter('title'))
    return SimpleVocabulary(terms)


class IEasyFormControlPanel(Interface):

    migrate_all_forms = schema.Bool(
        title=u'migrate all the forms to dexterity',
        description=u'This will migrate all the forms already present '
                    u'in the site from archetype to dexterity',
        required=False,
        default=False,
    )

    allowedFields = schema.List(
        title=_(u"Allowed Fields"),
        description=_(u"This Fields are available for your forms."),
        value_type=schema.Choice(
            description=_(
                u"help_registry_items",
                default=u"Select the registry items you desire to modify"
            ),
            required=False,
            vocabulary='collective.easyform.FieldsVocabulary',
        ),
        default=[],
    )


class EasyFormControlPanelForm(RegistryEditForm):
    schema = IEasyFormControlPanel
    schema_prefix = 'easyform'
    label = u'easyform Settings'

    def updateFields(self):
        super(EasyFormControlPanelForm, self).updateFields()
        self.fields['allowedFields'].widgetFactory = \
            CheckBoxFieldWidget


EasyFormControlPanelView = layout.wrap_form(
    EasyFormControlPanelForm, ControlPanelFormWrapper)
