# -*- coding: utf-8 -*-
from zope.interface import implements
from plone.dexterity.content import Item
from collective.easyform.interfaces import IEasyForm


class EasyForm(Item):
    implements(IEasyForm)
