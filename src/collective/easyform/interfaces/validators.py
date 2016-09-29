# -*- coding: utf-8 -*-
from Products.PageTemplates.Expressions import getEngine

import zope.interface
import zope.schema.interfaces
import zope.tales as tales


class InvalidTALESError(zope.schema.ValidationError):
    __doc__ = u'Please enter a valid TALES expression.'


def isTALES(value):
    if value.strip():
        try:
            getEngine().compile(value)
        except tales.CompilerError:
            raise InvalidTALESError
    return True
