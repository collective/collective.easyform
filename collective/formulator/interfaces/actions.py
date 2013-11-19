from zope.interface import Invalid, implements, Interface, invariant
from zope import schema as zs
from zope.schema.interfaces import IField

from plone.directives import form
from plone.supermodel.interfaces import ISchema
from plone.schemaeditor.interfaces import INewField, IFieldFactory, ID_RE
from collective.formulator import formulatorMessageFactory as _
from plone.schemaeditor import SchemaEditorMessageFactory as __

# -*- Additional Imports Here -*-
def isValidFieldName(value):
    if not ID_RE.match(value):
        raise Invalid(__(u'Please use only letters, numbers and the following characters: _.'))
    return True


class INewAction(Interface):

    title = zs.TextLine(
        title = __(u'Title'),
        required=True
        )

    __name__ = zs.ASCIILine(
        title=__(u'Short Name'),
        description=__(u'Used for programmatic access to the field.'),
        required=True,
        constraint=isValidFieldName,
        )

    description = zs.Text(
        title=__(u'Help Text'),
        description=__(u'Shows up in the form as help text for the field.'),
        required=False
        )

    factory = zs.Choice(
        title=_(u"Action type"),
        vocabulary="FormulatorActions",
        required=True,
        )

    @invariant
    def checkTitleAndDescriptionTypes(data):
        if data.__name__ is not None and data.factory is not None:
            if data.__name__ == 'title' and data.factory.fieldcls is not TextLine:
                raise Invalid(__(u"The 'title' field must be a Text line (string) field."))
            if data.__name__ == 'description' and data.factory.fieldcls is not Text:
                raise Invalid(__(u"The 'description' field must be a Text field."))

class IActionFactory(IField):
    """ A component that instantiates a action when called.
    """
    title = zs.TextLine(title=u'Title')
