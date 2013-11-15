# -*- coding: utf-8 -*-
from zope.interface import Interface, implements
from plone.dexterity.content import Item
from collective.formulator.interfaces import IFormulator
from plone.schemaeditor.interfaces import ISchemaContext


class Formulator(Item):
    implements(IFormulator)

