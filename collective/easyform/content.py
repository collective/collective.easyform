# -*- coding: utf-8 -*-
from collective.easyform.interfaces import IEasyForm
from plone.dexterity.content import Item
from zope.interface import implements


class EasyForm(Item):
    implements(IEasyForm)
