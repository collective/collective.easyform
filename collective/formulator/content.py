# -*- coding: utf-8 -*-
from zope.interface import implements
from plone.dexterity.content import Item
from collective.formulator.interfaces import IFormulator


class Formulator(Item):
    implements(IFormulator)
