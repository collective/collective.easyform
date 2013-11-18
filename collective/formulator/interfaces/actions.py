from zope.interface import implements, Interface
from zope import schema as zs
from plone.directives import form
from plone.supermodel.interfaces import ISchema
from plone.schemaeditor.interfaces import INewField, IFieldFactory
from collective.formulator import formulatorMessageFactory as _

# -*- Additional Imports Here -*-


class INewAction(INewField):

    factory = zs.Choice(
        title=_(u"Action type"),
        vocabulary="FormulatorActions",
        required=True,
        )

class IActionFactory(IFieldFactory):
    """ A component that instantiates a action when called.
    """
