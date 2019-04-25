# -*- coding: utf-8 -*-
from Products.PageTemplates.Expressions import getEngine
from zope.tales import tales

import zope.schema.interfaces


class InvalidTALESError(zope.schema.ValidationError):
    __doc__ = u"Please enter a valid TALES expression."


def isTALES(value):
    if value.strip():
        try:
            getEngine().compile(value)
        except tales.CompilerError:
            raise InvalidTALESError
    return True
