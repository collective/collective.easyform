# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory

formulatorMessageFactory = MessageFactory('collective.formulator')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
