# -*- coding: utf-8 -*-

from collective.easyform.api import set_actions
from collective.easyform.api import set_fields


def updateFields(obj, event):
    set_fields(obj.aq_parent, obj.schema)


def updateActions(obj, event):
    set_actions(obj.aq_parent, obj.schema)
